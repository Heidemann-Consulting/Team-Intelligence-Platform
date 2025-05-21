# ApexFusion Rituals & Practices

**Version:** 1.0
**Date:** May 17, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

- [ApexFusion Rituals \& Practices](#apexfusion-rituals--practices)
  - [1. Roles \& Daily Time-Budget](#1-roles--daily-time-budget)
  - [2. Cadence Overview](#2-cadence-overview)
  - [3. Initial Setup (Day 0 – 60 min)](#3-initial-setup-day-0--60-min)
  - [4. Best Practices](#4-best-practices)
  - [5. FAQ (excerpt)](#5-faq-excerpt)
  - [6. Estimated Weekly Effort Chart](#6-estimated-weekly-effort-chart)

## 1. Roles & Daily Time-Budget

| Emoji | Role | Core Duties | Daily Time |
|-------|------|------------|-----------|
| 🧭 | **Navigator** (rotates daily) | Triggers workflows, checks model output | 7 min |
| 🛠️ | **Contributor** | Provide raw notes, refine drafts | 15 min |
| 📊 | **Metrics Steward** (weekly) | Update KPI sources | 3 min |
| 📚 | **Editor-in-Chief** (weekly) | Final review of Weekly Review & deck | 5 min |

_Total ≤ 30 min per person._

---

## 2. Cadence Overview

| Cadence | Trigger | Workflow Stack | Human Steps | Outcome |
|---------|---------|----------------|-------------|---------|
| **Daily Stand-up (09:00)** | Calendar | — | Speak updates ▫ Navigator logs bullet points | Raw note doc |
| **Daily Log (09:10)** | Manual | DailyLog | Review & approve | `Daily_Log_<date>` |
| **Daily Planning (09:20)** | Manual | DailyPlan | Accept plan ▫ assign tasks | `Daily_Plan_<date>` |
| **Weekly Sprint Kick-off (Mon 09:00)** | Time | SprintKickoff | Tweak focus & capacity | `Weekly_Sprint_<week>` |
| **Weekly Review (Fri 16:00)** | Time | WeeklyReview | Comment on insights | `Weekly_Review_<week>` |
| **Monthly Strategy Check (1st biz day 14:00)** | Time | MonthlyStrategyCheck | Exec team review 15 min | Strategy deltas |
| **Prompt Workshop (bi-weekly 45 min)** | Calendar | PromptWorkshop | Pair-draft & test | Updated workflow |
| **Context Hygiene (ad-hoc)** | Size>6 K | ContextShrinker | Sanity-check summary | `Shrunk_*` |

---

## 3. Initial Setup (Day 0 – 60 min)

| Step | Owner | Time | Action |
|------|-------|------|--------|
| 1 | Admin | 15 min | Import **Templates** & **Workflows** |
| 2 | Team | 20 min | Create first `North_Star_Charter`, `Backlog`, `KPI_Baseline` |
| 3 | Navigator | 10 min | Schedule calendar events for all rituals |
| 4 | All | 15 min | Dry-run Daily Log & Plan workflows |

---

## 4. Best Practices

1. **Micro-context discipline** – paste only *delta* facts into prompts.
2. **Mandatory ⬜-Review** – unchecked box blocks commit.
3. **Compression before deletion** – use Shrinker.
4. **Prompt diff logs** – every prompt tweak logged via PromptWorkshop.
5. **Timeboxing** – stop when the timer hits; perfection deferred.

---

## 5. FAQ (excerpt)

* **Q:** What if the 30B model hallucinates?
  **A:** Editor-in-Chief flags, add counter-example to template few-shot, rerun.

* **Q:** How do we extend context size?
  **A:** Chain ContextShrinker → append summary, never raw dump.

* **Q:** Can we skip Daily Planning?
  **A:** Only if Daily Log shows zero blockers *and* Sprint burn-down is green.

---

## 6. Estimated Weekly Effort Chart

| Ritual | Team Minutes / Week |
|--------|--------------------|
| Daily Loops | 5 × 25 min = 125 |
| Weekly Kick-off | 20 |
| Weekly Review | 25 |
| Prompt Workshop | 45 (bi-weekly → 22.5) |
| **Total** | **~192 min/person ≈ 3 h 12 m** |
