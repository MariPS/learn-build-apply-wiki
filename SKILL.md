---
name: learn-build-apply-wiki
description: "Maintains three linked LLM wikis (Karpathy pattern) in Open Knowledge Format: one tracking job applications, one compiling study notes solely from material the user supplies, and one documenting the user's personal projects; job concepts and project docs link into the study wiki only where it already covers them. Postings and sources may be in any language; compiled pages are written in the wiki language the user configured. ALWAYS use this skill when the user pastes a job posting (URL, text, file), reports an application update (CV sent, interview scheduled, rejection, offer), attaches or points to the CV or cover letter they sent to a company, pastes study material (video transcript, book chapter, paper, web page, notes), asks a question about either wiki (\"which postings need Kubernetes?\", \"what do I know about vector databases?\", \"where am I weakest?\"), asks to prepare for an interview, asks to extend the study wiki with a new area, describes or documents a personal project (goal, architecture, data, experiments, decisions, deployment), asks a question about one, or asks to check or clean up the wikis. Do not wait for step-by-step instructions: autonomously apply the Ingest Job, Track, Ingest Source, Query, Prep, Lint, Extend and Document Project operations defined below."
---

# Learn Build Apply Wiki

Three linked knowledge bases — learn (`study-wiki`), build
(`project-wiki`), apply (`job-wiki`) — that turn a study plan, personal
projects and a job search into a compounding artifact instead of a pile of
browser tabs.

Following Karpathy's LLM Wiki pattern: *the LLM writes and maintains the
wiki; the human reads and asks questions.* The user should never have to
tell you which file to write or what section to put things in. That is
what this document is for.

## Architecture

Three side-by-side [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format)
v0.2 bundles, cross-linked.

### `job-wiki/` — what you applied to

- **`references/postings/`** — raw, immutable layer: the original text of
  each posting exactly as the user pasted it. `type: Reference`.
- **`references/submissions/`** — raw, immutable layer: the exact CV and
  cover letter files the user sent to each application, one folder per
  application. Kept as they were sent (usually PDF), never edited or
  regenerated, so you can always tell *which version* a company has seen.
- **`applications/`** — one page per application. `type: Job Application`.
- **`concepts/`** — the tools and theory postings ask for, shared across
  applications. `type: Technical Concept`. Each page carries a
  `study_topic` field pointing at the study-wiki page that already covers
  it (`../../study-wiki/<module>/<slug>.md`), or `null` when no topic covers
  it (yet).

### `study-wiki/` — what you actually know

The study wiki is **fed only by the user**: sources they add to
`references/sources/` (pasted, attached, or typed as their own notes) and
explicit instructions in the chat/CLI (including `scripts/add_module.py`).
Postings, applications and interview notes **never** write to it — not a
topic, not a stub, not an interview question, not a backlink. The link
runs one way: `job-wiki/concepts/` → a topic page in `study-wiki/`, and only when a
topic actually covers the concept.

- **`references/sources/`** — raw, immutable layer: one page per external
  source (video transcript, book chapter, paper, web page, course notes).
  `type: Reference`.
- **`<NN>-<module-slug>/`** — one folder per module (e.g. `01-data/`).
  Its `index.md` is the module page (no front matter, being an OKF index:
  it lists the topics with their `coverage`); the other files are one page per concept
  (`type: Study Topic`). This is where compiled knowledge accumulates.
  Topic slugs are unique across the whole study wiki, so a topic can move
  between modules without breaking its identity.

The module and topic skeleton is **imported from a curriculum the user
chooses** — a course syllabus, a textbook's table of contents, a company
interview guide, a personal checklist. It is defined in a JSON file under
`scripts/curricula/` and materialised with `scripts/add_module.py`. This
skill ships no curriculum of its own: the structure is the user's.

### `project-wiki/` — what you built

Documentation for the user's personal projects on the topics covered in
the study wiki. **One folder per project**, `project-wiki/<project-slug>/`,
holding its own pages:

