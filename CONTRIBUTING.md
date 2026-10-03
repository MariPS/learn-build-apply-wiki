# Contributing

Issues and pull requests welcome. A few things worth knowing before you
open one.

**This repo ships no curriculum.** Topic lists tied to a particular
course, vendor or book belong in your own fork, not here — the skeleton is
meant to be chosen by whoever installs the skill. Improvements to the
*mechanism* for importing a curriculum are very welcome.

**Changes to `SKILL.md` are the main surface area.** It's the file the
agent actually reads, so a change there changes behaviour. When proposing
one, say which operation it affects and what went wrong without it. Vague
additions make the skill longer without making it better, and a long skill
gets followed less faithfully.

**Keep it dependency-free.** Plain markdown, YAML front matter, and the
Python standard library. No database, no build step, no package manager.

**Your projects stay yours.** `project-wiki/` holds personal work and is
listed in `.gitignore`; only the mechanism (`add_project.py`, the schemas)
lives here.

**Examples stay fictional.** `examples/` uses invented companies and
placeholder sources on purpose. Don't add real postings or copyrighted
material.
