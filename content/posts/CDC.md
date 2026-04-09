---
title: " Change Data Capture (CDC) Summary"
date: 2026-04-09
draft: false
tags: ["blog", "engineering", "CDC"]
---

### Change Data Capture (CDC) Summary

- **Purpose**: Track and propagate data changes (insert, update, delete) from a source to downstream systems.

- **Write-Ahead Log (WAL)**: In relational databases (e.g., PostgreSQL), all changes are logged before being applied. CDC reads from the WAL to capture changes.

- **NoSQL**: In systems like DynamoDB, item-level streams capture changes in a similar fashion.

- **Pipeline Actions**:
  - Detect changes.
  - Send to downstream systems.
  - Examples: replicate to read replicas, sync to a search index (Elasticsearch), or forward to Kafka.

- **Key Considerations**:
  - **Ordering**: Ensure changes are applied in order or handle out-of-order events.
  - **Consistency**: Choose between eventual or strong consistency.
  - **Schema Evolution**: Manage schema changes over time.
  - **Performance**: Balance latency vs. throughput and handle backpressure.

- **Resilience**: Ensure fault tolerance—prepare for target system delays or failures.