---
type: Reference
title: "Talk: delivery semantics in practice (transcript)"
description: "Placeholder transcript of a fictional conference talk, used to show the source format."
resource: https://example.com/talks/delivery-semantics
source_kind: video
author: Example Speaker
published_at: 2025-09-12
captured_at: 2026-01-20
locator: "00:00-42:10"
covers_topics: [message-queues]
language: en
generated: { by: human:you, at: 2026-01-20T20:00:00Z }
---

# Transcript

<!-- A real entry holds the full transcript with timestamps. This is a
     placeholder showing the shape. -->

[04:12] ... the three delivery guarantees are at-most-once, at-least-once
and exactly-once, and only the middle one is cheap ...

[11:40] ... consumers that can be replayed need idempotent handlers, which
in practice means a deduplication key carried on the message ...

[27:05] ... a queue with an unbounded retention window is a log, and the
operational trade-offs are different ...
