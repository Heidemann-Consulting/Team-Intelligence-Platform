# **Fusion‑Loop · Rituals & Practices Handbook**

**Version:** 1.0
**Date:** May 17, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

*References: [Fusion‑Loop Templates Library](./fusion-loop-templates-library.md), [Fusion‑Loop Workflow Library](./fusion-loop-workflow-library.md)*

---

## ✨ Why read this guide?

This handbook distills the **how‑to** of running Fusion‑Loop—daily to quarterly—so your team can maximise **Return‑on‑Time** while keeping cognitive load low. Follow these rituals, plug the matching YAML from the Workflow Library, and copy the skeletons from the Templates Library to be productive in < 1 hour of setup.

---

## 1 Roles & Ownership

| Emoji | Role                     | Core Ownership                      | Typical Daily Time                 |
| ----- | ------------------------ | ----------------------------------- | ---------------------------------- |
| 🧭    | **Coordinator**          | Prompt Packet prep, Digest merge    |  ≈ 7 min                           |
| 🛠️   | **Contributors**         | Comment & Vote on LLM Drafts        |  ≈ 8 min                           |
| 📚    | **Editor‑in‑Chief**      | Condensed Context, Metrics snapshot |  Weekly ≈ 15 min; Monthly ≈ 30 min |
| 🔎    | **Analyst** *(optional)* | Curate External Feed relevance      |  Weekly ≈ 5 min                    |
| 🧑‍💻 | **Automation Bot**       | Executes YAML workflows (TIP)       | n/a                                |

> **Tip:** Keep the *Coordinator* rotating every quarter to spread know‑how.

---

## 2 Cadence Overview

| Cadence          | Duration (people) | Workflow Trigger                                                                      | Key Output                                           | Goal                       |
| ---------------- | ----------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------- | -------------------------- |
| **Daily**        | ≤ 25 min (team)   | `Fusion_DailyNewsAnalysis` ➔ `Generate_LLM_Draft_Fusion` ➔ `Digest_Compressor_Fusion` | *Fusion Daily Digest*                                | Ship value & log decisions |
| **Weekly (Mon)** | 15 min            | `Weekly_Kickoff_Fusion`                                                               | *Backlog Reprioritization*                           | Align sprint scope         |
| **Weekly (Fri)** | 15 min            | `Retro_Analyzer_Fusion`                                                               | *Retro Insights*                                     | Inspect‑&‑adapt            |
| **Monthly**      | 30 min            | `Fusion_StrategyAlignment`, `Metrics_Snapshot_Fusion`, `Context_Condensor_Fusion`     | *Strategy Alignment* + refreshed *Condensed Context* | Course‑correct             |
| **Quarterly**    | 60 min            | `Quarterly_Strategy_Review_Fusion`, `Innovation_Idea_Generation_Fusion`               | Updated *North Star Charter*                         | Long‑range steering        |

---

## 3 Daily Ritual Step‑by‑Step

<br>

### 3.1 📰 External Feed Picker (Automated) — *2 min build time, 0 min runtime*

* **Goal:** Funnel noise into *top‑3* actionable headlines.
* **How:** Workflow `Fusion_DailyNewsAnalysis` scans today’s `Fusion_ExternalFeed_YYYY‑MM‑DD.md` and posts analysis.
* **UX Boost:** Use the **🚦 colour labels** (red = urgent, amber = watch, green = reference) in your Markdown editor for quick scanning.

### 3.2 🧭 Prompt Packet — Coordinator (3 min)

* Open `Prompt_Packet_Daily.md` template.
* Fill **Objectives**, **Open Questions**, check **New Facts** auto‑inserted by previous step.
* Keep within the 150‑token soft limit for *Hot‑Context*.

### 3.3 🤖 LLM Draft + Self‑Critique — Workflow (≈ 2 min)

* `Generate_LLM_Draft_Fusion` composes a **Draft** with mandatory *Risks* & *👍/👎* blocks.
* Draft appears in TIP as `LLM_Draft_YYYY‑MM‑DD`.

### 3.4 👥 Triage & Voting — Contributors (async ≤ 8 min)

