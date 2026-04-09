---
title: "10 tips for SD"
date: 2026-04-08
draft: false
tags: ["blog", "engineering", "sd"]
---
# System Design Key Principles

## 1. Start with Functional Requirements
- Clearly define what the system needs to do.

## 2. Understand System Characteristics
- Is it **read-heavy** or **write-heavy**?
- Is it **user-centric** or **system-centric**?

## 3. CAP Trade-offs
- **Read-heavy systems** → prioritize **Availability > Consistency**
- **Financial / transactional systems** → prioritize **Consistency**

## 4. Examples
- Availability-focused:
  - TikTok store
  - DoorDash reviews
  - Library systems
  - Metrics systems
  - Google Drive / Dropbox
- Consistency-focused:
  - Payment systems
  - Online auction systems

## 5. Fault Tolerance
- Assume services can fail
- Use **Kafka / message queues** to buffer requests
- Enables recovery and continuation of processing

## 6. Read vs Write Handling
- **Write-heavy systems**
  - Must not lose data
  - Use Kafka for durability and async processing
- **Read-heavy systems**
  - Focus on low latency
  - Use caching (e.g., Redis)

## 7. Cache Strategy
- Redis improves read performance
- Not fully reliable → always have **DB fallback**

## 8. Read/Write Separation
- Separate **read and write services**
- Use **read replicas** for scaling reads