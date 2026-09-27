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

`example-curriculum.json` is a placeholder with three empty topics. Delete
it once you have your own.