- **`overview.md`** — `type: Project`: goal, scope, status, outcome.
- **Documentation pages** — `type: Project Doc`, one per `doc_kind`:
  `requirements`, `architecture`, `data`, `experiments`, `decisions`,
  `deployment`, or `notes` for anything else. The starter set is created
  by `scripts/add_project.py`; unneeded pages may be deleted, and extra
  pages added.
- **`references/`** — raw, immutable layer for the project: briefs,
  specs, pasted notes, documents received (any format), kept exactly as
  the user supplied them, with a reserved `index.md` describing each file.
  Never edit them; compile what matters into the doc pages and link back.
- **`index.md`** — the project's reserved index, listing its pages.

Project pages **reference** study topics where they rely on them: the
`study_topics` field plus a `# Study references` section with relative
links (`../../study-wiki/<module>/<slug>.md`) and one line on why the
topic matters *here*. The link runs one way, like the job wiki's: project
→ study, never the reverse. Documenting a project never writes to the
study wiki, and a project page never copies theory out of a topic: link to
it. Only link topics at `coverage` `stub` or above whose theory actually
treats the point; if none does, write the project page without a link and,
if useful, mention the gap in chat.

Project-wiki code, notebooks and data stay in the user's own repository;
the wiki holds the *documentation*, and `overview.md` records the repo
URL.

**Declared divergence from Karpathy's original layout** (`raw/` + a single
`wiki/`): the wiki is split because this domain holds knowledge with
different lifespans. An application is ephemeral — it closes. A technical
concept is durable. A study topic has a fixed shape imposed by the
curriculum. Keeping them apart stops study pages from filling up with
recruiting metadata.

## Languages

Material arrives in any language; the wiki is written in one.

- **Wiki language** — set in `wiki-config.json` at the root, next to the
  three bundles: `{ "language": "it" }` (a BCP 47 tag; `init_wiki.py --lang`
  writes it, default `en`). Read it before writing any compiled page. If
  the file is missing, ask once and create it.
- **Raw layer keeps the original.** `references/postings/` and
  `references/sources/` hold the text in the language it was written in,
  never translated, with a `language` field recording it.
- **Compiled pages are in the wiki language**: applications, concepts,
  modules, topics, project pages, `log.md` entries and your summaries to the user. When
  a source in another language introduces a term of art, keep the original
  term in parentheses on first use — "code di messaggi (*message
  queues*)" — so interview vocabulary survives the translation. Short
  quotations may stay in the original, followed by a translation.
- **Section headings and front matter keys stay as defined in this file**
  (`# 3. Theory in depth`, `coverage`, ...): they are structural anchors the
  operations rely on, not prose. Values such as `title` and `description`
  are in the wiki language.
- **Slugs are ASCII and language-neutral**: lowercase, hyphenated, accents
  stripped. For concepts use the most widely used technical name —
  usually the English one (`message-queues`, not `code-di-messaggi`) — so
  postings in different languages converge on the same page. Record the
  other names seen in postings or sources in an `aliases` list.
- **Match on meaning across languages.** "Kubernetes-Erfahrung", "esperienza
  con Kubernetes" and "Kubernetes experience" are one concept; a French
  source on *files de messages* feeds the `message-queues` topic. Check
  `title`, `aliases` and `description` before concluding nothing matches.
- If the wiki language changes, don't translate existing pages on your
  own: Lint reports the pages still in the old language and you translate
  on request.

## Naming conventions

All slugs are ASCII (see Languages).

- `job-wiki/applications/<company-slug>-<role-slug>.md`
- `job-wiki/concepts/<concept-slug>.md`
- `project-wiki/<project-slug>/<doc_kind>.md` — `overview.md` plus one
  file per documentation page; the project folder name is its slug.
  Project slugs are ASCII, short and stable once created.
- `job-wiki/references/postings/<company-slug>-<role-slug>-<YYYY-MM-DD>.md`
- `job-wiki/references/submissions/<company-slug>-<role-slug>/<kind>-<YYYY-MM-DD>.<ext>`
  — `<kind>` is `cv` or `cover-letter`, the date is when it was sent,
  `<ext>` is the original extension (`pdf`, or `md` for a cover letter
  pasted as text). A second file of the same kind on the same day gets a
  `-2`, `-3` suffix. The folder name matches the application's filename.
