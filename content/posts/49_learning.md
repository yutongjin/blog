---
title: "Practice 4-9"
date: 2026-04-09
draft: false
tags: ["blog", "engineering", "CDC"]
---

### Learning
# 🎬 Video Upload & Moderation System (TikTok-style)

## 1. Functional Requirements
- Creators can upload videos
- Users can view videos
- Reviewers can moderate videos
- Users get notified if content is banned

---

## 2. Non-Functional Requirements
- High availability (eventual consistency acceptable)
- High throughput for uploads and reads
- Low latency for video playback
- Scalable for viral (hot) content

---

## 3. High-Level Architecture

### Upload Flow
Client → API Gateway → UploadService → S3  
                                 ↓  
                              Kafka

### Read Flow
User → CDN → S3

### Metadata Flow
UploadService → Kafka → Metadata Service → Write DB  
Write DB → WAL → CDC → Read DB

### Moderation Flow
Reviewer → ReviewService → VideoModerationDB  
                              ↓  
                           Kafka → Notification Service

---

## 4. Upload Flow (Step-by-step)

1. Client requests upload URL:
   POST /videos/upload-url

2. UploadService:
   - Generates presigned URL (with TTL)
   - Creates metadata record with status = PENDING

3. Client uploads directly to S3:
   Client → S3 (presigned URL)

4. S3 emits event:
   S3 → Kafka

5. Processing Service:
   - Update status: UPLOADING → SUCCESS / FAILURE
   - Trigger processing pipeline

---

## 5. CDN (Critical)

Architecture:
User → CDN → S3

Why CDN?
- Reduce latency (edge caching)
- Offload S3 traffic
- Handle viral content
- Support range requests (streaming)

Optional:
- Signed URLs for access control

---

## 6. Video Metadata Schema

VideoMetadata
- videoId (PK)
- creatorId
- uploadAt
- updateAt

- storageKey
- cdnUrl

- uploadStatus (PENDING / UPLOADING / SUCCESS / FAILURE)
- processingStatus (PENDING / PROCESSING / DONE / FAILED)

- duration
- resolution
- thumbnailUrl

- title
- description
- visibility

---

## 7. Database Design

Primary Key (for user video listing):
- PK: creatorId
- SK: uploadAt

GSI (for video lookup):
- PK: videoId

---

## 8. Hot Partition Handling

Problem:
- Popular creators cause hotspot partitions

Solution:
- PK: creatorId#shardId
- shardId = hash(videoId) % N

---

## 9. Read / Write Separation (CDC)

Write DB → WAL → CDC → Read DB

- Write DB: optimized for writes
- Read DB: optimized for queries

---

## 10. Event-Driven System (Kafka)

Used for:
- Upload events
- Processing pipeline
- Moderation results
- Notifications

Benefits:
- Decoupling
- Retry handling
- Scalability

---

## 11. Processing Pipeline

Kafka → Processing Service:
- Transcoding (HD/SD)
- Thumbnail generation
- Content analysis / moderation

---

## 12. Moderation System

API:
POST /moderation/{videoId}

Body:
{
  decision: PASS / REJECT,
  reason: SPAM / VIOLENCE / PORN
}

Flow:
ReviewService → VideoModerationDB  
              → Kafka → Notification Service

---

## 13. APIs

- POST /videos/upload-url
- POST /videos/{id}/complete
- GET  /videos/{id}
- POST /moderation/{videoId}

---

## 14. Key Trade-offs

Consistency:
- Eventual consistency (CDC, async updates)

Latency vs Throughput:
- CDN improves read latency
- Kafka improves throughput

Scalability:
- Sharding avoids hot partitions
- Event-driven architecture scales well

---

## 15. Summary (Interview Closing)

This system uses presigned URLs for efficient uploads, CDN for low-latency video delivery, Kafka for decoupled event processing, and CDC for read/write separation. It handles hot partitions via sharding and supports both user-based listing and video-based lookup through proper indexing.


# Polished version 🎬 Video Upload & Moderation System (Interview Version)

## 1. Introduction
For this problem, I will design a video upload and moderation system. I will start with functional requirements, then non-functional requirements, and finally go into the system design.

