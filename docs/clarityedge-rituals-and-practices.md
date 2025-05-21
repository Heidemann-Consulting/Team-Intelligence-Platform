```markdown
<!--
Document: ClarityEdge – Rituals & Practices
**Version:** 1.0
**Date:** May 17, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0
-->

# ClarityEdge ™ Rituals & Practices
**A lightweight operating manual for running the ClarityEdge AI Co-Management Framework in TIP**

---

## Table of Contents
1. Purpose & Scope
2. Audience & Roles
3. Initial Setup (Day 0)
4. Onboarding a New Team Member
5. Operating Cadence
   - 5.1 Daily (≤ 30 min pp)
   - 5.2 Weekly
   - 5.3 Monthly
   - 5.4 Quarterly
   - 5.5 Annual
6. Best Practices & Guardrails
7. Frequently Asked Questions (FAQ)

---

## 1 • Purpose & Scope
This handbook turns the concept, templates, and workflows you installed in **Steps 1–3** into repeatable rituals that:

- **Achieve content goals** with a local 30 B reasoning model inside TIP.
- **Cap human effort at 30 minutes per person per day** while maximising ROI.
- **Continually compound knowledge** through Progressive Summaries and Decision Logs.

---

## 2 • Audience & Roles

| Role | Typical Seat(s) | Core Responsibilities | Daily Time-box |
|------|-----------------|-----------------------|---------------|
| **Lead** | Product/Team Manager | Approve outputs, queue strategic workflows, remove blockers | ≤ 10 min |
| **Contributor** | 1-8 Specialists | Produce inputs (meeting notes, briefs), trigger workflows, refine drafts | ≤ 15 min |
| **AI Liaison** | Rotating (weekly) | Monitor model health, token spend, metrics log | ≤ 5 min |

> **Tip:** The Liaison role rotates weekly to spread tooling literacy.

---

## 3 • Initial Setup (Day 0 ≈ 90 min total)

| Step | Owner | Time | Action |
|------|-------|------|--------|
| 1 | Admin | 15 min | Import all **ClarityEdge – Templates** into TIP’s *Templates* panel. |
| 2 | Admin | 20 min | Add all **Workflows** from the library in *Process Workflows*; validate with TIP’s tester. |
| 3 | Lead + Team | 30 min | For each strategic objective, create a **Goal Definition** doc, then run **Goal_Definition_to_Strategy_Map**. |
| 4 | Liaison | 10 min | Create empty yearly **Decision Log YYYY** & **Metrics Log** docs. |
| 5 | All | 15 min | Familiarise yourselves with the **AI Prompt Scaffold** and “Small Bites” principle. |

---

## 4 • Onboarding a New Team Member (≈ 45 min once)

1. **Send Welcome Pack** – This handbook + link to the Template Library (5 min Lead).
2. **Mini-Workshop** – Walk through creating a *Task Brief* and generating an *AI Prompt* live (25 min Lead).
3. **Assign First Task** – New member fills a *Daily Check-in*, triggers **Checkin_to_Daily_Summary** (10 min).
4. **Grant Rights** – Ensure “Global visibility = true” on templates & metrics docs (5 min Admin).

---

## 5 • Operating Cadence

### 5.1 Daily Ritual (≤ 30 min pp)

| Time | Actor | Activity | Tool / Doc | Duration |
|------|-------|----------|------------|----------|
| 09:00 | Contributor | Fill **Daily Check-in** | Template | 5 min |
| 09:05 | Contributor | Create / update **Task Briefs** & trigger **Task_Brief_to_AI_Prompt** | Workflow | 5 min |
| 09:10 | Contributor | Review yesterday’s **Draft** → approve or refine | Doc | 5 min |
| 09:15 | Lead | Trigger **Checkin_to_Daily_Summary** & scan blockers | Workflow | 5 min |
| 09:20 | Liaison | Check **Metrics Log** for anomalies | Doc | 5 min |
| *Slack* | Anyone | Ad-hoc **Meeting Notes** then **Meeting_Notes_to_Summary** |  | (counts toward 15 min where possible) |

### 5.2 Weekly (Friday PM, 25 min)

1. **Team Retrospective** (15 min) → fill *Retrospective* doc.
2. Trigger **Retro_to_Improvement_Actions** (automatic, 1 min).
3. Re-visit **Strategy Maps**; create any new *Decision Records* (9 min).

### 5.3 Monthly (45 min)

| Task | Owner | Time |
|------|-------|------|
| Review Goal metrics; adjust Success Criteria | Lead | 20 min |
| Refresh Progressive Summaries for large docs | Contributors | 15 min |
| Export **Metrics Log** slice → optional KPI deck | Liaison | 10 min |

### 5.4 Quarterly (60 min)

- Strategy deep-dive workshop (could extend outside daily cap once per quarter).
- Consolidate Decision Log; archive obsolete items.

### 5.5 Annual (90 min)

- Year-end Retrospective + new Goal Definitions.
- Purge or compress documents older than 12 months.
- Audit token spend vs. business outcomes for ROI proof.

---

## 6 • Best Practices & Guardrails

| Theme | Practice |
|-------|----------|
| **Prompt Craft** | Follow the 7-block scaffold; keep input ≤ 2 k tokens. |
| **Token Efficiency** | Always generate a *Progressive Summary* once a doc exceeds 1 000 words. |
| **Self-Critique** | Require models to rate Completeness & Clarity ≥ 9/10 before final output. |
| **Version Hygiene** | TIP versions automatically; still include dates in output names for quick scanning. |
| **Risk Management** | For critical assets, run **Draft_to_Final_Asset** twice: second pass with different temperature (0.2 → 0.5). |
| **Focus Discipline** | If a task feels > 30 human minutes, split it into two Task Briefs. |
| **Continuous Learning** | Save any high-performing prompt fragment as a **Prompt Snippet** for reuse. |

---

## 7 • FAQ

| Question | Quick Answer |
|----------|--------------|
| *Will the 30 B model understand our niche jargon?* | Yes—feed short glossaries in the *Context* block or link a Progressive Summary. |
| *What if the model times out?* | Re-run; if persistent, Liaison checks local server or slices the prompt into smaller chunks. |
| *Do I need to know YAML?* | Only Admins touching workflow definitions; everyday users operate through templates. |
| *How do we measure ROI?* | **Metrics Log** captures human-minutes saved; compare against historical baselines each quarter. |
| *Can we exceed 30 min on crunch days?* | Rarely—prefer tighter scoping or more AI delegation; consistency beats spikes. |

---

### 🔚  You’re Ready for Step 5
With rituals defined, teams can operate ClarityEdge smoothly inside TIP.
Proceed to **Step 5** to generate a slide deck that markets the framework, teaches essentials, and sparks adoption.
```
