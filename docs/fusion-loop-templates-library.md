# Fusion‑Loop Templates Library

**Version:** 1.0
**Date:** May 17, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

---

## About This Library

This document collects **all canonical templates** required to operate the *Fusion‑Loop* workflow. Each template follows three principles:

1. **Self‑contained** – can be copied into any TIP vault without external dependencies.
2. **Human‑first** – first line explains purpose; inline comments clarify intent.
3. **LLM‑friendly** – consistent front‑matter & section markers for automated parsing.

For every artifact you will find:

* **Filename pattern**
* **Purpose**
* **Markdown or CSV skeleton**
* **TIP workflow linkage** (➡️ which YAML injects the file)

Use these blueprints *as‑is* or fork them to match your conventions.

---

## 0. Naming Conventions

| Scope   | Pattern                           | Example                               |
| ------- | --------------------------------- | ------------------------------------- |
| Daily   | `Fusion_<Artifact>_YYYY‑MM‑DD.md` | `Fusion_Daily_Digest_2025‑05‑16.md`   |
| Weekly  | `Fusion_<Artifact>_YYYY‑KW.md`    | `Weekly_Trend_2025‑KW20.md`           |
| Monthly | `Fusion_<Artifact>_YYYY‑MM.md`    | `Fusion_StrategyAlignment_2025‑05.md` |
| Global  | `North_Star_Charter.md`           | —                                     |

---

## 1. Daily Ritual Templates

### 1.1 `Prompt_Packet_Daily.md`

```markdown
<!-- Fusion‑Loop · Daily Prompt Packet -->
<!-- PURPOSE: Provide the LLM with the minimal hot‑context needed for the daily cycle. -->
---
artifact: Prompt_Packet_Daily
run_date: {{DATE}}
coordinator: {{NAME}}
---

#### 1 · Objectives for Today
- _e.g._  Finish user‑story #123, clarify API rate limits.

#### 2 · Open Questions
1. *What is the latest blocker on feature X?*
2. *Which KPI is lagging >10 %?*

#### 3 · New Facts (auto‑import from External Feed)
<!-- injected by External Feed Picker → top‑3 bullets max -->
- {{FACT1}}
- {{FACT2}}
- {{FACT3}}

> **Guidelines:** Keep ≤ 150 tokens; link to source doc if long.
```

---

### 1.2 `Fusion_Daily_Digest_YYYY‑MM‑DD.md`

```markdown
<!-- Fusion‑Loop · Daily Digest (150 tokens target) -->
---
artifact: Fusion_Daily_Digest
source_prompt: {{PROMPT_PACKET_LINK}}
created_by: {{LLM_MODEL}} v{{VERSION}}
qa_status: pending
---

**Timeline Summary**
> *Auto‑generated*: Concise narrative of today’s progress, key decisions, blockers.

**Risks & Uncertainties**
- …

**Next‑Best Steps**
1. …
2. …

**LLM Self‑Critique**
👍 Confidence: _High/Medium/Low_
👎 Potential failure modes: _…_
```

---

### 1.3 `Fusion_ExternalFeed_YYYY‑MM‑DD.md`

```markdown
<!-- Fusion‑Loop · External Feed – Raw Import -->
---
artifact: Fusion_ExternalFeed
collected_via: rss‑bot v0.3
fetched_at: {{TIMESTAMP}}
---

| # | Headline | One‑Sentence Impact | Source |
|---|----------|--------------------|--------|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |

> *Down‑stream workflow `FeedPickerDaily` selects the top‑3 items into the Prompt Packet.*
```

---

## 2. Weekly Ritual Templates

### 2.1 `Weekly_Kickoff_YYYY‑KW.md`

```markdown
<!-- Fusion‑Loop · Weekly Kick‑off Pack -->
---
artifact: Weekly_Kickoff
week: {{YYYY‑KW}}
---

#### Snapshot KPIs (auto‑pull from Fusion_Metrics)
| KPI | Target | Last Wk | Trend |
|-----|--------|---------|-------|
| …   | …      | …       | …     |

#### Goals for the Week
- …

#### Open Risks from Last Retro
- …
```

### 2.2 `Weekly_Trend_YYYY‑KW.md`

```markdown
<!-- Fusion‑Loop · Weekly Trend Résumé (≤ 400 tokens) -->
---
artifact: Weekly_Trend
inputs:
  - Fusion_Daily_Digest_*
  - Fusion_ExternalFeed_*
---

**Internal Patterns**
- …

**External Signals**
- …

**LLM Self‑Critique**
👍 Confidence: …
👎 Weak signals not yet validated: …
```

### 2.3 `Weekly_Retro_YYYY‑KW.md`

```markdown
<!-- Fusion‑Loop · Team Retrospective -->
---
artifact: Weekly_Retro
facilitator: {{NAME}}
method: Start/Stop/Continue
---

| What to **Start**        | **Stop**                 | **Continue**            |
|--------------------------|--------------------------|-------------------------|
|                          |                          |                         |

**Action Items**
1. …
```

---

## 3. Monthly Ritual Templates

### 3.1 `Fusion_StrategyAlignment_YYYY‑MM.md`

