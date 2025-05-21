### Step 1 — Concept & Design Guidelines

*Process name: **ClarityEdge™ AI Co-Management Framework***

**Version:** 1.0
**Date:** May 17, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

---

## 1. Strategic Concept

| Aspect                 | Description                                                                                                                                                                                                                       | ULACM Benefit(s) Delivered |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| **Core Idea**          | Codify a lightweight, repeatable AI-assisted work system that turns every TIP team (1-9 people) into a high-leverage “human + AI” unit producing outsized results in ≤ 30 min per member per day.                                 | 2, 3, 6, 11, 13, 18        |
| **Value Proposition**  | *ClarityEdge* installs a shared “second brain”, automates rote synthesis/creation, and embeds continuous reflection loops—freeing humans for judgment and creativity.                                                             | 4, 5, 8, 10, 12, 17, 19    |
| **Process Pillars**    | 1 Collective Context Vault 2 AI-Optimised Workflows 3 Tight Feedback Rituals                                                                                                                                                      | 1, 7, 14, 21, 22           |
| **Time-ROI Guardrail** | Every activity is scoped to **≤ 30 min** per person daily; automation first, delegation second, manual last.                                                                                                                      | 6, 11, 15                  |
| **Tech Fit**           | Designed for a **local 30 B parameter reasoning model** behind TIP (e.g., Llama-3-30B-Instruct on Ollama). Constraints—context window, slower tokens—are mitigated through prompt-compression patterns and incremental workflows. | 18                         |

---

## 2. Design Principles

1. **Clarity First** – Explicit goals, roles, and success criteria precede every AI call.
2. **Small Bites** – Break tasks into atomic prompts < 1 000 input tokens; chain via TIP Workflows.
3. **Progressive Summarisation** – Summaries become the new context objects, keeping token use lean.
4. **Memory as Leverage** – Persist validated insights in Documents/Templates to avoid re-prompting.
5. **Fail-Fast** – Rapid draft → critique → refine loops optimise output quality within the 30-min cap.
6. **Human Oversight** – Final validation always by a human; AI proposes, team disposes.
7. **Default to Share** – Outputs are globally visible unless sensitive; knowledge compounds team-wide.

---

## 3. Prompt-Engineering Guidelines (State-of-the-Art, 30 B LLM)

| Section              | Guideline                                                                                                                                                           |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Structure**        | Use a seven-block scaffold: **(a) Role**, **(b) Objective**, **(c) Context**, **(d) Inputs**, **(e) Task-Steps**, **(f) Output Format**, **(g) Quality-Checklist**. |
| **Role Priming**     | Start with: *“You are a seasoned \<discipline> advisor…”* to steer style & depth.                                                                                   |
| **Compression**      | When passing large Docs, precede with: *“Summarise each section in ≤ 50 words; reference only bullet IDs in further reasoning.”*                                    |
| **Self-Critique**    | Append: *“Before final answer, rate your output 0-10 on Completeness & Clarity; if < 9 improve and rerate.”*                                                        |
| **Error Handles**    | Add concise fallback: *“If information missing, ask one clarifying question then stop.”*                                                                            |
| **Temperature**      | Default 0.2 for accuracy-heavy tasks; 0.7 for creative; set once in backend.                                                                                        |
| **Few-Shot**         | Store high-quality Q→A examples in “Prompt Snippets” Documents; reference with placeholders to save tokens.                                                         |
| **Token Budgeting**  | Target ≤ 2 000 tokens (input + output). For longer jobs, slice via multi-step Workflow.                                                                             |
| **Output Standards** | Enforce markdown tables, JSON, or enumerated lists so outputs slot into downstream Workflows without manual clean-up.                                               |

---

## 4. Template Design Guidelines

| Rule                         | Rationale                                                                                                 |
| ---------------------------- | --------------------------------------------------------------------------------------------------------- |
| **Prefix**                   | Every template name begins **“ClarityEdge – ”** to maintain grouping.                                     |
| **Lean Seeds**               | Provide minimal scaffolding plus examples; keep < 500 words so users aren’t overwhelmed.                  |
| **Token-Aware Placeholders** | Use double-braces (`{{ }}`) for dynamic fields; avoid injecting whole docs—point to summaries.            |
| **Embedded Checklist**       | End each template with a hidden HTML comment `<!-- QC: bullet list -->`; TIP users reveal when reviewing. |
| **Version Note**             | Top metadata block notes last major update & compatible Workflow.                                         |

---

## 5. Workflow Design Guidelines

1. **One Intent, One Output** – Each Workflow produces exactly one new Document type.
2. **Explicit Selectors** – Use rigorous `inputDocumentSelectors` and date filters to avoid accidental context bloat.
3. **Chaining Convention** – Downstream Workflow names must match *exact* output names of upstream docs (since TIP auto-strips prefix).
4. **Safety Nets** – Implement validation steps (LLM self-critique or regex checks) before saving outputs.
5. **Retry Logic** – If Ollama returns error, Workflow surfaces a descriptive message and aborts document creation.
6. **Audit Trail** – Workflow appends an auto-generated footer: *“Created by \<WorkflowName> on {{CurrentDate}} at {{CurrentTime}}”*.
7. **Performance Metric** – Each Workflow logs runtime and tokens used into a “ClarityEdge – Metrics” Document for ROI tracking.

---

## 6. Roles & Responsibilities (≤ 30 min ⁄ day pp)

| Role                      | Daily Time-box | Key Duties in *ClarityEdge*                                                   |
| ------------------------- | -------------- | ----------------------------------------------------------------------------- |
| **Lead**                  | 10 min         | Review yesterday’s AI outputs, approve/adjust, queue today’s Workflows.       |
| **Contributor(s)**        | 15 min         | Provide fresh inputs (e.g., meeting notes), trigger Workflows, refine drafts. |
| **AI Liaison** (rotating) | 5 min          | Monitor Ollama health & token spend; surface issues.                          |

---

## 7. Success Metrics

1. **Outcome Quality ≥ 9 / 10** (self-rated by team)
2. **Daily Person-Minutes Saved ≥ 50 %** vs. baseline manual effort
3. **Knowledge-Reuse Ratio** (citations to existing Docs per new output) **≥ 1.5**
4. **Team Engagement** (≥ 4 members triggering Workflows weekly)
5. **Zero Prompt Failures** caused by context overflow

---

## 8. Compliance with TIP Capabilities

* Uses Document Templates and Process Workflows exactly as defined in the TIP PRD/SRS (Markdown, YAML-like structure, global visibility flags).&#x20;
* All prompt text lives inside TIP objects—no external storage—aligning with self-contained, Dockerised architecture.
* Global default model + temperature keeps administration simple and consistent.

---

### ➡️ Next Step

With the **ClarityEdge** concept and design rules in place, we can proceed to **Step 2: Template Library**—creating the named, version-controlled templates that operationalise these guidelines.
