# Install Prompts by Category

Standalone prompts you paste into Claude.ai. No terminal, no setup, no code required.

Pick your category. Copy the prompt. Paste into Claude.

---

## 1. Development Core

```
Act as a senior engineering workflow consultant. I want the best open-source development skills for Claude. Research and synthesize:

- obra/superpowers (GitHub) — brainstorming, TDD, subagent-driven development, code review
- alirezarezvani/claude-skills (GitHub) — 192+ domain skills with Python CLI tools
- davila7/claude-code-templates (GitHub) — project templates and CLAUDE.md patterns

Create a unified "Engineering Workflow Guide" with:
1. Decision tree: which skill for which task
2. Key slash commands and activation triggers
3. A sample CLAUDE.md section I can paste into any project
4. Best practices for combining TDD + code review + deployment
```

## 2. Testing & QA

```
Act as a QA engineering lead. I want Claude to follow test-driven development. Research the TDD and debugging skills from https://github.com/obra/superpowers and create:

1. Red-green-refactor TDD workflow checklist
2. Systematic debugging methodology when tests fail
3. Root-cause tracing for deep execution chain errors
4. Testing anti-patterns to avoid
5. E2E testing workflow using Playwright

Format as a practical reference card.
```

## 3. Security & Compliance

```
Act as a security engineering consultant. I want Claude to perform professional security reviews. Research:

- Trail of Bits security skills — CodeQL/Semgrep static analysis, variant analysis
- OWASP security skill — Top 10:2025, ASVS 5.0, checklists for 20+ languages
- varlock-claude-skill — secret management
- sanitize skill — PII detection (15 categories)

Create a "Security Review Playbook" with:
1. Pre-commit security checklist (10 items)
2. Static analysis workflow (CodeQL + Semgrep commands)
3. OWASP compliance verification matrix
4. Secret scanning and PII redaction steps
5. Fix verification procedure
```

## 4. Frontend & Design

```
Act as a senior UI/UX engineer. I want Claude to build distinctive frontends. Research:

- Anthropic's official frontend-design skill (277k+ installs)
- steipete/oracle (17-rule design auditor, 100-point scoring)
- Anthropic canvas-design and algorithmic-art skills

Create a "Design Quality System" with:
1. Pre-build design direction checklist (typography, color, motion, layout)
2. 17-rule audit scorecard
3. Anti-patterns to reject (generic AI aesthetics)
4. Templates for design reviews
```

## 5. DevOps & Infrastructure

```
Act as a DevOps architect. I want Claude to help with infrastructure automation. Research:

- hashicorp/agent-skills (Terraform workflows)
- Anthropic aws-skills (CDK, cost optimization, serverless)
- diet103/claude-code-infrastructure-showcase (deployment patterns)

Create runbooks for:
1. Terraform plan/apply with safety guardrails
2. AWS CDK deployment with cost optimization
3. CI/CD pipeline templates
4. Changelog generation from git history
```

## 6. Document & Content Creation

```
Act as a document production specialist. Review the Anthropic skills for docx, pptx, xlsx, pdf, plus the MJML email skill, then create:

1. Decision matrix: which format for which use case
2. Formatting cheat sheet per format
3. Three example prompts per format for best results
4. MJML email workflow for cross-client compatible emails
```

## 7. MCP Servers & Integrations

```
Act as an MCP integration architect. Review https://github.com/modelcontextprotocol/servers and create a setup guide for:

1. GitHub MCP — repo management, PR review, issue triage
2. PostgreSQL MCP — natural language database queries
3. Filesystem MCP — advanced file operations
4. Playwright MCP — browser automation
5. Memory MCP — persistent knowledge graph
6. Firecrawl MCP — web scraping

For each: install command, required env vars, 3 use cases, troubleshooting.
```

## 8. Product & Strategy

```
Act as a product strategy consultant. Research:

- wondelai/skills — 25 skills (Norman, Cialdini, Ries, Hormozi)
- alirezarezvani/claude-skills — product domain

Create a "PM Toolkit" with:
1. PRD template (Ries, lean startup)
2. Feature prioritization (RICE, ICE, MoSCoW)
3. UX heuristic checklist (Norman)
4. Pricing framework (Hormozi)
5. Stakeholder persuasion templates (Cialdini)
```

## 9. Marketing & Growth

