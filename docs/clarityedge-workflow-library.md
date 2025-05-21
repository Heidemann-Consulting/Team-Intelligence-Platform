## Step 3 — ClarityEdge ™ Workflow Library

*All workflows are created by an **Administrator** in TIP’s “Process Workflows” section.
Each definition follows the YAML-like schema that TIP validates (`inputDocumentSelectors`, `inputDateSelector` optional, `outputName`, `prompt`).*&#x20;

**Version:** 1.0
**Date:** May 17, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

---

### 3.1 ClarityEdge – Goal\_Definition\_to\_Strategy\_Map

```yaml
# Converts a fresh Goal Definition into a one-page Strategy Map
inputDocumentSelectors:
  - "Goal Definition*"
inputDateSelector: "olderThanDays 0"    # only today’s or newer
outputName: "Strategy Map {{InputFileName}} {{Year}}-{{Month}}-{{Day}}"
prompt: |
  {{DocumentContext}}

  You are a senior strategy consultant. Translate the single-tweet goal above into a concise Strategy Map
  that shows 🔹Objectives ▸ 🔸Key Results ▸ 🔹Initiatives.
  • Use a Markdown table with three columns (Objective, Key Result, Initiative).
  • Re-use Success Criteria metrics verbatim.
  • Add at most 3 Initiatives per Objective.
  • Finish with a 50-word risk note.
  Before final answer, self-rate Completeness & Clarity 0-10; if any score < 9 improve and rerate.
```

*Runtime*: ≤ 1 min LLM, ≤ 2 min human review
*Roles*: Contributor triggers; Lead approves

---

### 3.2 ClarityEdge – Task\_Brief\_to\_AI\_Prompt

```yaml
# Builds a production-ready prompt from a Task Brief
inputDocumentSelectors:
  - "Task Brief*"
outputName: "AI Prompt for {{InputFileName}}"
prompt: |
  {{DocumentContext}}

  Fill the **AI Prompt Scaffold** precisely, optimised for a 30 B local reasoning model (2 k token budget).
  • Use the Task Brief fields to populate each scaffold block.
  • Compress any linked snippets to ≤ 500 tokens total.
  • Keep temperature comments out of the final prompt (handled globally).
  Append the filled scaffold only, nothing else.
```

*Runtime*: LLM ≤ 30 s, human skim ≤ 1 min
*Downstream workflow*: **AI\_Prompt\_to\_Draft** consumes the output “AI Prompt for …” document.

---

### 3.3 ClarityEdge – AI\_Prompt\_to\_Draft

```yaml
# Generates first-pass content from an AI Prompt
inputDocumentSelectors:
  - "AI Prompt for *"
outputName: "Draft {{InputFileName}} {{Year}}-{{Month}}-{{Day}}"
prompt: |
  {{DocumentContext}}

  Execute the embedded prompt.
  Then:
  1. Reflect on potential gaps in ≤ 80 words.
  2. Improve the draft until self-ratings ≥ 9 on Completeness & Clarity.
  Provide only the final draft (no reflections) in Markdown.
```

*Runtime*: LLM ≤ 2 min, human review ≤ 5 min

---

### 3.4 ClarityEdge – Draft\_to\_Final\_Asset

```yaml
# Polishes a draft into publishable output
inputDocumentSelectors:
  - "Draft *"
outputName: "Final {{InputFileName}}"
prompt: |
  {{DocumentContext}}

  You are an expert copy-editor. Elevate style, tighten structure, and ensure it meets all Acceptance Criteria
  from the originating Task Brief (quote them inline).
  Run a self-critique checklist (grammar, logical flow, tone consistency) and fix issues before output.
  Return only the polished Markdown asset.
```

*Runtime*: LLM ≤ 1 min, Lead approval ≤ 3 min

---

### 3.5 ClarityEdge – Meeting\_Notes\_to\_Summary

```yaml
# Creates an actionable meeting summary
inputDocumentSelectors:
  - "Meeting Notes*"
outputName: "Meeting Summary {{InputFileName}}"
prompt: |
  {{DocumentContext}}

  Produce:
  1. 120-word narrative summary
  2. Decisions table (Decision ▸ Owner ▸ Rationale)
  3. Action Items table (Action ▸ Owner ▸ Due)
  4. Suggested Progressive Summary block (≤ 200 tokens) ready for the next workflow.
```

*Runtime*: LLM 30 s, human post-send 1 min

---

### 3.6 ClarityEdge – AnyDoc\_to\_Progressive\_Summary

