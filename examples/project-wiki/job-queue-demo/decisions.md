---
type: Project Doc
title: "Decisions - Job queue demo"
description: "Decision log: what was chosen, and why."
project: job-queue-demo
doc_kind: decisions
study_topics: [../../study-wiki/01-foundations/message-queues.md]
language: en
generated: { by: human:you, at: 2026-02-02T09:00:00Z }
---

# Decisions

## 2026-02-05 At-least-once delivery

Context: jobs can be retried safely if handlers are idempotent. Options: at-most-once (jobs may be lost), at-least-once, exactly-once (costly). Choice: at-least-once with idempotent handlers. Why: losing a job is worse than processing one twice here.

# Study references

- [Message Queues](../../study-wiki/01-foundations/message-queues.md) - the delivery guarantees compared in the decision above.
