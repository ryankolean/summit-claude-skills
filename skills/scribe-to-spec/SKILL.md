---
name: scribe-to-spec
description: >
  Transform Scribe AI (scribe.com) process documentation — step-by-step guides
  with screenshots and click annotations — into a complete custom software solution
  design document. Takes the "how it works today" captured by Scribe and produces
  a spec for "how software should replace it." Activates when the user provides
  Scribe output (markdown, PDF, HTML, or link) or says "scribe to spec",
  "turn this Scribe into a spec", or "design software from this process."
---

# Scribe to Spec

Take process documentation captured by Scribe AI and transform it into a
complete software solution design document. Scribe captures *what humans do
today* — this skill designs *what software should do instead*.

## When to Activate

**Manual triggers:**
- "Scribe to spec"
- "Turn this Scribe into a spec"
- "Design software from this process"
- "Build a solution doc from this Scribe"
- "I captured this in Scribe — now make it into a software project"

**Auto-detect triggers:**
- User pastes or uploads content that matches Scribe's output format:
  numbered steps with screenshot descriptions, click annotations, and
  navigation paths
- User shares a Scribe link (scribe.com/...)
- User mentions "Scribe", "ScribeHow", or "process guide" alongside a
  request to build software

## Phase 1: Ingest the Scribe

Accept Scribe output in any format:
- **Markdown export** (preferred — structured, parseable)
- **PDF export** (extract text and step structure)
- **HTML export** (parse step-by-step structure)
- **Pasted text** (the user copies content from a Scribe page)
- **Scribe link** (fetch and parse if accessible)

Parse the Scribe to extract:
1. **Process name and description**
2. **Each step:** Step number, action description, UI element targeted,
   application/tool used, screenshot context
3. **Navigation flow:** How the user moves between screens/pages/tools
4. **Data touched:** What information is entered, read, transformed, or moved
5. **Decision points:** Any branching or conditional logic (if visible)
6. **Tools involved:** Every application, website, or system referenced

## Phase 2: Analyze the Process

Before writing the spec, analyze what Scribe captured through these lenses:

### Pain Point Extraction
For each step, evaluate:
- Is this step manual data entry that could be eliminated?
- Is the user copying data between systems?
- Is the user making a decision that follows clear rules?
- Is the user waiting for something (approval, data load, external response)?
- Is the user doing the same action repeatedly across different records?

### System Boundary Mapping
Identify every external system or tool referenced:
- What data goes INTO each system?
- What data comes OUT of each system?
- What's the integration point? (API, manual entry, file export/import, email)
- Can this integration be automated? (API available, webhook, Zapier, MCP)

### Data Model Discovery
From the fields the user interacts with, infer:
- What entities exist? (customers, orders, invoices, tickets, etc.)
- What are the key fields on each entity?
- What are the relationships between entities?
- What data is duplicated across systems?

## Phase 3: Ask Clarifying Questions

After analysis, ask one question at a time about gaps:

1. "The Scribe shows you doing [X step] — is this the same every time, or
   does it change based on [condition]?"
2. "I see data moving from [System A] to [System B]. Is there an API for
   [System B], or is manual entry the only option today?"
3. "Steps 4-7 look like they could be a single automated action. Is there
   a reason they're done separately? (e.g., approval needed between steps)"
4. "How many times per [day/week/month] does this full process run?"
5. "Who else touches this process besides you?"

## Phase 4: Generate the Solution Design Document

Produce a structured specification document:

