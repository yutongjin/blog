---
title: "Relational DB vs NoSQL"
date: 2026-04-19
draft: false
tags: ["blog", "engineering", "database", "nosql", "sql"]
---
## Relational DB vs NoSQL — Interview Answer Template (with QPS Details)

### 1. Throughput & Scalability

A relational database like MySQL can handle moderate QPS well.

#### Rough Numbers (rule of thumb, varies by setup):
- **Single MySQL instance**
  - ~1K – 5K QPS (typical production range)
- **With read replicas**
  - Reads can scale to **10K+ QPS**
- **With sharding**
  - Can scale to **100K+ QPS**, depending on number of shards

However, sharding introduces additional complexity:
- Choosing a good shard key
- Avoiding hotspot partitions
- Handling cross-shard queries
- Rebalancing data

#### Example Tradeoffs:
- **Shard by userId**
  - ✅ Good for user-centric queries
  - ⚠️ May cause hotspots if traffic is skewed (e.g., celebrity users)

- **Shard by itemId**
  - ✅ Better write distribution
  - ⚠️ Harder to query all items for one user (cross-shard reads)

---

### 2. Consistency & Query Flexibility

Relational databases are typically preferred when:
- Strong consistency is required (ACID transactions)
- Multi-row / multi-table transactions are needed
- Queries are complex (JOINs, filtering, aggregations)
- Schema is well-defined

---

### 3. NoSQL Characteristics

NoSQL databases are generally designed for higher scalability.

#### Rough Numbers:
- **Single node (e.g., DynamoDB / Cassandra node)**
  - Can handle **10K+ QPS**
- **Distributed cluster**
  - Can scale to **100K – millions of QPS**

They are better when:
- Very high read/write throughput is required
- Horizontal scaling is needed
- Access patterns are simple and predictable
- Schema flexibility is desired

⚠️ Tradeoffs:
- May provide weaker or tunable consistency (eventual consistency by default in many systems)
- Limited or more complex transaction support
- Less flexible querying compared to relational DBs

> Important:  
> It is not that NoSQL cannot support strong consistency,  
> but many NoSQL systems trade off some consistency or relational features  
> in exchange for better scalability.

---

### 4. Summary

- Choose **Relational DB** when:
  - Strong consistency and transactions are critical
  - Complex queries are needed
  - Scale is moderate (or manageable with sharding)

- Choose **NoSQL** when:
  - Massive scale (100K+ QPS) is required
  - Access patterns are simple
  - Horizontal scaling is a priority
  - Some tradeoffs in consistency or querying are acceptable

## Why NoSQL Is Better at Sharding

### 1. Built-in Horizontal Partitioning

NoSQL databases are designed to scale horizontally by default.

- Data is automatically partitioned across nodes
- The system handles:
  - routing (which node to read/write)
  - rebalancing
  - replication

Example:
- Cassandra → consistent hashing
- DynamoDB → partition key–based routing

👉 In contrast, MySQL/Postgres:
- Sharding is **application-level**
- You must manually:
  - choose shard key
  - route queries
  - manage rebalancing

---

### 2. Simple Access Patterns (Key-Based)

NoSQL systems usually enforce:
- Primary key or partition key access

Example:
```text
GET /user/{userId}