```yaml
# Compresses any long document into a token-lean memory
inputDocumentSelectors:
  - "*"
outputName: "Progressive Summary {{InputFileName}}"
prompt: |
  {{DocumentContext}}

  Summarise each top-level heading in ≤ 50 words.
  Output using the **Progressive Summary** template (leave placeholders where no content).
  If document < 400 words, abort with message “No summary needed”.
```

*Usage note*: Trigger from a single open document to avoid multi-match selection.

---

### 3.7 ClarityEdge – Checkin\_to\_Daily\_Summary

```yaml
# Rolls up team check-ins into one digest
inputDocumentSelectors:
  - "Daily Check-in*"
inputDateSelector: "between_{{CurrentDate}}_{{CurrentDate}}"
outputName: "Daily Summary {{CurrentDate}}"
prompt: |
  {{DocumentContext}}

  Combine all check-ins into:
  • Highlights (bullet list ≤ 5)
  • Blockers with suggested mitigations
  • AI Task queue graph (Markdown table)
  Finish with “#End”.
```

*Runtime*: LLM 20 s, team read 30 s

---

### 3.8 ClarityEdge – Retrospective\_to\_Improvement\_Actions

```yaml
# Extracts concrete follow-ups from a Retrospective
inputDocumentSelectors:
  - "Retrospective*"
outputName: "Improvement Actions {{InputFileName}}"
prompt: |
  {{DocumentContext}}

  List each “What should we try next?” item as an Improvement Action (Action ▸ Owner ▸ Expected Impact ▸ Due).
  Discard duplicates, group by theme.
  Output Markdown table only.
```

---

### 3.9 ClarityEdge – Decision\_Record\_to\_Log

```yaml
# Appends structured decisions into the annual log
inputDocumentSelectors:
  - "Decision Record*"
outputName: "Decision Log {{Year}}"
prompt: |
  Current Log (if any): {{ExistingDocument "Decision Log {{Year}}" | default="(none)"}}

  New Decision:
  {{DocumentContext}}

  Append the decision as a new row in a Markdown table (Date ▸ Title ▸ Owner ▸ Rationale ▸ Review Date).
  Return the full updated table.
```

*TIP will version the updated log automatically.*

---

### 3.10 ClarityEdge – Workflow\_Auto\_Metrics\_to\_Log

```yaml
# (System hook) records runtime + token metrics
inputDocumentSelectors:
  - "{{InputFileName}}"                # the document just produced
outputName: "Metrics Entry {{WorkflowName}} {{CurrentDate}}T{{CurrentTime}}"
prompt: |
  {{WorkflowName}} finished.
  Runtime: {{RuntimeSeconds}} s
  Tokens In: {{TokensIn}}
  Tokens Out: {{TokensOut}}
  Human Minutes Saved: “{{HumanMinutesSaved}}”
  Create a one-line CSV ready to be appended to Metrics Log.
```

*Called automatically at the end of every other workflow; yields a tiny doc that later feeds a SQL-style dashboard.*

---

### Inter-Workflow Map

| Upstream Output                           | Downstream Workflow(s)                                                                           |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Goal Definition** → *Strategy Map*      | —                                                                                                |
| **Strategy Map**                          | Manually feeds Task creation (outside workflow scope)                                            |
| **Task Brief** → *AI Prompt*              | **Task\_Brief\_to\_AI\_Prompt**                                                                  |
| **AI Prompt** → *Draft*                   | **AI\_Prompt\_to\_Draft**                                                                        |
| **Draft** → *Final*                       | **Draft\_to\_Final\_Asset**                                                                      |
| **Meeting Notes** → *Meeting Summary*     | **Meeting\_Notes\_to\_Summary** → *Progressive Summary* via **AnyDoc\_to\_Progressive\_Summary** |
| **Daily Check-in** → *Daily Summary*      | **Checkin\_to\_Daily\_Summary**                                                                  |
| **Retrospective** → *Improvement Actions* | **Retrospective\_to\_Improvement\_Actions**                                                      |
| **Decision Record** → *Decision Log*      | **Decision\_Record\_to\_Log**                                                                    |
| Every Workflow                            | **Workflow\_Auto\_Metrics\_to\_Log**                                                             |

---

### Governance & Quality Gates

* **Validation** – Each prompt block includes self-rating; humans approve final docs.
* **Token Discipline** – Upstream summaries keep inputs ≤ 2 k tokens for 30 B model limits.
* **Traceability** – Output names embed source doc or year; Metrics workflow provides auditable data.
* **Time-ROI** – No human step exceeds the 30-minute daily cap; most actions are 1–5 minutes.

> **Next:** Step 4 will describe rituals & practices that knit these templates and workflows into everyday team life.