```
# Software Solution Design Document

## 1. Executive Summary
[2-3 sentences: what process this replaces, key benefit, target users]

## 2. Current State (from Scribe)
### Process Overview
[Summary of the current manual process as captured by Scribe]

### Steps (As-Is)
| Step | Action | System | Data | Pain Point |
|---|---|---|---|---|
| 1 | [From Scribe] | [Tool used] | [Data touched] | [Manual/slow/error-prone] |
| 2 | ... | ... | ... | ... |

### Systems Involved
[List of all tools/apps/systems with their role in the process]

### Current Time Cost
[Estimated time per execution and frequency]

## 3. Proposed Solution (To-Be)
### Architecture Overview
[High-level description of the software solution]

### User Stories
As a [role], I want to [action] so that [benefit].
1. ...
2. ...
3. ...

### Functional Requirements
| ID | Requirement | Priority | Source Step |
|---|---|---|---|
| FR-1 | [Requirement] | Must Have | Step X from Scribe |
| FR-2 | ... | Should Have | Steps Y-Z |

### Data Model
[Entities, fields, relationships — inferred from the Scribe data]

#### Entities
- **[Entity Name]:** [Description, key fields]
- ...

#### Relationships
- [Entity A] has many [Entity B]
- ...

### Integration Points
| System | Direction | Method | Data |
|---|---|---|---|
| [System A] | Inbound | API / Webhook / Manual | [What data] |
| [System B] | Outbound | API / File Export | [What data] |

### Screens / UI Wireframes (Descriptions)
[For each major screen, describe: purpose, key elements, user actions,
data displayed. Reference original Scribe steps that this screen replaces.]

1. **[Screen Name]** — Replaces Scribe Steps X-Y
   - Purpose: [What the user does here]
   - Key elements: [Form fields, tables, buttons, status indicators]
   - Data: [What's displayed and where it comes from]

## 4. Automation Opportunities
[Steps from the Scribe that can be fully eliminated in the new system]

| Scribe Step | Automation | How |
|---|---|---|
| Step X: Manual data entry | Eliminated | API integration with [System] |
| Step Y: Copy-paste between tools | Eliminated | Automated sync |
| Step Z: Decision based on threshold | Automated | Business rule engine |

## 5. Implementation Roadmap
### Phase 1: MVP (Weeks 1-X)
[Core functionality that replaces the most painful manual steps]

### Phase 2: Integration (Weeks X-Y)
[Connect to external systems, automate data flows]

### Phase 3: Polish (Weeks Y-Z)
[UI refinements, edge cases, reporting, admin features]

## 6. Technical Recommendations
### Suggested Stack
[Based on the requirements, recommend appropriate technologies]

### Hosting / Infrastructure
[Cloud, self-hosted, serverless — with reasoning]

### Security Considerations
[Data sensitivity, auth requirements, compliance needs]

## 7. Success Metrics
[How to measure if the software solution is working]
- Time saved per process execution: [X minutes → Y minutes]
- Error rate reduction: [estimated]
- User satisfaction: [how to measure]

## 8. Open Questions
[Things that need answers before development starts]
1. ...
2. ...
```

## Rules

1. Every requirement in the spec must trace back to a specific Scribe step.
   Use "Source Step" references so stakeholders can verify the spec matches
   reality.

2. Don't just digitize the manual process. Look for steps that should be
   eliminated entirely in software, not just moved to a screen.

3. Infer the data model from what the user interacts with, but flag
   assumptions. "I'm inferring a Customer entity with these fields based
   on Step 4 — is that right?"

4. Recommend the simplest tech stack that solves the problem. Don't suggest
   microservices for a process that could be a well-designed form with an
   API integration.

5. Always include an MVP phase that addresses the top 3 pain points.
   Don't propose a 6-month build when a 2-week MVP would solve 80%.

6. If the Scribe reveals a broken process (not just a manual one), say so.
   "Before we build software, Step 5 seems like a workaround for [X].
   Should we fix the underlying issue first?"

## Chaining

- **scribe-to-spec → decompose:** Break the implementation roadmap into
  granular development tasks
- **scribe-to-spec → prompt-architect:** Build prompts for generating
  recurring artifacts (reports, emails) identified in the process
- **automate-audit → scribe-to-spec:** Audit finds a process to automate,
  user captures it in Scribe, skill generates the spec
