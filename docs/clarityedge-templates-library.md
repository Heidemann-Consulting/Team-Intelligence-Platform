## Step 2 — ClarityEdge ™ Template Library

*(All templates are Markdown files. Each file begins with an HTML comment that TIP uses as metadata. Replace every `{{…}}` placeholder before saving a live document.)*

**Version:** 1.0
**Date:** May 17, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0


---

### 1. **ClarityEdge – Goal Definition**

```markdown
<!--
Template: ClarityEdge – Goal Definition
Version: 1.0
Updated: 2025-05-17
Compatible_Workflow: Goal_Definition_to_Strategy_Map
-->

# 🎯  Goal Definition

**Owner:** {{Name}}  **Date Created:** {{YYYY-MM-DD}}

## 1. Objective
Describe, in one tweet (≤ 280 chars), the single most important result you want.

> {{Goal_Statement}}

## 2. Success Criteria (SMART)
| # | Metric | Baseline | Target | Deadline |
|---|--------|----------|--------|----------|
| 1 | {{}} | {{}} | {{}} | {{}} |
| 2 | {{}} | {{}} | {{}} | {{}} |

## 3. Background & Context
Summarise why this matters and relevant prior facts (≤ 150 words).
{{Background}}

## 4. Stakeholders & Roles
| Role | Person | Responsibility | Daily Time-box |
|------|--------|----------------|---------------|
| Lead | {{}} | {{}} | 10 min |
| Contributor(s) | {{}} | {{}} | 15 min |
| AI Liaison | {{}} | {{}} | 5 min |

## 5. Constraints & Risks
- {{Constraint_1}}
- {{Risk_1}}

## 6. Links
- Source Docs: {{URL-or-TIP-link}}
- Related Decisions: {{}}

<!-- QC:
- Goal fits in one tweet
- ≥ 2 quantitative metrics
- Total reading time < 3 min
-->
```

---

### 2. **ClarityEdge – Task Brief**

```markdown
<!--
Template: ClarityEdge – Task Brief
Version: 1.0
Updated: 2025-05-17
Compatible_Workflow: Task_Brief_to_AI_Prompt
-->

# 📌  Task Brief — {{Task_Name}}

| Field | Content |
|-------|---------|
| **Origin Goal** | {{Goal_Definition_Title}} |
| **Desired Output** | {{e.g., “One-page strategy map (Markdown)”}} |
| **Primary Audience** | {{Who will consume the output?}} |
| **Deadline** | {{YYYY-MM-DD HH:MM}} |
| **Owner** | {{Name}} |
| **Reviewers** | {{Names}} |

## Inputs Provided
- {{File_or_Link_1}}
- {{Snippet_Ref_1}}

## Acceptance Criteria
1. {{}}
2. {{}}

## Time Budget
⚡ Total human input ≤ 30 min (this brief + reviews).

<!-- QC:
- Acceptance criteria measurable
- Time budget respected
-->
```

---

### 3. **ClarityEdge – AI Prompt Scaffold**

````markdown
<!--
Template: ClarityEdge – AI Prompt Scaffold
Version: 1.0
Updated: 2025-05-17
Compatible_Workflow: AI_Prompt_to_Draft
-->

**Role**
You are a seasoned {{Discipline}} advisor with deep knowledge in {{Domain}}.

**Objective**
Generate a {{Output_Type}} that meets the Task Brief.

**Context**
Project goal: {{Goal_Statement}}
Key facts (bullet IDs only): {{Fact_IDs}}

**Inputs**
<copy-here any snippets, links or tables ≤ 500 tokens>

**Task-Steps**
1. Analyse relevance of each fact.
2. Draft output structure.
3. Populate with evidence.
4. Self-critique and improve.

**Output Format**
Provide **only**:
```markdown
# {{Title}}

{{Body}}

````

**Quality-Checklist**

* Completeness (0-10): *?*
* Clarity (0-10): *?*
  If any score < 9, improve and re-rate before finalising.

<!-- QC:
- All 7 blocks present
- Token count guideline obeyed
-->

````

---

### 4. **ClarityEdge – Daily Check-in**

```markdown
<!--
Template: ClarityEdge – Daily Check-in
Version: 1.0
Updated: 2025-05-17
Compatible_Workflow: Checkin_to_Daily_Summary
-->

# 🔄  Daily Check-in — {{Date}}

## 1. Yesterday’s Key Outcomes
- {{}}

## 2. Today’s Focus (max 3)
1. {{}}
2. {{}}
3. {{}}

## 3. Blockers / Needs
- {{}}

## 4. AI Tasks Queued
| # | Task Brief | Prompt ID |
|---|------------|-----------|
| 1 | {{}} | {{}} |

<!-- QC:
- ≤ 5 mins to fill
- No section left blank
-->
````

---

