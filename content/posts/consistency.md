---
title: "Consistency"
date: 2026-05-05
draft: false
tags: []
---

Consistency in distributed systems refers to whether different parts of the system observe the same data at the same time.

In strong consistency, every read returns the most recent write, so the system behaves like a single source of truth.

In eventual consistency, temporary inconsistencies are allowed, but the system guarantees that all replicas will converge to the same value over time.

In practice, we don’t apply strong consistency everywhere because it hurts latency and availability. Instead, we apply strong consistency only to critical data that affects correctness, such as ride-driver assignment in Uber, and use eventual consistency for high-throughput or latency-sensitive data like driver location updates.
