#!/usr/bin/env python3
"""Add a module (and its topics) to the study wiki.

Usage:
    python3 scripts/add_module.py scripts/curricula/my-module.json
    python3 scripts/add_module.py scripts/curricula/my-module.json --dry-run

The JSON definition looks like this:

{
  "number": "01",
  "slug": "foundations",
  "title": "Foundations",
  "curriculum": "Whatever syllabus, book or checklist this index came from",
  "resource": "https://example.com/syllabus",
  "language": "en",
  "topics": [
    {"name": "First Topic",
     "description": "One line on what this topic covers."},
    {"name": "Code di messaggi", "slug": "message-queues",
     "description": "An explicit slug overrides the one derived from the name."},
    {"name": "Second Topic",
     "description": "One line on what this topic covers."}
  ]
}

`number` orders modules and prefixes their filenames. `curriculum` and
`resource` are optional but recommended: they record where an index came
from. Set "origin": "extension" for modules added after the first import.

`language` is the language names and descriptions are written in; it
defaults to the wiki language in career-wiki.json (next to study-wiki/),
or "en". Slugs are always ASCII: accents are stripped, and a topic may set
its own "slug" to stay language-neutral (e.g. "message-queues" for a topic
named "Code di messaggi").

The script is idempotent: existing topic pages are never overwritten, so
you can add entries to the JSON and rerun it safely.
"""

import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "study-wiki")
ROOT = os.path.normpath(ROOT)
ACTOR = os.environ.get("WIKI_ACTOR", "human:you")
CONFIG = os.path.normpath(os.path.join(ROOT, "..", "career-wiki.json"))


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def wiki_language():
    if os.path.exists(CONFIG):
        return json.loads(read(CONFIG)).get("language", "en")
    return "en"


def slugify(s):
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii").lower()
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def topic_slug(t):
    return t.get("slug") or slugify(t["name"])


def topic_page(name, desc, module_label, module_link, lang):
    return f"""---
type: Study Topic
title: "{name}"
description: {desc}
tags: [{slugify(module_label.split(' - ', 1)[-1])}]
module: "{module_label}"
coverage: empty        # empty | stub | drafted | solid
language: {lang}
generated: {{ by: {ACTOR}, at: {NOW} }}
---

# In one sentence

<!-- The 30-second interview answer. Write this last, once the theory
     below is solid enough. -->

# Summary

{desc}

<!-- 5-10 lines: what it is, what it's for, where it sits. -->

# Theory in depth

<!-- The real body of the page, compiled from the sources listed in
     `sources`. Organise by theme, never by source: if three sources
     describe the same mechanism, that stays one subsection carrying
     three footnotes. Every claim taken from a source gets that source's
     footnote id. Formal definitions, step-by-step mechanisms, formulas,
     pseudocode, trade-offs, failure modes and comparisons between
     alternatives all belong here. -->

## <First subtheme>

# Key points

-

# Interview questions

-

# Sources read

-

# Links

- Module: [{module_label}](/modules/{module_link}.md)
"""


def module_page(m, topics, lang):
    label = f"{m['number']} - {m['title']}"
    rows = "\n".join(
        f"* [{t['name']}](/topics/{topic_slug(t)}.md) - {t['description']}"
        for t in topics
    )
    src_block = ""
    footnote = ""
    if m.get("resource"):
        src_block = f"""sources:
  - id: curriculum
    resource: {m['resource']}
    title: {m.get('curriculum', m['title'])}
"""
        footnote = (
            f"\nTopic index derived from: {m.get('curriculum', m['title'])}."
            "[^curriculum]\n\n[^curriculum]: "
            f"{m.get('curriculum', m['title'])}\n"
        )
    resource_line = f"resource: {m['resource']}\n" if m.get("resource") else ""
    return f"""---
type: Study Module
title: "{label}"
description: Module {m['number']} of the study curriculum.
{resource_line}tags: [curriculum, {slugify(m['title'])}]
module_number: {int(m['number'])}
origin: {m.get('origin', 'curriculum')}
language: {lang}
generated: {{ by: {ACTOR}, at: {NOW} }}
{src_block}---

# Topics in this module

{rows}
{footnote}"""


def append_module_index(m, n_topics):
    path = os.path.join(ROOT, "modules", "index.md")
    plural = "topic" if n_topics == 1 else "topics"
    line = f"* [{m['number']} - {m['title']}]({m['number']}-{m['slug']}.md) - {n_topics} {plural}"
    content = read(path).rstrip("\n")
    if line in content:
        return
    sep = "\n\n" if content.rstrip().endswith("# Modules") else "\n"
    write(path, content.rstrip("\n") + sep + line + "\n")


def append_topic_index(m, topics):
    path = os.path.join(ROOT, "topics", "index.md")
    content = read(path).rstrip("\n")
    header = f"# {m['number']} - {m['title']}"
    if header in content:
        return
    rows = "\n".join(
        f"* [{t['name']}]({topic_slug(t)}.md) - {t['description']}" for t in topics
    )
    write(path, f"{content}\n\n{header}\n\n{rows}\n")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(1)

    m = json.loads(read(args[0]))
    for key in ("number", "slug", "title", "topics"):
        if key not in m:
            sys.exit(f"Missing required field: {key}")

    lang = m.get("language") or wiki_language()
    label = f"{m['number']} - {m['title']}"
    link = f"{m['number']}-{m['slug']}"
    created, skipped = [], []

    for t in m["topics"]:
        path = os.path.join(ROOT, "topics", topic_slug(t) + ".md")
        if os.path.exists(path):
            skipped.append(os.path.basename(path))
            continue
        created.append(os.path.basename(path))
        if not dry:
            write(path, topic_page(t["name"], t["description"], label, link, lang))

    mod_path = os.path.join(ROOT, "modules", link + ".md")
    if not dry:
        write(mod_path, module_page(m, m["topics"], lang))
        append_module_index(m, len(m["topics"]))
        append_topic_index(m, m["topics"])
        log_path = os.path.join(ROOT, "log.md")
        today = str(datetime.now(timezone.utc).date())
        existing = read(log_path) if os.path.exists(log_path) else ""
        header = "" if f"## {today}" in existing else f"\n## {today}\n"
        entry = (
            f"* **Extend**: added module {label} with {len(m['topics'])} "
            f"topic{'' if len(m['topics']) == 1 else 's'} "
            f"({len(created)} new, {len(skipped)} already present).\n"
        )
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(header + entry)

    print(f"{'[dry-run] ' if dry else ''}Module {label}")
    print(f"  created: {len(created)} topic{'' if len(created) == 1 else 's'}")
    if skipped:
        print(f"  skipped: {len(skipped)} already present -> {', '.join(skipped)}")
    if not dry:
        print(f"  files:   modules/{link}.md, both index.md refreshed, log.md appended")


NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

if __name__ == "__main__":
    main()
