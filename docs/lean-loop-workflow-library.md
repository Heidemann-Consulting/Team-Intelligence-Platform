# **Lean‑Loop Workflow Library for Team Intelligence Platform (TIP)**

**Version:** 1.0
**Date:** May 14, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0
**Rituals & Practices Referenced:** [Lean‑Loop Rituals & Practices for TIP](./lean-loop-rituals-and-practices.md)
**Templates Library Referenced:** [Lean‑Loop Templates Library for TIP](./lean-loop-templates-library.md)

---

## **1 Purpose & Scope**

This library contains **ready‑to‑import YAML workflow definitions** for every cadence described in the *Lean‑Loop Rituals & Practices* document.
All workflow **names, glob‑patterns and output filenames** match those referenced in the Rituals guide and Templates Library, ensuring seamless linkage inside TIP’s execution engine (spec FR‑WFDEF‑003).

> **TIP YAML Schema Reminder** — required keys:
> `inputDocumentSelectors` (array), `outputName`, `prompt`.
> Optional keys: `inputDateSelector`, `model`, `temperature`, `maxTokens`.

---

## **2 Daily Workflows**

### 2.1 `Generate_LLM_Draft`

```yaml
inputDocumentSelectors:
  - "Prompt_Packet*"
  - "North_Star_Charter*"
  - "Working_Backlog_Current*"
  - "Daily_Digest*"
  - "Decision_Log*"
inputDateSelector: null
outputName: "LLM_Draft_{{CurrentDate}}"
prompt: |
  You are the **LLM Facilitator** for our Lean‑Loop team.

  ### Context
  <<<{{DocumentContext}}>>>

  ### Goals
  • Answer all items under **Questions Requiring Reasoning**.
  • Propose **Next‑Best‑Steps** ranked by ROI per human‑hour.

  ### Expected Sections
  1. **Draft** – coherent answer.
  2. **Risks** – bullet list of potential pitfalls.
  3. **Clarifying Questions** – what you still need.
  4. **👍‑Points / 👎‑Points** – self‑critique.
  5. **Next‑Best‑Steps** – top 3 actions with 1‑line rationales.

  ### Output Format
  Markdown only, ≤600 tokens.
  Prefix any uncertain statement with `(LOW‑CONF)`.
```

### 2.2 `Incorporate_Comments`

```yaml
inputDocumentSelectors:
  - "LLM_Draft*"
  - "Prompt_Packet*"
inputDateSelector: null
outputName: "LLM_Refined_{{CurrentDate}}"
prompt: |
  You are the **Reviser** responsible for integrating human feedback.

  ### Context
  <<<{{DocumentContext}}>>>

  ### Instructions
  1. Accept all inline 👍 comments and apply suggested edits.
  2. Ignore 👎 sections unless replacement text is provided.
  3. Compress the **Draft** section by ≈20 % while preserving meaning and bullet structure.
  4. Retain **Risks**, **Clarifying Questions**, and **Next‑Best‑Steps**.

  ### Output Format
  Markdown, ≤480 tokens.
```

### 2.3 `Digest_Compressor`

```yaml
inputDocumentSelectors:
  - "LLM_Refined*"
outputName: "Digest_{{CurrentDate}}"
prompt: |
  You are the **Daily Digest Writer**.

  ### Context
  <<<{{DocumentContext}}>>>

  ### Task
  Summarise the key insights, decisions and action items in **≤150 tokens**.

  ### Output Format
  Exactly three bullets followed by a **Next Action** line.
```

---

## **3 Weekly Workflows**

### 3.1 `Weekly_Kickoff`

```yaml
inputDocumentSelectors:
  - "Working_Backlog*"
  - "North_Star_Charter*"
  - "Daily_Digest*"
inputDateSelector: "olderThanDays 7"
outputName: "Backlog_Reprioritization_{{CurrentDate}}"
prompt: |
  You are the **Planning Analyst** preparing today’s Kick‑off.

  ### Context
  <<<{{DocumentContext}}>>>

  ### Objectives
  • Re‑rank the backlog for the coming week.
  • Estimate human vs LLM effort.
  • Surface scope‑creep risks.

  ### Output Format
  Sections – **Proposed Backlog** (ranked table), **Rationale**, **Risks**.
  Limit to ≤550 tokens.
```

### 3.2 `Retro_Analyzer`

```yaml
inputDocumentSelectors:
  - "Decision_Logv"
  - "LLM_Refined*"
inputDateSelector: "olderThanDays 7"
outputName: "Retro_Insights_Week_{{Year}}-W{{WeekNumber}}"
prompt: |
  You are the **Process Analyst**.

  ### Context
  <<<{{DocumentContext}}>>>

  ### Tasks
  1. Extract recurring **success** and **failure** patterns.
  2. Recommend the two highest‑ROI **process tweaks** (≤50 words each).
  3. Cite concrete examples (link‑style).

  ### Output Format
  Sections – **Patterns** / **Recommendations**.
```

---

## **4 Monthly Workflows**

### 4.1 `Metrics_Snapshot`

```yaml
inputDocumentSelectors:
  - "Decision_Log*"
  - "Daily_Digest*"
  - "LLM_Refined*"
inputDateSelector: "olderThanDays 30"
outputName: "Metrics_Snapshot_{{Year}}-{{Month}}"
prompt: |
  You are the **Metrics Auditor**.

  ### Context
  <<<{{DocumentContext}}>>>

  ### Tasks
  • Compute: Human‑minutes per deliverable, Accuracy (sample 10), NASA‑TLX average, Prompt reuse %.
  • Provide one‑paragraph commentary.

  ### Output Format
  Markdown table of the four metrics followed by commentary. ≤400 tokens.
```

### 4.2 `Context_Condensor`

```yaml
inputDocumentSelectors:
  - "Daily_Digest*"
  - "Decision_Log*"
inputDateSelector: "olderThanDays 30"
outputName: "Condensed_Context_{{Year}}-{{Month}}"
prompt: |
  You are the **Context Librarian**.

  ### Context
  <<<{{DocumentContext}}>>>

  ### Goal
  Produce a concise summary ≤1 500 tokens that preserves:
  • Key decisions, reasons, outcomes.
  • Enduring lessons learned.
  • Links to artefacts still required.

  ### Output Format
  Sections – **Decisions**, **Lessons Learned**, **Archived Links**.
```

---

## **5 Quarterly / Annual Workflows**

### 5.1 `Quarterly_Strategy_Review`

```yaml
inputDocumentSelectors:
  - "North_Star_Charter*"
  - "Metrics_Snapshot*"
  - "Working_Backlog*"
  - "Condensed_Context*"
inputDateSelector: "olderThanDays 90"
outputName: "Strategy_Review_{{Year}}-Q{{Quarter}}"
prompt: |
  You are the **Strategy Review Facilitator**.

  ### Context
  <<<{{DocumentContext}}>>>

  ### Tasks
  1. Evaluate KPI trajectory vs 3‑year objectives.
  2. Identify ≤3 strategic gaps or opportunities.
  3. Draft updated **OKRs** for the next quarter.
  4. Suggest backlog deletions or de‑prioritisations.

  ### Output Format
  – **Executive Summary** (≤120 words)
  – **Proposed OKRs** (table)
  – **Backlog Changes** (bullets)
```

---

## **6 Import Checklist**

1. TIP Admin ⇒ **Workflows → “Import YAML”**. Paste each block above exactly as shown.
2. Verify that your document names match the **inputDocumentSelectors**.
3. Test each cadence on a sandbox team before production roll‑out.
