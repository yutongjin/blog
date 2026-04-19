---
title: "Relational DB vs NoSQL"
date: 2026-04-19
draft: false
tags: ["blog", "engineering", "database", "nosql", "sql"]
---
## Relational DB vs NoSQL 

### 1. Throughput & Scalability

A relational database like MySQL can handle moderate QPS well, and we can scale it further with read replicas or sharding.

However, sharding introduces additional complexity:
- Choosing a good shard key
- Avoiding hotspot partitions
- Handling cross-shard queries
- Rebalancing data

#### Example Tradeoffs:
- **Shard by userId**
  - ✅ Good for user-centric queries
  - ⚠️ May cause hotspots if traffic is skewed toward a few users

- **Shard by itemId**
  - ✅ Better write distribution
  - ⚠️ Harder to query all items for one user (cross-shard reads)

---

### 2. Consistency & Query Flexibility

Relational databases are typically preferred when:
- Strong consistency is required
- Transactions are important
- Queries are complex (JOINs, filtering, ad hoc queries)
- Schema is well-defined

---

### 3. NoSQL Characteristics

NoSQL databases are generally better when:
- Very high read/write throughput is required
- Horizontal scalability is needed
- Access patterns are simple and predictable
- Schema flexibility is desired

⚠️ Tradeoffs:
- May provide weaker consistency guarantees (depending on system)
- Limited transaction support
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

- Choose **NoSQL** when:
  - Massive scale and high throughput are required
  - Access patterns are simple
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