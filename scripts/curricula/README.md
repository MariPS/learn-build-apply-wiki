# Curricula

One JSON file per module. Each defines a module and the topics inside it,
and is turned into wiki pages by `scripts/add_module.py`.

The skeleton is **yours to choose**. Reasonable sources for an index:

- the table of contents of a textbook you're working through
- a course or bootcamp syllabus
- an interview-prep checklist for the roles you're targeting
- the documentation outline of a framework you need to learn
- your own notes on what keeps coming up in postings

Fill in the `curriculum` field with where the index came from, so later you
know how much to trust its completeness. Number modules in the order you
want them listed; add `"origin": "extension"` to modules you add after the
first import, so what you imported stays distinguishable from what you
grew yourself.

Write topic names and descriptions in your wiki language (set in
`career-wiki.json`; override per module with `"language"`). Filenames are
always ASCII: accents are stripped, and you can pin a language-neutral
filename with `"slug"` — e.g. `{"name": "Code di messaggi", "slug":
"message-queues", ...}` — so postings in any language link to it.

Postings never add topics here: the study wiki grows only from the
curricula you import and the sources you ingest.

`example-curriculum.json` is a placeholder with three empty topics. Delete
it once you have your own.
