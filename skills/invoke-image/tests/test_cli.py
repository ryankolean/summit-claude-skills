import json
from pathlib import Path

import pytest

import invoke

FIXTURE = Path(__file__).parent / "fixtures" / "skill"


def run(capsys, *argv):
    code = invoke.main(["--skill-dir", str(FIXTURE), *argv])
    captured = capsys.readouterr()
    return code, captured.out, captured.err


@pytest.fixture
def repo(tmp_path, monkeypatch):
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def add_brand(repo):
    (repo / ".claude").mkdir()
    (repo / ".claude" / "image-brand.json").write_text(
        json.dumps({"client": "Fly Trap", "brand": "diner red", "avoid": ["text"]})
    )


def test_dry_run_without_brand(repo, capsys):
    code, out, _ = run(capsys, "gen", "--genre", "test-photo", "--subject", "red apple", "--seed", "5", "--dry-run")
    assert code == 0
    nodes = json.loads(out)["graph"]["nodes"]
    assert nodes["pos"]["prompt"] == "red apple, photograph"
    assert nodes["noise"] == {"id": "noise", "type": "noise", "seed": 5, "width": 1024, "height": 1024}
    assert nodes["model"]["model"] == {"key": "k-sdxl"}
    assert nodes["l2i"]["board"] == {"board_id": "dry-run"}
    assert not (repo / "generated").exists()


def test_dry_run_draft_and_aspect(repo, capsys):
    code, out, _ = run(capsys, "gen", "--genre", "test-photo", "--subject", "x", "--seed", "1",
                       "--aspect", "16:9", "--draft", "--dry-run")
    data = json.loads(out)
    assert code == 0 and (data["width"], data["height"], data["steps"]) == (1344, 768, 12)


def test_dry_run_with_brand(repo, capsys):
    add_brand(repo)
    code, out, _ = run(capsys, "gen", "--genre", "test-photo", "--subject", "pie", "--seed", "1", "--dry-run")
    data = json.loads(out)
    assert code == 0
    assert data["positive"] == "pie, photograph, diner red"
    assert data["negative"] == "blurry, text"


def test_noncommercial_model_refused_for_brand(repo, capsys):
    add_brand(repo)
    code, _, err = run(capsys, "gen", "--genre", "test-photo", "--subject", "pie", "--model", "test-nc", "--dry-run")
    assert code == 2 and "cc-by-nc-4.0" in err


def test_noncommercial_model_allowed_without_brand(repo, capsys):
    code, _, _ = run(capsys, "gen", "--genre", "test-photo", "--subject", "pie", "--model", "test-nc",
                     "--seed", "1", "--dry-run")
    assert code == 0


def test_bad_aspect_exit_2(repo, capsys):
    code, _, err = run(capsys, "gen", "--genre", "test-photo", "--subject", "pie", "--aspect", "5:4", "--dry-run")
    assert code == 2 and "16:9" in err


def test_unknown_genre_exit_2(repo, capsys):
    code, _, err = run(capsys, "gen", "--genre", "nope", "--subject", "pie", "--dry-run")
    assert code == 2 and "test-photo" in err


def test_version_gate():
    with pytest.raises(invoke.VersionMismatch, match="9.9.9"):
        invoke.check_version("5.0.0", {"invokeai_version": "9.9.9"}, accept=False)
    invoke.check_version("5.0.0", {"invokeai_version": "9.9.9"}, accept=True)


def test_capture_templatizes_raw_batch(tmp_path, capsys):
    skill = tmp_path / "skill"
    (skill / "graphs").mkdir(parents=True)
    raw = {"batch": {"graph": {"id": "x", "nodes": {
        "pos": {"prompt": "XPOSX"}, "noise": {"seed": 0, "width": 1152, "height": 896},
        "m": {"model": {"key": "mk", "name": "J"}}, "out": {"board": {"board_id": "bid"}}}, "edges": []},
        "data": [[{"node_path": "noise", "field_name": "seed", "items": [424242]}]]}}
    raw_path = tmp_path / "raw.json"
    raw_path.write_text(json.dumps(raw))
    code = invoke.main(["--skill-dir", str(skill), "capture", "--raw", str(raw_path), "--name", "sdxl",
                        "--positive", "XPOSX", "--seed", "424242", "--width", "1152", "--height", "896",
                        "--model-key", "mk", "--board-id", "bid"])
    assert code == 0
    written = json.loads((skill / "graphs" / "sdxl.json").read_text())
    assert written["nodes"]["noise"] == {"seed": "{{seed}}", "width": "{{width}}", "height": "{{height}}"}
    assert written["nodes"]["m"]["model"] == "{{model}}"


def test_capture_unmatched_sentinel_exit_2(tmp_path, capsys):
    skill = tmp_path / "skill"
    (skill / "graphs").mkdir(parents=True)
    raw_path = tmp_path / "raw.json"
    raw_path.write_text(json.dumps({"batch": {"graph": {"nodes": {"pos": {"prompt": "XPOSX"}}}}}))
    code = invoke.main(["--skill-dir", str(skill), "capture", "--raw", str(raw_path), "--name", "sdxl",
                        "--positive", "XPOSX", "--steps", "23"])
    assert code == 2 and "steps" in capsys.readouterr().err


def test_adhoc_genre_is_plain():
    g = invoke.adhoc_genre("selftest", "m", 4, 3.5)
    assert g.positive == "{subject}" and g.allowed_models == ["m"] and g.steps == 4


def test_gate_verdict():
    assert invoke.gate_verdict(120.0) == "ok"
    assert invoke.gate_verdict(301.0).startswith("SLOW")
    assert invoke.gate_verdict(None).startswith("SLOW")


def test_is_blank_detects_flat_image(tmp_path):
    import subprocess
    flat = tmp_path / "flat.png"
    busy = tmp_path / "busy.png"
    subprocess.run(["magick", "-size", "64x64", "xc:#3a3a3a", str(flat)], check=True)
    subprocess.run(["magick", "-size", "64x64", "plasma:red-blue", str(busy)], check=True)
    assert invoke.is_blank(flat)
    assert not invoke.is_blank(busy)
