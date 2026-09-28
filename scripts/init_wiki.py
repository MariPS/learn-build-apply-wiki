#!/usr/bin/env python3
"""Create the two empty OKF bundles this skill maintains.

Usage:
    python3 scripts/init_wiki.py              # create in the current directory
    python3 scripts/init_wiki.py --lang it    # set the wiki language (default: en)
    python3 scripts/init_wiki.py --force      # overwrite existing index/log files

Creates:

    job-wiki/      applications/  concepts/  references/postings/  index.md  log.md
    study-wiki/    modules/       topics/    references/sources/    index.md  log.md

    career-wiki.json   { "language": "<tag>" } - the language compiled pages
                       are written in; postings and sources keep their own

It never touches content pages, only the scaffolding. Safe to rerun.
Populate the study wiki afterwards with:

    python3 scripts/add_module.py scripts/curricula/<your-curriculum>.json
"""

import json
import os
import sys
from datetime import date

ROOT = os.getcwd()
FORCE = "--force" in sys.argv
CONFIG = "career-wiki.json"


def lang_arg():
    if "--lang" in sys.argv:
        i = sys.argv.index("--lang")
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        sys.exit("--lang needs a language tag, e.g. --lang it")
    return None


def write_config(path, config):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(config, indent=2) + "\n")

DIRS = [
    "job-wiki/applications",
    "job-wiki/concepts",
    "job-wiki/references/postings",
    "study-wiki/modules",
    "study-wiki/topics",
    "study-wiki/references/sources",
]

FILES = {
    "job-wiki/index.md": """---
okf_version: "0.2"
---

# Job Wiki

* [Applications](applications/) - one page per job application
* [Concepts](concepts/) - tools and theory the postings ask for
* [Postings](references/postings/) - the original text of each posting

Each page in `concepts/` links, where one already covers it, to the
matching topic in the [study wiki](../study-wiki/index.md).
""",
    "job-wiki/log.md": "# Change log\n",
    "job-wiki/applications/index.md": "# Applications\n\n<!-- One row per application. Kept in sync by the Lint operation. -->\n",
    "job-wiki/concepts/index.md": "# Concepts\n\n<!-- One row per concept. Kept in sync by the Lint operation. -->\n",
    "study-wiki/index.md": """---
okf_version: "0.2"
---

# Study Wiki

* [Modules](modules/) - the curriculum skeleton
* [Topics](topics/) - one page per concept
* [Sources](references/sources/) - raw external material

Written only from the sources and instructions you provide. The
[job wiki](../job-wiki/index.md) links here where a topic already covers
a concept a posting requires; nothing flows the other way.
""",
    "study-wiki/log.md": "# Change log\n",
    "study-wiki/modules/index.md": "# Modules\n",
    "study-wiki/topics/index.md": """# Topics

Coverage: `empty` (no sources) - `stub` (some material) - `drafted`
(theory written) - `solid` (interview-ready).
""",
    "study-wiki/references/sources/index.md": """# Sources

Raw, immutable material. One file per source, whatever its original format
(book, paper, web page, video transcript, course notes).
""",
}


def main():
    created, skipped = [], []
    for d in DIRS:
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)

    for path, content in FILES.items():
        full = os.path.join(ROOT, path)
        if os.path.exists(full) and not FORCE:
            skipped.append(path)
            continue
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        created.append(path)

    config_path = os.path.join(ROOT, CONFIG)
    lang = lang_arg()
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
        if lang and config.get("language") != lang:
            print(f"Wiki language: {config.get('language')} -> {lang}. "
                  "Existing pages are not translated; Lint will report them.")
            config["language"] = lang
            write_config(config_path, config)
    else:
        config = {"language": lang or "en"}
        write_config(config_path, config)
        created.append(CONFIG)

    for log in ("job-wiki/log.md", "study-wiki/log.md"):
        if log in created:
            with open(os.path.join(ROOT, log), "a", encoding="utf-8") as f:
                f.write(f"\n## {date.today()}\n* **Init**: bundle created.\n")

    print(f"Created {len(created)} files across 2 OKF bundles.")
    print(f"Wiki language: {config['language']}")
    if skipped:
        print(f"Skipped {len(skipped)} already present (use --force to overwrite):")
        for p in skipped:
            print(f"  {p}")
    print("\nNext: python3 scripts/add_module.py scripts/curricula/example-curriculum.json")


if __name__ == "__main__":
    main()
