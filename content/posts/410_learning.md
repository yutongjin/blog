---
title: "Practice 4-10"
date: 2026-04-10
draft: false
tags: ["blog", "engineering", "email"]
---
# Lessons Learned from My Product Discovery Journey

## Key Lessons

### 1. Start with a minimal product scope
I learned that I should begin with a small and clear set of functional requirements instead of adding extra features too early. In system design interviews, simple is usually better than broad. I should focus first on the core user needs and avoid introducing features that are not explicitly required.

### 2. Always call out non-functional requirements early
One of my biggest takeaways is that I need to explicitly mention non-functional requirements such as:
- high availability
- high scalability
- fault tolerance

I should also ask the interviewer whether there are any additional priorities, such as latency, consistency, or cost. This helps show that I understand what drives the architecture.

### 3. Do not assume every system needs an API discussion
Another lesson is that I should not automatically include API design in every interview answer. Some systems may have another team owning the API layer, or the interviewer may not care about that part. I should confirm the scope first and only go into API design if it is relevant.

### 4. Keep the high-level design simple
I learned that I should keep the architecture clean and easy to follow:
- one component for one responsibility
- no duplicated services
- no unnecessary complexity

This makes the design more structured, easier to explain, and more aligned with what interviewers want.

### 5. System design is also product discovery
A system design interview is not just about proposing components. It is also about discovering the right scope, understanding the actual problem, and making good tradeoffs. I should first clarify what needs to be built before jumping into the solution.

### 6. Simplicity shows maturity
A strong design is not the one with the most services. A strong design is the one that is simple, scalable, and directly tied to the requirements. I learned that a simpler design often communicates better and feels more senior.

### 7. Follow interviewer guidance closely
If the interviewer says a part of the system can be assumed or is owned by another team, I should accept that and move on. I should align with the interviewer’s direction instead of trying to force extra details into the discussion.

---

## Final Design: Email Delivery System

## 1. Scope

### Functional Requirements
- Send an email
- Deliver the email to recipients
- Support retry if delivery fails

### Non-Functional Requirements
- High availability
- High scalability
- Fault tolerance

I would also ask the interviewer whether there are other priorities, such as latency, ordering, or consistency.

---

## 2. Assumption
We assume the API layer is handled by another team, so this design starts from the internal email delivery service after the request is accepted.

---

## 3. High-Level Design

### Components
1. **Email Service**
   - Receives validated email send requests from the upstream system
   - Persists email metadata and delivery status
   - Pushes a delivery task into the queue

2. **Storage**
   - Stores email metadata, recipient list, delivery state, and retry state

3. **Queue**
   - Buffers delivery tasks
   - Decouples request acceptance from actual email delivery
   - Helps absorb traffic spikes and improve scalability

4. **Delivery Worker**
   - Consumes tasks from the queue
   - Attempts email delivery
   - Updates delivery result in storage
   - Retries failed deliveries when needed

5. **SMTP Gateway**
   - Sends the email to external mail servers

---

## 4. End-to-End Flow

### Send Flow
1. The upstream system sends a validated email request to the **Email Service**
2. The **Email Service** stores the email record in **Storage** with an initial status such as `PENDING`
3. The **Email Service** publishes a delivery task to the **Queue**
4. A **Delivery Worker** reads the task from the **Queue**
5. The **Delivery Worker** sends the email through the **SMTP Gateway**
6. If delivery succeeds, the worker updates the email status in **Storage** to `SENT`
7. If delivery fails, the worker updates the retry state and re-enqueues the task for another attempt

---

## 5. Why This Design Works

### Scalability
- The **Queue** allows the system to handle large traffic spikes
- The **Delivery Workers** can be scaled horizontally
- The **Email Service** remains lightweight because delivery is asynchronous

### High Availability
- Multiple instances of **Email Service** and **Delivery Worker** can run at the same time
- If one worker fails, another worker can continue processing queued tasks

### Fault Tolerance
- Failed deliveries are retried instead of being dropped
- The queue prevents temporary downstream failures from losing requests
- Delivery status is stored persistently, so recovery is possible after crashes

---

## 6. Design Principles Reflected Here

This final design reflects the lessons I learned:
- start with minimal requirements
- explicitly mention scalability, availability, and fault tolerance
- avoid unnecessary API discussion when it is out of scope
- keep the design simple
- assign one clear responsibility to each component

---

## 7. Final Summary
For this email delivery system, I would keep the design simple: an **Email Service** writes email jobs to **Storage** and a **Queue**, **Delivery Workers** process those jobs asynchronously, and an **SMTP Gateway** handles external delivery. This design is scalable, highly available, fault tolerant, and easy to explain in an interview.