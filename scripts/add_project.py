#!/usr/bin/env python3
"""Add a project folder, with starter documentation pages, to the project wiki.

Usage:
    python3 scripts/add_project.py "Air quality forecasting"
    python3 scripts/add_project.py "Air quality forecasting" --slug air-quality \\
        --description "Hourly PM10 forecasts from public data" --lang it
    python3 scripts/add_project.py "Air quality forecasting" --dry-run

Creates, under project-wiki/:

    <slug>/
        overview.md        type: Project      goal, scope, status, outcome
        requirements.md    type: Project Doc  problem framing, success criteria
        architecture.md    type: Project Doc  components, data flow, stack
        data.md            type: Project Doc  sources, schema, quality, splits
        experiments.md     type: Project Doc  what was tried, results
        decisions.md       type: Project Doc  decision log, with the why
        deployment.md      type: Project Doc  serving, monitoring, operations
        index.md           reserved index listing the pages above
        references/        raw, immutable material for this project (specs,
                           briefs, datasets descriptions); index.md inside

and one line for the project in project-wiki/index.md and project-wiki/log.md.
Existing pages and the project index are never overwritten, so it is safe
to rerun. Delete the
starter pages a project doesn't need; add others (type: Project Doc,
doc_kind: notes) freely.

The wiki language comes from wiki-config.json (next to project-wiki/), or
"en"; --lang overrides it.
"""

import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ROOT = os.path.join(BASE, "project-wiki")
CONFIG = os.path.join(BASE, "wiki-config.json")
ACTOR = os.environ.get("WIKI_ACTOR", "human:you")
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# doc_kind -> (file, page title, description, sections)
DOCS = [
    ("requirements", "Requirements", "Problem framing and success criteria.",
     ["Problem", "Users and consumers", "Success criteria", "Constraints", "Out of scope"]),
    ("architecture", "Architecture", "Components, data flow and technology choices.",
     ["Overview", "Components", "Data flow", "Stack", "Trade-offs"]),
    ("data", "Data", "Sources, schema, quality checks and splits.",
     ["Sources", "Schema", "Quality and cleaning", "Splits and leakage"]),
    ("experiments", "Experiments", "What was tried and what came out of it.",
     ["Baseline", "Experiments", "Results", "What to try next"]),
    ("decisions", "Decisions", "Decision log: what was chosen, and why.",
     ["Decisions"]),
    ("deployment", "Deployment", "Serving, monitoring and operations.",
     ["Serving", "Monitoring", "Retraining and maintenance", "Known risks"]),
]


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


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


def arg(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        sys.exit(f"{name} needs a value")
    return None


def overview(name, slug, desc, lang):
    return f"""---
type: Project
title: "{name}"
description: {json.dumps(desc, ensure_ascii=False)}
project_status: idea        # idea | active | paused | done | archived
started_at: {NOW[:10]}
repo: null                  # URL of the code repository, if any
study_modules: []           # study-wiki modules this project exercises
language: {lang}
generated: {{ by: {ACTOR}, at: {NOW} }}
---

# Goal

{desc}

# Scope

<!-- What the project includes, and what it deliberately leaves out. -->

# Status

<!-- Where things stand now, in a few lines. Keep it current. -->

# Outcome

<!-- Filled in when the project is done: what was delivered, what was
     learned, what you would do differently. -->

# Documentation

See [index](index.md).
"""


def doc_page(kind, title, desc, sections, name, slug, lang):
    body = "\n\n".join(f"# {s}\n\n<!-- -->" for s in sections)
    if kind == "decisions":
        body = ("# Decisions\n\n<!-- One entry per decision, newest first:\n"
                "     ## <YYYY-MM-DD> <decision>\n"
                "     Context, options considered, choice, why. -->")
    return f"""---
type: Project Doc
title: "{title} - {name}"
description: {json.dumps(desc, ensure_ascii=False)}
project: {slug}
doc_kind: {kind}
study_topics: []            # relative links to the study topics this page relies on
language: {lang}
generated: {{ by: {ACTOR}, at: {NOW} }}
---

{body}

# Study references

<!-- Link a study topic only where this page leans on it, with one line on
     why it matters here. Only topics that already exist, at coverage `stub`
     or above. Study pages never link back. Example:
     - [Model monitoring](../../study-wiki/03-ml-system-design/model-monitoring.md)
       - why drift matters for this project. -->
"""


def project_index(name, files):
    rows = "\n".join(f"* [{t}]({f}) - {d}" for f, t, d in files)
    return f"# {name}\n\n{rows}\n"


def update_root_index(name, slug, desc):
    path = os.path.join(ROOT, "index.md")
    line = f"* [{name}]({slug}/index.md) - {desc}"
    content = read(path).rstrip("\n")
    lines = content.split("\n")
    for i, existing in enumerate(lines):
        if f"({slug}/index.md)" in existing:
            lines[i] = line
            write(path, "\n".join(lines) + "\n")
            return
    write(path, content + "\n" + line + "\n")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flag_values = {arg(f) for f in ("--slug", "--description", "--lang") if f in sys.argv}
    args = [a for a in args if a not in flag_values]
    if not args:
        print(__doc__)
        sys.exit(1)
    name = args[0]
    slug = arg("--slug") or slugify(name)
    desc = arg("--description") or f"Documentation of the {name} project."
    lang = arg("--lang") or wiki_language()
    dry = "--dry-run" in sys.argv
    if not os.path.isdir(ROOT):
        sys.exit("project-wiki/ not found: run scripts/init_wiki.py first")

    pdir = os.path.join(ROOT, slug)
    pages = [("overview.md", overview(name, slug, desc, lang))]
    listing = [("overview.md", "Overview", "Goal, scope, status and outcome.")]
    for kind, title, d, sections in DOCS:
        pages.append((f"{kind}.md", doc_page(kind, title, d, sections, name, slug, lang)))
        listing.append((f"{kind}.md", title, d))

    created, skipped = [], []
    if not dry:
        os.makedirs(os.path.join(pdir, "references"), exist_ok=True)
        ref_index = os.path.join(pdir, "references", "index.md")
        if not os.path.exists(ref_index):
            write(ref_index, "# References\n\nRaw, immutable material for this project, kept as received.\n")
    for fname, text in pages:
        path = os.path.join(pdir, fname)
        if os.path.exists(path):
            skipped.append(fname)
            continue
        created.append(fname)
        if not dry:
            write(path, text)

    if not dry:
        index_path = os.path.join(pdir, "index.md")
        if not os.path.exists(index_path):  # never clobber a hand-maintained index
            existing = [f for f in sorted(os.listdir(pdir)) if f.endswith(".md") and f != "index.md"]
            files = [(f, t, d) for f, t, d in listing if f in existing]
            write(index_path, project_index(name, files))
        update_root_index(name, slug, desc)
        if not created:
            print(f"Project {name}: nothing new to create.")
            return
        log_path = os.path.join(ROOT, "log.md")
        today = str(datetime.now(timezone.utc).date())
        old = read(log_path) if os.path.exists(log_path) else ""
        header = "" if f"## {today}" in old else f"\n## {today}\n"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{header}* **Add project**: `{slug}` ({len(created)} pages created).\n")

    print(f"{'[dry-run] ' if dry else ''}Project {name} -> project-wiki/{slug}/")
    print(f"  created: {', '.join(created) or 'none'}")
    if skipped:
        print(f"  skipped: {', '.join(skipped)} (already present)")


if __name__ == "__main__":
    main()
