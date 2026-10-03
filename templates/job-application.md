---
type: Job Application
title: "<Role> @ <Company>"
description: <one line>
resource: <posting URL, if any>
tags: []
company: <Company>
role: <Role>
posted_at: <YYYY-MM-DD>
cv_sent_at: <YYYY-MM-DD>
application_status: candidate   # candidate | applied | interview | rejected | offer | withdrawn
status: draft                   # draft | stable | deprecated (document lifecycle, not the application's)
language: <wiki language>       # from wiki-config.json
generated: { by: human:you, at: <timestamp> }
sources:
  - id: posting
    resource: /references/postings/<file>.md
    title: <original posting title>
documents_sent: []              # filled by Track; one entry per CV / cover letter sent:
#  - kind: cv                    # cv | cover-letter
#    sent_at: <YYYY-MM-DD>
#    file: /references/submissions/<application-slug>/cv-<YYYY-MM-DD>.pdf   # or null
#    original_name: <filename as you had it>
#    language: <language of the document>
#    note: <optional: channel, recipient, what was tailored>
---

# Job description

<Summary of the posting.>[^posting]

# Responsibilities

-

# Required tools

-

# Theory to review

<Links to concepts/, which in turn link to study topics.>

# Personal notes

-

[^posting]: <original posting title>
