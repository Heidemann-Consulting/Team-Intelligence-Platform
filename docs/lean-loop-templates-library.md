# **Lean‑Loop Templates Library for Team Intelligence Platform (TIP)**

**Version:** 1.0
**Date:** May 14, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0
**Rituals & Practices Referenced:** [Lean‑Loop Rituals & Practices for TIP](./lean-loop-rituals-and-practices.md)
**Workflow Library Referenced:** [Lean‑Loop Workflow Library for TIP](./lean-loop-workflow-library.md)

---

## **1 Purpose**

This library provides **copy‑paste‑ready Markdown templates** used to instantiate all core Lean‑Loop artefacts in TIP.  Each template follows TIP’s formatting guidelines (FR‑DOC‑FMT‑001) and naming conventions so they work seamlessly with the glob‑based workflow selectors.

---

## **2 Template Index**

| #  | Template Name                | Purpose                               | Suggested File Name                              | Consumed by Workflows  |
| -- | ---------------------------- | ------------------------------------- | ------------------------------------------------ | ---------------------- |
| 1  | North‑Star Charter           | Mission, 3‑year objectives & KPIs     | `North_Star_Charter`                             | Context inject (daily) |
| 2  | Working Backlog              | Rolling 12‑week ranked deliverables   | `Working_Backlog_Current`                        | Context inject (daily) |
| 3  | Decision Log                 | Timestamped rationale for key choices | `Decision_Log`                                   | Retro Analyzer         |
| 4  | Prompt Packet                | Daily context for LLM run             | `Prompt_Packet_YYYY‑MM‑DD`                       | Generate\_LLM\_Draft   |
| 5  | Daily Digest                 | Rolling 14‑day compressed history     | `Daily_Digest`                                   | Context inject (daily) |
| 6  | Prompt Library               | Re‑usable prompt snippets             | `Prompt_Library`                                 | Human lookup           |
| 7  | Resource Vault               | Links / docs repository               | `Resource_Vault`                                 | Manual reference       |
| 8  | Capacity Snapshot (optional) | Today’s availabilities & skills       | Inline section or `Capacity_Snapshot_YYYY‑MM‑DD` | Generate\_LLM\_Draft   |
| 9  | Metrics Dashboard            | Weekly KPI table                      | `Lean_Loop_Metrics`                              | Metrics Snapshot       |
| 10 | Lean‑Loop Guide              | Onboarding cheat‑sheet                | `Lean_Loop_Guide`                                | Human reference        |

---

## **3 Naming Convention Reminder**

* **Dated artefacts:** `[TemplateName]_YYYY‑MM‑DD` (ISO‑8601).
* **Living artefacts:** `[TemplateName]_Current` (or no suffix).
  These patterns map directly to the glob selectors inside the Lean‑Loop workflow YAML.

---

## **4 Template Source Blocks**

> Copy the code block *including* the opening & closing back‑ticks into a new TIP document.

### 4.1 North‑Star Charter

```markdown
# North‑Star Charter
<-- 1‑page evergreen mission & 3‑year objectives -->

## Mission
-

## 3‑Year Objectives & KPIs
| Objective | KPI | Target by <YYYY‑MM> |
|-----------|-----|---------------------|
|

## Success Metrics Definition
- **Value Created:**
- **Quality Bar:**
- **Velocity Target:**

## Last Charter Review
<YYYY‑MM‑DD> — summary of changes
```

---

### 4.2 Working Backlog

```markdown
# Working Backlog  (rolling 12 weeks)
<-- Ordered so top = next work item -->

| Rank | Deliverable | Owner | Due | Status | Notes |
|------|-------------|-------|-----|--------|-------|
| 1 |  |  |  | ☐ To Do |  |
```

---

### 4.3 Decision Log

```markdown
# Decision Log
<-- When a consequential choice is made, add one row -->

| When (UTC) | What we decided | Why | Next Action | Link(s) |
|------------|-----------------|-----|-------------|---------|
|            |                 |     |             |         |
```

---

### 4.4 Prompt Packet

```markdown
# Prompt Packet {{CurrentDate}}
<-- Filled daily by the Coordinator -->

## Goal of the Day
-

## New Facts / Resources
-

## Questions Requiring Reasoning
1.

## Desired Output Format
Markdown bullets, ≤300 tokens

## Capacity / Constraints (optional)
| Person | Available hrs today | Key skills / notes |
|--------|--------------------|--------------------|
```

---

### 4.5 Daily Digest (14‑day rolling)

```markdown
# Daily Digest

<-- Coordinator pastes the 150‑token summary produced by the Digest Compressor.
Delete entries older than 14 days to keep the context small. -->

## {{CurrentDate}}
…
```

---

### 4.6 Prompt Library

```markdown
# Prompt Library
<-- Keep only prompts that scored ≥4/5 usefulness -->

| Tag | Prompt Snippet | Use Case | Last Success Date |
|-----|---------------|----------|-------------------|
```

---

### 4.7 Resource Vault

```markdown
# Resource Vault
<-- Curated links, datasets, style guides, credentials, etc. -->

## Docs & Specs
-

## Data Sources
-

## Style Guides / Reference
-
```

---

### 4.8 Capacity Snapshot (optional standalone)

```markdown
# Capacity Snapshot {{CurrentDate}}

| Person | Available hrs today | Key skills / notes |
|--------|--------------------|--------------------|
```

---

### 4.9 Metrics Dashboard

```markdown
# Lean‑Loop KPI Dashboard

| Week | Human minutes / deliverable | Accuracy (sample 5‑pt) | NASA‑TLX | Prompt reuse % |
|------|----------------------------|------------------------|----------|----------------|
|      |                            |                        |          |                |
```

---

### 4.10 Lean‑Loop Guide (Quick Ref)

```markdown
# Lean‑Loop Guide (Quick Reference)

## Daily at a Glance
1. Coordinator fills Prompt Packet (≤5 min).
2. Run **Generate LLM Draft** workflow.
3. Contributors comment 👍/👎 (async).
4. Run **Incorporate Comments** workflow.
5. Coordinator compresses into Daily Digest.

## Weekly at a Glance
- Monday Kick‑off (15 min sync).
- Friday Retro (LLM‑led, 10 min async).

## Artefact Locations
- Charter: `North_Star_Charter`
- Backlog: `Working_Backlog_Current`
- Decision Log: `Decision_Log`
- Digest: `Daily_Digest`
- Prompt Library: `Prompt_Library`
```

---

## **5 How to Import**

1. In TIP, click **Create Document → Paste Markdown**.
2. Name the document following the **Suggested File Name** column above.
3. Save. TIP’s versioning & permissions apply automatically.
