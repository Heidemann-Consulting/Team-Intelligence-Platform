# **Lean AI Co-Management (LACM) Workflow Library for TIP**

**Version:** 1.0
**Date:** May 11, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

## **Table of Contents**

- [**Lean AI Co-Management (LACM) Workflow Library for TIP**](#lean-ai-co-management-lacm-workflow-library-for-tip)
  - [**Table of Contents**](#table-of-contents)
  - [**Introduction**](#introduction)
  - [**Core LACM Workflows for TIP**](#core-lacm-workflows-for-tip)
    - [**Phase 1: Daily Routine Workflows**](#phase-1-daily-routine-workflows)
      - [1. Daily News \& Environment Analysis Workflow](#1-daily-news--environment-analysis-workflow)
      - [2. Daily Review \& Context Capture Workflow](#2-daily-review--context-capture-workflow)
      - [3. Daily Planning Workflow](#3-daily-planning-workflow)
    - [**Phase 2: Weekly Routine Workflows**](#phase-2-weekly-routine-workflows)
      - [4. Weekly Analysis Summary \& Trend Identification Workflow](#4-weekly-analysis-summary--trend-identification-workflow)
      - [5. Weekly Retrospective Preparation Workflow](#5-weekly-retrospective-preparation-workflow)
      - [6. Weekly Planning Preview Workflow](#6-weekly-planning-preview-workflow)
    - [**Phase 3: Monthly Routine Workflows**](#phase-3-monthly-routine-workflows)
      - [7. Monthly Analysis \& Strategy Check Workflow](#7-monthly-analysis--strategy-check-workflow)
      - [8. Context Condensation Workflow](#8-context-condensation-workflow)
      - [9. Monthly Process Retrospective Preparation Workflow](#9-monthly-process-retrospective-preparation-workflow)
    - [**Phase 4: Quarterly \& Annual Routine Workflows**](#phase-4-quarterly--annual-routine-workflows)
      - [10. Quarterly Review \& Goal Setting Preparation Workflow](#10-quarterly-review--goal-setting-preparation-workflow)
      - [11. Innovation Idea Generation Workflow](#11-innovation-idea-generation-workflow)
      - [12. Annual Strategy Analysis Preparation Workflow](#12-annual-strategy-analysis-preparation-workflow)
    - [**General Purpose / Pair Working Workflows (LACM Context)**](#general-purpose--pair-working-workflows-lacm-context)
      - [13. Draft Document Section Workflow (LACM Pair Working)](#13-draft-document-section-workflow-lacm-pair-working)
      - [14. Brainstorm Ideas Workflow (LACM Pair Working)](#14-brainstorm-ideas-workflow-lacm-pair-working)
      - [15. Analyze Text Segment Workflow (LACM Pair Working)](#15-analyze-text-segment-workflow-lacm-pair-working)
  - [**Notes on Usage by Team Users in TIP**](#notes-on-usage-by-team-users-in-tip)
  - [**Notes for Administrators in TIP**](#notes-for-administrators-in-tip)

## **Introduction**

This document serves as a library of predefined Process Workflows specifically designed for the Lean AI Co-Management (LACM) process running on the Team Intelligence Platform (TIP). These workflows are intended to be created and managed by System Administrators within TIP's Process Workflow management area. Team Users can then execute these globally visible workflows, using their TIP Documents as inputs, to assist with their daily, weekly, monthly, and other strategic routines.

Each workflow definition below is presented in the YAML-like format expected by TIP's Markdown editor for Process Workflows. The prompts are designed to work with LLMs that **do not have internet or external tool access**, relying solely on the content of the input TIP Document(s).

All input documents for these workflows are expected to be **TIP Documents**, often created using templates from the `LACM Templates Library for TIP`. Output documents will also be TIP Documents.

## **Core LACM Workflows for TIP**

### **Phase 1: Daily Routine Workflows**

#### 1. Daily News & Environment Analysis Workflow

* **Workflow Name (in TIP):** `LACM_Workflow_DailyNewsAnalysis`
* **Description:** Analyzes manually inputted news (from a TIP Document) against strategy, competitor, and market context documents to identify relevant external events.
* **Ritual Relevance:** LACM Phase 1.1: Daily News & Environment Analysis.
* **Expected Input TIP Document Name(s) / Template Origin:**
    * Primary Input: `LACM_ManualNewsInput_YYYY-MM-DD` (created from `LACM_ManualNewsInput`)
    * Context Documents (User selects all that apply):
        * `LACM_Strategy_*`
        * `LACM_Competitors_*`
        * `LACM_TargetMarkets_*`
* **TIP Process Workflow Definition:**

```yaml
# Workflow Name: LACM_Workflow_DailyNewsAnalysis
# Description: Analyzes manually inputted news against strategy, competitors, and markets.

inputDocumentSelectors: # User will select relevant documents based on these patterns
  - "LACM_ManualNewsInput_*" # Expecting one for the current day
  - "LACM_Strategy_*"
  - "LACM_Competitors_*"
  - "LACM_TargetMarkets_*"
inputDateSelector: null # User selects the relevant dated 'ManualNewsInput'
outputName: "LACM_DailyNewsAnalysis_{{Year}}-{{Month}}-{{Day}}" # Tries to use date from input filename
prompt: |
  **Role:** You are an AI News Analyst supporting the LACM process. Your task is to filter and assess external information provided MANUALLY in the input documents for operational relevance.
  **Goal:** Identify and concisely summarize the MOST relevant news impacting our strategy and markets from the provided input, directly supporting informed daily decision-making.
  **Context:**
  - Primary Input: News items are provided in a document matching the pattern "LACM_ManualNewsInput_*". This document contains manually gathered summaries or pasted text of news from the last 24-48 hours.
  - Assessment Criteria: Evaluate news relevance based on potential direct impact on objectives outlined in the "LACM_Strategy_*" document, activities mentioned in the "LACM_Competitors_*" document, and trends within the "LACM_TargetMarkets_*" document. All these context documents are part of the input.
  - Today's Date: {{CurrentDate_YYYY-MM-DD}}.

  **Task:**
  1. Carefully review all provided input documents: the news input document and the context documents (Strategy, Competitors, Target Markets).
  2. From the "LACM_ManualNewsInput_*" document, select ONLY THE TOP 3-5 items with the HIGHEST potential relevance based on the Assessment Criteria found in the other provided context documents. Prioritize actionable information over general updates.
  3. For each selected news item, write a concise summary covering:
      - Source: (As provided in the input document)
      - Key Point: (1-2 sentence summary of the core information)
      - Relevance/Impact: (Briefly explain WHY it's relevant based on the provided Strategy, Competitors, or Target Markets documents. Focus on potential consequence or required action.)
  4. If an item requires URGENT attention (e.g., significant competitor move, major policy change impacting core business based on provided context), prefix its summary with the flag "**FLAG: IMPORTANT** - ". Use this flag sparingly.
  5. Generate the output strictly in Markdown format.

  **Format:**
  ```markdown
  # Daily News & Environment Analysis - {{CurrentDate_YYYY-MM-DD}}
  *Based on manual input from {{InputFileName}} and contextual documents.*

  ## Top Relevant News Items

  - **Source:** [Source Name from input]
    **Key Point:** [1-2 sentence summary]
    **Relevance/Impact:** [Brief explanation of why it matters based on provided Strategy/Competitors/Target Markets documents]

  - **FLAG: IMPORTANT** - **Source:** [Source Name from input]
    **Key Point:** [1-2 sentence summary of urgent item]
    **Relevance/Impact:** [Explanation of urgency and potential consequence based on provided Strategy/Competitors/Target Markets documents]

  *(Repeat for other selected items, max 3-5 total)*
  ```
  **Constraints:** Be factual and objective. Base your analysis ONLY on the content within the provided input documents. Avoid speculation. Exclude items with low or indirect relevance. Focus on clarity and brevity.
  {{DocumentContext}} # This will contain all selected input documents concatenated.
```
```

#### 2. Daily Review & Context Capture Workflow

* **Workflow Name (in TIP):** `LACM_Workflow_DailyLogGenerator`
* **Description:** Processes team member inputs (from a TIP Document like `LACM_DailyLogInput_YYYY-MM-DD`) and contextual documents to create a structured daily log.
* **Ritual Relevance:** LACM Phase 1.2: Daily Review & Context Capture.
* **Expected Input TIP Document Name(s) / Template Origin:**
    * Primary Input: `LACM_DailyLogInput_YYYY-MM-DD` (created from `LACM_DailyLogInput`)
    * Context Documents (User selects relevant ones):
        * `LACM_YYYY-MM-DD-1_DailyPlan` (Previous day's plan)
        * `LACM_DailyNewsAnalysis_YYYY-MM-DD` (Today's analysis, generated by Workflow 1)
* **TIP Process Workflow Definition:**

```yaml
# Workflow Name: LACM_Workflow_DailyLogGenerator
# Description: Structures team inputs into a formal daily log.

inputDocumentSelectors:
  - "LACM_DailyLogInput_*" # Primary input with team's raw notes
  - "LACM_*_DailyPlan" # Previous day's plan (user selects the correct one)
  - "LACM_DailyNewsAnalysis_*" # Today's news analysis (user selects the correct one)
inputDateSelector: null
outputName: "LACM_DailyLog_{{InputFileName | replace: 'LACM_DailyLogInput_', '' | replace: '.md', ''}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  **Role:** You are an AI Documenter supporting the LACM process. Your task is to accurately capture and structure the team's daily operational context based on the provided input documents.
  **Goal:** Consolidate and structure the essential events, outcomes, and insights from the team's input (found in "LACM_DailyLogInput_*") covering the last 24 hours, creating a clear record for knowledge preservation and planning. Use the previous day's plan ("LACM_*_DailyPlan") and today's news analysis ("LACM_DailyNewsAnalysis_*") for context.
  **Context:**
  - Primary Input Document (Team Notes): Content matching "LACM_DailyLogInput_*".
  - Supporting Context Documents:
    - Previous Day's Plan: Content matching "LACM_*_DailyPlan".
    - Today's News Analysis: Content matching "LACM_DailyNewsAnalysis_*".
  - Today's Date: {{CurrentDate_YYYY-MM-DD}}.

  **Task:**
  1. Carefully analyze all provided input documents.
  2. From the "LACM_DailyLogInput_*" document, extract and categorize information clearly under the predefined headings below. Focus on concrete facts and outcomes.
  3. Compare achievements against the "LACM_*_DailyPlan" (previous day's plan) if possible, and note alignment or deviations if explicitly mentioned in the input notes.
  4. Note any relevant links to the day's external context if mentioned in the input notes or found in "LACM_DailyNewsAnalysis_*".
  5. Generate the structured Markdown file.

  **Format:** Use the following Markdown structure precisely:
  ```markdown
  # Daily Log - {{CurrentDate_YYYY-MM-DD}}

  ## 1. Accomplishments
  *(Summarize from "Key Accomplishments" in the input document)*
  - [Specific task completed or milestone reached. Briefly mention outcome/value.]
  - [Another accomplishment.]

  ## 2. Challenges & Blockers
  *(Summarize from "Challenges & Blockers Encountered" in the input document)*
  - [Specific problem encountered. Mention root cause if known from input.]
  - [Any blockers preventing progress? Who/what is needed, if mentioned?]

  ## 3. Key Interactions (Internal/External)
  *(Summarize from "Key Interactions" in the input document)*
  - **Interaction:** [Meeting/Call with X from input]
    **Outcome:** [Decision made, key info received, next step agreed from input]
  - **Interaction:** [Customer email/call from input]
    **Outcome:** [Feedback received, issue resolved, follow-up needed from input]

  ## 4. Learnings & Insights
  *(Summarize from "Learnings & Insights" in the input document)*
  - [Key takeaway, discovery, or something learned that could improve future work from input.]
  - [Insight gained from data, analysis, or observation from input.]

  ## 5. Open Points / Action Items (for today or carry-over)
  *(Summarize from "Open Points / Questions / Items for Next 24h Focus" in the input document)*
  - [Specific small task identified that needs doing from input.]
  - [Carry-over item from yesterday needing attention from input.]

  ## 6. Relevant External Context (If mentioned in inputs or News Analysis)
  - [Reference any item from the provided "LACM_DailyNewsAnalysis_*" or "Relevant External Context Items" in input that directly impacted the day's status or plans.]
  ```
  **Constraints:** Use neutral, factual language. Avoid interpretation unless explicitly stated as a 'Learning/Insight' in the input. Ensure all key input points are captured concisely under the correct heading. This structure is critical for process consistency and future analysis. Base your output ONLY on the content of the provided documents.
  {{DocumentContext}}
```
```

#### 3. Daily Planning Workflow

* **Workflow Name (in TIP):** `LACM_Workflow_DailyPlanGenerator`
* **Description:** Drafts a daily plan based on various contextual TIP documents.
* **Ritual Relevance:** LACM Phase 1.3: Daily Planning.
* **Expected Input TIP Document Name(s) / Template Origin:**
    * `LACM_Strategy_*`
    * `LACM_Goals_Quarter_*` (current quarter)
    * `LACM_KW*_WeeklyPlanPreview_*` (current week)
    * `LACM_DailyLog_YYYY-MM-DD` (today's log, generated by Workflow 2)
    * `LACM_DailyNewsAnalysis_YYYY-MM-DD` (today's analysis, generated by Workflow 1)
    * `LACM_TaskList_*`
    * `LACM_AvailableTime_*` (today's or current week's)
* **TIP Process Workflow Definition:**

```yaml
# Workflow Name: LACM_Workflow_DailyPlanGenerator
# Description: Drafts a daily plan considering strategic goals, weekly focus, daily context, tasks, and available time.

inputDocumentSelectors: # User selects all relevant documents
  - "LACM_Strategy_*"
  - "LACM_Goals_Quarter_*"
  - "LACM_KW*_WeeklyPlanPreview_*"
  - "LACM_DailyLog_*" # Today's log
  - "LACM_DailyPlan_*" # Today's plan
  - "LACM_DailyNewsAnalysis_*" # Today's news analysis
  - "LACM_TaskList_*"
  - "LACM_AvailableTime_*"
inputDateSelector: null
outputName: "LACM_DailyPlan_{{InputFileName | regex_replace: '.*(LACM_DailyLog_|LACM_AvailableTime_)([^_]+_[^_]+_[^_]+).*', '$2'}}_{{Year}}-{{Month}}-{{Day}}" # Complex attempt to get date part
prompt: |
  **Role:** You are an AI Planning Assistant supporting the LACM process. Your task is to draft a focused and realistic daily plan.
  **Goal:** Propose a prioritized, actionable plan for the next 24 hours that directly contributes to the current Weekly Objectives (from "LACM_KW*_WeeklyPlanPreview_*") and Quarterly Goals (from "LACM_Goals_Quarter_*"), considering today's context ("LACM_DailyLog_*", "LACM_DailyNewsAnalysis_*"), overall tasks ("LACM_TaskList_*"), and available capacity ("LACM_AvailableTime_*"). Also provide a brief forward look.
  **Context:**
  - Strategic Direction: Content from "LACM_Strategy_*", "LACM_Goals_Quarter_*".
  - Weekly Focus: Crucially, align with "LACM_KW*_WeeklyPlanPreview_*". Identify the current week number if possible from file names or content.
  - Today's Status: Content from "LACM_DailyLog_*" (Accomplishments, Blockers, Open Points).
  - External Factors: Content from "LACM_DailyNewsAnalysis_*".
  - Resources: Content from "LACM_TaskList_*" (Backlog), "LACM_AvailableTime_*" (Capacity for next 24h).
  - Today: {{CurrentDate_YYYY-MM-DD}}. Let's assume Current Week is {{CurrentWeekNumber}}.

  **Task:**
  1. **Analyze Inputs:** Synthesize information from all provided documents, paying special attention to the objectives in "LACM_KW*_WeeklyPlanPreview_*".
  2. **Identify Priorities:** Determine the most critical tasks based on:
      - Direct contribution to Weekly/Quarterly goals.
      - Urgency arising from "LACM_DailyLog_*" (e.g., resolving blockers).
      - Tasks from "LACM_TaskList_*" that align with weekly objectives.
  3. **Propose 24h Plan:** Draft a list of specific, achievable tasks for the next 24 hours.
      - Prioritize mercilessly based on alignment and urgency.
      - Consider dependencies between tasks mentioned in the inputs.
      - **Crucially, compare proposed effort against "LACM_AvailableTime_*" for feasibility.**
      - Suggest task assignments ('Who') if obvious from context or roles. Estimate rough effort ('Effort') if possible (e.g., S/M/L or hours).
  4. **Propose 7d Outlook:** Briefly list the 1-3 most important tasks/themes from the "LACM_KW*_WeeklyPlanPreview_*" that should be kept in focus over the next 7 days.
  5. **Propose 31d Outlook:** Briefly list 1-2 key strategic themes or milestones from "LACM_Goals_Quarter_*" or "LACM_Strategy_*" relevant in the next month.
  6. Generate the Markdown file.

  **Format:** Use the following Markdown structure precisely:
  ```markdown
  # Daily Plan - {{CurrentDate_YYYY-MM-DD}}

  ## Plan Next 24h (Aligned with KW{{CurrentWeekNumber}} Objectives)

  | Priority | Task Description                      | Who    | Effort | Notes / Dependency |
  | :------- | :------------------------------------ | :----- | :----- | :----------------- |
  | High     | [Specific, actionable task 1]         | [Name] | [S/M/L]| [e.g., Blocked by X]|
  | High     | [Specific, actionable task 2]         | [Name] | [S/M/L]|                    |
  | Medium   | [Specific, actionable task 3]         | [Name] | [S/M/L]|                    |
  | Low      | [Specific, actionable task 4]         | [Name] | [S/M/L]|                    |
  *Feasibility Check: Proposed effort roughly aligns with available time stated in "LACM_AvailableTime_*".*

  ## Outlook Next 7 Days (Focus on KW{{CurrentWeekNumber}} Objectives)
  - [Key Task/Theme 1 from Weekly Plan Preview document]
  - [Key Task/Theme 2 from Weekly Plan Preview document]

  ## Outlook Next 31 Days (Strategic Focus)
  - [Key Strategic Theme/Milestone 1 from Goals/Strategy documents]
  ```
  **Constraints:** Be concrete and action-oriented in the 24h plan. Ensure proposed tasks directly support stated goals found in the input documents. The feasibility check against available time is critical. Keep outlooks high-level. Base your output ONLY on the content of the provided documents.
  {{DocumentContext}}
```
```

### **Phase 2: Weekly Routine Workflows**

#### 4. Weekly Analysis Summary & Trend Identification Workflow

* **Workflow Name (in TIP):** `LACM_Workflow_WeeklyAnalysis`
* **Description:** Synthesizes the week's daily external analyses and assesses strategic relevance.
* **Ritual Relevance:** LACM Phase 2.1.
* **Expected Input TIP Document Name(s) / Template Origin:**
    * Multiple `LACM_DailyNewsAnalysis_YYYY-MM-DD` files from the past 7 days.
    * `LACM_Strategy_*`
* **TIP Process Workflow Definition:**
```yaml
# Workflow Name: LACM_Workflow_WeeklyAnalysis
# Description: Summarizes daily news analyses for the week and identifies trends against strategy.

inputDocumentSelectors:
  - "LACM_DailyNewsAnalysis_*" # User selects 5-7 relevant daily analyses for the week
  - "LACM_Strategy_*"
inputDateSelector: null # User manually selects the relevant week's documents
outputName: "LACM_KW{{CurrentWeekNumber}}_WeeklyAnalysis_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  **Role:** You are an AI Analyst supporting the LACM process by synthesizing weekly external trends.
  **Goal:** Summarize the provided daily external analyses (from "LACM_DailyNewsAnalysis_*" documents), identify significant recurring themes or emerging trends/patterns, and assess their potential cumulative impact on our strategy (from "LACM_Strategy_*") to inform tactical planning for Week {{CurrentWeekNumber}}.
  **Context:**
  - Primary Input: Content from several "LACM_DailyNewsAnalysis_*" documents for the past week.
  - Strategic Lens: Assess findings against objectives and focus areas in the provided "LACM_Strategy_*" document.
  - Current Week: {{CurrentWeekNumber}}. Today's Date: {{CurrentDate_YYYY-MM-DD}}.

  **Task:**
  1. Analyze all provided "LACM_DailyNewsAnalysis_*" documents.
  2. **Identify Recurring Themes:** Group similar news items or recurring topics mentioned throughout these documents.
  3. **Highlight Emerging Trends/Patterns:** Look for developments that show a direction or acceleration over the week based on the inputs.
  4. **Synthesize Top 3-5 Insights:** Determine the most strategically significant themes or trends based on their potential impact (positive or negative) on the objectives outlined in "LACM_Strategy_*".
  5. **Assess Cumulative Impact:** For each key insight, briefly explain its potential implication for our strategy or operations, based on the provided strategy document.
  6. **Identify Discussion Points:** Flag 1-2 key insights that most warrant discussion regarding potential tactical adjustments for the upcoming week.
  7. Generate the Markdown file.

  **Format:** Use the following Markdown structure precisely:
  ```markdown
  # Weekly Analysis Summary - Week {{CurrentWeekNumber}} (Generated: {{CurrentDate_YYYY-MM-DD}})

  ## Key External Themes & Trends Observed This Week
  *(Based on provided Daily News Analysis documents)*

  1.  **Theme/Trend:** [Concise description of the first major theme/trend]
      **Observations:** [Briefly mention specific examples from daily analyses supporting this]
      **Potential Strategic Impact (based on `LACM_Strategy_*`):** [Assess how this could affect goals in the provided strategy document]

  2.  **Theme/Trend:** [Concise description of the second major theme/trend]
      **Observations:** [...]
      **Potential Strategic Impact (based on `LACM_Strategy_*`):** [...]

  *(Repeat for Top 3-5 insights)*

  ## Key Discussion Points for Tactical Planning
  - **Point 1:** [Highlight the insight most needing discussion regarding next week's actions]
  - **Point 2:** [Optional: Second point for discussion]
  ```
  **Constraints:** Focus on synthesis and strategic relevance, not just listing daily news. Prioritize insights with potential actionable consequences. Maintain a neutral, analytical tone. Base your output ONLY on the content of the provided documents.
  {{DocumentContext}}
```
```

#### 5. Weekly Retrospective Preparation Workflow

* **Workflow Name (in TIP):** `LACM_Workflow_WeeklyRetroPrep`
* **Description:** Analyzes the week's daily logs to identify patterns for the retrospective.
* **Ritual Relevance:** LACM Phase 2.2.
* **Expected Input TIP Document Name(s) / Template Origin:**
    * Multiple `LACM_DailyLog_YYYY-MM-DD` files from the past 7 days.
    * `LACM_KW*_WeeklyPlanPreview_*` (the plan for the week being reviewed).
    * `LACM_Processes_*` (optional, for context on documented processes).
* **TIP Process Workflow Definition:**
```yaml
# Workflow Name: LACM_Workflow_WeeklyRetroPrep
# Description: Analyzes weekly daily logs and plan to prepare for a retrospective.

inputDocumentSelectors:
  - "LACM_DailyLog_*" # User selects 5-7 daily logs for the week
  - "LACM_KW*_WeeklyPlanPreview_*" # User selects the plan for the week being reviewed
  - "LACM_Processes_*" # Optional, user selects if relevant
inputDateSelector: null
outputName: "LACM_KW{{CurrentWeekNumber}}_RetroPreparation_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  **Role:** You are an AI Analyst supporting the LACM weekly retrospective by identifying patterns in operational data.
  **Goal:** Analyze the provided "LACM_DailyLog_*" documents for Week {{CurrentWeekNumber}}, compare against the objectives in "LACM_KW*_WeeklyPlanPreview_*", and identify recurring patterns (positive and negative) related to workflow, collaboration, and goal achievement. This will provide objective data points for the team retrospective. Reference "LACM_Processes_*" if provided and relevant.
  **Context:**
  - Primary Input: Content from "LACM_DailyLog_*" documents for the past 7 days.
  - Planned Work: Content from "LACM_KW*_WeeklyPlanPreview_*" (objectives set for this week).
  - Documented Processes (Optional): Content from "LACM_Processes_*".
  - Current Week: {{CurrentWeekNumber}}. Today's Date: {{CurrentDate_YYYY-MM-DD}}.

  **Task:**
  1. Analyze all provided "LACM_DailyLog_*" documents, focusing on sections: 'Accomplishments', 'Challenges & Blockers', 'Learnings & Insights'.
  2. **Identify Positive Patterns:** Note recurring types of successes, frequently mentioned effective actions, or positive feedback loops from the logs. Compare accomplishments against the weekly plan document.
  3. **Identify Negative Patterns:** Note recurring challenges, frequently mentioned blockers, reported inefficiencies, or deviations from planned work in the weekly plan document, based on the daily logs.
  4. **Correlate with Processes (If `LACM_Processes_*` is provided):** Where possible, tentatively link identified patterns (especially negative ones) to specific steps or areas in "LACM_Processes_*". Note if issues seem related to undocumented workflows.
  5. **Synthesize Key Data Points:** Prepare a neutral summary listing the most prominent positive and negative patterns observed. Avoid judgmental language.
  6. **Formulate Open Questions:** Based on the patterns, formulate 2-3 open-ended questions designed to spark discussion during the retrospective (e.g., "What contributed to the recurring success in X?", "What might be underlying the repeated challenges with Y?", "How could process Z (from `LACM_Processes_*` if provided) be adjusted based on observation W?").
  7. Generate the Markdown file.

  **Format:** Use the following Markdown structure precisely:
  ```markdown
  # Weekly Retro Preparation - Week {{CurrentWeekNumber}} (Generated: {{CurrentDate_YYYY-MM-DD}})

  ## Data Analysis from Daily Logs & Weekly Plan

  **Observed Positive Patterns:**
  - [Recurring success type 1, e.g., "Consistent positive feedback on X demos mentioned in logs"] (Mention frequency if possible from logs)
  - [Effective action/workflow, e.g., "Use of specific approach Y repeatedly noted as helpful in logs"]
  - [Alignment: Weekly objectives A & B (from plan document) largely achieved per logs]

  **Observed Challenges/Negative Patterns:**
  - [Recurring blocker/issue 1, e.g., "Delays in receiving input for task Z mentioned 3 times in logs"] (Note potential link to a process in "LACM_Processes_*" if provided and clear from logs)
  - [Inefficiency noted, e.g., "Multiple logs mention difficulty finding information for task X"]
  - [Deviation: Weekly objective C (from plan document) appears significantly behind based on logs]

  **Potential Discussion Questions:**
  1. [Open question related to a key positive pattern]
  2. [Open question related to a key negative pattern/challenge]
  3. [Optional: Open question about process (from `LACM_Processes_*` if provided) or collaboration based on data]
  ```
  **Constraints:** Present data objectively. Clearly separate observations from potential discussion questions. Focus on patterns, not isolated incidents. Ensure questions are open-ended and promote reflection, not blame. Base your output ONLY on the content of the provided documents.
  {{DocumentContext}}
```
```

#### 6. Weekly Planning Preview Workflow

* **Workflow Name (in TIP):** `LACM_Workflow_WeeklyPlanPreviewGenerator`
* **Description:** Drafts objectives and key tasks for the upcoming week based on analysis, retro, and strategic goals.
* **Ritual Relevance:** LACM Phase 2.3.
* **Expected Input TIP Document Name(s) / Template Origin:**
    * `LACM_KW*_WeeklyAnalysis_*` (current week's analysis)
    * `LACM_KW*_WeeklyRetroSummary_*` (current week's retro summary)
    * `LACM_Strategy_*`
    * `LACM_Goals_Quarter_*` (current quarter)
    * `LACM_TaskList_*`
    * `LACM_PrioritizedInnovationInitiatives_*` (optional)
* **TIP Process Workflow Definition:**
```yaml
# Workflow Name: LACM_Workflow_WeeklyPlanPreviewGenerator
# Description: Drafts a plan preview for the upcoming week.

inputDocumentSelectors:
  - "LACM_KW*_WeeklyAnalysis_*"
  - "LACM_KW*_WeeklyRetroSummary_*"
  - "LACM_Strategy_*"
  - "LACM_Goals_Quarter_*"
  - "LACM_TaskList_*"
  - "LACM_PrioritizedInnovationInitiatives_*" # Optional, user may not select if N/A
inputDateSelector: null
outputName: "LACM_KW{{CurrentWeekNumber + 1}}_WeeklyPlanPreview_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  **Role:** You are an AI Planning Assistant supporting the LACM weekly planning cycle.
  **Goal:** Draft a focused and achievable preview of the main objectives and key tasks for the upcoming week (KW{{CurrentWeekNumber + 1}}), ensuring alignment with quarterly goals (from "LACM_Goals_Quarter_*"), strategic priorities (from "LACM_Strategy_*"), and incorporating insights from the previous week's analysis ("LACM_KW*_WeeklyAnalysis_*") and retrospective summary ("LACM_KW*_WeeklyRetroSummary_*"). Consider tasks from "LACM_TaskList_*" and initiatives from "LACM_PrioritizedInnovationInitiatives_*" if provided.
  **Context:**
  - Strategic Guidance: Content from "LACM_Strategy_*", "LACM_Goals_Quarter_*".
  - Key Inputs from Current Week (Week {{CurrentWeekNumber}}): "LACM_KW*_WeeklyAnalysis_*", "LACM_KW*_WeeklyRetroSummary_*".
  - Task & Initiative Context: "LACM_TaskList_*", "LACM_PrioritizedInnovationInitiatives_*" (if provided).
  - Upcoming Week: {{CurrentWeekNumber + 1}}. Today's Date: {{CurrentDate_YYYY-MM-DD}}.

  **Task:**
  1. **Synthesize Inputs:** Analyze all context documents to identify key drivers for the upcoming week.
  2. **Identify Strategic Themes:** Extract relevant objectives from "LACM_Goals_Quarter_*" and "LACM_Strategy_*" that require progress in KW{{CurrentWeekNumber + 1}}. Include prioritized innovation initiatives if provided and relevant.
  3. **Incorporate Recent Insights:** Explicitly consider the 'Discussion Points' from "LACM_KW*_WeeklyAnalysis_*" and any actionable improvement items from "LACM_KW*_WeeklyRetroSummary_*".
  4. **Propose 3-5 Main Weekly Objectives:** Draft clear, outcome-oriented objectives for KW{{CurrentWeekNumber + 1}}. These should be stepping stones towards the quarterly goals. Frame them as "Achieve X", "Complete Y", "Decide on Z".
  5. **List Key Supporting Tasks/Projects:** Identify the most significant tasks or project milestones from "LACM_TaskList_*" or implied by the objectives that need to be tackled in KW{{CurrentWeekNumber + 1}}. Differentiate between ongoing work and new initiatives.
  6. **Generate the Markdown file.**

  **Format:** Use the following Markdown structure precisely:
  ```markdown
  # Weekly Plan Preview - Week {{CurrentWeekNumber + 1}} (Generated: {{CurrentDate_YYYY-MM-DD}})

  *This plan provides focus for daily planning cycles in the upcoming week.*

  ## Main Objectives for Week {{CurrentWeekNumber + 1}} (Aligned with QX Goals)

  1.  **Objective:** [Clear, outcome-oriented objective 1, e.g., "Finalize specification for Feature X"] (Link to QX Goal if clear from input documents)
      *Why:* [Briefly state strategic reason or context based on inputs]
  2.  **Objective:** [Clear, outcome-oriented objective 2, e.g., "Resolve key issues identified in KW{{CurrentWeekNumber}} Retro"]
      *Why:* [Connects to continuous improvement based on retro summary]
  3.  **Objective:** [Clear, outcome-oriented objective 3]
      *Why:* [...]
  *(Max 3-5 objectives)*

  ## Key Tasks / Projects Requiring Focus in Week {{CurrentWeekNumber + 1}}
  *(Derived from Task List, Innovation Initiatives, or supporting the objectives above)*
  - **Task/Project:** [Significant task 1]
    *Related Objective(s):* [Link to objective number(s) above]
  - **Task/Project:** [Significant task 2]
    *Related Objective(s):* [...]
  - **Task/Project:** [Action item from Retro needing completion]
    *Related Objective(s):* [Objective 2, or relevant objective]
  - ...

  *Note: Detailed task breakdown occurs during Daily Planning.*
  ```
  **Constraints:** Objectives must be specific and outcome-focused. Ensure a clear link between weekly objectives and quarterly goals/strategy based on the provided documents. Keep the list of key tasks high-level. The 'Why' justification for objectives is important. Base your output ONLY on the content of the provided documents.
  {{DocumentContext}}
```
```

### **Phase 3: Monthly Routine Workflows**

#### 7. Monthly Analysis & Strategy Check Workflow

* **Workflow Name (in TIP):** `LACM_Workflow_MonthlyAnalysisStrategyCheck`
* **Description:** Synthesizes weekly analyses, evaluates progress against goals, and checks strategic alignment.
* **Ritual Relevance:** LACM Phase 3.1.
* **Expected Input TIP Document Name(s) / Template Origin:**
    * Multiple `LACM_KW*_WeeklyAnalysis_*` files from the past 4-5 weeks.
    * `LACM_Strategy_*`
    * `LACM_Goals_Quarter_*` (current quarter)
    * `LACM_YYYY-MM-1_MonthlyAnalysisStrategyCheck` (previous month's, optional for trend comparison)
* **TIP Process Workflow Definition:**
```yaml
# Workflow Name: LACM_Workflow_MonthlyAnalysisStrategyCheck
# Description: Performs a monthly analysis of weekly trends against strategy and goals.

inputDocumentSelectors:
  - "LACM_KW*_WeeklyAnalysis_*" # User selects 4-5 weekly analyses for the month
  - "LACM_Strategy_*"
  - "LACM_Goals_Quarter_*" # Current quarter's goals
  - "LACM_*_MonthlyAnalysisStrategyCheck" # Optional: previous month's report
inputDateSelector: null
outputName: "LACM_{{Year}}-{{Month}}_MonthlyAnalysisStrategyCheck"
prompt: |
  **Role:** You are an AI Strategy Analyst supporting the LACM monthly review cycle.
  **Goal:** Synthesize the past month's weekly analyses (from "LACM_KW*_WeeklyAnalysis_*"), identify significant trends/deviations, and rigorously assess alignment with current strategy ("LACM_Strategy_*") and quarterly goals ("LACM_Goals_Quarter_*"). Highlight key points for strategic discussion. If the previous month's analysis ("LACM_*_MonthlyAnalysisStrategyCheck") is provided, use it for trend comparison.
  **Context:**
  - Primary Input: Content from "LACM_KW*_WeeklyAnalysis_*" documents for the specified month.
  - Strategic Framework: Content from "LACM_Strategy_*", "LACM_Goals_Quarter_*".
  - Historical Context (Optional): Content from a previous "LACM_*_MonthlyAnalysisStrategyCheck".
  - Current Month/Year: {{CurrentMonthName}} {{CurrentYear}}. Assume the Quarter from the "LACM_Goals_Quarter_*" filename (e.g., Q{{CurrentQuarterNumber}}).

  **Task:**
  1. **Analyze Weekly Inputs:** Review all provided "LACM_KW*_WeeklyAnalysis_*" documents.
  2. **Synthesize Monthly Trends:** Identify the 3-5 most significant overarching trends (external or internal patterns implied by multiple weekly reports). If previous month's analysis is available, compare and note continuing or new trends.
  3. **Assess Goal Progress:** Evaluate progress towards the objectives listed in "LACM_G_Quarter_*" based on the cumulative information from the weekly analyses. Note areas clearly on track, lagging, or facing significant challenges.
  4. **Perform Strategy Alignment Check:** Explicitly compare the identified monthly trends and goal progress against the key pillars/objectives defined in "LACM_Strategy_*". Are we still aligned? Are strategic assumptions holding?
  5. **Identify Key Deviations/Challenges/Opportunities:** Highlight significant variances from plan, persistent challenges, or new strategic opportunities revealed during the month.
  6. **Formulate Strategic Discussion Points:** Based on the analysis, formulate 2-4 specific, high-level questions or points that require management attention or strategic decision-making.
  7. Generate the Markdown file.

  **Format:** Use the following Markdown structure precisely:
  ```markdown
  # Monthly Analysis & Strategy Check - {{CurrentMonthName}} {{CurrentYear}}

  ## 1. Key Trends Observed This Month
  *(Based on provided Weekly Analysis documents)*
  - **Trend 1:** [Description of significant trend, note if continuing from last month if that document was provided]
    *Supporting Evidence:* [Brief reference to weekly analysis themes]
  - **Trend 2:** [...]
  - **Trend 3:** [...]
  *(Max 3-5 key trends)*

  ## 2. Progress Towards Quarterly Goals (Q{{CurrentQuarterNumber}} {{CurrentYear}} from "LACM_Goals_Quarter_*")
  - **Objective:** [Objective from "LACM_Goals_Quarter_*"]
    *Status:* [On Track / At Risk / Off Track / Completed - based on analysis of weekly reports]
    *Observations:* [Brief explanation based on monthly analysis of weekly reports]
  - **Objective:** [...]
    *Status:* [...]
    *Observations:* [...]
  *(Cover all current Quarter Goals based on provided "LACM_Goals_Quarter_*")*

  ## 3. Strategic Alignment Assessment
  *(Based on comparison with provided "LACM_Strategy_*")*
  - [Assessment point 1 regarding alignment of trends/progress with strategy. Is a specific strategic assumption challenged?]
  - [Assessment point 2...]

  ## 4. Significant Deviations / Challenges / Opportunities
  - **Deviation/Challenge:** [Description of major variance or persistent issue]
  - **Opportunity:** [Description of new strategic opportunity identified]

  ## 5. Key Points for Strategic Discussion
  1. [Specific question or topic needing management attention, e.g., "How should we respond to Trend X impacting Goal Y?"]
  2. [Another strategic question, e.g., "Does persistent Challenge Z require a change in approach outlined in Strategy section A?"]
  *(Max 2-4 points)*
  ```
  **Constraints:** Focus on strategic implications. Ensure clear linkage between observations, goal progress, and strategic alignment. Discussion points should be forward-looking. Maintain a concise, executive summary style. Base your output ONLY on the content of the provided documents.
  {{DocumentContext}}
```
```

#### 8. Context Condensation Workflow

* **Workflow Name (in TIP):** `LACM_Workflow_ContextCondensation`
* **Description:** Summarizes older daily/weekly files to preserve essential long-term insights.
* **Ritual Relevance:** LACM Phase 3.2.
* **Expected Input TIP Document Name(s) / Template Origin:**
    * User selects multiple older, detailed TIP documents (e.g., `LACM_DailyLog_YYYY-MM-DD`, `LACM_KWXX_WeeklyAnalysis` from a specific past month).
* **TIP Process Workflow Definition:**
```yaml
# Workflow Name: LACM_Workflow_ContextCondensation
# Description: Condenses multiple older documents into a summary of key strategic insights.

inputDocumentSelectors: # User selects a batch of older documents to condense
  - "LACM_DailyLog_*"
  - "LACM_KW*_WeeklyAnalysis_*"
  - "LACM_DailyNewsAnalysis_*"
inputDateSelector: null # User should select documents from a specific past period.
outputName: "LACM_CondensedContext_{{InputFileName | replace: 'LACM_', '' | truncate: 30, ''}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  **Role:** You are an AI Archivar supporting the LACM process by condensing historical operational context.
  **Goal:** From the provided set of older documents ({{InputFileNames}}), extract and synthesize ONLY the most critical long-term strategic events, decisions, trends, and insights. Discard transient operational details, routine updates, and information not relevant for future strategic reviews (e.g., 6-12+ months from now). The aim is to create a highly concise digest.
  **Context:**
  - Input Files: The content of multiple documents selected by the user. These could be daily logs, weekly analyses, etc., from a past period.
  - Retention Focus: Identify information with potential relevance for future annual reviews or understanding long-term strategic evolution. Discard details relevant only to the specific day/week they were created unless they represent a major strategic point.

  **Task:**
  1. Analyze all provided input documents.
  2. **Identify Core Strategic Content:** Extract only points discussing:
      - Major market shifts or significant competitor actions with lasting impact.
      - Key strategic decisions made, and their rationale if stated.
      - Significant trends (internal or external) with long-term implications identified during that period.
      - Outcomes that directly impacted long-term goals or required a shift in strategy.
      - Significant, unique learnings that changed fundamental approaches.
  3. **Synthesize and Condense:** Rewrite the extracted core content into a very brief, integrated summary for the entire period covered by the input documents. Use bullet points for clarity. Eliminate redundancy.
  4. **Ensure No Critical Loss:** Double-check that no truly critical strategic information (as defined above) has been omitted, even if condensing heavily.
  5. Generate the Markdown file.

  **Format:** Use the following Markdown structure precisely:
  ```markdown
  # Condensed Context Summary
  *Source Documents (approximate period): {{InputFileNames}} (Processed on {{CurrentDate_YYYY-MM-DD}})*

  *This summary preserves key strategic insights from the input documents while omitting operational details.*

  ## Key Strategic Events & Decisions
  - [Summary of major event/decision 1 from the period]
  - [...]

  ## Significant Long-Term Trends Identified
  - [Summary of major trend 1 observed during the period]
  - [...]

  ## Major Challenges/Outcomes Impacting Strategy
  - [Summary of significant challenge or outcome related to long-term goals during the period]
  - [...]

  ## Key Learnings with Enduring Value
  - [A significant learning that influenced long-term direction or process]
  - [...]
  ```
  **Constraints:** **Be extremely concise.** The primary goal is significant size reduction. Only retain information likely needed for strategic look-backs months or years later. If multiple documents cover the same event, synthesize it once. Base your output ONLY on the content of the provided documents.
  {{DocumentContext}}
```
```

#### 9. Monthly Process Retrospective Preparation Workflow

* **Workflow Name (in TIP):** `LACM_Workflow_MonthlyProcessRetroPrep`
* **Description:** Analyzes a month's weekly retro summaries to identify recurring process issues.
* **Ritual Relevance:** LACM Phase 3.3.
* **Expected Input TIP Document Name(s) / Template Origin:**
    * Multiple `LACM_KW*_WeeklyRetroSummary_*` files from the past 4-5 weeks.
    * `LACM_Processes_*` (current documented processes).
* **TIP Process Workflow Definition:**
```yaml
# Workflow Name: LACM_Workflow_MonthlyProcessRetroPrep
# Description: Analyzes monthly weekly retro summaries for process improvement insights.

inputDocumentSelectors:
  - "LACM_KW*_WeeklyRetroSummary_*" # User selects 4-5 weekly retro summaries for the month
  - "LACM_Processes_*" # The current documented processes
inputDateSelector: null
outputName: "LACM_{{Year}}-{{Month}}_ProcessRetroPreparation"
prompt: |
  **Role:** You are an AI Process Analyst supporting the LACM monthly process review.
  **Goal:** Analyze the provided "LACM_KW*_WeeklyRetroSummary_*" documents for the month of {{CurrentMonthName}} {{CurrentYear}}. Identify recurring feedback, suggestions, or issues specifically related to the documented workflows in the provided "LACM_Processes_*" document. This will provide structured input for the team's process improvement discussion.
  **Context:**
  - Primary Input: Content from "LACM_KW*_WeeklyRetroSummary_*" documents. Focus on sections about challenges and improvement ideas.
  - Process Documentation: Content from "LACM_Processes_*".
  - Current Month/Year: {{CurrentMonthName}}, {{CurrentYear}}.

  **Task:**
  1. Analyze the relevant sections (challenges, improvement ideas, action items) of all provided "LACM_KW*_WeeklyRetroSummary_*" documents.
  2. **Filter for Process Relevance:** Extract only those points that directly mention, criticize, or suggest changes to a specific process or step documented in "LACM_Processes_*", or highlight a clear gap where a documented process might be needed.
  3. **Group by Process Area:** Group the extracted points according to the relevant process name or area from "LACM_Processes_*".
  4. **Identify Recurring Themes:** Within each process area, note if the same issue or suggestion appears multiple times across different weekly retros.
  5. **Synthesize Findings:** Prepare a concise list summarizing the process-related feedback, grouped by process area and highlighting recurring themes.
  6. Generate the Markdown file.

  **Format:** Use the following Markdown structure precisely:
  ```markdown
  # Process Retro Preparation - {{CurrentMonthName}} {{CurrentYear}}
  *Summary of process-related feedback from weekly retrospectives, cross-referenced with "LACM_Processes_*".*

  ## Process Area: [Name of Process 1 from "LACM_Processes_*"]
  - **Recurring Issue/Suggestion:** [Theme identified across multiple retros, e.g., "Lack of clarity on input requirements for Step X"] (Mention frequency if clear from inputs, e.g., "Noted in 3 retros")
  - **Specific Feedback:** [Isolated but relevant point from one retro]
  - ...

  ## Process Area: [Name of Process 2 from "LACM_Processes_*"]
  - **Recurring Issue/Suggestion:** [...] (Frequency: X)
  - **Specific Feedback:** [...]
  - ...

  ## Potential Process Gaps / Undocumented Areas Mentioned
  - [Note feedback suggesting a need for process clarification or documentation in a specific area, e.g., "Confusion about handover between Role A and Role B"]

  ```
  **Constraints:** Focus strictly on feedback related to defined processes or clear process gaps, as found in the input documents. Avoid general complaints not tied to a workflow. Clearly indicate recurring themes. Maintain neutral language. Base your output ONLY on the content of the provided documents.
  {{DocumentContext}}
```
```

### **Phase 4: Quarterly & Annual Routine Workflows**

#### 10. Quarterly Review & Goal Setting Preparation Workflow

* **Workflow Name (in TIP):** `LACM_Workflow_QuarterlyReviewPrep`
* **Description:** Synthesizes quarterly performance, evaluates previous goals, and drafts OKRs for the next quarter.
* **Ritual Relevance:** LACM Phase 4.1.
* **Expected Input TIP Document Name(s) / Template Origin:**
    * Multiple `LACM_YYYY-MM_MonthlyAnalysisStrategyCheck` files for the quarter.
    * `LACM_Strategy_*`
    * `LACM_SalesHandbook_*` (optional)
    * The expiring `LACM_Goals_Quarter_Q[CurrentQuarter]_[Year]`
    * `LACM_PrioritizedInnovationInitiatives_*` (optional)
    * Other relevant performance data documents (user-created TIP docs).
* **TIP Process Workflow Definition:**
```yaml
# Workflow Name: LACM_Workflow_QuarterlyReviewPrep
# Description: Prepares analysis and draft OKRs for quarterly review and planning.

inputDocumentSelectors: # User selects all relevant documents for the quarter
  - "LACM_*_MonthlyAnalysisStrategyCheck"
  - "LACM_Strategy_*"
  - "LACM_SalesHandbook_*" # Optional
  - "LACM_Goals_Quarter_*" # Expiring and potentially next quarter's draft if iterative
  - "LACM_PrioritizedInnovationInitiatives_*" # Optional
  - "LACM_QuarterlyPerformanceData_*" # User-created doc with metrics
inputDateSelector: null
outputName: "LACM_Q{{CurrentQuarterNumber}}_{{Year}}_ReviewPreparation_DraftOKRs_Q{{CurrentQuarterNumber + 1}}"
prompt: |
  **Role:** You are an AI Strategy Analyst supporting the LACM quarterly review and planning cycle.
  **Goal:** Synthesize the concluding quarter's (Q{{CurrentQuarterNumber}} {{CurrentYear}}) performance and strategic context based on provided monthly reports and performance data. Evaluate progress against Q{{CurrentQuarterNumber}} goals (OKRs from "LACM_Goals_Quarter_Q{{CurrentQuarterNumber}}_{{Year}}"). Assess strategic alignment based on "LACM_Strategy_*" and "LACM_SalesHandbook_*" (if provided). Propose data-informed, draft Objectives and Key Results (OKRs) for the upcoming quarter (Q{{CurrentQuarterNumber + 1}}) considering "LACM_PrioritizedInnovationInitiatives_*" (if provided).
  **Context:**
  - Monthly Summaries: Content from "LACM_*_MonthlyAnalysisStrategyCheck" for Q{{CurrentQuarterNumber}}.
  - Strategic Framework: Content from "LACM_Strategy_*", "LACM_SalesHandbook_*".
  - Concluding Goals: Content from "LACM_Goals_Quarter_Q{{CurrentQuarterNumber}}_{{Year}}".
  - Future Focus (Optional): Content from "LACM_PrioritizedInnovationInitiatives_*".
  - Other Inputs (Optional): Relevant financial/performance data summaries provided in other input documents.
  - Concluded Quarter: Q{{CurrentQuarterNumber}}, {{CurrentYear}}. Upcoming Quarter: Q{{CurrentQuarterNumber + 1}}.

  **Task:**
  1. **Synthesize Quarterly Performance:** Analyze the monthly reports and performance data. Summarize the 3-5 most significant strategic findings, trends, and outcomes for Q{{CurrentQuarterNumber}}.
  2. **Evaluate Q{{CurrentQuarterNumber}} OKR Achievement:** For each Objective and Key Result in "LACM_Goals_Quarter_Q{{CurrentQuarterNumber}}_{{Year}}", assess the final status (e.g., Achieved, Partially Achieved, Not Achieved) and briefly note key contributing factors or reasons based on the monthly analyses.
  3. **Assess Strategic Alignment & Validity:** Review the findings from Task 1 & 2 against "LACM_Strategy_*". Highlight areas where strategic assumptions were validated or challenged. Suggest specific sections of "LACM_Strategy_*" or "LACM_SalesHandbook_*" that may warrant discussion or updates.
  4. **Incorporate Innovation Focus:** Consider "LACM_PrioritizedInnovationInitiatives_*" if provided; identify which initiatives are ready for potential inclusion in the next quarter's goals.
  5. **Draft Q{{CurrentQuarterNumber + 1}} OKRs:** Based on the analysis (especially strategic gaps/opportunities and unfinished business from Q{{CurrentQuarterNumber}}), propose 3-5 ambitious but achievable Objectives for Q{{CurrentQuarterNumber + 1}}. For each Objective, propose 2-4 specific, measurable, achievable, relevant, time-bound (SMART) Key Results. Ensure these draft OKRs clearly contribute to the overarching "LACM_Strategy_*".
  6. **Structure for Review:** Generate the Markdown file.

  **Format:** Use the following Markdown structure precisely:
  ```markdown
  # Quarterly Review Prep & Q{{CurrentQuarterNumber + 1}} Draft OKRs - Q{{CurrentQuarterNumber}} {{CurrentYear}} (Generated: {{CurrentDate_YYYY-MM-DD}})

  ## 1. Q{{CurrentQuarterNumber}} Performance Summary & Key Strategic Insights
  *(Based on provided Monthly Analysis, Performance Data, etc.)*
  - **Insight 1:** [Significant finding/trend from the quarter]
  - **Insight 2:** [...]
  - **Insight 3:** [...]
  *(Max 3-5 key insights)*

  ## 2. Final Status of Q{{CurrentQuarterNumber}} OKRs
  *(Based on provided "LACM_Goals_Quarter_Q{{CurrentQuarterNumber}}_{{Year}}" and performance data)*
  - **Objective 1:** [Objective text from input]
    *Final Status:* [Achieved / Partially Achieved / Not Achieved]
    *Key Results & Notes:*
      - KR 1.1: [KR text from input] - Status: [Final score/status]. Notes: [Brief reason/context from inputs]
      - KR 1.2: [...] - Status: [...]. Notes: [...]
  - **Objective 2:** [...]
  *(Cover all Q{{CurrentQuarterNumber}} Objectives)*

  ## 3. Strategic Alignment & Validity Check
  *(Based on comparison with "LACM_Strategy_*" and "LACM_SalesHandbook_*")*
  - [Assessment of how Q{{CurrentQuarterNumber}} outcomes impact a strategic assumption from "LACM_Strategy_*"]
  - [Suggestion: Review section X of "LACM_Strategy_*" based on finding Y]

  ## 4. Draft OKRs for Q{{CurrentQuarterNumber + 1}} {{CurrentYear}} (Proposal for Discussion)
  *(Considering strategic alignment, Q{{CurrentQuarterNumber}} outcomes, and Innovation Initiatives if provided)*
  - **Objective 1:** [Proposed Objective - Clear, ambitious, qualitative]
    *Alignment:* [Links to Strategy Goal X from "LACM_Strategy_*"]
    *Key Results:*
      - KR 1.1: [Specific, measurable result 1]
      - KR 1.2: [Specific, measurable result 2]
  - **Objective 2:** [Proposed Objective 2...]
  *(Propose 3-5 Objectives, each with 2-4 KRs)*
  ```
  **Constraints:** Ensure analysis is strategic. OKR evaluation should be factual. Draft OKRs must follow SMART principles. Base your output ONLY on the content of the provided documents.
  {{DocumentContext}}
```
```

#### 11. Innovation Idea Generation Workflow

* **Workflow Name (in TIP):** `LACM_Workflow_InnovationIdeaGeneration`
* **Description:** Generates new ideas based on various analytical documents.
* **Ritual Relevance:** LACM Phase 4.2.
* **Expected Input TIP Document Name(s) / Template Origin:**
    * `LACM_QuarterlyReviewPrep_*` (or monthly/weekly analyses)
    * `LACM_Competitors_*`
    * `LACM_CustomerFeedback_*`
    * `LACM_IdeaBacklog_*` (to avoid duplicates)
    * `LACM_Strategy_*`
* **TIP Process Workflow Definition:**
```yaml
# Workflow Name: LACM_Workflow_InnovationIdeaGeneration
# Description: Generates new ideas based on provided analytical and strategic documents.

inputDocumentSelectors: # User selects relevant context documents
  - "LACM_*Analysis*" # Various analysis reports
  - "LACM_Competitors_*"
  - "LACM_CustomerFeedback_*"
  - "LACM_IdeaBacklog_*"
  - "LACM_Strategy_*"
inputDateSelector: null
outputName: "LACM_NewIdeas_Q{{CurrentQuarterNumber}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  **Role:** You are an AI Ideation Catalyst supporting the LACM innovation process.
  **Goal:** Generate 5-10 concrete, relevant, and potentially innovative ideas for new products, services, process improvements, or strategic approaches. Base these ideas ONLY on the analysis of the provided input documents: recent performance/trend reports (various *Analysis*.md files), "LACM_Competitors_*", "LACM_CustomerFeedback_*", "LACM_Strategy_*". Check "LACM_IdeaBacklog_*" to avoid duplicating existing ideas.
  **Context:**
  - Performance & Trends: Content from various *Analysis*.md documents provided.
  - Market & Customer: Content from "LACM_Competitors_*", "LACM_CustomerFeedback_*".
  - Internal State: Content from "LACM_IdeaBacklog_*" (for checking existing ideas), "LACM_Strategy_*" (for identifying gaps or areas needing innovation).

  **Task:**
  1. **Analyze Context Deeply:** Review all provided input documents to identify:
      - Unmet customer needs or recurring complaints (from "LACM_CustomerFeedback_*").
      - Competitor weaknesses or market gaps (from "LACM_Competitors_*", analysis documents).
      - Emerging technological or market trends (from analysis documents).
      - Internal process bottlenecks or inefficiencies (from analysis documents, if mentioned).
      - Areas where "LACM_Strategy_*" indicates a need for new approaches or has gaps.
  2. **Generate Diverse Ideas:** Based on this analysis, generate 5-10 distinct ideas. Aim for a mix covering: New Product/Service concepts, Enhancements, Process Improvements, Novel Strategic Approaches. Do not suggest ideas already listed in the "LACM_IdeaBacklog_*" document.
  3. **Formulate Ideas Clearly:** For each idea, provide:
      - A short, descriptive title.
      - A brief explanation (1-3 sentences) of the core concept and the problem it solves or opportunity it addresses based on the input documents.
      - The primary source of inspiration from the input documents (e.g., "Inspired by customer feedback on X in `LACM_CustomerFeedback`", "Addresses competitor Y's weakness noted in `LACM_Competitors`").
  4. Generate the Markdown file.

  **Format:** Use the following Markdown structure precisely:
  ```markdown
  # New Ideas Generated - Q{{CurrentQuarterNumber}} {{CurrentYear}} (Based on Provided Documents)

  ## Idea 1: [Descriptive Title]
  - **Concept:** [Brief explanation of the idea and problem/opportunity addressed.]
  - **Inspiration (from input documents):** [Source document and specific point, e.g., "LACM_CustomerFeedback.md - recurring request for feature Z"]

  ## Idea 2: [Descriptive Title]
  - **Concept:** [...]
  - **Inspiration (from input documents):** [...]

  *(Repeat for 5-10 ideas)*
  ```
  **Constraints:** Ideas should be concrete. Ensure ideas are relevant to the business context defined in "LACM_Strategy_*". Aim for novelty where possible. Clearly state the inspiration/rationale based ONLY on the provided documents.
  {{DocumentContext}}
```
```

#### 12. Annual Strategy Analysis Preparation Workflow

* **Workflow Name (in TIP):** `LACM_Workflow_AnnualStrategyAnalysisPrep`
* **Description:** Synthesizes the year's performance and learnings to support annual strategic review.
* **Ritual Relevance:** LACM Phase 4.3.
* **Expected Input TIP Document Name(s) / Template Origin:**
    * All `LACM_Q*_ReviewPreparation_*` files for the year.
    * `LACM_YYYY_AnnualFinancialReport` (if created as a TIP doc by user)
    * User-created TIP documents summarizing market research.
    * The expiring `LACM_Strategy_*`.
* **TIP Process Workflow Definition:**
```yaml
# Workflow Name: LACM_Workflow_AnnualStrategyAnalysisPrep
# Description: Prepares a comprehensive analysis for the annual strategy review.

inputDocumentSelectors: # User selects all relevant documents for the year
  - "LACM_Q*_ReviewPreparation_*" # All quarterly review preps
  - "LACM_*_AnnualFinancialReport" # Optional, if user created this
  - "LACM_MarketResearchSummary_*" # Optional, user-created
  - "LACM_Strategy_*" # The strategy document for the year being reviewed
inputDateSelector: null
outputName: "LACM_{{Year}}_AnnualStrategyAnalysisInput"
prompt: |
  **Role:** You are an AI Senior Strategy Analyst supporting the LACM annual strategic review for the year {{CurrentYear}}.
  **Goal:** Synthesize the entire year's performance, learnings, and market context based on the provided quarterly review preparation documents, financial reports (if any), market research summaries (if any), and the expiring strategy document ("LACM_Strategy_*" for {{CurrentYear}}). Critically evaluate the effectiveness and ongoing validity of the current strategy. Identify major strategic challenges and opportunities to support leadership's decision-making for the upcoming year.
  **Context:**
  - Quarterly Performance: Content from "LACM_Q*_ReviewPreparation_*" documents for {{CurrentYear}}.
  - Financials (If provided): Content from "LACM_*_AnnualFinancialReport".
  - Market (If provided): Content from "LACM_MarketResearchSummary_*".
  - Current Strategy: The expiring "LACM_Strategy_*" for {{CurrentYear}}.
  - Completed Year: {{CurrentYear}}.

  **Task:**
  1. **Synthesize Annual Performance:** Analyze all inputs to identify the most significant strategic outcomes, trends, successes, and failures over the entire year. Compare overall performance against the goals stated in the expiring "LACM_Strategy_*".
  2. **Critically Evaluate Current Strategy:** Assess each major section/pillar of the expiring "LACM_Strategy_*". Based on the year's evidence from the inputs, which assumptions held true? Which were challenged? Which strategic initiatives were most/least effective? Is the overall strategic logic still sound given the current market context (as described in inputs)?
  3. **Identify Major Strategic Challenges & Opportunities:** Based on the year's performance and updated market understanding (from inputs), what are the 3-5 most critical strategic challenges the organization faces going into next year? What are the 2-3 most significant strategic opportunities?
  4. **Structure Findings for Leadership Review:** Generate a comprehensive Markdown report summarizing findings from tasks 1-3 in a clear, evidence-based manner suitable for executive review.

  **Format:** Use the following Markdown structure precisely:
  ```markdown
  # Annual Strategy Analysis Input - Year {{CurrentYear}} (Generated: {{CurrentDate_YYYY-MM-DD}})
  *Based on analysis of provided quarterly reviews, financial data (if any), market research (if any), and the {{CurrentYear}} strategy document.*

  ## 1. {{CurrentYear}} Performance Summary & Key Strategic Outcomes
  - [Overall Finding 1 regarding annual performance against strategic goals...]
  - [Overall Finding 2 regarding significant trends observed throughout the year...]
  - ...

  ## 2. Critical Evaluation of {{CurrentYear}} Strategy (from "LACM_Strategy_*")
  - **Strategic Pillar/Section A:** [Assessment of its validity/effectiveness based on evidence from inputs. Were assumptions met? What were key outcomes related to this pillar?]
  - **Strategic Pillar/Section B:** [...]
  - ...

  ## 3. Top Strategic Challenges Identified for {{CurrentYear + 1}}
  *(Based on analysis of all provided documents)*
  - [Challenge 1 description and evidence from inputs...]
  - [Challenge 2 description and evidence from inputs...]
  - ...

  ## 4. Top Strategic Opportunities Identified for {{CurrentYear + 1}}
  *(Based on analysis of all provided documents)*
  - [Opportunity 1 description and evidence from inputs...]
  - [Opportunity 2 description and evidence from inputs...]
  - ...
  ```
  **Constraints:** Maintain a high-level strategic perspective. Analysis must be evidence-based, drawing directly from the provided input documents. Evaluation of the strategy should be objective and critical. Challenges/Opportunities identified must be truly strategic. Output should be structured logically. Base your output ONLY on the content of the provided documents.
  {{DocumentContext}}
```
```

### **General Purpose / Pair Working Workflows (LACM Context)**

These are adaptable for various ad-hoc tasks within the LACM framework, such as drafting meeting summaries, analyzing specific text segments, or brainstorming. They are similar to the TIP Phase 2 general workflows but framed for LACM document inputs.

#### 13. Draft Document Section Workflow (LACM Pair Working)

* **Workflow Name (in TIP):** `LACM_Workflow_DraftSection`
* **Description:** Helps a team member draft a section of a TIP Document based on a provided topic, keywords, or an outline contained within another TIP Document.
* **Ritual Relevance:** LACM Phase 1.4: Continuous Documentation & Context Curation (ad-hoc assistance).
* **Expected Input TIP Document Name(s) / Template Origin:** User creates a TIP Document (e.g., `LACM_PairInput_DraftProductDescription_YYYY-MM-DD`) containing their specific request (topic, keywords, outline).

**TIP Process Workflow Definition:**
```yaml
# Workflow Name: LACM_Workflow_DraftSection
# Description: Drafts a text section based on topic, keywords, or outline from an input document.

inputDocumentSelectors:
  - "LACM_PairInput_*"
inputDateSelector: null
outputName: "LACM_DraftOutput_from_{{InputFileName | replace: 'LACM_PairInput_', '' | truncate: 30, ''}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  The input document titled "{{InputFileName}}" contains a request to draft a text section.
  The request might include a topic, keywords, a brief outline, or some source material from other parts of the document.

  Based **only** on the information provided in the input document below, please draft the requested text section.
  Aim for clarity, conciseness, and adhere to any specified tone or style if mentioned in the input.
  If the input is an outline, expand on each point.
  If keywords are provided, weave them naturally into the text.

  Input Document Content:
  ```
  {{DocumentContext}}
  ```

  Begin your response directly with the drafted section. Do not add any prefatory remarks or conversation.
```

#### 14. Brainstorm Ideas Workflow (LACM Pair Working)

* **Workflow Name (in TIP):** `LACM_Workflow_BrainstormIdeas`
* **Description:** Generates a list of ideas based on a problem statement, question, or topic provided in an input TIP Document.
* **Ritual Relevance:** Ad-hoc ideation, potentially supporting LACM Phase 4.2.
* **Expected Input TIP Document Name(s) / Template Origin:** User creates a TIP Document (e.g., `LACM_PairInput_BrainstormSolutionsForX_YYYY-MM-DD`) detailing the brainstorming subject.

**TIP Process Workflow Definition:**
```yaml
# Workflow Name: LACM_Workflow_BrainstormIdeas
# Description: Brainstorms ideas based on a problem statement or topic from an input document.

inputDocumentSelectors:
  - "LACM_PairInput_*"
inputDateSelector: null
outputName: "LACM_BrainstormOutput_from_{{InputFileName | replace: 'LACM_PairInput_', '' | truncate: 30, ''}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  The input document "{{InputFileName}}" contains a request for brainstorming ideas.
  This request could be a problem statement, a question, or a topic.

  Based **only** on the information and request provided in the input document below, generate a list of 5-10 distinct ideas related to the core request.
  Present the ideas as a bulleted list. Each idea should be concise.

  Input Document Content:
  ```
  {{DocumentContext}}
  ```

  Begin your response directly with the list of brainstormed ideas. Do not add any prefatory remarks.
```

#### 15. Analyze Text Segment Workflow (LACM Pair Working)

* **Workflow Name (in TIP):** `LACM_Workflow_AnalyzeTextSegment`
* **Description:** Performs a specific analysis (e.g., identify pros and cons, extract key arguments, summarize a short segment) on a piece of text provided in an input TIP Document. The user specifies the type of analysis in their input document.
* **Ritual Relevance:** Ad-hoc analysis for various LACM phases.
* **Expected Input TIP Document Name(s) / Template Origin:** User creates a TIP Document (e.g., `LACM_PairInput_AnalyzeFeedback_YYYY-MM-DD`) with the text and the analysis request.

**TIP Process Workflow Definition:**
```yaml
# Workflow Name: LACM_Workflow_AnalyzeTextSegment
# Description: Analyzes a provided text segment based on instructions in the input document.

inputDocumentSelectors:
  - "LACM_PairInput_*"
inputDateSelector: null
outputName: "LACM_AnalysisOutput_from_{{InputFileName | replace: 'LACM_PairInput_', '' | truncate: 30, ''}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  The input document "{{InputFileName}}" contains a segment of text and a specific request for how to analyze that text.
  Carefully read the "Analysis Request" (or similar instruction) and the "Text to Analyze" (or similar content section) within the input document.

  Perform **only** the requested analysis on the provided text segment.
  Structure your output clearly based on the nature of the analysis requested. For example, if asked for pros and cons, use those headings. If asked for themes, list them. If asked for a summary, provide a concise summary.

  Input Document Content:
  ```
  {{DocumentContext}}
  ```

  Begin your response directly with the results of your analysis. Do not add any prefatory remarks.
```

## **Notes on Usage by Team Users in TIP**

* To use these workflows, navigate to the "Run Workflows" section in TIP.
* Select the desired LACM workflow by its name (e.g., `LACM_Workflow_DailyNewsAnalysis`).
* TIP will then prompt you to select the input TIP Document(s) based on the `inputDocumentSelectors` defined in the workflow.
    * Ensure your input TIP Documents are named according to conventions that match the selectors (e.g., a document named `LACM_ManualNewsInput_2025-05-11` for the `LACM_Workflow_DailyNewsAnalysis`).
    * For "Pair Working" workflows (like `LACM_Workflow_DraftSection`), you will typically create a new TIP Document (e.g., `LACM_PairInput_MyTopic_YYYY-MM-DD`) containing the specific text or instructions for the LLM, then select this document as input.
* The workflow will process the content of the selected input document(s) using the LLM and its defined prompt.
* A new TIP Document will be created with the output, named according to the `outputName` template defined in the workflow. You can then review, edit, and use this AI-generated document as part of the LACM process.
* Since the LLM in TIP has no internet or external tool access, **all necessary information for the workflow must be contained within the selected input TIP Document(s).**

## **Notes for Administrators in TIP**

* These workflow definitions should be created in the "Workflow Management" area of TIP, accessible via the Admin interface.
* The "Workflow Name (in TIP)" mentioned above is the human-readable name you assign to the Process Workflow when creating it. This is the name Team Users will see.
* The YAML content provided for each workflow should be pasted into the Markdown editor when creating/editing the Process Workflow's content definition in TIP.
* Ensure that the prompts are well-suited for the capabilities of the locally configured LLM in your TIP instance. Refine prompts based on observed output quality and team feedback.
* The global LLM model and temperature settings configured in the TIP backend will apply to these workflows unless the underlying Ollama service or TIP itself allows overriding these per call in the future (currently, PRD indicates global settings).
* Regularly review the effectiveness of these workflows and update their prompts or structure as the LACM process evolves within the team. Collaboration with teams on prompt improvements (documented in "Prompt Development Workshop" TIP Documents) is encouraged.
* Make sure these workflows are marked as "globally visible" so that team users can access and execute them.
