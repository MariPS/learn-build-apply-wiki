---
type: Study Topic
title: "Message Queues"
description: Asynchronous message transport, delivery guarantees, and consumer design.
tags: [foundations]
module: "01 - Foundations"
coverage: drafted
language: en
generated: { by: human:you, at: 2026-01-20T20:15:00Z }
sources:
  - id: talk-semantics
    resource: /references/sources/example-talk-queue-semantics.md
    title: "Talk: delivery semantics in practice"
    author: Example Speaker
    last_modified: 2025-09-12
---

# 1. In one sentence

A broker between producers and consumers that trades synchronous coupling
for asynchronous delivery, at the cost of having to reason explicitly
about ordering, duplication and failure.

# 2. Summary

A message queue decouples a producer from a consumer: instead of calling a
service and waiting, the producer hands a message to a broker, and one or
more consumers pick it up on their own schedule. This buys independent
scaling, load smoothing and tolerance of consumer downtime. What it costs
is that guarantees which came for free in a synchronous call — ordering,
exactly-once execution, immediate error feedback — now have to be designed
for.

# 3. Theory in depth

## 3.1 Delivery guarantees

Three semantics are usually distinguished: at-most-once, at-least-once,
and exactly-once. Only at-least-once is cheap to implement in practice;
exactly-once generally means at-least-once delivery combined with
idempotent consumers rather than a genuinely single delivery.[^talk-semantics]

- **At-most-once** — the broker forgets a message after dispatch. Loss is
  possible, duplication is not. Acceptable for telemetry, not for orders.
- **At-least-once** — the broker retains the message until acknowledged.
  Duplication is possible whenever an acknowledgement is lost after the
  consumer has done its work.
- **Exactly-once** — achieved at the application level, not the transport
  level, by making handlers idempotent.

## 3.2 Idempotent consumers

A consumer that may see the same message twice must produce the same end
state either way. In practice this means carrying a deduplication key on
the message and recording processed keys, so a repeat is recognised and
dropped.[^talk-semantics]

The failure mode to watch for: a handler that is idempotent in its own
database but not in its side effects. Writing a row twice is caught by a
unique constraint; sending an email twice is not.

## 3.3 Queues versus logs

A queue whose retention window is unbounded is effectively a log, and the
operational trade-offs change: consumers hold their own offset and can
replay history, but storage grows with throughput rather than with
backlog.[^talk-semantics] Replay requirements are therefore an argument
for a log-shaped broker, not a queue-shaped one.

# 4. Key points

- Exactly-once is a property of the consumer, not the transport.
- Deduplication keys are the standard mechanism for idempotency.
- Idempotency in the database does not imply idempotency in side effects.
- A replay requirement points at a log rather than a queue.

# 5. Interview questions

- **How would you handle a consumer that needs to replay three days of
  events?** Retention window long enough to cover the replay, consumer-held
  offsets, and idempotent handlers so the replay is safe.
- **Why is exactly-once delivery usually a misnomer?** Because the
  guarantee is implemented as at-least-once delivery plus deduplication.

# 6. Sources read

- *Talk: delivery semantics in practice* — the three guarantees, the
  deduplication-key pattern, and the queue-versus-log distinction.

# 7. Links

- Module: [01 - Foundations](index.md)

[^talk-semantics]: Talk: delivery semantics in practice