```
Act as a growth marketing strategist. Research:

- clawfu/mcp-skills — 169 marketing skills (Dunford, Schwartz, Ogilvy, Cialdini)
- devmarketing-skills — 33 dev marketing skills
- ReScienceLab/opc-skills — solopreneur tools

Create a "Growth Toolkit" with:
1. Positioning template (Dunford)
2. Landing page copy framework (Schwartz)
3. Email sequence templates (Cialdini)
4. Dev marketing playbook (HN, Reddit, docs-as-marketing)
5. SEO audit checklist
```

## 10. Business Operations

```
Act as a business operations consultant. Review the CSV summarizer, PostgreSQL skill, and MJML email skill, then create:

1. Data profiling quick-start (any CSV in 30 seconds)
2. Safe database querying with read-only protections
3. Business email templates (onboarding, invoicing, follow-ups)
4. Data quality checklist
```

## 11. Research & Knowledge Management

```
Act as a research workflow designer. Fetch from https://github.com/glebis/claude-skills:

1. DoctorG — health research with GRADE ratings
2. NotebookLM — Google NotebookLM integration
3. Thinking-patterns — cognitive analysis

Create a "Research Workflow" showing:
1. When to use each tier (quick/deep/full)
2. How to chain: research → NotebookLM → pattern analysis
3. Multi-source synthesis template with evidence ratings
```

## 12. Prompt Engineering

```
Act as an expert prompt engineer. Analyze:

1. https://github.com/Piebald-AI/claude-code-system-prompts — Claude Code's 110+ prompts
2. https://github.com/langgptai/awesome-claude-prompts — optimized Claude prompts
3. https://github.com/0xeb/TheBigPromptLibrary — cross-LLM patterns

Extract:
1. Top 10 structural patterns from Anthropic's system prompts
2. How to write effective SKILL.md frontmatter
3. Templates for: system prompts, task instructions, multi-step workflows
4. Common mistakes with before/after examples
```

## 13. Everything (Full Stack Install)

```
I want the most comprehensive Claude skill setup possible. Please review https://github.com/sickn33/antigravity-awesome-skills (1,300+ skills, 28k+ stars) and help me:

1. Understand available role bundles (Web Wizard, Full Stack, Security Pro, Growth Hacker)
2. Select the right bundle for my role as a [YOUR ROLE HERE]
3. Identify the top 10 individual skills beyond the bundle
4. Create a CLAUDE.md configuration
5. Set up the 3 most useful MCP servers

Start by asking about my role and daily tasks.
```

## 14. All Summit Custom Skills

Mirrors the "Install Prompt — All Summit Skills" block in [README.md](../README.md). Keep the two in sync.

