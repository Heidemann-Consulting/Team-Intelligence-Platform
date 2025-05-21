# ApexFusion Framework – Concept & Design Guidelines

**Version:** 1.0
**Date:** May 17, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

- [ApexFusion Framework – Concept \& Design Guidelines](#apexfusion-framework--concept--design-guidelines)
  - [1. Purpose](#1-purpose)
  - [2. Core Priorities](#2-core-priorities)
  - [3. Design Principles (synthesised from ClarityEdge, Fusion-Loop, Lean-Loop, Phase-Approach, LACM)](#3-design-principles-synthesised-from-clarityedge-fusion-loop-lean-loop-phase-approach-lacm)
  - [4. Prompt-Engineering Guidelines](#4-prompt-engineering-guidelines)
  - [5. Naming Conventions](#5-naming-conventions)
  - [6. Mitigating 30B-Model Limits](#6-mitigating-30b-model-limits)
  - [7. Success Metrics](#7-success-metrics)

## 1. Purpose
Deliver the complete set of TIP benefits—strategic memory, AI-powered capacity, workflow optimisation, brand-safe communication, decision support—within a 30 min/day/person budget. :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}

## 2. Core Priorities
1. **Content Goals First** – meet TIP-Benefits targets.
2. **ROI & Efficiency** – maximise value per human minute.
3. **Usability & UX** – friction-free rituals and clear artefacts.

## 3. Design Principles (synthesised from ClarityEdge, Fusion-Loop, Lean-Loop, Phase-Approach, LACM)
| Principle | Inherited Strength | ApexFusion Enhancement |
|-----------|-------------------|------------------------|
| Compound Knowledge (ClarityEdge)| Progressive summaries | Adds auto-compression workflow + token-budget guard |
| ROI-per-Minute (Fusion-Loop) | 7-min coordinator loops | Hard 30 min/person cap & dashboard time trackers |
| Lean Token Usage (Lean-Loop) | Context buckets | Adds “Essential ≠ Everything” rule-set & auto-pruning |
| Multi-Phase Maturity (Phase) | Crawl/Walk/Run gates | One-click upgrade paths in template comments |
| Tight AI Oversight (LACM) | Transparent review | Adds mandatory ⬜human-check box in every output doc |

## 4. Prompt-Engineering Guidelines
1. **Structured Roles** – always start with `**Role:**` & `**Goal:**`.
2. **Explicit Context Windows** – state *exact* token limits for the 30B model (≤ 8 K recommended).
3. **Self-Critique** – require a `<Model-Reflection>` block in outputs.
4. **Few-Shot > Zero-Shot** – embed 1-2 canonical examples—for stability—inside templates.
5. **Guardrail List** – finish every system prompt with *“Refuse if…”* clauses covering off-scope topics.
6. **Compression Chain** – cascade long inputs through `ApexFusion_ContextShrinker` before final prompts.

## 5. Naming Conventions
* **Templates**: `ApexFusion_<Artifact>_Template`
* **Workflows**: `ApexFusion_<Function>Workflow`
* **Documents** (runtime): plain descriptive names, e.g. `Daily_Log_2025-05-18`.
* **Versioning** handled automatically by TIP—no manual suffixes.

## 6. Mitigating 30B-Model Limits
* Keep each inference ≤ 1 K tokens output.
* Pre-chunk large context with the ContextShrinker workflow.
* Provide deterministic skeleton sections in templates to steer reasoning.
* Use chain-of-thought only internally; final answers auto-redact internal reasoning.

## 7. Success Metrics
* ≤ 30 min average daily human effort (TIP time-tracker widget).
* ≥ 40 % search-time reduction after 4 weeks (team survey).
* ≥ 25 % faster meeting throughput vs. baseline (calendar analytics).
* ≥ 50 % doc quality increase (editor-in-chief scoring rubric).