---

## 2. Functional Requirements
- Creators can upload videos  
- Reviewers can fetch videos and make moderation decisions  
- The system determines whether a video is valid or violates policies  
- Creators are notified if their video is banned, along with a reason  

---

## 3. Non-Functional Requirements
- High availability (prioritized over consistency)  
- Eventual consistency is acceptable (moderation is async)  
- High throughput for uploads and reads  
- Low latency for video playback  
- Scalable to handle large traffic and viral content  

---

## 4. Core Entities
- Creator  
- Reviewer  
- Video  
- VideoMetadata  
- VideoModerationRecord  

---

## 5. API Design

### Upload Video
POST /videos/upload-url

### Get Video
GET /videos/{videoId}

### Moderate Video
POST /moderation/{videoId}

Request Body:
{
  "decision": "PASS" | "REJECT",
  "reason": "SPAM | VIOLENCE | PORN"
}

---

## 6. High-Level Architecture

### Upload Flow
Client → API Gateway → UploadService → S3 → Kafka

### Read Flow
User → CDN → S3

### Metadata Flow
UploadService → Write DB → CDC → Read DB

### Moderation Flow
Reviewer → ReviewService → Moderation DB → Kafka → Notification Service

---

## 7. Upload Flow (Step-by-step)

1. Client requests upload URL:
   POST /videos/upload-url

2. UploadService:
   - Generates a presigned URL (with TTL)
   - Creates metadata record with status = PENDING

3. Client uploads video directly to S3:
   Client → S3 (via presigned URL)

4. S3 triggers events:
   - Upload started → status = UPLOADING  
   - Upload finished → status = SUCCESS / FAILURE  

---

## 8. Video Metadata Schema

VideoMetadata
- videoId (PK)
- creatorId
- uploadAt
- updateAt
- storageKey
- cdnUrl
- uploadStatus (PENDING / UPLOADING / SUCCESS / FAILURE)
- processingStatus (PENDING / PROCESSING / DONE / FAILED)
- duration
- resolution
- thumbnailUrl
- title
- description
- visibility

---

## 9. Moderation System

Flow:
- Reviewer fetches video metadata  
- Uses S3 URL to view video  
- Makes moderation decision  

VideoModeration Table:
- PK: videoId  
- SK: createdAt  
- reviewerId  
- decision  
- reason  

---

## 10. Notification System
- If video is rejected:
  - Emit event to Kafka  
  - Notification Service consumes event  
  - Notify creator with reason  

---

## 11. Read / Write Separation (CDC)

Problem:
- Upload service and review service share the same DB  
- High write traffic impacts read performance  

Solution:
Write DB → WAL → CDC → Read DB  

- Write DB handles uploads  
- Read DB serves queries  
- Only SUCCESS videos are replicated  

---

## 12. Event-Driven Architecture (Kafka)

Used for:
- Upload events  
- Moderation results  
- Notifications  

Benefits:
- Decoupling  
- Retry handling  
- Scalability  

---

## 13. CDN (Critical for Video Delivery)

Architecture:
User → CDN → S3  

Benefits:
- Reduce latency via edge caching  
- Offload traffic from S3  
- Handle viral content efficiently  
- Support range requests for streaming  

---

## 14. Database Design

Primary Key (user video listing):
- PK: creatorId  
- SK: uploadAt  

GSI (video lookup):
- PK: videoId  

---

## 15. Hot Partition Handling

Problem:
- Popular creators create hotspot partitions  

Solution:
- PK: creatorId#shardId  
- shardId = hash(videoId) % N  

---

## 16. Key Trade-offs

Consistency:
- Eventual consistency (CDC, async moderation)  

Latency vs Throughput:
- CDN improves read latency  
- Kafka improves throughput  

Scalability:
- Sharding avoids hot partitions  
- Event-driven design scales well  

---

## 17. Summary

This system uses presigned URLs for efficient uploads, CDN for low-latency delivery, Kafka for decoupled event processing, and CDC for read/write separation. It supports scalable moderation and notification pipelines while handling hot partitions through sharding and proper indexing.