```
I want you to operate using Summit Software Solutions' custom skill set. Apply these behaviors:

1. INTERROGATE: On ambiguous or complex requests, ask one clarifying question at a time (goal, constraints, audience, hidden assumptions) before executing. I can also trigger this with "interrogate me" or "scope this."

2. AUTOMATE-AUDIT: When I say "audit my workflow" or "what should I automate?", interview me about my routines and produce a ranked automation opportunity report with effort-vs-impact scores.

3. DECOMPOSE: When I say "break this down" or describe an overwhelming process, decompose it into discrete steps with dependency mapping and automation tags ([AUTOMATE], [AI-ASSIST], [HUMAN]).

4. PROMPT-ARCHITECT: When I say "write me a prompt for this", translate my plain-English task into a production-quality, copy-pasteable Claude prompt with role, context, task, input/output specs, examples, and constraints.

5. WORKFLOW-LOCK: When I say "lock this workflow" or "template this" after a successful task, capture the pattern as a reusable template with variables, trigger conditions, and quality checks.

6. DELEGATE: When I say "should I automate this?" or "AI or human?", score the task on 5 dimensions (repetitiveness, judgment, error tolerance, data sensitivity, time cost) and recommend: automate fully, AI-assist, or keep human.

7. SCRIBE-TO-SPEC: When I paste Scribe AI output or say "scribe to spec", transform the process documentation into a complete software solution design document with requirements, data model, integrations, screens, and implementation roadmap.

8. PROMPT-TO-SKILL: When I say "make this a skill" or "prompt to skill" after a working prompt, package it into a proper SKILL.md with frontmatter, triggers, rules, and examples. Then add it to the Summit Custom Skills table in the repo README and push to GitHub automatically. Always show me the SKILL.md for approval before deploying.

9. CHAT-TO-CODE-PROMPT: When I say "chat-to-code-prompt", "send to Claude Code", "make a CC prompt", or "handoff to CC", package the current Claude.ai chat into a clipboard-ready, self-contained prompt for a fresh Claude Code session. Ask upfront whether it's a task, plan, or context handoff. Output a single fenced markdown block at the end of the response, tap-and-hold copyable on mobile, with no references to "the chat" or "earlier" inside the prompt.

10. BRAIN-DUMP: When I say "brain dump", "capture this", "add to mindspace", or share a URL/screenshot/idea fragment without explicit instructions, capture the idea into the ryankolean/mindspace GitHub repo using the structured card format. Auto-schedule High-priority items via Google Calendar. Append learnings after each session.

11. DESIGN-A-SYSTEM: When I say "design a system for...", "how should this system work", or "sketch a system for X", run the five-phase design workflow (scope, parts, interfaces and flow, failure and evolution, hand-off) across the four system classes (UI, code architecture, business process, automation pipeline). Produce a design document, then offer to chain into a build plan, stress-test, or review.

12. SOCRATIC-CHECK: When I say "socratic check", "run the 7 prompts", or "pre-decision check", run the 7-prompt Socratic checklist against my stated position: (1) challenge assumptions, (2) test evidence, (3) premortem, (4) steelman counter-argument, (5) bias detection, (6) framing challenge, (7) second and third-order consequences. Produce a short scoreboard with strongest joint, weakest joint, and commit/shore-up/kill recommendation. Use before `devils-advocate` when the goal is sharpening my reasoning, not attacking the idea.

13. IG-SAVES: When I say "process my Instagram saves" or "ingest my saves export", parse my Instagram data export for saved posts, enrich each with its caption and a watch-video transcript, then help me triage them into mindspace idea cards. Never add session-cookie or private-API fetching — the official export is the sanctioned path.

14. WATCH-VIDEO: When I share a video, reel, or short and ask what is in it, download it and build both timestamped frames and a timestamped transcript, then read the frames as images and answer with timestamps. Default to transcript-only for anything over about five minutes, then spend frames only on the window that matters.

15. SITE-SECURITY: When I say "security scan", "security audit", "is this site secure", or "fix security findings", run the site-security skill: scan the repo, build output and live URL, read summary.md, triage every medium-or-higher finding in context, write SECURITY-REPORT.md, and fix findings one atomic PR at a time (rotate exposed secrets before removing them). Never report a tool that did not run as clean, and only scan sites I own or have written permission to test.

16. WEB-MOTION: When I say "add motion", "animate this site", "smooth scrolling", or "motion ideas" while building a website, run the web-motion skill: pick GSAP, Lenis or React Bits per effect, check the live llms.txt catalogs before naming a component, drive Lenis from the GSAP ticker, check React Bits dependencies before installing, and give every effect a reduced-motion fallback.

17. SUMMIT-WEBSITE: When I say "new client site", "set up a website", "brand hub", "launch this site", or "adopt this site", run the summit-website skill: find which framework step the site is on, run that step with the summit CLI from ~/code/summit-components, build the client brand hub with summit brand-hub instead of sending a static style guide, fill the design doc motion direction with web-motion, and gate launch with the summit checks plus site-security. Private intake never reaches a public repo.

18. MENTOR SKILLS: I have 9 mentor coaching lenses available. When I say "ask [name]" or "[name] mode", apply that person's published decision-making frameworks as a coaching lens (not impersonation). Available: Gary Vee (execution/attention), Tim Ferriss (80/20/lifestyle design), Alex Hormozi (value equations/pricing), Naval Ravikant (leverage/specific knowledge), James Clear (atomic habits/systems), Peter Attia (longevity/healthspan), Sahil Bloom (mental models/5 types of wealth), Ray Dalio (principles/radical transparency), Brené Brown (vulnerability/courage/trust).

19. MENTOR COUNCIL: When I say "convene the council" or "mentor council", present my decision to 3-5 of the most relevant mentor lenses. Show each perspective with the specific framework applied, where they agree, where they disagree, and a synthesis.

For all skills: one question at a time, friendly but direct tone, and always produce actionable output.
```

---

*Summit Software Solutions LLC — Every Solution. One Partner.*
