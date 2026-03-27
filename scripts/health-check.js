#!/usr/bin/env node

/**
 * Summit Claude Skills — Repo Health Check
 *
 * 1. Fetches current GitHub stars and last commit dates for all tracked repos
 * 2. Generates HEALTH-REPORT.md with status indicators
 * 3. Updates the "Last updated" date in README.md
 *
 * Runs weekly via GitHub Actions. Can also run manually:
 *   GITHUB_TOKEN=ghp_xxx node scripts/health-check.js
 */

const fs = require('fs');
const path = require('path');

const REPOS = [
  'obra/superpowers',
  'obra/superpowers-skills',
  'obra/superpowers-lab',
  'alirezarezvani/claude-skills',
  'davila7/claude-code-templates',
  'zebbern/claude-code-guide',
  'BehiSecc/awesome-claude-skills',
  'ChrisWiles/claude-code-showcase',
  'steipete/oracle',
  'hashicorp/agent-skills',
  'diet103/claude-code-infrastructure-showcase',
  'modelcontextprotocol/servers',
  'mendableai/firecrawl',
  'wondelai/skills',
  'ReScienceLab/opc-skills',
  'glebis/claude-skills',
  'x1xhlol/system-prompts-and-models-of-ai-tools',
  'Piebald-AI/claude-code-system-prompts',
  'EliFuzz/awesome-system-prompts',
  'langgptai/awesome-claude-prompts',
  '0xeb/TheBigPromptLibrary',
  'sickn33/antigravity-awesome-skills',
  'travisvn/awesome-claude-skills',
  'hesreallyhim/awesome-claude-code',
  'ComposioHQ/awesome-claude-skills',
  'VoltAgent/awesome-agent-skills',
  'abubakarsiddik31/claude-skills-collection',
  'Comfy-Org/comfy-claude-prompt-library',
  'dontriskit/awesome-ai-system-prompts',
];

const INACTIVE_THRESHOLD_DAYS = 60;

async function fetchRepo(owner, repo) {
  const token = process.env.GITHUB_TOKEN;
  const headers = {
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'summit-claude-skills-health-check',
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  try {
    const res = await fetch(`https://api.github.com/repos/${owner}/${repo}`, { headers });
    if (!res.ok) {
      console.error(`  [ERROR] ${owner}/${repo}: ${res.status}`);
      return null;
    }
    return await res.json();
  } catch (err) {
    console.error(`  [ERROR] ${owner}/${repo}: ${err.message}`);
    return null;
  }
}

function daysSince(dateStr) {
  return Math.floor((Date.now() - new Date(dateStr).getTime()) / 86400000);
}

function formatStars(n) {
  return n >= 1000 ? `${(n / 1000).toFixed(1).replace(/\.0$/, '')}k` : String(n);
}

function todayFormatted() {
  const d = new Date();
  const months = ['January','February','March','April','May','June',
    'July','August','September','October','November','December'];
  return `${months[d.getUTCMonth()]} ${d.getUTCDate()}, ${d.getUTCFullYear()}`;
}

async function main() {
  const rootDir = path.join(__dirname, '..');
  const readmePath = path.join(rootDir, 'README.md');
  const reportPath = path.join(rootDir, 'HEALTH-REPORT.md');

  console.log('=== Summit Claude Skills — Repo Health Check ===');
  console.log(`Date: ${new Date().toISOString().split('T')[0]}`);
  console.log(`Repos: ${REPOS.length}\n`);

  const results = [];
  const warnings = [];

  for (const fullName of REPOS) {
    const [owner, repo] = fullName.split('/');
    process.stdout.write(`  ${fullName} ... `);

    const data = await fetchRepo(owner, repo);
    if (!data) {
      warnings.push(`${fullName}: FETCH FAILED — may be deleted or private`);
      console.log('FAILED');
      continue;
    }

    const days = daysSince(data.pushed_at);
    const status = data.archived ? 'ARCHIVED'
      : days > INACTIVE_THRESHOLD_DAYS ? 'INACTIVE' : 'ACTIVE';

    if (data.archived) warnings.push(`${fullName}: ARCHIVED`);
    else if (days > INACTIVE_THRESHOLD_DAYS) warnings.push(`${fullName}: Inactive ${days}d`);

    results.push({
      full_name: fullName,
      stars: data.stargazers_count,
      forks: data.forks_count,
      issues: data.open_issues_count,
      pushed_at: data.pushed_at,
      archived: data.archived,
      days_since_push: days,
      status,
    });

    console.log(`${formatStars(data.stargazers_count)} stars | ${status} (${days}d)`);
    await new Promise(r => setTimeout(r, process.env.GITHUB_TOKEN ? 150 : 1200));
  }

  // ---- Write HEALTH-REPORT.md ----
  const active = results.filter(r => r.status === 'ACTIVE').length;
  const inactive = results.filter(r => r.status === 'INACTIVE').length;
  const archived = results.filter(r => r.status === 'ARCHIVED').length;
  const totalStars = results.reduce((s, r) => s + r.stars, 0);

  let report = `# Repo Health Report\n\n`;
  report += `**Generated:** ${todayFormatted()}  \n`;
  report += `**Repos checked:** ${results.length}/${REPOS.length}  \n`;
  report += `**Total stars:** ${totalStars.toLocaleString()}  \n`;
  report += `**Active:** ${active} | **Inactive (60d+):** ${inactive} | **Archived:** ${archived}\n\n`;

  if (warnings.length > 0) {
    report += `## Warnings\n\n`;
    warnings.forEach(w => report += `- ${w}\n`);
    report += '\n';
  }

  report += `## All Repos\n\n`;
  report += `| Repository | Stars | Forks | Last Push | Status |\n`;
  report += `|---|---:|---:|---|---|\n`;
  results.sort((a, b) => b.stars - a.stars);
  for (const r of results) {
    const emoji = r.status === 'ACTIVE' ? '🟢' : r.status === 'INACTIVE' ? '🟡' : '🔴';
    const pushed = r.pushed_at ? r.pushed_at.split('T')[0] : '?';
    report += `| [${r.full_name}](https://github.com/${r.full_name}) | ${r.stars.toLocaleString()} | ${r.forks.toLocaleString()} | ${pushed} | ${emoji} ${r.status} |\n`;
  }

  fs.writeFileSync(reportPath, report);
  console.log(`\nWrote HEALTH-REPORT.md`);

  // ---- Update README "Last updated" date ----
  if (fs.existsSync(readmePath)) {
    let readme = fs.readFileSync(readmePath, 'utf-8');
    const updated = readme.replace(
      /\*Last updated:.*?\*/,
      `*Last updated: ${todayFormatted()}*`
    );
    if (updated !== readme) {
      fs.writeFileSync(readmePath, updated);
      console.log(`Updated README date to ${todayFormatted()}`);
    }
  }

  // ---- Summary ----
  console.log(`\nTotal stars: ${totalStars.toLocaleString()}`);
  if (warnings.length) {
    console.log(`\n${warnings.length} warning(s):`);
    warnings.forEach(w => console.log(`  - ${w}`));
  }
  console.log('\nDone.');
}

main().catch(err => { console.error(err); process.exit(1); });