### 5. **ClarityEdge – Meeting Notes**

```markdown
<!--
Template: ClarityEdge – Meeting Notes
Version: 1.0
Updated: 2025-05-17
Compatible_Workflow: Meeting_Notes_to_Summary
-->

# 📝  Meeting Notes — {{Topic}} ({{YYYY-MM-DD}})

**Attendees:** {{List}}
**Facilitator:** {{Name}}
**Duration:** {{Start-End}}

## Agenda & Discussion Highlights
1. {{}}
2. {{}}

## Decisions Made
| # | Decision | Owner |
|---|----------|-------|
| 1 | {{}} | {{}} |

## Action Items
| # | Action | Owner | Due |
|---|--------|-------|-----|
| 1 | {{}} | {{}} | {{}} |

<!-- QC:
- Every decision has an owner
- Notes ≤ 300 words
-->
```

---

### 6. **ClarityEdge – Progressive Summary**

```markdown
<!--
Template: ClarityEdge – Progressive Summary
Version: 1.0
Updated: 2025-05-17
Compatible_Workflow: AnyDoc_to_Progressive_Summary
-->

# 🗂️  Progressive Summary — {{Source_Doc_Title}}

> **Purpose:** Maintain a compressed, living memory of the source document for token-efficient reuse.

| Section | 50-Word Summary |
|---------|-----------------|
| {{1}} | {{}} |
| {{2}} | {{}} |

_Last updated {{YYYY-MM-DD HH:MM}}_

<!-- QC:
- Each summary ≤ 50 words
- Updated timestamp present
-->
```

---

### 7. **ClarityEdge – Decision Record**

```markdown
<!--
Template: ClarityEdge – Decision Record
Version: 1.0
Updated: 2025-05-17
Compatible_Workflow: Decision_Record_to_Log
-->

# ✅  Decision Record — {{Title}}

| Field | Entry |
|-------|-------|
| **Context** | {{What problem / opportunity?}} |
| **Options Considered** | {{1-2 sentence list}} |
| **Decision** | {{Chosen option}} |
| **Rationale** | {{Why?}} |
| **Date** | {{YYYY-MM-DD}} |
| **Owner** | {{Name}} |
| **Review Date** | {{YYYY-MM-DD}} |

## Expected Impact
- {{Bullet 1}}
- {{Bullet 2}}

<!-- QC:
- Rationale explains “why not” for alternatives
- Review date ≤ 6 months ahead
-->
```

---

### 8. **ClarityEdge – Retrospective**

```markdown
<!--
Template: ClarityEdge – Retrospective
Version: 1.0
Updated: 2025-05-17
Compatible_Workflow: Retro_to_Improvement_Actions
-->

# 🔍  Retrospective — {{Period}}

| Prompt | Notes |
|--------|-------|
| **What went well?** | {{}} |
| **What didn’t?** | {{}} |
| **What should we try next?** | {{}} |

### Improvement Actions
| # | Action | Owner | Due |
|---|--------|-------|-----|
| 1 | {{}} | {{}} | {{}} |

<!-- QC:
- At least 1 action item
- Doc fits on one screen
-->
```

---

### 9. **ClarityEdge – Metrics Log**

```markdown
<!--
Template: ClarityEdge – Metrics Log
Version: 1.0
Updated: 2025-05-17
Compatible_Workflow: Workflow_Auto_Metrics_to_Log
-->

# 📊  Metrics Log

| Date | Workflow | Runtime (s) | Tokens In | Tokens Out | Human Minutes Saved |
|------|----------|-------------|-----------|------------|---------------------|
| {{}} | {{}} | {{}} | {{}} | {{}} | {{}} |

_Formula for savings: manual_estimate – (actual_human_time)._

<!-- QC:
- Row added automatically by Workflow
-->
```

---

### 10. **ClarityEdge – Prompt Snippet**

```markdown
<!--
Template: ClarityEdge – Prompt Snippet
Version: 1.0
Updated: 2025-05-17
Compatible_Workflow: Snippet_to_Prompt_Library
-->

> **Snippet ID:** {{UID}}  **Use-case:** {{e.g., “Summarise PDF”}}

```

<insert tested prompt fragment here>
```

**Expected Output Pattern**

```markdown
{{Example_Output}}
```

<!-- QC:
- Snippet ≤ 120 tokens
- Example output provided
-->

```

---

### How to Install These Templates in TIP

1. In TIP’s **Templates** panel, create a new Markdown template for each file above.
2. Leave the filename identical to the first heading (TIP auto-strips “ClarityEdge – ” when generating documents).
3. Verify that hidden QC comments survive the save-and-render cycle—they do not appear to end-users.
4. Optionally, set **global visibility = true** so every team member can instantiate templates without extra permissions.

*Proceed to Step 3 (Workflow Library) once the templates are loaded and synced.*
```