* Add inline `👍` comments for solid parts; suggest replacements for `👎`.
* Use **Git‑style suggestions** (\`\`\`suggestion) for quick merges.

### 3.5 📑 Refine — Workflow (1 min)

* `Incorporate_Comments_Fusion` applies accepted changes, compresses by 20 %.

### 3.6 🔖 Digest & Log — Coordinator (4 min)

* Review refined output, hit *Run Digest* (`Digest_Compressor_Fusion`).
* Confirm 150‑token *Fusion Daily Digest* posted.
* Append atomic decision(s) to `Decision_Log.md`.

> **Shortcut:** Keyboard ⇧⌘S triggers all three daily workflows via TIP’s Quick‑Run palette.

---

## 4 Weekly Rituals

### 4.1 Monday Kick‑off (15 min)

1. **Input:** Latest *Weekly Trend*, *Working Backlog*, *North Star Charter*.
2. Run `Weekly_Kickoff_Fusion` and skim the produced *Backlog Reprioritization*.
3. **Round‑the‑Room Lightning:** each owner commits to next‑best steps (< 30 sec each).
4. Post recap in chat with 📌 pin.

### 4.2 Friday Retro (15 min)

1. Trigger `Retro_Analyzer_Fusion` to prepare the canvas.
2. Facilitate **Start—Stop—Continue** board (use 🍺 emoji for ‘cheers’ moments).
3. Convert top 3 Action Items into backlog entries.

> **Facilitator’s UX Tip:** Use a *Fist‑of‑5* quick poll (⭐ 1 low → ⭐ 5 great) after Retro to gauge session value.

---

## 5 Monthly Rituals

### 5.1 Strategy Alignment (30 min)

* Schedule at the month’s first working day, immediately after daily loop.
* Run `Fusion_StrategyAlignment`; the big‑context model compares KPI trends vs charter.
* **Review Checklist** (5‑10 min):

  * ⚖️ Delta Table complete?
  * 🧐 Assumptions explicit?
  * ❓ Blind spots plausible?
* **Decision Gate:** Accept or request follow‑up analysis.

### 5.2 Metrics Snapshot (5 min async)

* `Metrics_Snapshot_Fusion` dumps time‐spent, tokens, accuracy sample results into `Fusion_Metrics.csv`.
* Editor‑in‑Chief embeds the graph into your dashboard (TIP widget).

### 5.3 Context Condensor (Automated)

* `Context_Condensor_Fusion` reduces prior month content to ≤ 3 % tokens.
* Human spot‑check redacts any PII before archiving.

---

## 6 Quarterly Rituals

### 6.1 North‑Star Charter Review (60 min)

* Input: last three *Strategy Alignment* docs, external market shifts, customer feedback.
* Update **Mission**, **3‑Year Objectives**, guardrails.
* Vote 👍/👎 on new Charter; on majority 👍, publish and tag version.

### 6.2 Innovation Sprint Kick‑off

* Run `Innovation_Idea_Generation_Fusion` to seed brainstorm backlog.
* Time‑box ideation week; shortlist ideas for next planning cycle.

---

## 7 Tool Hygiene & UX Best Practices

1. **Single‑source filenames** — Copy exact patterns from Templates Library to keep workflows working 🔗.
2. **Emoji markers** —

   * `⚠️` for blockers, `💡` for insights, `✅` for done.
3. **Focus Mode** — TIP’s *Shift‑P* palette → *Hide Noise* hides all but Daily Digest & Prompt Packet.
4. **Self‑Critique Discipline** — If a draft lacks *Risks* or *👍/👎*, send it back.
5. **Stopwatch Bot** — Start timer at ritual begin; autopost to `Fusion_Metrics.csv` on stop.
6. **Notification Hygiene** — Mute all channels except `#fusion‑alerts` to reduce context switching.

---

## 8 Getting Started — 30‑Minute Setup

1. **Clone** both libraries into your TIP vault.
2. Create first `North_Star_Charter.md` (use template).
3. Schedule workflows via TIP *Admin → Schedules* (copy cron from Workflow Library).
4. Run **Trial Day** with a buddy; log friction points.
5. Hold first Friday Retro; fix naming / permissions.

---

## 9 FAQ (Curated)

| Question                          | Quick Answer                                                                         |
| --------------------------------- | ------------------------------------------------------------------------------------ |
| *What if we miss a daily digest?* | Create a back‑fill digest manually; context condensor will catch it monthly.         |
| *Token costs spiking?*            | Check big‑model usage; downgrade monthly run to local if budget tight.               |
| *Can I add a new artifact?*       | Yes—fork a template, but update `inputDocumentSelectors` first to avoid orphan docs. |

---

> **Remember:** *Fusion‑Loop is lightweight by design.  If the process feels heavy, remove friction before adding more tools.*

*End of Handbook*
