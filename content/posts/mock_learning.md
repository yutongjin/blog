# System Design Interview Feedback (Calendar System)

---

## 🟢 Overall Feedback

- Functional design was mostly correct
- Reminder workflow was well structured
- High-level direction was solid
- Some gaps existed but were mostly trivial

---

## 🧩 Requirements & Scoping

### ✅ Strengths
- Covered core functional requirements
- API design was reasonable
- Non-functional requirements were acceptable

### ⚠️ Improvements
- Did not explicitly capture **recurring events early**
  - Impacts storage, reads, and notifications

---

## 🧱 Data Modeling & Schema

### ✅ Strengths
- Entity design was reasonable
- Core fields identified correctly

### ⚠️ Improvements
- Avoid defining full schema too early
- Do schema after high-level design
- Partitioning strategy needs improvement

---

## 🧠 Partitioning

### ❌ Current approach
- Partition by event ID

### ⚠️ Problem
- Optimizes writes, not reads

### ✅ Recommended
- Partition by time (start time / next start time)

### 💡 Reason
- Main read paths:
  - GET events by date range
  - Scheduler scans
- Time-based partitioning narrows scan range and improves performance

---

## 🔁 Recurring Events Design

### ❌ Problematic approach
- Pre-populating all occurrences

### Issues
- Data duplication
- Infinite recurrence problems
- Hard to update or cancel

### ✅ Recommended
- Store recurrence rules and frequency
- Return to client
- Let client compute occurrences

### 💡 Benefits
- Avoid duplication
- Better scalability
- Easier maintenance

---

## 🔔 Notification / Scheduler Design

### ✅ Strengths
- Scheduler + queue architecture was correct
- Recognized pattern: calendar = distributed scheduler

### ⭐ Strong point
- Correct use of delayed queue (e.g., SQS)

---

## 🧠 System Pattern Recognition

> User provides data now, system acts later → scheduler pattern

Applies to:
- reminders
- subscriptions
- delayed jobs

---

## ⚡ Burst Handling

### ✅ Strength
- Correct instinct to add buffering

### ❌ Issue
- Queue placed before service layer

### ✅ Correct design
- Service → Queue → DB

### 💡 Reason
- Protect DB from overload
- Prevent retry amplification

---

## 🧠 Read Optimization

### ❌ Issue
- Added general read cache unnecessarily

### ⚠️ Problem
- Cache inconsistency and complexity

### ✅ Better approach
- Fix partitioning first

### 🟡 Valid cache use case
- Cache recently canceled events (within ~10 min window)

---

## 🏗️ Architecture Design

### ⚠️ Improvement
- Move to microservices earlier

### 💡 Reason
- Read and write paths scale differently

### ✅ Suggested split
- Read service
- Write service
- Scheduler service

### 🎯 Benefit
- Fault isolation
- Better scalability

---

## ⚖️ CAP & Partitioning

| Goal              | Strategy        |
|------------------|----------------|
| High consistency | Partition by ID |
| High availability| Partition by access pattern |

👉 Calendar is read-heavy → optimize reads

---

## 🧮 Estimation

### Insight
- Not always required

### When needed
- Infra-heavy systems

### For product systems
- Rough estimates are sufficient

---

## 🧠 Interview Performance

### ✅ Strengths
- Handled edge cases well
- Responded well to hints

### ⚠️ Improvements
- Did not proactively drive deep-dive discussion

---

## 🚀 To Improve

- Identify bottlenecks proactively
- Raise tradeoffs without prompting
- Think about:
  - race conditions
  - scaling limits
  - edge cases

---

## 📈 Practice Strategy

### ❌ Avoid
- Over-consuming solutions

### ✅ Do
- Solve independently first
- Then compare with references

### 💡 Method
- Annotate differences
- Track improvements

---

## 🔁 Practice Loop

Solve → Compare → Improve → Repeat

---

## 🎯 Key Advice

- Consistency > volume
- Practice 1–2 problems per day
- Build your own design library

---

## 🧠 Final Insight

Strong candidates don’t just solve — they challenge their own design

Ask:
- Where are bottlenecks?
- What breaks at scale?
- What edge cases exist?

---

## 🚀 TL;DR

- Good functional design
- Missed recurring events early
- Partitioning should be time-based
- Scheduler pattern recognized
- Need stronger proactive deep-dive