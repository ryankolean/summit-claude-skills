# Capture flow by input type

Per-input-type rules. The capture algorithm in SKILL.md applies; this file specifies the extraction step.

## URL — generic web page

1. `web_fetch` the URL.
2. Extract: page title, author/byline if present, publication, key claims (3-5 bullet points), one-paragraph summary in Ryan's voice.
3. Frontmatter `source: web`, `source_url: <url>`, `source_publication: <name>`.
4. Body sections: Summary, Key claims, Why it matters (Ryan's framing), Action.

## URL — social media post (X, LinkedIn, Reddit, HN, Threads, Bluesky)

1. `web_fetch` the URL. If the post is paywalled or requires auth, capture what's available and flag in the card.
2. Extract: post body, author handle + display name, platform, post date, engagement signals if visible (likes/replies counts).
3. Frontmatter `source: social`, `source_platform: <platform>`, `source_url: <url>`, `source_author: <handle>`.
4. Body sections: Post (verbatim, indented blockquote), Why it matters, Action.

## URL — YouTube video

1. `web_fetch` the URL for title, channel, description, length.
2. Frontmatter `source: video`, `source_platform: youtube`, `source_url: <url>`, `source_channel: <name>`, `source_duration: <minutes>`.
3. Body sections: Description, Why it matters, Action. If user provides timestamps of interesting moments, include them.

## URL — Substack / blog newsletter

1. `web_fetch`. Extract author byline (these get missed often — check for Substack-specific bylines).
2. Frontmatter `source: newsletter`, `source_publication: <substack name>`, `source_author: <name>`.
3. Same body sections as generic web.

## Image — screenshot of a UI / product

1. Describe the visible UI: product, screen, feature shown, any visible state.
2. If text is visible, transcribe critical text (headers, key labels, error messages, CTAs).
3. Frontmatter `source: screenshot`, `source_app: <product if identifiable>`.
4. Body sections: What it shows, Why it matters, Action.

## Image — screenshot of text content

1. Transcribe the text fully.
2. Identify the source if visible (browser URL bar, app header).
3. Frontmatter `source: screenshot`, `source_url: <if visible>`.
4. Body: transcribed text in blockquote, Why it matters, Action.

## Image — photo (real-world)

1. Describe the subject.
2. Frontmatter `source: photo`.
3. Body: Description, Why it matters, Action.

## Plain text — pasted snippet

1. Treat the text as the body. If it's clearly multiple ideas, split into multiple cards.
2. Frontmatter `source: text`.
3. Body: Snippet (blockquote), Why it matters, Action.

## Voice transcript

1. Read the full transcript first. Identify topic shifts.
2. Split into discrete idea fragments. One idea = one card.
3. Frontmatter `source: voice`, `source_session: <YYYY-MM-DD-HHMM>` so multiple cards from one ramble can be linked.
4. Body: Transcript fragment (lightly cleaned — fix obvious transcription errors, keep Ryan's voice), Why it matters, Action.

## Calendar inbox event

Triggered when a Google Calendar event titled `[Inbox] *` is found during a session.

1. Pull event title (strip `[Inbox] ` prefix), description, date.
2. Frontmatter `source: calendar`, `source_event_id: <id>`.
3. Body: Description as-is, Why it matters, Action.
4. After successful capture, **delete the calendar event** to avoid re-capture next session.

## iOS Shortcut payload

Triggered when the shortcut POSTs to GitHub. The payload arrives as a pre-formatted markdown file in `inbox/` with frontmatter `source: shortcut`. The skill's job is to:

1. Read the raw payload.
2. Apply the same classification proposal step as any other capture.
3. Move from `inbox/` to `library/` after triage.

## "Other" — anything else

When the input doesn't fit a category above, ask one clarifying question: "What is this and where did it come from?" Then proceed with a generic flow: extract what you can, frontmatter `source: other`, body has Description + Why it matters + Action.
