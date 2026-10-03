# Worked example

A tiny, fully fictional pair of bundles showing what the wikis look like
once they have content in them. Everything here is invented: "Example
Corp" is not a company, and the sources are placeholders.

Read it in this order to see the cross-link at work:

1. `job-wiki/references/postings/example-corp-backend-engineer-2026-01-15.md`
   — the raw posting, exactly as pasted.
2. `job-wiki/applications/example-corp-backend-engineer.md` — what the
   agent extracted from it.
3. `job-wiki/concepts/message-queues.md` — a concept the posting requires,
   shared across applications, pointing at the study wiki.
4. `study-wiki/01-foundations/message-queues.md` — the study page, showing a
   filled-in `# 3. Theory in depth` with per-claim footnotes.
5. `study-wiki/references/sources/example-talk-queue-semantics.md` — the
   source the theory was compiled from.
6. `job-wiki/references/submissions/example-corp-backend-engineer/` — the
   CV (PDF) and cover letter (pasted as text) sent with the application,
   listed under `documents_sent` in the application page.
7. `project-wiki/job-queue-demo/` — a personal project whose architecture
   and decision pages reference the same study topic. The link runs from
   the project to the study page, never back.

Note what the theory page does *not* contain: any mention of Example Corp,
salary, seniority, or even a link back to the job wiki. The link runs one
way, from the concept to the topic — and the logs show it was only set on
2026-01-20, once the talk had been ingested and the topic actually covered
the subject. On 2026-01-15, when the posting arrived, the concept stayed at
`study_topic: null` and the study wiki was left alone.

`wiki-config.json` sets the wiki language (`en` here). Postings and
sources carry their own `language`, and may differ from it.
