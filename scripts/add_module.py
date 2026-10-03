#!/usr/bin/env python3
"""Add a module (and its topics) to the study wiki.

A module is a folder, `study-wiki/<number>-<slug>/`, holding its own
`index.md` (the module page) and one page per topic. Organise modules by
whatever axis helps you study: for an ML/AI wiki, the stages of the
pipeline (data, modeling, deployment, operations, ...).

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

`number` orders modules and prefixes their folder names. `curriculum` and
`resource` are optional but recommended: they record where an index came
from. Set "origin": "extension" for modules added after the first import.

`language` is the language names and descriptions are written in; it
defaults to the wiki language in wiki-config.json (next to study-wiki/),
or "en". Slugs are always ASCII: accents are stripped, and a topic may set
its own "slug" to stay language-neutral (e.g. "message-queues" for a topic
named "Code di messaggi").

The script is idempotent: a topic page that already exists anywhere in the
study wiki is never overwritten or duplicated (so you can move a topic
between modules by hand), and you can add entries to the JSON and rerun it
safely. Topic slugs are unique across the whole study wiki.
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
CONFIG = os.path.normpath(os.path.join(ROOT, "..", "wiki-config.json"))


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


def topic_page(name, desc, module_label, lang):
    return f"""---
type: Study Topic
title: "{name}"
description: {json.dumps(desc, ensure_ascii=False)}
tags: [{slugify(module_label.split(' - ', 1)[-1])}]
module: "{module_label}"
coverage: empty        # empty | stub | drafted | solid
language: {lang}
generated: {{ by: {ACTOR}, at: {NOW} }}
---

# 1. In one sentence

<!-- The 30-second interview answer. Write this last, once the theory
     below is solid enough. -->

# 2. Summary

{desc}

<!-- 5-10 lines: what it is, what it's for, where it sits. -->

# 3. Theory in depth

<!-- The real body of the page, compiled from the sources listed in
     `sources`. Organise by theme, never by source: if three sources
     describe the same mechanism, that stays one subsection carrying
     three footnotes. Number each subsection 3.1, 3.2, ... Every claim taken from a source gets that source's
     footnote id. Formal definitions, step-by-step mechanisms, formulas,
     pseudocode, trade-offs, failure modes and comparisons between
     alternatives all belong here. -->

## 3.1 <First subtheme>

# 4. Key points

-

# 5. Interview questions

-

# 6. Sources read

-

# 7. Links

- Module: [{module_label}](index.md)
"""


def find_topic(slug):
    """Path of an existing topic page, in any module folder, or None."""
    for entry in sorted(os.listdir(ROOT)):
        path = os.path.join(ROOT, entry, slug + ".md")
        if os.path.isdir(os.path.join(ROOT, entry)) and os.path.exists(path):
            return path
    return None


def coverage_of(path):
    if path and os.path.exists(path):
        m = re.search(r"^coverage:\s*(\w+)", read(path), re.M)
        if m:
            return m.group(1)
    return "empty"


def module_page(m, topics, lang, mod_dir):
    label = f"{m['number']} - {m['title']}"
    rows = []
    for n, t in enumerate(topics, 1):
        path = find_topic(topic_slug(t))
        if path and os.path.dirname(path) != mod_dir:
            link = f"../{os.path.basename(os.path.dirname(path))}/{topic_slug(t)}.md"
        else:
            link = f"{topic_slug(t)}.md"
        rows.append(f"{n}. [{t['name']}]({link}) - `{coverage_of(path)}` · {t['description']}")
    rows = "\n".join(rows)
    origin = m.get("origin", "curriculum")
    source = m.get("curriculum", m["title"])
    note = f"Origin: `{origin}` · Index derived from: {source}."
    if m.get("resource"):
        note = f"Origin: `{origin}` · Index derived from: [{source}]({m['resource']})."
    # index.md is an OKF reserved file: no front matter
    return f"""# {label}

{m.get('description', '')}

{note}

Coverage: `empty` (no sources) - `stub` (some material) - `drafted`
(theory written) - `solid` (interview-ready).

# Topics in this module

{rows}
"""


def update_study_index(m, n_topics):
    """One line per module in study-wiki/index.md, refreshed on rerun."""
    path = os.path.join(ROOT, "index.md")
    plural = "topic" if n_topics == 1 else "topics"
    link = f"{m['number']}-{m['slug']}/index.md"
    line = f"* [{m['number']} - {m['title']}]({link}) - {n_topics} {plural}"
    content = read(path).rstrip("\n")
    lines = content.split("\n")
    for i, existing in enumerate(lines):
        if f"({link})" in existing:
            lines[i] = line
            write(path, "\n".join(lines) + "\n")
            return
    if "## Modules" not in content:
        content += "\n\n## Modules\n"
    # keep module lines together and ordered by number
    lines = content.split("\n")
    start = lines.index("## Modules") + 1
    end = start
    while end < len(lines) and (lines[end].startswith("* [") or not lines[end].strip()):
        end += 1
    block = [l for l in lines[start:end] if l.strip()] + [line]
    block.sort(key=lambda l: re.search(r"\[(\d+)", l).group(1) if re.search(r"\[(\d+)", l) else "")
    lines[start:end] = [""] + block + [""]
    write(path, "\n".join(lines).rstrip("\n") + "\n")


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
    mod_dir = os.path.join(ROOT, link)
    created, skipped = [], []

    if not dry:
        os.makedirs(mod_dir, exist_ok=True)
    for t in m["topics"]:
        if find_topic(topic_slug(t)):
            skipped.append(topic_slug(t) + ".md")
            continue
        created.append(topic_slug(t) + ".md")
        if not dry:
            write(
                os.path.join(mod_dir, topic_slug(t) + ".md"),
                topic_page(t["name"], t["description"], label, lang),
            )

    if not dry:
        write(os.path.join(mod_dir, "index.md"), module_page(m, m["topics"], lang, mod_dir))
        update_study_index(m, len(m["topics"]))
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
        print(f"  files:   {link}/index.md, study-wiki/index.md refreshed, log.md appended")


NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

if __name__ == "__main__":
    main()
