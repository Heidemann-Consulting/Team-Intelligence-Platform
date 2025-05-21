# **Lean‑Loop LLM Facilitator – Rituals & Practices for Team Intelligence Platform (TIP)**

**Version:** 1.0
**Date:** May 14, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0
**Templates Library Referenced:** [Lean‑Loop Templates Library for TIP](./lean-loop-templates-library.md)
**Workflow Library Referenced:** [Lean‑Loop Workflow Library for TIP](./lean-loop-workflow-library.md)

---

## **Table of Contents**

- [**Lean‑Loop LLM Facilitator – Rituals \& Practices for Team Intelligence Platform (TIP)**](#leanloop-llm-facilitator--rituals--practices-for-team-intelligence-platform-tip)
  - [**Table of Contents**](#table-of-contents)
  - [**1 Executive Summary**](#1executive-summary)
  - [**2 Prerequisites – Initial Document Setup in TIP**](#2prerequisites-initial-document-setup-in-tip)
  - [**3 Core Principles of Lean‑Loop in TIP**](#3core-principles-of-leanloop-in-tip)
  - [**4 Lean‑Loop Overview – Phases \& Routines**](#4leanloop-overview-phases--routines)
  - [**5 Phase 1 – Daily Lean Loop**](#5phase1-daily-lean-loop)
    - [5.1 Prepare **Prompt Packet**](#51prepare-prompt-packet)
    - [5.2 Generate \& Self‑Check](#52generate--selfcheck)
    - [5.3 Triage](#53triage)
    - [5.4 Refine](#54refine)
    - [5.5 Commit \& Compress](#55commit--compress)
  - [**6 Phase 2 – Weekly Cadence**](#6phase2-weekly-cadence)
    - [6.1 Monday Kick‑off](#61monday-kickoff)
    - [6.2 Friday Retrospective](#62friday-retrospective)
    - [6.3 Metric Logging](#63metric-logging)
  - [**7 Phase 3 – Monthly Cadence**](#7phase3-monthly-cadence)
  - [**8 Phase 4 – Quarterly \& Annual Cadence**](#8phase4-quarterly--annual-cadence)
  - [**9 Ad‑hoc AI Pair Working**](#9adhoc-ai-pair-working)
  - [**10 Implementation Notes for TIP Users**](#10implementation-notes-for-tip-users)
    - [10.1 Naming Conventions](#101naming-conventions)
    - [10.2 Running Workflows](#102running-workflows)
    - [10.3 Review Discipline](#103review-discipline)
  - [**11 Continuous Improvement of Lean‑Loop Practices**](#11continuous-improvement-of-leanloop-practices)

---

## **1 Executive Summary**

The **Lean‑Loop LLM Facilitator** is a minimal‑overhead workflow that turns a 128 K‑token reasoning‑grade language model into a *shared strategic aide* for teams of 1‑9 people.  It marries cognitive‑science‑driven prompt patterns with tight artefact discipline so that every human minute adds compoundable value toward long‑term goals.  This document codifies the **rituals, cadences and artefacts** required to run Lean‑Loop entirely inside the **Team Intelligence Platform (TIP)**.

---

## **2 Prerequisites – Initial Document Setup in TIP**

Before starting, create the following TIP Documents from the Lean‑Loop Templates Library:

| Template name          | Resulting living TIP Document | Notes                             |
| ---------------------- | ----------------------------- | --------------------------------- |
| **North‑Star Charter** | `North_Star_Charter`          | Mission & 3‑year KPIs             |
| **Working Backlog**    | `Working_Backlog_Current`     | 12‑week ranked deliverables       |
| **Decision Log**       | `Decision_Log`                | Timestamped decisions             |
| **Prompt Library**     | `Prompt_Library`              | Re‑usable prompt snippets         |
| **Daily Digest**       | `Daily_Digest`                | Rolling 14‑day compressed context |
| **Resource Vault**     | `Resource_Vault`              | Links to specs, style guides etc. |
| **Lean‑Loop Guide**    | `Lean_Loop_Guide`             | (this document)                   |

Your TIP Administrator should also have imported all workflows defined in the **Lean‑Loop Workflow Library for TIP**.

---

## **3 Core Principles of Lean‑Loop in TIP**

1. **Single‑threaded context**: All knowledge lives in TIP Documents; the LLM sees only what is explicitly injected via workflows.
2. **ROI‑per‑token mindset**: Charter, Backlog and the last two Digest days (~4 K tokens) are the default context; anything else is pulled ad‑hoc.
3. **Mixed‑initiative by design**: The LLM proposes; humans vote 👍/👎 and refine ‑‑ preserving trust calibration.
4. **Visible metacognition**: Self‑critique steps and risk sections are mandatory in LLM outputs.
5. **Compression > deletion**: Old context is summarised monthly, never blindly discarded.
6. **Markdown everywhere**: Ensures human & machine readability and diff‑friendly version history.

---

## **4 Lean‑Loop Overview – Phases & Routines**

| Cadence              | Purpose                                   | Main Workflows                                                    | Key Outputs                             |
| -------------------- | ----------------------------------------- | ----------------------------------------------------------------- | --------------------------------------- |
| **Daily**            | Decide next‑best steps & capture progress | `Generate_LLM_Draft`, `Incorporate_Comments`, `Digest_Compressor` | Refined deliverable, Daily Digest entry |
| **Weekly**           | Adjust priorities, learn & improve        | `Retro_Analyzer`, `Weekly_Kickoff`                                | Retro insights, updated Backlog         |
| **Monthly**          | Manage context, track KPIs                | `Metrics_Snapshot`, `Context_Condensor`                           | KPI dashboard, condensed context        |
| **Quarterly/Annual** | Strategic alignment & goal reset          | `Quarterly_Strategy_Review`                                       | Updated Charter & Backlog               |

---

## **5 Phase 1 – Daily Lean Loop**

### 5.1 Prepare **Prompt Packet**

* **Who:** Coordinator
* **Time:** ≤ 5 min
* **How (Manual):** Create `Prompt_Packet_YYYY‑MM‑DD` from template; fill sections:

  * Goal of the Day
  * New Facts / Resources
  * Questions Requiring Reasoning
  * (Optional) Capacity Snapshot

### 5.2 Generate & Self‑Check

* **Who:** LLM via `Generate_LLM_Draft` workflow
* **Output:** `LLM_Draft_YYYY‑MM‑DD` with sections Draft / Risks / Clarifying Questions / 👍/👎 markers / **Next‑Best‑Steps** (ranked by ROI per human hour).

### 5.3 Triage

* **Who:** Domain Contributors (async)
* **Time:** 3‑10 min each
* **Action:**  Add inline 👍/👎, supply missing facts in comments.

### 5.4 Refine

* **Who:** LLM via `Incorporate_Comments` workflow
* **Output:** `LLM_Refined_YYYY‑MM‑DD` compressed by ≈20 %.

### 5.5 Commit & Compress

* **Who:** Coordinator
* **Workflow:** `Digest_Compressor`
* **Action:**  Copy 150‑token summary into `Daily_Digest` and prune entries >14 days.

> **Daily aggregate human time:** ≈ 25 minutes for a 5‑person team.

---

## **6 Phase 2 – Weekly Cadence**

### 6.1 Monday Kick‑off

* **Sync (15 min)**: Editor‑in‑Chief reviews KPI deltas; Backlog reordered.
* **LLM Assist:** Run `Weekly_Kickoff` workflow to propose backlog changes.

### 6.2 Friday Retrospective

* **Async (10 min)**: Run `Retro_Analyzer` workflow on week’s Decision Log and Digest.
* **Team Vote:** 👍/👎 on the two highest‑ROI process tweaks.

### 6.3 Metric Logging

Coordinator updates KPI dashboard inside `Lean_Loop_Guide`.

---

## **7 Phase 3 – Monthly Cadence**

1. **Metrics Snapshot** workflow captures human‑minutes‑per‑deliverable, accuracy samples and NASA‑TLX scores.
2. **Context Condensor** generates `Condensed_Context_YYYY‑MM` from >30‑day artefacts; humans verify before archiving originals.

---

## **8 Phase 4 – Quarterly & Annual Cadence**

* **Quarterly Strategy Review** workflow analyses KPI trends vs Charter; outputs draft Objective updates.
* Team revises and publishes new `North_Star_Charter` version plus refreshed `Working_Backlog_Current`.

---

## **9 Ad‑hoc AI Pair Working**

Any team member may create `Pair_Input_[Task]_[Date]` and invoke general‑purpose drafting or analysis workflows.  Save effective prompts to the `Prompt_Library`.

---

## **10 Implementation Notes for TIP Users**

### 10.1 Naming Conventions

`[DocumentPurpose]_[YYYY‑MM‑DD]` for dated artefacts; `[DocumentPurpose]_Current` for living docs.  Keep names short to aid glob selectors.

### 10.2 Running Workflows

1. Prepare or update required input documents.
2. *Run Workflow* → select inputs → execute.
3. Review LLM output; **edit & save** to commit.

### 10.3 Review Discipline

Humans are the quality gate. No LLM output becomes canonical until a team member saves it.

---

## **11 Continuous Improvement of Lean‑Loop Practices**

* Reserve 5 minutes in the Friday Retro to ask: *“Did Lean‑Loop save us time this week?”*
* Capture improvement ideas in `Prompt_Library` or `Decision_Log`.
* Administrators refine workflows monthly based on feedback.