```markdown
<!-- Fusion‑Loop · Monthly Strategy Alignment -->
---
artifact: Fusion_StrategyAlignment
month: {{YYYY‑MM}}
model: gpt‑4o‑128k
context:
  - North_Star_Charter
  - Working_Backlog_Current
  - Weekly_Trend_*
  - Condensed_Context_*
---

#### Executive Summary (≤ 250 tokens)
…

#### KPI Delta Analysis
| KPI | Target | Actual | Delta | Root Cause |
|-----|--------|--------|-------|-----------|
|     |        |        |       |           |

#### Strategic Gaps & Opportunities
1. …

#### Recommendations
- …

**LLM Self‑Critique**
👍 Assumptions explicit: …
👎 Blind spots: …
```

### 3.2 `Condensed_Context_YYYY‑MM.md`

```markdown
<!-- Fusion‑Loop · Monthly Condensor Output (≤ 3 % tokens of source) -->
---
artifact: Condensed_Context
source_range: {{YYYY‑MM‑01}} – {{YYYY‑MM‑31}}
method: "Compression > Deletion"
---

> *Chunked summary produced by Condensor workflow. Human editable.*
```

---

## 4. Quarterly / Global Templates

### 4.1 `North_Star_Charter.md`

```markdown
<!-- Fusion‑Loop · Multi‑year Mission Charter -->
---
artifact: North_Star_Charter
owner: {{EXEC_SPONSOR}}
rev: {{YYYY‑Qn}}
---

**Mission Statement**
> …

**3‑Year Objectives**
1. …

**Key Metrics (North‑Star KPIs)**
| KPI | Definition | Baseline | 3‑Year Target |
|-----|------------|----------|---------------|
|     |            |          |               |

**Guardrails**
- …
```

### 4.2 `Working_Backlog_Current.md`

```markdown
<!-- Fusion‑Loop · Rolling 12‑Week Backlog -->
---
artifact: Working_Backlog_Current
updated: {{DATE}}
---

| Rank | Epic / User Story | Est. Effort | Owner | Status | Due By |
|------|-------------------|-------------|-------|--------|--------|
| 1    |                   |             |       |        |        |
```

---

## 5. Metrics & Logs

### 5.1 `Decision_Log.md`

```markdown
<!-- Fusion‑Loop · Atomic Decision Log (append‑only) -->
| Timestamp | Title | Category | Decision | Rationale | Link to Evidence |
|-----------|-------|----------|----------|-----------|------------------|
```

### 5.2 `Fusion_Metrics.csv`

```csv
# Fusion‑Loop · Ops Metrics (machine‑readable)
period,kpi,value,unit,source
2025‑05‑16,time_spent_daily,28,minutes,StopwatchBot
2025‑05‑16,token_usage,12.4,USD,OpenAI
…
```

---

## 6. Workflow YAML Examples

### 6.1 `workflow/DailyLoop.yaml`

```yaml
name: Fusion Daily Loop
triggers:
  schedule: "0 8 * * *"  # 08:00 local
jobs:
  fetch_feed:
    uses: rss‑bot@v0.3
  pick_top3:
    uses: FeedPickerDaily@v1
    needs: fetch_feed
  generate_draft:
    uses: LocalLLM@v1
    with:
      prompt: Prompt_Packet_Daily.md
  self_critique:
    uses: LocalLLM@v1
    needs: generate_draft
    with:
      system_prompt: "Add Risks & 👍/👎"
  commit_digest:
    uses: DigestWriter@v2
    needs: self_critique
```

### 6.2 `workflow/WeeklyTrend.yaml`

```yaml
name: Weekly Trend Synthesis
on:
  schedule:
    - cron: "0 16 * * FRI"
jobs:
  aggregate:
    uses: LocalLLM@v1
    with:
      inputs: [Fusion_Daily_Digest_*, Fusion_ExternalFeed_*]
```

### 6.3 `workflow/StrategyAlignment.yaml`

```yaml
name: Monthly Strategy Alignment
on:
  schedule:
    - cron: "0 10 1 * *"  # first day monthly
jobs:
  align:
    uses: BigLLM128k@cloud
    with:
      context_files:
        - North_Star_Charter.md
        - Working_Backlog_Current.md
        - Weekly_Trend_*
        - Condensed_Context_*
```

### 6.4 `workflow/Condensor.yaml`

```yaml
name: Monthly Condensor
on:
  manual:
    inputs:
      month: {required: true}
jobs:
  condense:
    uses: LocalLLM@v1
    with:
      compression_ratio: 0.03
```

---

## 7. Glossary

| Term                     | Meaning                                                                   |
| ------------------------ | ------------------------------------------------------------------------- |
| **Hot‑Context**          | Latest working set (≤ 4 K tokens) always provided to the local LLM.       |
| **Self‑Critique**        | Explicit Risks & Confidence section appended by the LLM itself.           |
| **Condensor**            | Automated summarisation process using "Compression > Deletion" principle. |
| **External Feed Picker** | Script selecting top‑3 external headlines for the Prompt Packet.          |
| **StopwatchBot**         | CLI that logs ritual time into Fusion\_Metrics.csv.                       |

---

*End of Library*
