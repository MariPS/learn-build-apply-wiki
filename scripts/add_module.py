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
  "topics": [
    {"name": "First Topic",
     "description": "One line on what this topic covers."},
    {"name": "Second Topic",
     "description": "One line on what this topic covers."}
  ]
}

`number` orders modules and prefixes their filenames. `curriculum` and
`resource` are optional but recommended: they record where an index came
from. Set "origin": "extension" for modules added after the first import.

The script is idempotent: existing topic pages are never overwritten, so
you can add entries to the JSON and rerun it safely.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "study-wiki")
ROOT = os.path.normpath(ROOT)
ACTOR = os.environ.get("WIKI_ACTOR", "human:you")


def slugify(s):
    s = s.lower()
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def topic_page(name, desc, module_label, module_link):
    return f"""---
type: Study Topic
title: "{name}"
description: {desc}
tags: [{slugify(module_label.split(' - ', 1)[-1])}]
module: "{module_label}"
coverage: empty        # empty | stub | drafted | solid
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


def module_page(m, topics):
    label = f"{m['number']} - {m['title']}"
    rows = "\n".join(
        f"* [{t['name']}](/topics/{slugify(t['name'])}.md) - {t['description']}"
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
generated: {{ by: {ACTOR}, at: {NOW} }}
{src_block}---

# Topics in this module

{rows}
{footnote}"""


def append_module_index(m, n_topics):
    path = os.path.join(ROOT, "modules", "index.md")
    plural = "topic" if n_topics == 1 else "topics"
    line = f"* [{m['number']} - {m['title']}]({m['number']}-{m['slug']}.md) - {n_topics} {plural}"
    content = open(path).read().rstrip("\n")
    if line in content:
        return
    sep = "\n\n" if content.rstrip().endswith("# Modules") else "\n"
    open(path, "w").write(content.rstrip("\n") + sep + line + "\n")


def append_topic_index(m, topics):
    path = os.path.join(ROOT, "topics", "index.md")
    content = open(path).read().rstrip("\n")
    header = f"# {m['number']} - {m['title']}"
    if header in content:
        return
    rows = "\n".join(
        f"* [{t['name']}]({slugify(t['name'])}.md) - {t['description']}" for t in topics
    )
    open(path, "w").write(f"{content}\n\n{header}\n\n{rows}\n")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(1)

    m = json.load(open(args[0]))
    for key in ("number", "slug", "title", "topics"):
        if key not in m:
            sys.exit(f"Missing required field: {key}")

    label = f"{m['number']} - {m['title']}"
    link = f"{m['number']}-{m['slug']}"
    created, skipped = [], []

    for t in m["topics"]:
        path = os.path.join(ROOT, "topics", slugify(t["name"]) + ".md")
        if os.path.exists(path):
            skipped.append(os.path.basename(path))
            continue
        created.append(os.path.basename(path))
        if not dry:
            open(path, "w").write(topic_page(t["name"], t["description"], label, link))

    mod_path = os.path.join(ROOT, "modules", link + ".md")
    if not dry:
        open(mod_path, "w").write(module_page(m, m["topics"]))
        append_module_index(m, len(m["topics"]))
        append_topic_index(m, m["topics"])
        log_path = os.path.join(ROOT, "log.md")
        today = str(datetime.now(timezone.utc).date())
        existing = open(log_path).read() if os.path.exists(log_path) else ""
        header = "" if f"## {today}" in existing else f"\n## {today}\n"
        entry = (
            f"* **Extend**: added module {label} with {len(m['topics'])} "
            f"topic{'' if len(m['topics']) == 1 else 's'} "
            f"({len(created)} new, {len(skipped)} already present).\n"
        )
        with open(log_path, "a") as f:
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
