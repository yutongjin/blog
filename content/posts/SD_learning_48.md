---
title: "10 tips for SD"
date: 2026-04-08
draft: false
tags: ["blog", "engineering", "sd"]
---
# 10 System Design Tips (Senior-Level)

April 8, 2026  
Yutong Jin

---

## 🧠 System Design Key Principles

### 1. Start with Functional Requirements

Clearly define what the system needs to do:
- Core APIs (read/write flows)
- User interactions
- Edge cases

💡 Tip:
Do NOT spend too long here — 2–3 minutes is enough in interviews.

---

### 2. Identify the Core Bottleneck Early

Before designing, ask:
- What is the expected QPS?
- Where will the system break first?

Common bottlenecks:
- Feed systems → fanout explosion
- Chat systems → message ordering
- Payment systems → consistency

💡 Senior mindset:
> Design starts from bottlenecks, not components.

---

### 3. Classify the System Type

Go beyond "read-heavy vs write-heavy":

| Type | Example | Key Requirement |
|------|--------|----------------|
| Latency-sensitive | Feed / Search | Low latency |
| Throughput-heavy | Logging / Metrics | High ingestion |
| Consistency-critical | Payment / Auction | Strong consistency |

💡 This classification drives all design decisions.

---

### 4. CAP Trade-offs = Product Decisions

CAP is not theory — it’s a user experience tradeoff.

- Availability-focused (AP):
  - Feed systems (TikTok, Instagram)
  - Metrics systems
  - Google Drive / Dropbox (eventual consistency)

- Consistency-focused (CP):
  - Payment systems
  - Auction systems

💡 Example:
> Slightly stale feed is acceptable → choose Availability  
> Double charge is unacceptable → choose Consistency

---

### 5. Design for Failure by Default

Assume every component can fail.

Key techniques:
- Retry + exponential backoff
- Idempotency (critical for payments)
- Dead letter queue (DLQ)
- Fallback strategies

💡 Principle:
> Design for partial failure, not full system failure.

---

### 6. Sync vs Async is a Core Decision

| Sync | Async |
|------|------|
| Low latency | High reliability |
| Strong consistency | Eventual consistency |
| User blocking | Decoupled |

Examples:
- Post creation → async fanout
- Payment → sync confirmation + async settlement

💡 Tradeoff:
Async improves scalability but adds complexity.

---

### 7. Fault Tolerance via Message Queues

Use systems like Kafka to:
- Buffer traffic spikes
- Enable retries
- Decouple services

Benefits:
- Prevent data loss
- Smooth traffic bursts
- Allow downstream recovery

💡 Important:
Kafka is not just a queue — it's a durability and replay system.

---

### 8. Read vs Write Optimization

#### Write-heavy systems:
- Must not lose data
- Use:
  - Kafka (durability)
  - Batch writes
  - Idempotent operations

#### Read-heavy systems:
- Optimize for latency
- Use:
  - Caching (Redis)
  - Read replicas
  - Precomputation

---

### 9. Cache Strategy (Performance vs Consistency)

Cache improves performance but introduces inconsistency.

Common patterns:
- Cache-aside (most common)
- Write-through
- Write-back

Key decisions:
- TTL vs explicit invalidation
- Handling stale data
- Cache fallback to DB

💡 Principle:
> Cache is not just optimization — it is a consistency tradeoff.

---

### 10. Read/Write Separation

Separate services:
- Write service → handles mutations
- Read service → optimized for queries

Techniques:
- Read replicas
- CQRS (Command Query Responsibility Segregation)

Benefits:
- Better scalability
- Independent optimization

---

## 🔥 Advanced Principles (Senior-Level Thinking)

### 11. Data Model Drives the System

Schema design determines scalability.

Examples:
- Feed: (user_id, timestamp)
- Chat: (chat_id, message_id)
- DynamoDB: PK + SK + GSI

💡 Principle:
> Bad schema cannot be fixed by scaling.

---

### 12. Avoid Hotspots

Common issues:
- Hot keys (celebrity users)
- Hot partitions (Kafka)

Solutions:
- Sharding
- Consistent hashing
- Randomization

---

### 13. Always Design Fallback Paths

Never rely on a single component.

Examples:
- Cache miss → DB fallback
- ML ranking timeout → heuristic ranking
- Service failure → degraded experience

💡 Principle:
> A degraded system is better than a broken system.

---

### 14. Measure and Iterate

Add observability:
- Metrics (QPS, latency)
- Logging
- Alerting

Use:
- Rollout (A/B testing)
- Dark traffic

💡 Real-world:
Production systems evolve, not designed once.

---

## 🧩 Summary

System design is not about drawing boxes — it is about making tradeoffs:

- Latency vs Consistency
- Throughput vs Cost
- Simplicity vs Scalability

💡 Final takeaway:
> Good engineers design systems that work.  
> Great engineers design systems that still work when things fail.

---

© 2026 Yutong Jin