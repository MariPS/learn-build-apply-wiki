# career-wiki

**An Agent Skill for running a job search as an LLM wiki — two linked
knowledge bases in [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format),
maintained by your agent instead of by you.**

A job search generates two kinds of knowledge that usually get lost in
separate places: what you applied to, and what you had to learn because of
it. This skill keeps both as markdown, and links them.

- **`job-wiki/`** — one page per application: company, role, dates,
  status, required tools, the original posting kept verbatim.
- **`study-wiki/`** — one page per concept, grouped into modules imported
  from a curriculum *you* choose, fed by books, papers, video transcripts,
  documentation and your own notes.

The link runs through a `study_topic` field: every concept a posting
requires points at the study page where its theory lives. Which means the
system can answer *which topics do my active applications need that I
haven't studied yet* — the one question a pile of bookmarks can't.

Built on [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f):
the LLM writes and maintains the wiki, the human reads and asks questions.
Compiled pages, not retrieval over raw chunks.

## What the agent does on its own

| Operation | Trigger | Result |
|---|---|---|
| **Ingest Job** | you paste a posting | raw posting saved, application page written, required concepts created or updated and linked to study topics |
| **Track** | "sent my CV to X", "they rejected me" | status and dates updated, dated note added |
| **Ingest Source** | you paste a transcript, chapter, paper, page | source saved raw, triaged to the topics it covers, theory written with per-claim footnotes |
| **Query** | "what do I know about X?" | answer compiled from the wiki, with citations |
| **Prep** | "interview tomorrow with X" | briefing from the linked topics, plus the gaps to close first |
| **Lint** | "check the wikis" | index drift and broken links fixed; duplicates, orphans and uncovered priority topics reported |
| **Extend** | "add a module on system design" | new module scaffolded, orphaned concepts reconnected |

You never say which file to write. That's the point.

## Install

```bash
git clone https://github.com/<you>/career-wiki.git
cd career-wiki
python3 scripts/init_wiki.py
```

Then make `SKILL.md` available to your agent:

- **Claude Code, Cursor, Codex and other Agent Skills tools** — copy the
  repository into your skills directory (e.g.
  `.claude/skills/career-wiki/`).
- **Chat interfaces** — load it as a custom skill if your setup allows
  one, otherwise attach `SKILL.md` alongside your wiki files at the start
  of a session.

Requirements: Python 3.8+ for the two scripts. Nothing else — no
dependencies, no database, no build step. It's markdown and git.

## Bring your own curriculum

The study wiki's skeleton is not shipped with this repo, on purpose. Any
index that's useful for *your* interviews will do:

- the table of contents of a textbook you're working through
- a course or bootcamp syllabus
- an interview-prep checklist for your target roles
- the documentation outline of a framework you need to learn
- your own list of what keeps coming up in postings

Describe it as JSON and materialise it:

```bash
cp scripts/curricula/example-curriculum.json scripts/curricula/01-foundations.json
$EDITOR scripts/curricula/01-foundations.json
python3 scripts/add_module.py scripts/curricula/01-foundations.json --dry-run
python3 scripts/add_module.py scripts/curricula/01-foundations.json
```

One JSON file per module. The script creates the module page and topic
stubs, updates both indexes and appends to the log. It's idempotent: add
topics to the JSON later and rerun — only the new ones appear, and pages
you've already filled in are never touched.

Record where an index came from in the `curriculum` field, so later you
know how much to trust its completeness. Mark modules you add after the
first import with `"origin": "extension"`.

## How a study page is shaped

```
# In one sentence     the 30-second interview answer, written last
# Summary             5-10 lines, enough for a quick refresher
# Theory in depth     the real body of the page
# Key points          facts to memorise, extracted from the theory
# Interview questions each with an answer outline
# Sources read        what each source contributed, so you know where you stopped
# Links               parent module, related topics, concepts pointing here
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
theory. Postings feed `concepts/`, which *point at* topics. The cross-link
does the work — never duplicated content.

## Layout

```
SKILL.md                  the agent's instructions — architecture, schemas, operations
scripts/
  init_wiki.py            create the two empty bundles
  add_module.py           materialise a curriculum module into pages
  curricula/              your module definitions, as JSON
templates/                page types, for creating one by hand
examples/                 a small worked example with fictional data
```

Everything is plain markdown with YAML front matter. Use git for history
and provenance; there's nothing else to back up.

## See also

- [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format)
  — the spec these bundles conform to
- [Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
  — the pattern this implements
- [Agent Skills](https://agentskills.io) — the skill format

## License

MIT. See [LICENSE](LICENSE).