- `study-wiki/<NN>-<module-slug>/<topic-slug>.md` — slugs are fixed at
  import; never rename them. The module folder is `<NN>-<module-slug>/`,
  its page `index.md`.
- `study-wiki/references/sources/<author-or-channel>-<title-slug>.md`

## Front matter schemas

**Job Application** (custom fields on top of the OKF standard ones):

```yaml
type: Job Application
title: "<Role> @ <Company>"
description: "<one line>"
resource: <posting URL, if any>
tags: [...]
company: <Company>
role: <Role>
posted_at: <posting date, ISO 8601>
cv_sent_at: <date the first CV was sent, ISO 8601>
application_status: candidate | applied | interview | rejected | offer | withdrawn
status: draft | stable | deprecated   # deprecated once the position closes
language: <wiki language>
generated: { by: <actor>, at: <timestamp> }
sources:
  - id: posting
    resource: /references/postings/<file>.md
    title: <original posting title>
documents_sent:                       # one entry per file sent, oldest first
  - kind: cv | cover-letter
    sent_at: <ISO 8601 date>
    file: /references/submissions/<application-slug>/<file>   # or null: sent, file not supplied
    original_name: <filename as the user had it, e.g. CV_Rossi_EN_2026.pdf>
    language: <language the document is written in>
    note: <optional: channel, recipient, what was tailored>
```

`documents_sent` is the record of what the company actually received.
`cv_sent_at` stays as a quick filter and always equals the `sent_at` of the
first `cv` entry. An application with no documents sent yet has
`documents_sent: []`.

**Technical Concept** (in `job-wiki/concepts/`):

```yaml
type: Technical Concept
title: <Concept name, in the wiki language>
description: "<one line>"
aliases: [<names seen in postings/sources, any language>]
tags: [...]
study_topic: ../../study-wiki/<module>/<slug>.md   # or null: no topic covers it (yet)
language: <wiki language>
generated: { by: <actor>, at: <timestamp> }
```

`study_topic` is set only when the target topic is at `coverage` `stub`
or above **and** its theory actually treats the concept. An empty stub
with the right name is not coverage.

**Study Topic** (in `study-wiki/<NN>-<module-slug>/`):

```yaml
type: Study Topic
title: <Topic name, as the curriculum calls it>
description: "<one line>"
tags: [...]
module: "<NN> - <module name>"
coverage: empty | stub | drafted | solid
language: <wiki language>
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
| `# 1. In one sentence` | The 30-second interview answer. Written last. |
| `# 2. Summary` | 5-10 lines: what it is, what it's for, where it sits. Enough for a quick refresher. |
| `# 3. Theory in depth` | **The real body of the page.** Formal definitions, step-by-step mechanisms, formulas, pseudocode, trade-offs, failure modes, comparisons between alternatives. Split into `##` subsections **by theme, never by source**. |
| `# 4. Key points` | Facts to memorise, extracted from the theory above. |
| `# 5. Interview questions` | Questions taken from the user's sources or dictated by the user, each with the outline of an answer. Never copied in from postings or application notes. |
| `# 6. Sources read` | One line per source already absorbed, and what it contributed. |
| `# 7. Links` | Parent module, related topics. No links into the job wiki. |

**Numbering.** The seven sections are chapters with fixed numbers 1-7,
and the `##` subsections of `# 3. Theory in depth` are numbered `3.1`,
`3.2`, ... (a third level, if ever needed, `3.1.1`). Numbers are part of
the heading text and keep the page navigable as an outline. Everywhere
else in this file the sections are cited by name without the number
("`# Theory in depth`"): match on the text after the number. When you add,
remove or reorder a subsection, renumber the ones that follow.

Claims taken from a specific source are attributed with a markdown
footnote whose label is the source's `id` in `sources`, as OKF prescribes:
`...it works like X.[^source-id]`. Theory is the one section allowed to
grow without bound.

