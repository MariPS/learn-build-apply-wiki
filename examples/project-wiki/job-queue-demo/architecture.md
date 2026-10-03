---
type: Project Doc
title: "Architecture - Job queue demo"
description: "Components, data flow and technology choices."
project: job-queue-demo
doc_kind: architecture
study_topics: [../../study-wiki/01-foundations/message-queues.md]
language: en
generated: { by: human:you, at: 2026-02-02T09:00:00Z }
---

# Overview

The producer publishes a job message; a worker pool consumes, processes and acknowledges it.

# Components

- Producer: a small script that enqueues jobs.
- Queue: a managed broker.
- Workers: stateless processes, scaled by queue depth.

# Data flow

producer → queue → worker → (acknowledge). A job not acknowledged in time is redelivered, so handlers must be idempotent.

# Stack

Python workers, managed queue service.

# Trade-offs

At-least-once delivery is simpler than exactly-once, at the cost of idempotent handlers (see [decisions](decisions.md)).

# Study references

- [Message Queues](../../study-wiki/01-foundations/message-queues.md) - delivery guarantees explain why workers must be idempotent here.
