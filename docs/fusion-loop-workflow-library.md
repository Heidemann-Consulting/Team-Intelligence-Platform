# **Fusion‑Loop Workflow Library for Team Intelligence Platform (TIP)**

**Version:** 1.0
**Date:** May 17, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0
**Templates Library Referenced:** [Fusion‑Loop Templates Library](./fusion-loop-templates-library.md)

---

## **Table of Contents**

1. [Purpose & Design Principles](#1-purpose--design-principles)
2. [Daily Workflows](#2-daily-workflows)
3. [Weekly Workflows](#3-weekly-workflows)
4. [Monthly Workflows](#4-monthly-workflows)
5. [Quarterly & Annual Workflows](#5-quarterly--annual-workflows)
6. [Import Checklist](#6-import-checklist)

---

## 1 Purpose & Design Principles

This library provides **ready‑to‑import YAML workflow definitions** for every cadence of the *Fusion‑Loop* process.  All definitions reuse the **exact same syntax elements** found in the Lean‑Loop and LACM libraries – namely the TIP keys `inputDocumentSelectors`, `inputDateSelector`, `outputName`, and `prompt` – ensuring compatibility with TIP’s existing execution engine (see Lean‑Loop spec FR‑WFDEF‑003 citeturn4file11).

Core ideas:

* **Lean‑style Guardrails** – mandatory *Risks* & *👍/👎* self‑critique sections.
* **LACM‑style Context Breadth** – external news & strategy checks baked in.
* **Two‑tier Model Use** is handled by admins; the YAML here stays model‑agnostic.

---

## 2 Daily Workflows

### 2.1 `Fusion_DailyNewsAnalysis`

Derived from `LACM_Workflow_DailyNewsAnalysis` citeturn5file7.  It filters an *auto‑collected* or manually curated feed to the three most relevant items for today.

```yaml
inputDocumentSelectors:
  - "Fusion_ExternalFeed_*"   # Raw RSS/API import or manual paste
  - "North_Star_Charter*"     # Optional, for mission anchor
  - "Working_Backlog*" # Optional, to gauge immediate impact
inputDateSelector: null
outputName: "Fusion_DailyNewsAnalysis_{{CurrentDate}}"
prompt: |
  You are an **AI News Analyst**.
  ### Context
  <<<{{DocumentContext}}>>>
  ### Task
  1. Select the **top‑3** feed items most likely to influence today’s decisions.
  2. For each item add *Key Point* and *Relevance* (≤ 40 words).
  3. Prefix urgent items with `FLAG: IMPORTANT –`.
  ### Format
  Markdown bullets only; ≤ 220 tokens.
```

### 2.2 `Generate_LLM_Draft_Fusion`

Lean‑Loop’s original `Generate_LLM_Draft` with an extra feed hook citeturn4file0.

```yaml
inputDocumentSelectors:
  - "Prompt_Packet*"
  - "Fusion_DailyNewsAnalysis_*"
  - "North_Star_Charter*"
  - "Working_Backlog*"
  - "Fusion_Daily_Digest*"
inputDateSelector: null
outputName: "LLM_Draft_{{CurrentDate}}"
prompt: |
  You are the **LLM Facilitator**.
  ### Context
  <<<{{DocumentContext}}>>>
  ### Goals
  • Answer all *Open Questions*.
  • Propose **Next‑Best Steps** ranked by ROI/human‑hour.
  ### Mandatory Sections
  1. **Draft**
  2. **Risks**
  3. **Clarifying Questions**
  4. **👍‑Points / 👎‑Points** (self‑critique)
  5. **Next‑Best Steps** (max 3)
  Markdown ≤ 600 tokens; mark low‑confidence statements `(LOW‑CONF)`.
```

### 2.3 `Incorporate_Comments_Fusion`

Identical structure to Lean‑Loop’s `Incorporate_Comments` citeturn4file0.

```yaml
inputDocumentSelectors:
  - "LLM_Draft_*"
  - "Prompt_Packet*"
inputDateSelector: null
outputName: "LLM_Refined_{{CurrentDate}}"
prompt: |
  You are the **Reviser**.
  <<<{{DocumentContext}}>>>
  Apply 👍 suggestions, ignore 👎 unless replacement text provided, then compress **Draft** by ≈ 20 %.  Keep **Risks** & **Next‑Best Steps** intact.  ≤ 480 tokens.
```

### 2.4 `Digest_Compressor_Fusion`

Same as Lean‑Loop’s daily condensor citeturn4file0.

```yaml
inputDocumentSelectors:
  - "LLM_Refined_*"
outputName: "Fusion_Daily_Digest_{{CurrentDate}}"
prompt: |
  You are the **Daily Digest Writer** – produce a 150‑token summary, list blockers & decisions.
```

---

## 3 Weekly Workflows

### 3.1 `Weekly_Trend_Summary`

Adapted from `LACM_Workflow_WeeklyAnalysis` citeturn5file11.

```yaml
inputDocumentSelectors:
  - "Fusion_DailyNewsAnalysis_*"   # Past 7 days
  - "Fusion_Daily_Digest_*"        # Past 7 days
  - "North_Star_Charter*"
inputDateSelector: "olderThanDays 7"
outputName: "Weekly_Trend_{{Year}}-W{{WeekNumber}}"
prompt: |
  You are an **AI Trend Synthesizer**.
  ### Context
  <<<{{DocumentContext}}>>>
  ### Produce
  • Top 3–5 internal + external trends.
  • Potential impact on KPIs.
  • Two discussion points for Monday Kick‑off.  ≤ 550 tokens.
```

### 3.2 `Weekly_Kickoff_Fusion`

Straight reuse of Lean‑Loop `Weekly_Kickoff` citeturn5file19; extra selector to pull the new trend doc.

```yaml
inputDocumentSelectors:
  - "Working_Backlog*"
  - "North_Star_Charter*"
  - "Weekly_Trend_*"
inputDateSelector: "olderThanDays 7"
outputName: "Backlog_Reprioritization_{{CurrentDate}}"
prompt: |
  (Same prompt as Lean‑Loop Weekly_Kickoff.)
```

### 3.3 `Retro_Analyzer_Fusion`

Unchanged from Lean‑Loop citeturn5file19.

### 3.4 `Weekly_Plan_Preview`

Uses `LACM_Workflow_WeeklyPlanPreviewGenerator` pattern citeturn3file15; provides next‑week outlook.

```yaml
inputDocumentSelectors:
  - "Weekly_Trend_*"
  - "Retro_Insights_*"
  - "North_Star_Charter*"
inputDateSelector: null
outputName: "Weekly_Plan_Preview_{{Year}}-W{{WeekNumber}}"
prompt: |
  Draft a high‑level plan for Week {{WeekNumber}} aligning backlog, trends & retro findings.  Use table: *Rank / Item / Rationale / Owner*.
```

---

## 4 Monthly Workflows

### 4.1 `Fusion_StrategyAlignment`

Hybrid of LACM’s monthly strategy check citeturn5file17 and Lean‑Loop guardrails.

```yaml
inputDocumentSelectors:
  - "Weekly_Trend_*"
  - "Condensed_Context_*"
  - "North_Star_Charter*"
  - "Working_Backlog*"
inputDateSelector: "olderThanDays 30"
outputName: "Fusion_StrategyAlignment_{{Year}}-{{Month}}"
prompt: |
  You are the **Strategy Alignment Analyst**.
  <<<{{DocumentContext}}>>>
  1. Summarise KPI deltas (table).
  2. Flag gaps to Charter (≤3).
  3. Recommend backlog shifts.
  4. Append *Risks* & self‑👍/👎.  ≤ 700 tokens.
```

### 4.2 `Metrics_Snapshot_Fusion`

Alias of Lean‑Loop `Metrics_Snapshot` citeturn5file1.

### 4.3 `Context_Condensor_Fusion`

Alias of Lean‑Loop `Context_Condensor` citeturn5file1.

---

## 5 Quarterly & Annual Workflows

### 5.1 `Quarterly_Strategy_Review_Fusion`

Directly inherits Lean‑Loop definition citeturn5file1.

### 5.2 `Innovation_Idea_Generation_Fusion`

Borrowed from `LACM_Workflow_InnovationIdeaGeneration` citeturn5file4 to feed longer‑range planning.

```yaml
inputDocumentSelectors:
  - "Fusion_StrategyAlignment_*"
  - "Competitors*"           # If maintained
  - "CustomerFeedback_*"
  - "IdeaBacklog*"
inputDateSelector: null
outputName: "Fusion_Innovation_Ideas_Q{{Quarter}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  Generate 5–10 innovation ideas not in current backlog; cite triggering doc in each bullet.
```

---

## 6 Import Checklist

1. TIP Admin → **Workflows → “Import YAML”** and paste each block above exactly.
2. Ensure your document names match the `inputDocumentSelectors` patterns.
3. Test each cadence in a sandbox team before production.

---

*End of Fusion‑Loop Workflow Library*