**Reference** (posting, in `job-wiki/references/postings/`):

```yaml
type: Reference
title: <descriptive title>
description: "Full text of the posting, verbatim, not summarised."
resource: <URL, if any>
language: <language of the posting as published>
generated: { by: <actor>, at: <timestamp> }
```

**Submitted documents** (in `job-wiki/references/submissions/`): PDFs and
other binary files carry no front matter — their metadata lives in the
application's `documents_sent`. A cover letter the user pasted as text is
saved as `.md`, verbatim, with:

```yaml
type: Reference
title: "Cover letter — <Role> @ <Company>"
description: "Cover letter as sent, verbatim."
language: <language of the letter>
generated: { by: <actor>, at: <timestamp> }
```

**Reference** (study source, in `study-wiki/references/sources/`):

```yaml
type: Reference
title: <descriptive title>
description: "<what it contains>"
resource: <URL, if any>
source_kind: video | book | paper | webpage | course | notes
author: <author or channel>
published_at: <date or year>
captured_at: <date you collected it>
locator: <chapter/pages/timestamps, where applicable>
covers_topics: [<topic-slug>, ...]
language: <language of the source>
generated: { by: <actor>, at: <timestamp> }
```

**Project** (`project-wiki/<project-slug>/overview.md`):

```yaml
type: Project
title: <Project name>
description: "<one line>"
project_status: idea | active | paused | done | archived
started_at: <ISO 8601 date>
repo: <URL of the code repository, or null>
study_modules: [<study-wiki module folder>, ...]   # areas it exercises
language: <wiki language>
generated: { by: <actor>, at: <timestamp> }
```

Body: `# Goal`, `# Scope`, `# Status`, `# Outcome` (filled when done),
`# Documentation`.

**Project Doc** (other pages in the project folder):

```yaml
type: Project Doc
title: <Page title - project name>
description: "<one line>"
project: <project-slug>
doc_kind: requirements | architecture | data | experiments | decisions | deployment | notes
study_topics: [../../study-wiki/<module>/<slug>.md, ...]   # may be empty
language: <wiki language>
generated: { by: <actor>, at: <timestamp> }
```

Body: sections suited to the `doc_kind` (the starter pages created by
`add_project.py` show them), ending with `# Study references`. In
`decisions`, one `##` entry per decision, newest first, each stating
context, options considered, choice and *why*. In `experiments`, every
entry records what changed, the metric, the result and the conclusion, so
a result can be reproduced or ruled out later. Write in the wiki language;
claims taken from an external source cite it with a link to its
`references/sources/` page when one exists.

## Routing — where does pasted material go?

Users paste things without saying which wiki they belong to. You decide,
using this procedure, **before** writing any file.

### Explicit marker (overrides everything)

If the message opens with one of these, stop reasoning and route:

- `job:` or `posting:` → Ingest Job
- `study:` or `source:` → Ingest Source
- `project:` → Document Project
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

### Signals of a submitted document (→ `job-wiki/references/submissions/`)

- A CV/résumé or a cover letter: the user's own name, experience,
  education and skills, or a letter addressed to a company about a role.
- The user says they sent it, or is about to ("here's the CV I sent to X").

It is never a posting and never a study source: it goes through Track. If
it's unclear which application it belongs to, or whether it was actually
sent or is still a draft, ask.

### Signals of a study source (→ `study-wiki`)

- **Explains how something works** rather than requiring that you know it.
- Is a transcript, chapter, paper, tutorial, documentation page, technical
  thread, or set of notes.
- The URL belongs to a video platform, a preprint server, official docs, a
  technical blog, or a code repository.
- Contains timestamps, page numbers, citations, formulas, or explanatory
  code blocks.

### Signals of project material (→ `project-wiki`)

- The user talks about *their own* work: "my project", "I'm building",
  "I chose X because", results of a run, an architecture sketch, a dataset
  they are using, a deployment they set up, a decision they made.
- A named project already in `project-wiki/`, or a request to document a
  new one.
- It is first-person and about what *was done*, not an explanation of how
  something works in general (that is a study source) nor a role someone
  is hiring for (that is a posting).

