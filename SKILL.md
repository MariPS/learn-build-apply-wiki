---
name: career-wiki
description: Maintains two linked LLM wikis (Karpathy pattern) in Open Knowledge Format: one tracking job applications, one compiling study notes on the concepts those jobs require. ALWAYS use this skill when the user pastes a job posting (URL, text, file), reports an application update (CV sent, interview scheduled, rejection, offer), pastes study material (video transcript, book chapter, paper, web page, notes), asks a question about either wiki ("which postings need Kubernetes?", "what do I know about vector databases?", "where am I weakest?"), asks to prepare for an interview, asks to extend the study wiki with a new area, or asks to check or clean up the wikis. Do not wait for step-by-step instructions: autonomously apply the Ingest Job, Track, Ingest Source, Query, Prep, Lint and Extend operations defined below.
---

# Career Wiki

Two linked knowledge bases that turn a job search into a compounding
artifact instead of a pile of browser tabs.

Following Karpathy's LLM Wiki pattern: *the LLM writes and maintains the
wiki; the human reads and asks questions.* The user should never have to
tell you which file to write or what section to put things in. That is
what this document is for.

## Architecture

Two side-by-side [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format)
v0.2 bundles, cross-linked.

### `job-wiki/` — what you applied to

- **`references/postings/`** — raw, immutable layer: the original text of
  each posting exactly as the user pasted it. `type: Reference`.
- **`applications/`** — one page per application. `type: Job Application`.
- **`concepts/`** — the tools and theory postings ask for, shared across
  applications. `type: Technical Concept`. Each page carries a
  `study_topic` field pointing at the matching page in the study wiki
  (`../../study-wiki/topics/<slug>.md`), or `null` when the concept falls
  outside the study curriculum.

### `study-wiki/` — what you actually know

- **`references/sources/`** — raw, immutable layer: one page per external
  source (video transcript, book chapter, paper, web page, course notes).
  `type: Reference`.
- **`modules/`** — the curriculum skeleton. `type: Study Module`.
- **`topics/`** — one page per concept, grouped into modules.
  `type: Study Topic`. This is where compiled knowledge accumulates.

The module and topic skeleton is **imported from a curriculum the user
chooses** — a course syllabus, a textbook's table of contents, a company
interview guide, a personal checklist. It is defined in a JSON file under
`scripts/curricula/` and materialised with `scripts/add_module.py`. This
skill ships no curriculum of its own: the structure is the user's.

**Declared divergence from Karpathy's original layout** (`raw/` + a single
`wiki/`): the wiki is split because this domain holds knowledge with
different lifespans. An application is ephemeral — it closes. A technical
concept is durable. A study topic has a fixed shape imposed by the
curriculum. Keeping them apart stops study pages from filling up with
recruiting metadata.

## Naming conventions

- `job-wiki/applications/<company-slug>-<role-slug>.md`
- `job-wiki/concepts/<concept-slug>.md`
- `job-wiki/references/postings/<company-slug>-<role-slug>-<YYYY-MM-DD>.md`
- `study-wiki/topics/<topic-slug>.md` — slugs are fixed at import; never
  rename them
- `study-wiki/references/sources/<author-or-channel>-<title-slug>.md`

## Front matter schemas

**Job Application** (custom fields on top of the OKF standard ones):

```yaml
type: Job Application
title: "<Role> @ <Company>"
description: <one line>
resource: <posting URL, if any>
tags: [...]
company: <Company>
role: <Role>
posted_at: <posting date, ISO 8601>
cv_sent_at: <date CV was sent, ISO 8601>
application_status: candidate | applied | interview | rejected | offer | withdrawn
status: draft | stable | deprecated   # deprecated once the position closes
generated: { by: <actor>, at: <timestamp> }
sources:
  - id: posting
    resource: /references/postings/<file>.md
    title: <original posting title>
```

**Technical Concept** (in `job-wiki/concepts/`):

```yaml
type: Technical Concept
title: <Concept name>
description: <one line>
tags: [...]
study_topic: ../../study-wiki/topics/<slug>.md   # or null if out of scope
generated: { by: <actor>, at: <timestamp> }
```

**Study Topic** (in `study-wiki/topics/`):

```yaml
type: Study Topic
title: <Topic name, as the curriculum calls it>
description: <one line>
tags: [...]
module: "<NN> - <module name>"
coverage: empty | stub | drafted | solid
generated: { by: <actor>, at: <timestamp> }
sources:
  - id: <short-id>
    resource: /references/sources/<file>.md
    title: <source title>
    author: <author or channel>
    last_modified: <publication date, if known>
```

Study Topic body, in this order:

| Section | Contents |
|---|---|
| `# In one sentence` | The 30-second interview answer. Written last. |
| `# Summary` | 5-10 lines: what it is, what it's for, where it sits. Enough for a quick refresher. |
| `# Theory in depth` | **The real body of the page.** Formal definitions, step-by-step mechanisms, formulas, pseudocode, trade-offs, failure modes, comparisons between alternatives. Split into `##` subsections **by theme, never by source**. |
| `# Key points` | Facts to memorise, extracted from the theory above. |
| `# Interview questions` | Questions collected, each with the outline of an answer. |
| `# Sources read` | One line per source already absorbed, and what it contributed. |
| `# Links` | Parent module, related topics, concepts in the job wiki pointing here. |

Claims taken from a specific source are attributed with a markdown
footnote whose label is the source's `id` in `sources`, as OKF prescribes:
`...it works like X.[^source-id]`. Theory is the one section allowed to
grow without bound; past roughly 400 lines, propose splitting a subtheme
into its own topic (needs the user's go-ahead — see Extend).

**Reference** (posting, in `job-wiki/references/postings/`):

```yaml
type: Reference
title: <descriptive title>
description: Full text of the posting, verbatim, not summarised.
resource: <URL, if any>
generated: { by: <actor>, at: <timestamp> }
```

**Reference** (study source, in `study-wiki/references/sources/`):

```yaml
type: Reference
title: <descriptive title>
description: <what it contains>
resource: <URL, if any>
source_kind: video | book | paper | webpage | course | notes
author: <author or channel>
published_at: <date or year>
captured_at: <date you collected it>
locator: <chapter/pages/timestamps, where applicable>
covers_topics: [<topic-slug>, ...]
generated: { by: <actor>, at: <timestamp> }
```

## Routing — where does pasted material go?

Users paste things without saying which wiki they belong to. You decide,
using this procedure, **before** writing any file.

### Explicit marker (overrides everything)

If the message opens with one of these, stop reasoning and route:

- `job:` or `posting:` → Ingest Job
- `study:` or `source:` → Ingest Source
- `job+study:` → both (rare: e.g. a company engineering post that is
  simultaneously a hiring pitch and real technical material)

### Signals of a job posting (→ `job-wiki`)

- Names a company **as an employer** alongside a role title.
- Contains sections like responsibilities, requirements, what we offer,
  seniority, salary range, location, contract type, how to apply.
- The URL belongs to a job board or a company careers page
  (`*/careers/*`, `*/jobs/*`, and the usual applicant tracking systems).
- Second-person register aimed at a candidate: "you will own", "we're
  looking for someone who".

### Signals of a study source (→ `study-wiki`)

- **Explains how something works** rather than requiring that you know it.
- Is a transcript, chapter, paper, tutorial, documentation page, technical
  thread, or set of notes.
- The URL belongs to a video platform, a preprint server, official docs, a
  technical blog, or a code repository.
- Contains timestamps, page numbers, citations, formulas, or explanatory
  code blocks.

### The case that actually matters

A posting **mentions** technologies without explaining them. It stays a
posting. Never treat it as a study source: a list of requirements teaches
nothing, and it would pollute topic pages with recruiting language dressed
up as theory. The posting feeds `concepts/`, which **point at** topics —
the cross-link does the work, not duplicated content.

Conversely, a study source that talks about a company (an engineering talk
from a well-known firm) stays a source: nobody is hiring.

### When you're unsure

Ask, in one short question, with your guess already stated: "This looks
like study material on vector databases — treat it as a source, or is it a
posting to track?" Don't guess silently: a posting that lands in `topics/`
has to be cleaned out of two places by hand.

Cases that **must** trigger the question: a bare URL with no context; a
file with an ambiguous name; text describing a role but seemingly lifted
from a course ("what an ML engineer does"); material containing both a
posting and the company's technical blog.

## Operations

### 1. Ingest Job — a new posting

Trigger: the user pastes a URL, posting text, or attaches a file that
routing identified as a posting.

1. Create `job-wiki/references/postings/<slug>-<date>.md` holding the
   verbatim text (`type: Reference`).
2. Check `applications/index.md`: is this already tracked (same company +
   role)? If so, update the existing page instead of creating a new one.
3. Create or update `applications/<slug>.md`: extract company, role,
   posting date, job description, responsibilities, required tools. Link
   `sources` to the reference you just created.
4. For each required tool or theoretical concept: first search
   `concepts/index.md` for an existing page covering it (match on meaning,
   not just wording). If one exists, update it with the new context and a
   link to the new application; otherwise create a minimal new page. Never
   duplicate a concept.
5. **Link to study**: for each concept touched, if it has no `study_topic`
   yet, look for the matching page in `study-wiki/topics/index.md`.
   - Found → set `study_topic` in front matter and add a `# Further study`
     section with the relative link.
   - Not found, but clearly inside the curriculum's scope → propose
     creating a new Study Topic and say which module you'd file it under.
     Don't create it yourself: the skeleton comes from the curriculum.
   - Out of scope → set `study_topic: null` with a short comment.
6. Append a line to the job wiki's `log.md`.
7. Refresh the affected rows in `applications/index.md` and
   `concepts/index.md`.
8. Summarise in a few lines what you created or updated, and flag any
   linked study topics still at `coverage: empty` — that's the preparation
   debt this posting just created.

### 2. Track — application status update

Trigger: the user reports an event on a tracked application ("sent my CV
to X", "interview with Y on Thursday", "Z rejected me", "took the offer").

1. Find the matching application (company/role; if ambiguous, ask which).
2. Update the relevant front matter fields (`cv_sent_at`,
   `application_status`, any new dates) and add a dated note under
   `# Personal notes` in the body.
3. If the status becomes `rejected`/`withdrawn`, or the position closes,
   set `status: deprecated` on the document — still readable, no longer
   active.
4. Append a line to `log.md`.

### 3. Ingest Source — new study material

Trigger: the user pastes a video link or transcript, a book chapter or
excerpt, a paper, a web page, course notes — any study material, usually
without saying which topic it belongs to.

1. Create `study-wiki/references/sources/<slug>.md` holding the raw
   content (`type: Reference`, with `source_kind`, `author`,
   `published_at`, `locator`). For long copyrighted sources (books, paywalled
   papers) do not paste the full text: keep short excerpts, definitions and
   the user's own notes, each with a page reference or timestamp.
2. **Triage**: read the source and decide which topics it covers, checking
   `topics/index.md`. One source often covers several. Record the list in
   `covers_topics` on the reference.
3. For each covered topic, update its page — **most of the work belongs in
   `# Theory in depth`**, not in the summary:
   - add the source to `sources` with a stable `id`;
   - pour the substantive content into the theory: mechanisms, formal
     definitions, formulas, pseudocode, numbers, trade-offs, failure
     modes. Don't compress until the page stops being useful — if the
     source explains an algorithm in ten steps, the page holds ten steps;
   - **organise by theme, not by source**: if three sources describe the
     same mechanism, that stays one subsection carrying three footnotes.
     Never title a subsection after a source;
   - update `# Summary` only if the new theory changes the overall picture,
     and `# Key points` by extracting from the theory you just wrote;
   - if the source offers a question or example useful in an interview, add
     it to `# Interview questions` with an answer outline;
   - add a line to `# Sources read` saying what this source contributed;
   - **if a source contradicts what's already written**, do not overwrite:
     record both versions with their respective footnotes and flag the
     conflict to the user;
   - update `coverage` per the ladder below.

   `coverage` ladder:

   | Value | Condition |
   |---|---|
   | `empty` | no sources |
   | `stub` | at least one source, theory still fragmentary |
   | `drafted` | `# Theory in depth` covers the whole topic and `# Summary` is written |
   | `solid` | plus `# In one sentence` and `# Interview questions` filled in |

   Never promote a page to `drafted` on the strength of a summary alone:
   the theory is exactly what separates an index from a notebook.

4. If a concept in `job-wiki/concepts/` points at this topic, nothing
   further is needed — the link already works both ways.
5. If the source matches no existing topic, say so and propose where it
   belongs. Don't invent new topics on your own initiative.
6. Append a line to the study wiki's `log.md`.

### 4. Query — questions about the wikis

Trigger: a question about the contents ("which postings need Kubernetes?",
"who have I sent my CV to?", "what do I know about vector databases?",
"what sources do I have on distributed tracing?").

Answer starting from the two `index.md` files, descending into pages only
when more detail is needed. For a technical question the answer comes from
the topic's `# Theory in depth`, not the summary: the summary tells *you*
whether the page is relevant, the theory is what the user asked for. Don't
re-read raw `references/` when the compiled page suffices — that's the
whole point of the pattern.

Always cite wiki pages with relative links, and when a claim comes from a
specific external source, cite that too. Never write to disk for a query
unless the user asks to archive the answer.

### 5. Prep — interview preparation

Trigger: "I have an interview with X tomorrow", "quiz me on Y", "where am
I weakest?".

1. Open the matching application and extract the required concepts.
2. Follow their `study_topic` links and read those pages.
3. Produce a two-level briefing: for each relevant topic the
   `# In one sentence` line (the fast refresher) and, for the two or three
   most likely to come up, the passages of `# Theory in depth` that are
   easy to trip over — the ones with formulas, trade-offs or failure modes.
   Add the questions already collected.
4. Highlight the gaps: topics at `coverage: empty` or `stub`, and
   `drafted` topics whose theory covers only part of the subject. For each,
   suggest what kind of source to look for.
5. This is conversational output: don't write files unless asked.

### 6. Lint — wiki health check

Trigger: the user asks to check or clean up the wikis; also run it
yourself whenever you notice inconsistencies during another operation.

Fix automatically:
- `index.md` rows missing or out of sync with the files present, in both
  wikis.
- Broken internal links pointing at a file you know was renamed or moved.
- Front matter missing `type` (add it when the content makes it obvious).
- `coverage` out of step with the page's actual contents.
- `study_topic` pointing at a nonexistent file.

Report without fixing (ask first):
- Duplicate or near-duplicate concepts in `concepts/` that should merge.
- `concepts/*.md` with neither a `study_topic` nor an explicit `null`: the
  cross-link was never assessed.
- Orphan `applications/*.md` (no links to or from `concepts/`) — usually a
  sign the tool extraction was incomplete.
- Postings with an old `posted_at` still at `application_status: candidate`
  — probably a forgotten application.
- **Uncovered priority topics**: topics at `coverage: empty` that are
  linked from concepts required by *active* applications. Rank them by how
  many applications cite them: that's the study list that actually pays.
- Topics with many sources but still at `stub`: material collected and
  never synthesised.
- Topics with a `# Summary` but an empty `# Theory in depth`: an index
  wearing a notebook's clothes.
- Theory subsections titled after a source ("What the video says") rather
  than a theme: reorganise by theme.
- Sources with an empty `covers_topics`: never triaged.

### 7. Extend — a new study module

Trigger: the user wants to cover ground outside the imported curriculum
("add system design", "I need distributed systems"), or you repeatedly hit
a concept in postings that no existing topic can house.

Non-negotiable rules:

- Numbers already used by the imported curriculum are **reserved**. An
  added module takes the next free number and carries `origin: extension`
  in its front matter, so what came from the curriculum stays
  distinguishable from what the user added later.
- Don't smuggle foreign topics into existing modules for convenience.
- Every added module declares its structural source in the `curriculum`
  field (a book, a syllabus, an interview checklist, or plainly "personal
  notes"). It records where the index came from and how much to trust its
  completeness.
- Before creating a module, check its proposed topics don't already exist
  elsewhere. The script skips exact filename collisions; a near-duplicate
  under a different name it cannot catch.

Procedure:

1. Agree the scope with the user: module title, source of the index, and
   the list of topics with a one-line description each. If the request is
   vague ("add system design"), propose a reasoned index of 5-10 topics and
   get it approved — don't generate thirty stubs that will stay empty
   forever.
2. Write the definition to `scripts/curricula/<NN>-<slug>.json`, following
   `scripts/curricula/example-curriculum.json`.
3. Run `python3 scripts/add_module.py scripts/curricula/<file>.json`. It
   creates the module page and topic stubs, updates both `index.md` files,
   and writes to `log.md`. It is idempotent: add topics to the JSON later
   and rerun, and only the new ones appear. `--dry-run` previews without
   writing.
4. **Reconnect orphaned concepts**: scan `job-wiki/concepts/*.md` for pages
   at `study_topic: null` that now have a home, and update their
   cross-links. This is the point of extending — a module that closes no
   `null` probably wasn't needed.
5. Report how many concepts were reconnected and which remain uncovered.

## When not to extend

A new module earns its place when the subject recurs across postings and
has a structure of its own. If a concept appears in a single application
and won't come back, the page in `job-wiki/concepts/` is enough on its own:
leaving it at `study_topic: null` is a legitimate answer, not a gap. The
study wiki stays useful only while it stays smaller than what you'd
actually study.

## General rules

- Don't ask for confirmation field by field: apply the schemas above and
  show a short summary at the end. Ask only on genuine ambiguity (already
  tracked? which application?).
- `references/` is write-once. Never rewrite a reference after creating it.
- `log.md` is append-only.
- Prefer enriching an existing page (`concepts/` or `topics/`) over
  creating a new one — that's what makes the wiki compound.
- The `modules/` and `topics/` skeleton comes from the curriculum: never
  add, rename or delete topics on your own initiative. Propose it, wait for
  the go-ahead, then use Extend.
- A source never replaces the synthesis: `references/sources/` stays raw,
  compiled knowledge lives in `topics/`.
- Respect the baseline OKF v0.2 constraints: every non-reserved `.md` has a
  `type`; `index.md` and `log.md` carry no front matter, except
  `okf_version` in each bundle's root `index.md`.
