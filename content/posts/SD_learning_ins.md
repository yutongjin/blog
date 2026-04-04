+++
date = '2026-01-27T19:44:50-08:00'
draft = false
title = 'Designing Instagram: Media Upload & Feed System'
+++

## Overview

When designing an Instagram-like system, two of the most critical components are:

- Media uploading pipeline
- Feed generation strategy

This post summarizes key design decisions and tradeoffs.

---

## 1. Media Uploading Pipeline

### High-level flow

1. Client requests a **pre-signed URL** from backend
2. Backend returns S3 pre-signed URL
3. Client uploads media **directly to S3 (chunked upload)**
4. S3 triggers an event (e.g., via notification / event bridge)
5. Backend processes the upload asynchronously

---

### Key design decisions

#### 1. Create post record early

Before upload starts:

- Create a post record in DB
- Mark status as `PENDING`

**Why?**

- Enables tracking upload progress
- Supports retries / failure handling
- Avoids dangling uploads

---

#### 2. Asynchronous post-processing

After upload completes:

- Update post status → `READY`
- Trigger background jobs:
  - Metadata extraction
  - Thumbnail generation

---

#### 3. Transcoding for multi-device support

Media is converted into multiple formats:

- Different resolutions (e.g., 480p / 720p / 1080p)
- Different bitrates

**Why?**

- Optimize for different network conditions
- Reduce latency on low bandwidth devices

---

#### 4. CDN for fast delivery

- Media is served via CDN
- Requests are routed to nearest edge

**Benefit:**

- Lower latency
- Reduced origin load

---

## 2. Feed Generation Strategy

The main challenge: **fanout strategy**

---

### Option 1: Fanout-on-write (Push Model)

When a user posts:

- Push content into all followers' feed

**Pros:**

- Fast read (low latency feed loading)
- Simple read path

**Cons:**

- Expensive for high-follower users
- Write amplification problem

---

### Option 2: Fanout-on-read (Pull Model)

When a user opens feed:

- Dynamically fetch posts from followed users

**Pros:**

- Avoids massive write cost
- Scales better for large accounts

**Cons:**

- Higher read latency
- More complex aggregation logic

---

### Hybrid Strategy (Real-world approach)

Use different strategies based on user type:

#### Regular users (e.g., < 500 followers)

- Use **fanout-on-write**
- Push posts into followers' feeds

#### Celebrity / hot users

- Use **fanout-on-read**
- Do NOT push to all followers
- Instead:
  - Store posts separately
  - Merge during read time

---

### Key insight

> Not all users are equal — optimize based on follower count.

This hybrid model balances:

- Write scalability
- Read latency
- System cost

---

## Final Thoughts

Designing Instagram-like systems requires balancing:

- Latency vs cost
- Write amplification vs read complexity
- User experience vs system scalability

Two key takeaways:

1. Always separate **upload path** and **processing path**
2. Use **hybrid strategies** for feed generation

---

## What I Learned

- Pre-signed URL + direct upload is essential for scalability
- Async processing is critical for media pipelines
- Feed systems must adapt based on user scale