Project material never becomes a study source, even when it contains
explanations: theory the user wants kept goes through Ingest Source on
their explicit request. If a message mixes both ("here is how I did X,
and here is a paper on it"), split it: the paper is a source, the rest is
project documentation.

### The case that actually matters

A posting **mentions** technologies without explaining them. It stays a
posting. Never treat it as a study source: a list of requirements teaches
nothing, and it would pollute topic pages with recruiting language dressed
up as theory. The posting feeds `concepts/`, which **point at** topics
the user has already covered — the cross-link does the work, not
duplicated content. A posting never creates, extends or annotates
anything in the study wiki.

Conversely, a study source that talks about a company (an engineering talk
from a well-known firm) stays a source: nobody is hiring.

### When you're unsure

Ask, in one short question, with your guess already stated: "This looks
like study material on vector databases — treat it as a source, or is it a
posting to track?" Don't guess silently: a posting that lands among the topics
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
   verbatim text in its original language (`type: Reference`, with
   `language`).
2. Check `applications/index.md`: is this already tracked (same company +
   role)? If so, update the existing page instead of creating a new one.
3. Create or update `applications/<slug>.md` in the wiki language:
   extract company, role, posting date, job description, responsibilities,
   required tools. Link `sources` to the reference you just created.
4. For each required tool or theoretical concept: first search
   `concepts/index.md` for an existing page covering it (match on meaning,
   across languages — check `aliases`). If one exists, update it with the
   new context, add any new wording to `aliases`, and link the new
   application; otherwise create a minimal new page. Never duplicate a
   concept.
5. **Link to study, read-only**: for each concept touched with no
   `study_topic` yet, look in the module `index.md` files (listed in `study-wiki/index.md`) for a topic
   that already covers it (see the rule under the Technical Concept
   schema).
   - Covered → set `study_topic` and add a `# Further study` section with
     the relative link.
   - Not covered → `study_topic: null`. Stop there: don't propose topics,
     modules or sources, and don't touch any file in `study-wiki/`.
6. If the user also attached a CV or cover letter they sent for this
   posting, record it as in Track (step 3).
7. Append a line to the job wiki's `log.md`.
8. Refresh the affected rows in `applications/index.md` and
   `concepts/index.md`.
9. Summarise in a few lines what you created or updated, and which
   concepts got linked to an existing study topic.

### 2. Track — application status update

Trigger: the user reports an event on a tracked application ("sent my CV
to X", "interview with Y on Thursday", "Z rejected me", "took the offer"),
or hands you the CV or cover letter they sent.

1. Find the matching application (company/role; if ambiguous, ask which).
2. Update the relevant front matter fields (`cv_sent_at`,
   `application_status`, any new dates) and add a dated note under
   `# Personal notes` in the body.
3. **Documents sent.** When the event involves sending a CV or cover
   letter (an application, a follow-up with an updated CV, a letter sent
   later):
   - If the user didn't attach the file or give its path, ask once which
     file it was ("which PDF did you send? give me the path or attach
     it"). Don't block on it: if they don't have it, record the entry with
     `file: null`.
   - **Copy** the file — never move it, never alter it, never re-export or
     regenerate it — to
     `references/submissions/<application-slug>/<kind>-<YYYY-MM-DD>.<ext>`.
     A cover letter pasted as text becomes a verbatim `.md` with the
     Reference front matter above.
   - Append an entry to `documents_sent` with `kind`, `sent_at`, `file`,
     `original_name`, `language` (read it from the document) and, if the
     user said so, a `note` (channel, recipient, what was tailored).
   - For a `cv` entry, set `cv_sent_at` if it's still empty; move
     `application_status` from `candidate` to `applied` unless the user
     says otherwise.
   - If the file is identical to one already sent to another application
     (same content), still copy it: each application's folder must be
     self-contained. Mention it in the summary ("same CV you sent to Y").
4. If the status becomes `rejected`/`withdrawn`, or the position closes,
   set `status: deprecated` on the document — still readable, no longer
   active.
5. Append a line to `log.md`, naming the documents recorded.
6. Refresh the application's row in `applications/index.md`.

### 3. Ingest Source — new study material

Trigger: the user pastes a video link or transcript, a book chapter or
excerpt, a paper, a web page, course notes, or dictates their own notes
in the chat/CLI — any study material, usually without saying which topic
it belongs to. Also: the user drops a file into `references/sources/`
by hand and asks you to process it (skip step 1, fill in the missing
front matter).

This is the only operation, together with Extend, that writes study
content.

1. Create `study-wiki/references/sources/<slug>.md` holding the raw
   content in its original language (`type: Reference`, with
   `source_kind`, `author`, `published_at`, `locator`, `language`). For
   long copyrighted sources (books, paywalled papers) do not paste the
   full text: keep short excerpts, definitions and the user's own notes,
   each with a page reference or timestamp.
2. **Triage**: read the source and decide which topics it covers, checking
   the module `index.md` files. One source often covers several. Record the list in
   `covers_topics` on the reference.
3. For each covered topic, update its page in the wiki language,
   whatever the source's language — **most of the work belongs in
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

4. **Link from jobs**: for each topic that now reaches `stub` or above,
   scan `job-wiki/concepts/` for pages at `study_topic: null` whose
   concept this topic's theory now covers. Set their `study_topic`, add
   `# Further study`, and log it in the job wiki's `log.md`. This writes
   only to the job wiki; the topic page itself stays unaware of postings.
5. If the source matches no existing topic, say so and propose where it
   belongs. Don't invent new topics on your own initiative.
6. Append a line to the study wiki's `log.md`.

### 4. Query — questions about the wikis

Trigger: a question about the contents ("which postings need Kubernetes?",
"who have I sent my CV to?", "which CV did X get?", "which applications
got a cover letter?", "what do I know about vector databases?",
"what sources do I have on distributed tracing?").

Answer starting from the relevant `index.md` files (`project-wiki/index.md` and the project's own for questions about a project: "what did I decide about the model?", "which projects use feature stores?"), descending into pages only
when more detail is needed. For a technical question the answer comes from
the topic's `# Theory in depth`, not the summary: the summary tells *you*
whether the page is relevant, the theory is what the user asked for. Don't
re-read raw `references/` when the compiled page suffices — that's the
whole point of the pattern. Questions about documents sent are answered
from `documents_sent`; open the files themselves only when the question is
about their content ("what did I say about Kafka in the letter to X?").

Always cite wiki pages with relative links, and when a claim comes from a
specific external source, cite that too. Never write to disk for a query
unless the user asks to archive the answer.

### 5. Prep — interview preparation

Trigger: "I have an interview with X tomorrow", "quiz me on Y", "where am
I weakest?".

1. Open the matching application and extract the required concepts.
   Read the CV and cover letter in its `documents_sent`: the interviewer
   has them in front of them, so surface what they claim (projects,
   skills, numbers) that is likely to be probed, and any claim touching a
   gap found in step 4.
2. Follow their `study_topic` links and read those pages.
3. Produce a two-level briefing: for each relevant topic the
   `# In one sentence` line (the fast refresher) and, for the two or three
   most likely to come up, the passages of `# Theory in depth` that are
   easy to trip over — the ones with formulas, trade-offs or failure modes.
   Add the questions already collected.
4. Highlight the gaps: required concepts at `study_topic: null` (the study
   wiki doesn't cover them), linked topics still at `stub`, and `drafted`
   topics whose theory covers only part of the subject. For each, suggest
   what kind of source to look for.
5. This is conversational output: don't write files unless asked — in
   particular, never add the gaps to the study wiki. What gets studied is
   the user's call, made by adding sources.
6. Answer in the wiki language, quoting technical terms in the language
   the interview will be held in when that differs (usually the posting's
   `language`).

### 6. Lint — wiki health check

Trigger: the user asks to check or clean up the wikis; also run it
yourself whenever you notice inconsistencies during another operation.

Fix automatically:
- Study topic headings: sections missing their number (1-7) or
  theory subsections out of sequence (`3.1`, `3.2`, ...) → renumber.
- `index.md` rows missing or out of sync with the files present, in all
  wikis (module indexes list their topics as a numbered list, in curriculum
  order).
- Links to a folder (`](folder/)`) instead of its `index.md`: Obsidian
  treats them as a missing note and creates an empty `folder.md` in the root
  when clicked → point them at `folder/index.md`, creating it if absent.
- Front matter that doesn't parse as YAML (typically an unquoted
  `description` containing `: `) → wrap the value in double quotes.
- Broken internal links pointing at a file you know was renamed or moved.
- Front matter missing `type` (add it when the content makes it obvious).
- `coverage` out of step with the page's actual contents.
- `study_topic` pointing at a nonexistent file, or at a topic at
  `coverage: empty` → reset to `null`.
- **Missed links**: `concepts/*.md` at `study_topic: null` (or with no
  `study_topic` at all) whose concept is now covered by a topic → set the
  link and add `# Further study`. Match on meaning, across languages.
- **Leaks into the study wiki**: study pages that link into the job wiki,
  name companies or postings, or carry interview questions taken from
  postings or application notes → remove them (the concept page in the
  job wiki is where that belongs; move it there if it isn't already).
- Missing `language` on a compiled page: add it (the wiki language, or
  whatever the page is actually written in).
- Project pages: `study_topics` or `# Study references` links to a missing
  file or to a topic at `coverage: empty` → remove the link; project
  folders missing from `project-wiki/index.md`, or pages missing from the
  project's `index.md`; `overview.md` missing.
- **Leaks into the study wiki** (extended): study pages that link into the
  project wiki, or contain a user's project decisions or results → remove
  them (they belong in `project-wiki/`).
- `cv_sent_at` out of step with the first `cv` entry in `documents_sent`;
  applications with no `documents_sent` field → add `documents_sent: []`.

Report without fixing (ask first):
- Duplicate or near-duplicate concepts in `concepts/` that should merge,
  including the same concept filed under names in two languages.
- Orphan `applications/*.md` (no links to or from `concepts/`) — usually a
  sign the tool extraction was incomplete.
- Postings with an old `posted_at` still at `application_status: candidate`
  — probably a forgotten application.
- Compiled pages whose `language` differs from the wiki language:
  translate on request.
- References missing `language` (they're write-once: add it only with the
  user's go-ahead).
- Topics with many sources but still at `stub`: material collected and
  never synthesised.
- Topics with a `# Summary` but an empty `# Theory in depth`: an index
  wearing a notebook's clothes.
- Theory subsections titled after a source ("What the video says") rather
  than a theme: reorganise by theme.
- Sources with an empty `covers_topics`: never triaged.
- Projects at `project_status: active` with no log activity for a long
  time; projects at `done` with an empty `# Outcome`; decisions or
  experiments pages left as the untouched template.
- `documents_sent` entries whose `file` doesn't exist, or is `null`
  (ask the user for the file).
- Files in `references/submissions/` not listed in any application's
  `documents_sent`: which application, and when were they sent?
- Applications at `applied` or beyond with no `cv` entry in
  `documents_sent`: the CV sent isn't on record.

### 7. Document Project — a personal project

Trigger: the user describes or updates one of their projects (a goal, a
design, a dataset, an experiment and its result, a decision, a deployment
step), asks you to document it, or asks to start a new project wiki
entry. Also when a study checklist or plan turns out to be project
documentation: propose moving it, don't move it silently.

1. **Find the project.** Match on meaning against the folders of
   `project-wiki/` (and `index.md`). If it doesn't exist, create it with
   `python3 scripts/add_project.py "<name>" --description "<one line>"`,
   after confirming the name in one short question if it isn't obvious.
   Never create a second folder for a project that exists under another
   name.
2. **Raw material first.** A brief, spec, dataset description or pasted
   notes about the project is copied unchanged into
   `<project>/references/` and listed in its `index.md`; then compile it
   into the doc pages below.
3. **Route the content** to the page of the right `doc_kind`, creating a
   `notes` page only when nothing fits. Enrich the existing section
   rather than appending at the bottom; keep `experiments` and
   `decisions` chronological and append-only in spirit (correct a past
   entry by adding a new one that supersedes it, dated).
4. **Link to study, read-only.** For each concept the page relies on, look
   in the study module `index.md` files for a topic that covers it
   (`coverage` `stub` or above, theory actually treating the point). Add
   the relative link to `study_topics` and a line in `# Study references`
   saying why it matters here. If no topic covers it, write the page
   without a link. **Never** create, edit or annotate anything in
   `study-wiki/`, and don't propose new topics unless asked.
5. Update `overview.md`: `# Status`, `project_status` when it changes, and
   `study_modules`. When a project is `done`, fill in `# Outcome`.
6. Refresh the project's `index.md` if pages were added or removed, and
   the project's row in `project-wiki/index.md`.
7. Append a line to `project-wiki/log.md` naming the project and pages
   touched.
8. Summarise in a few lines what you wrote, and which study topics you
   linked.

Do not invent results, metrics or decisions: write only what the user
told you or what is in files they gave you. Mark anything inferred as
such, or ask.

### 8. Extend — a new study module

Trigger: **only** an explicit request from the user to cover ground
outside the imported curriculum ("add system design", "I need distributed
systems"), or the user running `scripts/add_module.py` themselves. Never
propose or start an extension because postings keep asking for something:
the study wiki follows the user's plan, not the job market.

Non-negotiable rules:

- Numbers already used by the imported curriculum are **reserved**. An
  added module takes the next free number and carries `origin: extension`
  in its curriculum JSON and on its `index.md`, so what came from the curriculum stays
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
   creates the module folder with its `index.md` and the topic stubs,
   updates `study-wiki/index.md`, and writes to `log.md`. It is idempotent: add topics to the JSON later
   and rerun, and only the new ones appear. `--dry-run` previews without
   writing. Topic names and descriptions go in the wiki language; give a
   topic an explicit `"slug"` when its name alone wouldn't produce the
   language-neutral slug you want.
4. New topics start at `coverage: empty`, so no job concept links to them
   yet: links appear once Ingest Source fills them in.

## When not to extend

A new module earns its place when the user wants to study a subject with
a structure of its own. A concept that shows up in postings but not in
the study wiki is not a gap to close: `study_topic: null` is a legitimate,
permanent answer. The study wiki stays useful only while it stays smaller
than what you'd actually study.

## General rules

- Don't ask for confirmation field by field: apply the schemas above and
  show a short summary at the end. Ask only on genuine ambiguity (already
  tracked? which application?).
- **Study wiki boundary**: only Ingest Source, Extend and explicit user
  requests add content to `study-wiki/`; Lint may only repair it (indexes,
  links, `coverage`, removing job and project leaks). Ingest Job, Track,
  Prep, Query and Document Project never write there. Cross-links are written on the job side only.
- Compiled pages in the wiki language; raw references in their original
  language (see Languages).
- `references/` is write-once. Never rewrite a reference after creating it.
  For `references/submissions/` this is strict: the file is what the
  company received, byte for byte. A newer CV is a new file and a new
  `documents_sent` entry, never a replacement.
- `log.md` is append-only.
- Prefer enriching an existing page (`concepts/` or a study topic) over
  creating a new one — that's what makes the wiki compound.
- The module/topic skeleton comes from the curriculum: never
  add, rename or delete topics on your own initiative. Propose it, wait for
  the go-ahead, then use Extend.
- A source never replaces the synthesis: `references/sources/` stays raw,
  compiled knowledge lives in the topic pages.
- Respect the baseline OKF v0.2 constraints: every non-reserved `.md` has a
  `type`; `index.md` and `log.md` carry no front matter, except
  `okf_version` in each bundle's root `index.md`.
- Front matter must be valid YAML (Obsidian shows "invalid properties"
  otherwise). Always write `description` (and `title`) as a double-quoted
  string: an unquoted value containing `: ` or `#` breaks the parse.
  Escape inner double quotes as `\"`.
