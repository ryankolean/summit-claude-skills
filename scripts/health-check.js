#!/usr/bin/env node

/**
 * Repo Health Check Script
 * Fetches GitHub stars and last commit dates for all tracked repositories.
 * Outputs a report and updates README badge counts.
 *
 * Usage: GITHUB_TOKEN=ghp_xxx node scripts/health-check.js
 */

const fs = require('fs');
const path = require('path');

const REPOS = [
  'obra/superpowers',
  'obra/superpowers-skills',
  'obra/superpowers-lab',
  'alirezarezvani/claude-skills',
  'davila7/claude-code-templates',
  'trailofbits/publications',  // Trail of Bits parent
  'zebbern/claude-code-guide',
  'BehiSecc/awesome-claude-skills',
  'ChrisWiles/claude-code-showcase',
  'steipete/oracle',
  'hashicorp/agent-skills',
  'diet103/claude-code-infrastructure-showcase',
  'modelcontextprotocol/servers',
  'microsoft/playwright-mcp',
  'mendableai/firecrawl',
  'wondelai/skills',
  'clawfu/mcp-skills',
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

async function fetchRepoData(owner, repo) {
  const token = process.env.GITHUB_TOKEN;
  const headers = {
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'summit-claude-skills-health-check',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`https://api.github.com/repos/${owner}/${repo}`, { headers });
    if (!response.ok) {
      console.error(`  [ERROR] ${owner}/${repo}: ${response.status} ${response.statusText}`);
      return null;
    }
    const data = await response.json();
    return {
      full_name: data.full_name,
      stars: data.stargazers_count,
      forks: data.forks_count,
      open_issues: data.open_issues_count,
      pushed_at: data.pushed_at,
      archived: data.archived,
      description: data.description,
    };
  } catch (err) {
    console.error(`  [ERROR] ${owner}/${repo}: ${err.message}`);
    return null;
  }
}

function daysSince(dateStr) {
  const then = new Date(dateStr);
  const now = new Date();
  return Math.floor((now - then) / (1000 * 60 * 60 * 24));
}

async function main() {
  console.log('=== Summit Claude Skills — Repo Health Check ===\n');
  console.log(`Date: ${new Date().toISOString().split('T')[0]}`);
  console.log(`Checking ${REPOS.length} repositories...\n`);

  const results = [];
  const warnings = [];

  for (const fullName of REPOS) {
    const [owner, repo] = fullName.split('/');
    process.stdout.write(`  Checking ${fullName}...`);
    const data = await fetchRepoData(owner, repo);

    if (!data) {
      warnings.push(`${fullName}: FAILED TO FETCH — may be deleted or private`);
      console.log(' FAILED');
      continue;
    }

    const inactive = daysSince(data.pushed_at);
    const status = data.archived ? 'ARCHIVED' : inactive > INACTIVE_THRESHOLD_DAYS ? 'INACTIVE' : 'ACTIVE';

    if (data.archived) {
      warnings.push(`${fullName}: ARCHIVED`);
    } else if (inactive > INACTIVE_THRESHOLD_DAYS) {
      warnings.push(`${fullName}: No commits in ${inactive} days`);
    }

    results.push({ ...data, inactive_days: inactive, status });
    console.log(` ${data.stars} stars, ${status} (${inactive}d ago)`);

    // Rate limit: 1 req/sec for unauthenticated, faster with token
    await new Promise(r => setTimeout(r, process.env.GITHUB_TOKEN ? 100 : 1100));
  }

  // Generate report
  const reportPath = path.join(__dirname, '..', 'HEALTH-REPORT.md');
  let report = `# Repo Health Report\n\n`;
  report += `**Generated:** ${new Date().toISOString().split('T')[0]}\n`;
  report += `**Repos Checked:** ${results.length}/${REPOS.length}\n\n`;

  if (warnings.length > 0) {
    report += `## Warnings\n\n`;
    for (const w of warnings) {
      report += `- ${w}\n`;
    }
    report += '\n';
  }

  report += `## All Repos\n\n`;
  report += `| Repository | Stars | Forks | Last Push | Status |\n`;
  report += `|---|---|---|---|---|\n`;
  for (const r of results.sort((a, b) => b.stars - a.stars)) {
    report += `| [${r.full_name}](https://github.com/${r.full_name}) | ${r.stars.toLocaleString()} | ${r.forks.toLocaleString()} | ${r.inactive_days}d ago | ${r.status} |\n`;
  }

  fs.writeFileSync(reportPath, report);
  console.log(`\nReport written to ${reportPath}`);

  if (warnings.length > 0) {
    console.log(`\n${warnings.length} WARNING(S):`);
    for (const w of warnings) {
      console.log(`  - ${w}`);
    }
  }

  console.log('\nDone.');
}

main().catch(console.error);
