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
