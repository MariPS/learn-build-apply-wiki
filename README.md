# learn-build-apply-wiki

**An Agent Skill that keeps the whole path from studying to getting hired
as an LLM wiki: what you learn, what you build, what you apply to — three
linked knowledge bases in [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format),
maintained by your agent instead of by you.**

Learning a field, building projects to prove it and applying for jobs
generate knowledge that usually gets lost in separate places. This skill
keeps all three as markdown, and links them: the study wiki holds what you
know, the project wiki documents what you built and points at the study
topics behind it, the job wiki tracks what you applied to and what each
posting asked for.

*Learn → Build → Apply.*

- **`job-wiki/`** — one page per application: company, role, dates,
  status, required tools, the original posting kept verbatim, and the
  exact CV and cover letter you sent (PDFs kept as they were).
- **`study-wiki/`** — one page per concept, grouped into modules (one
  folder each; for an ML/AI wiki, the stages of the pipeline) imported
  from a curriculum *you* choose, fed **only** by what you give it: books,
  papers, video transcripts, documentation and your own notes, added to
  `references/sources/` or through the chat/CLI.
- **`project-wiki/`** — documentation of your personal projects, one
  folder per project (overview, requirements, architecture, data,
  experiments, decisions, deployment, plus a `references/` folder for the
  raw briefs and specs). Pages reference the study topics
  they rely on, so the theory lives once and the projects point at it.

The link runs one way, through a `study_topic` field: when a concept a
posting requires is already covered by a study page, the concept points at
it. Postings never write to the study wiki — no stubs, no "you should
study this" topics. What you study stays your plan; the job wiki just tells
you where your notes already apply.

Postings and sources can be in any language. You pick the language the
wiki itself is written in; the raw material is kept as it came.

Built on [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f):
the LLM writes and maintains the wiki, the human reads and asks questions.
Compiled pages, not retrieval over raw chunks.

## What the agent does on its own

| Operation | Trigger | Result |
|---|---|---|
| **Ingest Job** | you paste a posting | raw posting saved, application page written, required concepts created or updated and linked to study topics that already cover them |
| **Track** | "sent my CV to X" (with the PDF), "they rejected me" | status and dates updated, dated note added; the CV / cover letter sent copied into the wiki and recorded on the application |
| **Ingest Source** | you paste a transcript, chapter, paper, page, or your own notes | source saved raw, triaged to the topics it covers, theory written with per-claim footnotes; job concepts now covered get linked |
| **Query** | "what do I know about X?" | answer compiled from the wiki, with citations |
| **Prep** | "interview tomorrow with X" | briefing from the linked topics, plus the gaps — in chat, never written into the study wiki |
| **Lint** | "check the wikis" | index drift, broken and missed job→study links fixed, job content leaked into study pages removed; duplicates and orphans reported |
| **Document Project** | "in my project I chose X because…", "document this experiment" | project folder created if new; the content filed in the right page (architecture, experiments, decisions…), with links to the study topics it relies on; nothing written to the study wiki |
| **Extend** | "add a module on system design" (only when you ask) | new module scaffolded |

You never say which file to write. That's the point.

## Install

```bash
git clone https://github.com/MariPS/learn-build-apply-wiki.git
cd learn-build-apply-wiki
python3 scripts/init_wiki.py --lang it   # the language the wiki is written in; default en
```

Then make `SKILL.md` available to your agent:

- **Claude Code, Cursor, Codex and other Agent Skills tools** — copy the
  repository into your skills directory (e.g.
  `.claude/skills/learn-build-apply-wiki/`).
- **Chat interfaces** — load it as a custom skill if your setup allows
  one, otherwise attach `SKILL.md` alongside your wiki files at the start
  of a session.

Requirements: Python 3.8+ for the scripts. Nothing else — no
dependencies, no database, no build step. It's markdown and git.

## Bring your own curriculum

The study wiki's skeleton is not shipped with this repo, on purpose. Any
index that's useful for *your* interviews will do:

- the table of contents of a textbook you're working through
- a course or bootcamp syllabus
- an interview-prep checklist for your target roles
- the documentation outline of a framework you need to learn
- your own list of what you've decided to study

Describe it as JSON and materialise it:

```bash
cp scripts/curricula/example-curriculum.json scripts/curricula/01-foundations.json
$EDITOR scripts/curricula/01-foundations.json
python3 scripts/add_module.py scripts/curricula/01-foundations.json --dry-run
python3 scripts/add_module.py scripts/curricula/01-foundations.json
```

One JSON file per module. The script creates the module folder (with its `index.md`) and topic
stubs, updates the study index and appends to the log. It's idempotent: add
topics to the JSON later and rerun — only the new ones appear, and pages
you've already filled in are never touched.

Record where an index came from in the `curriculum` field, so later you
know how much to trust its completeness. Mark modules you add after the
first import with `"origin": "extension"`.

## How a study page is shaped

```
# 1. In one sentence   the 30-second interview answer, written last
# 2. Summary           5-10 lines, enough for a quick refresher
# 3. Theory in depth   the real body, subsections 3.1, 3.2, ...
# 4. Key points        facts to memorise, extracted from the theory
# 5. Interview questions each with an answer outline
# 6. Sources read      what each source contributed, so you know where you stopped
# 7. Links             parent module, related topics (never the job wiki)
```

Two rules make the difference between a notebook and an index:

**Theory is organised by theme, never by source.** If three sources
describe the same mechanism, that stays one subsection carrying three
footnotes. Subsections titled "what the video says" are how these systems
degenerate into a stack of disconnected summaries.

**A page with a summary but no theory does not reach `drafted`.** Coverage
runs `empty` → `stub` → `drafted` → `solid`, and the ladder is anchored to
the theory section, not to how many sources you've collected.

Attribution uses OKF footnotes, so any claim can be traced back to the
source it came from. When two sources disagree, both versions stay, with
their respective footnotes, and the agent flags the conflict.

## Posting or study source?

The agent routes pasted material on its own, before writing anything:
explicit marker first, then signals in the text, then a question when it's
genuinely ambiguous.

Prefix a message to remove all doubt:

```
job:    <the posting>
study:  <the transcript, chapter, paper>
```

The case worth knowing: **a posting that mentions technologies stays a
posting.** A list of requirements teaches nothing, and letting it into a
topic page fills your study notes with recruiting language dressed up as
theory. Postings feed `concepts/`, which *point at* topics you've already
covered. The cross-link does the work — never duplicated content.

## Languages

`wiki-config.json` holds one setting, the wiki language:

```json
{ "language": "it" }
```

- Postings and sources are saved **as they came**, in their own language,
  with a `language` field.
- Everything the agent writes — applications, concepts, topics, logs,
  answers — is in the wiki language. Terms of art from a source in another
  language keep the original in parentheses on first use, so interview
  vocabulary isn't lost.
- Filenames are ASCII and language-neutral (`message-queues.md`), and
  concepts carry `aliases`, so a German posting and an English one land on
  the same page.
- Section headings (`# 3. Theory in depth`, ...) and front matter keys stay in
  English: they're the structure the agent navigates by.

Change the language with `python3 scripts/init_wiki.py --lang <tag>`.
Existing pages aren't translated automatically; Lint lists them and the
agent translates on request.

## Layout

```
SKILL.md                  the agent's instructions — architecture, schemas, operations
wiki-config.json          wiki language (created by init_wiki.py)
scripts/
  init_wiki.py            create the three empty bundles
  add_module.py           materialise a curriculum module into pages
  add_project.py          create a project folder with starter doc pages
  curricula/              your module definitions, as JSON
templates/                page types, for creating one by hand
examples/                 a small worked example with fictional data
```

Everything is plain markdown with YAML front matter, plus the CV and
cover letter files you sent, kept under
`job-wiki/references/submissions/<application>/`. Use git for history
and provenance; there's nothing else to back up.

Those files hold personal data. If you push your wikis anywhere public,
keep `job-wiki/references/submissions/` out of it (see `.gitignore`).

## Documenting a project

```bash
python3 scripts/add_project.py "Air quality forecasting" --description "Hourly PM10 forecasts"
```

creates `project-wiki/air-quality-forecasting/` with starter pages. After
that you just tell the agent what you did and decided; it files it in the
right page and links the study topics involved. The link runs one way, from
project to study, never back.

## See also

- [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format)
  — the spec these bundles conform to
- [Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
  — the pattern this implements
- [Agent Skills](https://agentskills.io) — the skill format

## License

MIT. See [LICENSE](LICENSE).
