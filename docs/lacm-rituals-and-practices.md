# **Lean AI Co-Management (LACM) Rituals & Practices for Team Intelligence Platform (TIP)**

**Version:** 1.0
**Date:** May 11, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0
**Templates Library Referenced:** [LACM Templates Library for TIP](./lacm-templates-library.md)
**Workflow Library Referenced:** [LACM Workflow Library for TIP](./lacm-workflow-library.md)

## **Table of Contents**

- [**Lean AI Co-Management (LACM) Rituals \& Practices for Team Intelligence Platform (TIP)**](#lean-ai-co-management-lacm-rituals--practices-for-team-intelligence-platform-tip)
  - [**Table of Contents**](#table-of-contents)
  - [**1. Executive Summary**](#1-executive-summary)
  - [**2. Prerequisites: Initial Document Setup in TIP**](#2-prerequisites-initial-document-setup-in-tip)
  - [**3. Core Principles of LACM in TIP**](#3-core-principles-of-lacm-in-tip)
  - [**4. LACM Overview: Phases and Routines in TIP**](#4-lacm-overview-phases-and-routines-in-tip)
  - [**5. Phase 1: Daily Routine in TIP**](#5-phase-1-daily-routine-in-tip)
    - [5.1. Daily News \& Environment Analysis](#51-daily-news--environment-analysis)
    - [5.2. Daily Review \& Context Capture](#52-daily-review--context-capture)
    - [5.3. Daily Planning](#53-daily-planning)
    - [5.4. Continuous Documentation \& Context Curation](#54-continuous-documentation--context-curation)
  - [**6. Phase 2: Weekly Routine in TIP**](#6-phase-2-weekly-routine-in-tip)
    - [6.1. Weekly Analysis Summary \& Trend Identification](#61-weekly-analysis-summary--trend-identification)
    - [6.2. Weekly Review \& Retrospective](#62-weekly-review--retrospective)
    - [6.3. Weekly Planning (Preview for Next Week)](#63-weekly-planning-preview-for-next-week)
  - [**7. Phase 3: Monthly Routine in TIP**](#7-phase-3-monthly-routine-in-tip)
    - [7.1. Monthly Analysis Summary \& Strategy Check](#71-monthly-analysis-summary--strategy-check)
    - [7.2. Context Size Management (Context Condensation)](#72-context-size-management-context-condensation)
    - [7.3. Monthly Process Retrospective \& Update](#73-monthly-process-retrospective--update)
  - [**8. Phase 4: Quarterly \& Annual Routine in TIP**](#8-phase-4-quarterly--annual-routine-in-tip)
    - [8.1. Quarterly Review \& Goal Setting](#81-quarterly-review--goal-setting)
    - [8.2. Innovation Management: Idea Generation \& Evaluation](#82-innovation-management-idea-generation--evaluation)
    - [8.3. Annual Strategy Review \& Long-Term Planning](#83-annual-strategy-review--long-term-planning)
  - [**9. Ad-hoc AI Pair Working in TIP**](#9-ad-hoc-ai-pair-working-in-tip)
  - [**10. Implementation Notes for TIP Users**](#10-implementation-notes-for-tip-users)
    - [10.1. Document Naming Conventions](#101-document-naming-conventions)
    - [10.2. Using TIP Workflows](#102-using-tip-workflows)
    - [10.3. Reviewing and Editing AI Outputs](#103-reviewing-and-editing-ai-outputs)
  - [**11. Continuous Improvement of LACM Practices in TIP**](#11-continuous-improvement-of-lacm-practices-in-tip)
  - [**12. Appendices**](#12-appendices)
    - [12.1. Referenced LACM Templates Library for TIP](#121-referenced-lacm-templates-library-for-tip)
    - [12.2. Referenced LACM Workflow Library for TIP](#122-referenced-lacm-workflow-library-for-tip)

## **1. Executive Summary**

This document outlines the Lean AI Co-Management (LACM) rituals and practices, adapted for use within the Team Intelligence Platform (TIP). LACM provides a structured approach for teams to integrate Artificial Intelligence (AI) into their daily, weekly, monthly, and strategic operations, leveraging TIP's capabilities for document management, versioning, and AI-driven workflow execution.

The focus is on transforming AI into an active collaborator. By following these rituals, teams will use TIP Documents as their shared knowledge base and TIP Process Workflows (pre-defined by Administrators) to assist with analysis, documentation, planning, and other knowledge-intensive tasks. This guide details the "how-to" for team users to implement these practices directly within the TIP environment, enhancing decision-making, efficiency, and knowledge preservation.

---

## **2. Prerequisites: Initial Document Setup in TIP**

Before commencing the LACM routines, your team needs a set of foundational TIP Documents. These provide essential context for both the team and the AI workflows. An Administrator should have already created the necessary "Document Templates" in TIP, as defined in the `LACM Templates Library for TIP`.

Your team should create the following TIP Documents using those templates:
* `LACM_Strategy_Current` (from `LACM_Strategy`)
* `LACM_Competitors_Current` (from `LACM_Competitors`)
* `LACM_TargetMarkets_Current` (from `LACM_TargetMarkets`)
* `LACM_Goals_Q[CurrentQuarter]_[CurrentYear]` (from `LACM_QuarterlyGoals`)
* `LACM_KW[CurrentWeek]_WeeklyPlanPreview_InitialSetup` (from `LACM_WeeklyPlanPreview_Initial` for the very first week)
* `LACM_TaskList_Current` (from `LACM_TaskList`)
* `LACM_AvailableTime_Current` (from `LACM_AvailableTime`)
* `LACM_Processes_Internal` (from `LACM_Processes`, can be initially basic)
* Other documents like `LACM_IdeaBacklog`, `LACM_CustomerFeedback_Log`, `LACM_SalesHandbook_Internal` can be created as needed using their respective templates.

Refer to the (separate) "LACM Onboarding Guide for TIP" for detailed instructions on creating and populating these initial documents. Ensure these core documents are saved in TIP before starting Phase 1.

---

## **3. Core Principles of LACM in TIP**

The LACM process in TIP is guided by these core principles:

1.  **Collective Context in TIP:** All knowledge, inputs, and outputs for AI and team collaboration reside as versioned **TIP Documents**. Consistent naming is key.
2.  **Explicit AI Roles via TIP Workflows:** AI performs defined tasks (e.g., Analyst, Documenter, Planning Assistant) through pre-configured **TIP Process Workflows** that operate on TIP Documents.
3.  **Integration in Routines:** AI-assisted steps are embedded in regular daily, weekly, monthly, and strategic cycles within the TIP environment.
4.  **Transparent Evaluation:** Humans always review, edit (if necessary), and explicitly save (creating a new version) AI-generated TIP Documents before they become part of the official knowledge base.
5.  **Continuous Learning:** The process facilitates iterative improvement of inputs to TIP Workflows, manual processes, and the knowledge base itself, all documented within TIP.
6.  **Markdown Standard:** Markdown is the universal format for all TIP Documents, ensuring human and machine readability.
7.  **Local AI Processing:** All AI processing via TIP Workflows uses the locally configured LLM, ensuring data privacy. No internet or external tool access by the LLM is assumed or utilized.

---

## **4. LACM Overview: Phases and Routines in TIP**

The LACM process is structured into iterative phases and routines:

* **Phase 1: Daily Routine:** Focus on operational excellence, capturing daily context, and maintaining alignment with weekly goals.
* **Phase 2: Weekly Routine:** Emphasizes tactical adjustments, team learning, process improvement, and setting the focus for the upcoming week.
* **Phase 3: Monthly Routine:** Zooms out to check strategic alignment, identify larger trends, and manage the size and health of the TIP knowledge base.
* **Phase 4: Quarterly & Annual Routine:** Addresses significant strategic planning, goal setting, and innovation.

Each routine involves specific rituals and practices detailed below, leveraging TIP Documents and Process Workflows.

---

## **5. Phase 1: Daily Routine in TIP**

**Objective:** Maintain operational momentum, capture daily context efficiently for knowledge preservation within TIP, and ensure alignment with weekly goals for enhanced decision-making.

### 5.1. Daily News & Environment Analysis

* **Purpose:** To identify relevant external events (from manually gathered information) that might impact operations or strategy, enabling proactive adjustments.
* **Cadence & Format:** Daily, typically early morning (approx. 15-30 min for manual input, then 5-10 min for AI + review).
* **Participants:** Team Member(s) (for manual research and input), AI (via TIP Workflow).
* **Process in TIP:**
    1.  **How (User - Manual Input):**
        * Manually research relevant news, articles, competitor updates, market signals from the last 24-48 hours.
        * In TIP, create a new TIP Document named `LACM_ManualNewsInput_YYYY-MM-DD` (e.g., `LACM_ManualNewsInput_2025-05-11`) using the `LACM_ManualNewsInput` from the LACM Templates Library.
        * Paste summaries, key points, or relevant text snippets into this document. Save the document.
    2.  **How (User - AI Processing):**
        * Navigate to "Run Workflows" in TIP.
        * Select the Admin-created Process Workflow: `LACM_Workflow_DailyNewsAnalysis`.
        * When prompted, select the following TIP Documents as inputs:
            * The `LACM_ManualNewsInput_YYYY-MM-DD` you just created.
            * The current `LACM_Strategy_Current`.
            * The current `LACM_Competitors_Current`.
            * The current `LACM_TargetMarkets_Current`.
        * Execute the workflow.
    3.  **AI Does (via TIP Workflow `LACM_Workflow_DailyNewsAnalysis`):**
        * Processes the content of the selected TIP Documents.
        * Analyzes the manually provided news against the strategic context documents.
        * Generates a new TIP Document summarizing relevant news and potential impacts.
    4.  **You Do (User - Review):**
        * Open and briefly review the AI-generated TIP Document (e.g., `LACM_DailyNewsAnalysis_2025-05-11_..`) for relevant insights. This document will be an input for subsequent steps. No explicit save/commit is needed by you on this AI output document unless you wish to make corrective edits (which would create a new version).
* **Tools:** TIP for document creation/editing and workflow execution. External tools/websites for manual news research.
* **Artifacts (TIP Documents):**
    * Input: `LACM_ManualNewsInput_YYYY-MM-DD`
    * Context: `LACM_Strategy_Current`, `LACM_Competitors_Current`, `LACM_TargetMarkets_Current`
    * Output: `LACM_DailyNewsAnalysis_YYYY-MM-DD_..` (exact name based on workflow output template)
* **Value:** Early awareness of opportunities/threats from your curated information, provides external context for daily decisions.
* **TIP:** If the AI analysis seems off, review the content and clarity of your `LACM_ManualNewsInput_YYYY-MM-DD` and the detail in your strategy/competitor/market documents.

### 5.2. Daily Review & Context Capture

* **Purpose:** To review the past 24h (progress, issues, learnings) and capture this operational context efficiently in TIP for knowledge preservation and planning.
* **Cadence & Format:** Daily (e.g., 15-20 min for manual input, then 5-10 min for AI + review).
* **Participants:** All Team Members (for providing input), AI (via TIP Workflow).
* **Process in TIP:**
    1.  **How (User - Manual Input):**
        * Reflect on your last 24 hours of work (achievements, challenges, interactions, learnings).
        * In TIP, create/update a TIP Document, e.g., `LACM_DailyLogInput_Team_YYYY-MM-DD` (or individual files like `LACM_DailyLogInput_UserA_YYYY-MM-DD` then manually consolidate if preferred) using `LACM_DailyLogInput`. Enter your reflections. Save the document.
    2.  **How (User - AI Processing):**
        * Navigate to "Run Workflows" in TIP.
        * Select the Admin-created Process Workflow: `LACM_Workflow_DailyLogGenerator`.
        * When prompted, select as inputs:
            * The `LACM_DailyLogInput_..._YYYY-MM-DD` containing the team's (or your) raw notes.
            * The previous day's plan (e.g., `LACM_DailyPlan_YYYY-MM-DD-1`).
            * Today's analysis document (e.g., `LACM_DailyNewsAnalysis_YYYY-MM-DD_..`).
        * Execute the workflow.
    3.  **AI Does (via TIP Workflow `LACM_Workflow_DailyLogGenerator`):**
        * Processes the content of the selected TIP Documents.
        * Structures the inputs into a draft daily log.
    4.  **You Do (User - Review & Commit):**
        * Open the AI-generated TIP Document (e.g., `LACM_DailyLog_YYYY-MM-DD_..`).
        * **Crucially, review this draft carefully.** Correct inaccuracies, add missing details, refine phrasing directly in the TIP editor.
        * Once satisfied, **Save** the document in TIP. This action creates a new version, making it the official log for the day.
* **Tools:** TIP for document creation/editing and workflow execution.
* **Artifacts (TIP Documents):**
    * Input: `LACM_DailyLogInput_..._YYYY-MM-DD`, `LACM_DailyPlan_YYYY-MM-DD-1`, `LACM_DailyNewsAnalysis_YYYY-MM-DD_..`.
    * Output: `LACM_DailyLog_YYYY-MM-DD_..` (reviewed and saved by user).
* **Value:** Captures vital operational context, creates a record of progress and issues, documents learnings.
* **TIP:** Be thorough in your review and editing of the AI-generated daily log. Consistent structure (guided by the AI's output format) is key for future analysis.

### 5.3. Daily Planning

* **Purpose:** To define actionable and prioritized tasks for the next 24h, aligned with weekly/quarterly goals, considering available capacity, and informed by daily context.
* **Cadence & Format:** Daily (following Daily Review, approx. 15-30 min including AI + review).
* **Participants:** All Team Members (review and refine plan), AI (via TIP Workflow).
* **Process in TIP:**
    1.  **How (User - Input Preparation & AI Processing):**
        * Ensure your `LACM_AvailableTime_Current` and `LACM_TaskList_Current` TIP Documents are up-to-date. Save any changes.
        * Navigate to "Run Workflows" in TIP.
        * Select the Admin-created Process Workflow: `LACM_Workflow_DailyPlanGenerator`.
        * When prompted, select all relevant input TIP Documents:
            * Today's `LACM_DailyLog_YYYY-MM-DD_..` (from step 5.2).
            * Today's `LACM_DailyNewsAnalysis_YYYY-MM-DD_..` (from step 5.1).
            * Current `LACM_Strategy_Current`.
            * Current `LACM_Goals_Quarter_Q[CurrentQuarter]_[CurrentYear]`.
            * Current week's `LACM_KW[CurrentWeek]_WeeklyPlanPreview_...`.
            * Current `LACM_TaskList_Current`.
            * Current `LACM_AvailableTime_Current`.
        * Execute the workflow.
    2.  **AI Does (via TIP Workflow `LACM_Workflow_DailyPlanGenerator`):**
        * Analyzes the provided TIP Documents.
        * Prioritizes tasks, considers available time.
        * Generates a draft daily plan TIP Document.
    3.  **You Do (User - Review & Commit):**
        * Open the AI-generated TIP Document (e.g., `LACM_DailyPlan_YYYY-MM-DD_..`).
        * Review the plan. Does it make sense? Is it realistic? Are priorities correct?
        * Use the structure from `LACM_DailyPlanReview` as a mental guide for your review, or to manually adjust/override sections.
        * Edit the plan directly in the TIP editor as needed.
        * Once satisfied, **Save** the document in TIP. This is your team's plan for the day.
        * Manually update your primary task management system (if external to `LACM_TaskList_Current`) based on this plan.
* **Tools:** TIP for document management and workflow execution.
* **Artifacts (TIP Documents):**
    * Inputs: Various context documents as listed above.
    * Output: `LACM_DailyPlan_YYYY-MM-DD_..` (reviewed and saved by user).
* **Value:** Provides a clear, prioritized, and achievable plan for the day, aligned with larger goals.
* **TIP:** The AI's plan is a *suggestion*. Use your judgment. If the plan seems too ambitious, adjust it or update `LACM_AvailableTime_Current` for the next day.

### 5.4. Continuous Documentation & Context Curation

* **Purpose:** To maintain an up-to-date, accessible, and version-controlled knowledge base in TIP.
* **Cadence & Format:** Continuously, as needed, throughout the day.
* **Participants:** All Team Members. AI can assist on-demand.
* **Process in TIP:**
    1.  **How (User - Manual Documentation):**
        * As you attend meetings, make decisions, conduct research, or complete work, capture notes and outcomes directly in new or existing TIP Documents.
        * Use clear, consistent naming conventions (e.g., `LACM_MeetingSummary_[Topic]_[YYYY-MM-DD]` from `LACM_MeetingSummary`, or `LACM_DecisionLog_TeamName` from `LACM_DecisionLog`).
        * Reference other relevant TIP Documents by name within your notes to create manual links (e.g., "Decision related to `LACM_Strategy_Current` section 4").
        * Save your documents regularly in TIP.
    2.  **How (User - AI-Assisted Documentation, Ad-hoc):**
        * For tasks like summarizing meeting notes or analyzing a piece of text, prepare an input TIP Document (e.g., `LACM_PairInput_SummarizeNotes_YYYY-MM-DD`) with the raw text and your request.
        * Navigate to "Run Workflows" in TIP. Select a general-purpose workflow like `LACM_Workflow_DraftSection` or `LACM_Workflow_AnalyzeTextSegment`.
        * Provide your prepared TIP Document as input.
        * Execute the workflow.
    3.  **AI Does (via selected TIP Workflow):**
        * Processes your input document and generates an output TIP Document (e.g., `LACM_DraftOutput_SummarizeNotes_..`).
    4.  **You Do (User - Review & Integrate):**
        * Review the AI-generated TIP Document. Edit and refine it.
        * Incorporate the polished content into your main project documentation, meeting summaries, or other relevant TIP Documents. Save these updates.
* **Tools:** TIP for document creation, editing, versioning, and workflow execution.
* **Artifacts (TIP Documents):** Various project notes, meeting summaries, decision logs, research notes, etc. All stored and versioned in TIP.
* **Value:** Builds the core "Collective Context." Makes information searchable and reusable. Preserves knowledge.
* **TIP:** Develop consistent naming conventions for your TIP Documents. Manually "link" related documents by explicitly mentioning their names in the text (e.g., "As detailed in `LACM_Competitors_Current`...").

---

## **6. Phase 2: Weekly Routine in TIP**

**Objective:** Step back from daily execution, analyze weekly trends using TIP-based data, learn from experience, improve processes (documented in TIP), and set the focus for the upcoming week.

### 6.1. Weekly Analysis Summary & Trend Identification

* **Purpose:** To synthesize daily external analyses (from TIP Documents) to identify emerging trends and assess their cumulative strategic relevance.
* **Cadence & Format:** Once per week (e.g., Friday PM or Monday AM, approx. 30-45 min including AI + review).
* **Participants:** Team Member(s) (for selecting inputs and review), AI (via TIP Workflow).
* **Process in TIP:**
    1.  **How (User - AI Processing):**
        * Navigate to "Run Workflows" in TIP.
        * Select the Admin-created Process Workflow: `LACM_Workflow_WeeklyAnalysis`.
        * When prompted, select the `LACM_DailyNewsAnalysis_YYYY-MM-DD_..` TIP Documents from the past 7 days, and the current `LACM_Strategy_Current`.
        * Execute the workflow.
    2.  **AI Does (via TIP Workflow `LACM_Workflow_WeeklyAnalysis`):**
        * Processes the selected daily analysis documents and the strategy document.
        * Identifies recurring themes/trends and assesses strategic relevance.
        * Generates a new TIP Document (e.g., `LACM_KW[CurrentWeek]_WeeklyAnalysis_YYYY-MM-DD`).
    3.  **You Do (User - Review & Commit):**
        * Open and review the AI-generated weekly analysis TIP Document.
        * Discuss findings with the team. Add any manual insights or corrections.
        * Save the document in TIP.
* **Tools:** TIP for document selection and workflow execution.
* **Artifacts (TIP Documents):**
    * Input: Multiple `LACM_DailyNewsAnalysis_YYYY-MM-DD_..` files, `LACM_Strategy_Current`.
    * Output: `LACM_KW[CurrentWeek]_WeeklyAnalysis_YYYY-MM-DD`.
* **Value:** Higher-level view of the external environment, informs weekly planning.
* **TIP:** If insights are weak, check if the daily news inputs were sufficiently detailed or if the `LACM_Strategy_Current` needs more specific keywords/focus areas.

### 6.2. Weekly Review & Retrospective

* **Purpose:** To reflect on the past week's work, identify improvements, and foster team learning, with AI assisting in data preparation.
* **Cadence & Format:** Once per week (e.g., 60-90 min).
* **Participants:** All Team Members, Facilitator, AI (via TIP Workflow for prep).
* **Process in TIP:**
    1.  **How (User - Retro Prep - AI Processing):**
        * Navigate to "Run Workflows" in TIP.
        * Select the Admin-created Process Workflow: `LACM_Workflow_WeeklyRetroPrep`.
        * When prompted, select as inputs:
            * The `LACM_DailyLog_YYYY-MM-DD_..` TIP Documents from the past 7 days.
            * The `LACM_KW[CurrentWeek-1]_WeeklyPlanPreview_...` (the plan for the week being reviewed).
            * Optionally, the current `LACM_Processes_Internal`.
        * Execute the workflow.
    2.  **AI Does (via TIP Workflow `LACM_Workflow_WeeklyRetroPrep`):**
        * Analyzes the daily logs and weekly plan.
        * Generates a `LACM_KW[CurrentWeek]_RetroPreparation_YYYY-MM-DD` TIP Document with data points and discussion questions.
    3.  **You Do (User - Conduct Retro & Document):**
        * Team reviews the AI-generated `LACM_KW[CurrentWeek]_RetroPreparation_YYYY-MM-DD`.
        * Conduct the retrospective discussion (What went well? Challenges? Learnings? Improvements?).
        * Manually create a new TIP Document named `LACM_KW[CurrentWeek]_WeeklyRetroSummary_YYYY-MM-DD` using `LACM_WeeklyRetroSummary`. Capture key discussion points and agreed action items in this document.
        * Save the summary document. If process changes are agreed, update the `LACM_Processes_Internal` TIP Document and save it.
        * Manually transfer action items to `LACM_TaskList_Current` or your external task manager.
* **Tools:** TIP for document management and workflow execution.
* **Artifacts (TIP Documents):**
    * Input: Multiple `LACM_DailyLog_..` files, `LACM_KW[CurrentWeek-1]_WeeklyPlanPreview_...`, `LACM_Processes_Internal`.
    * AI Output: `LACM_KW[CurrentWeek]_RetroPreparation_YYYY-MM-DD`.
    * Human Output: `LACM_KW[CurrentWeek]_WeeklyRetroSummary_YYYY-MM-DD`, updated `LACM_Processes_Internal`, updated `LACM_TaskList_Current`.
* **Value:** Drives continuous improvement, addresses recurring issues.
* **TIP:** Use the AI-prepared document as a starting point for discussion, not the only source. Human insights and feelings are crucial in a retrospective.

### 6.3. Weekly Planning (Preview for Next Week)

* **Purpose:** To establish focus areas and key objectives for the upcoming week, translating strategic goals and recent learnings into a tactical roadmap.
* **Cadence & Format:** Once per week (typically after Weekly Retro, approx. 30-60 min).
* **Participants:** All Team Members (review & refine), AI (via TIP Workflow).
* **Process in TIP:**
    1.  **How (User - AI Processing):**
        * Navigate to "Run Workflows" in TIP.
        * Select the Admin-created Process Workflow: `LACM_Workflow_WeeklyPlanPreviewGenerator`.
        * When prompted, select as inputs:
            * Current week's `LACM_KW[CurrentWeek]_WeeklyAnalysis_YYYY-MM-DD`.
            * Current week's `LACM_KW[CurrentWeek]_WeeklyRetroSummary_YYYY-MM-DD`.
            * Current `LACM_Strategy_Current`.
            * Current `LACM_Goals_Quarter_Q[CurrentQuarter]_[CurrentYear]`.
            * Current `LACM_TaskList_Current`.
            * Optionally, `LACM_PrioritizedInnovationInitiatives_Current`.
        * Execute the workflow.
    2.  **AI Does (via TIP Workflow `LACM_Workflow_WeeklyPlanPreviewGenerator`):**
        * Analyzes inputs, proposes objectives for the next week.
        * Generates a draft `LACM_KW[NextWeek]_WeeklyPlanPreview_YYYY-MM-DD` TIP Document.
    3.  **You Do (User - Review & Commit):**
        * Open and review the AI-generated draft plan. Does it capture the right focus? Are objectives clear and achievable?
        * Edit and refine the plan directly in the TIP editor.
        * Save the document in TIP. This becomes a key input for next week's Daily Planning.
* **Tools:** TIP for document management and workflow execution.
* **Artifacts (TIP Documents):**
    * Inputs: Various context documents as listed above.
    * Output: `LACM_KW[NextWeek]_WeeklyPlanPreview_YYYY-MM-DD`.
* **Value:** Sets clear priorities for the upcoming week.
* **TIP:** Ensure the "Why" for each objective in the preview is clear and compelling for the team.

---

## **7. Phase 3: Monthly Routine in TIP**

**Objective:** Consolidate weekly insights for a strategic perspective, check alignment with goals, identify larger trends, and manage knowledge base size.

### 7.1. Monthly Analysis Summary & Strategy Check

* **Purpose:** To synthesize weekly trends, evaluate progress against strategy and quarterly goals, and identify emerging strategic issues.
* **Cadence & Format:** Once per month (approx. 45-90 min including AI + review).
* **Participants:** Management/Strategy Lead(s), Team Representatives, AI (via TIP Workflow).
* **Process in TIP:**
    1.  **How (User - AI Processing):**
        * Select `LACM_Workflow_MonthlyAnalysisStrategyCheck`.
        * Inputs: `LACM_KW*_WeeklyAnalysis_*` (for the month), `LACM_Strategy_Current`, `LACM_Goals_Quarter_Current`, previous month's `LACM_MonthlyAnalysisStrategyCheck_..` (optional).
    2.  **AI Does:** Generates `LACM_YYYY-MM_MonthlyAnalysisStrategyCheck`.
    3.  **You Do:** Review, discuss, and save the document. Use as input for strategic discussions.
* **Artifacts:** `LACM_YYYY-MM_MonthlyAnalysisStrategyCheck`.
* **Value:** Consolidated strategic view, data-informed reviews.

### 7.2. Context Size Management (Context Condensation)

* **Purpose:** To summarize older data while preserving essential insights, ensuring optimal AI performance.
* **Cadence & Format:** Monthly or as needed (requires significant human review post-AI).
* **Participants:** Knowledge Manager/Team Rep, AI (via TIP Workflow).
* **Process in TIP:**
    1.  **How (User - AI Processing):**
        * Select `LACM_Workflow_ContextCondensation`.
        * Inputs: Select multiple older TIP documents (e.g., daily logs, weekly analyses from >60 days ago).
    2.  **AI Does:** Generates a `LACM_CondensedContext_[Period]_[Date]` summary document.
    3.  **You Do:** **Carefully review the AI-generated summary.** Ensure no critical long-term information was lost. Save the summary. Then, *manually* decide whether to archive or delete the original detailed TIP documents (this action is outside the AI workflow and is a manual TIP operation).
* **Artifacts:** `LACM_CondensedContext_[Period]_[Date]`.
* **Value:** Keeps knowledge base lean and relevant for AI.
* **TIP:** This step requires significant human judgment. The AI provides a *draft* condensation. The decision to remove original documents is critical.

### 7.3. Monthly Process Retrospective & Update

* **Purpose:** Dedicated review of operational processes based on a month's feedback for documented improvements.
* **Cadence & Format:** Once per month (approx. 60-90 min).
* **Participants:** Process Owner(s), Team Members, AI (via TIP Workflow for prep).
* **Process in TIP:**
    1.  **How (User - AI Processing):**
        * Select `LACM_Workflow_MonthlyProcessRetroPrep`.
        * Inputs: `LACM_KW*_WeeklyRetroSummary_*` (for the month), `LACM_Processes_Internal`.
    2.  **AI Does:** Generates `LACM_YYYY-MM_ProcessRetroPreparation` summarizing process feedback.
    3.  **You Do:** Review AI prep doc. Discuss process issues. Manually update the `LACM_Processes_Internal` TIP Document with agreed improvements. Save the changes.
* **Artifacts:** `LACM_YYYY-MM_ProcessRetroPreparation`, updated `LACM_Processes_Internal`.
* **Value:** Systematic improvement of core operational workflows.

---

## **8. Phase 4: Quarterly & Annual Routine in TIP**

**Objective:** Review long-term performance, adjust strategy, drive innovation, and set overarching direction.

### 8.1. Quarterly Review & Goal Setting

* **Purpose:** Review quarterly performance against OKRs, analyze strategic checks, and define OKRs for the next quarter.
* **Cadence & Format:** Once per quarter (major planning session, can be several hours).
* **Participants:** Management/Strategy Lead(s), Team Representatives, AI (via TIP Workflow for prep).
* **Process in TIP:**
    1.  **How (User - AI Processing):**
        * Select `LACM_Workflow_QuarterlyReviewPrep`.
        * Inputs: `LACM_YYYY-MM_MonthlyAnalysisStrategyCheck` (for the quarter), expiring `LACM_Goals_Quarter_Current`, `LACM_Strategy_Current`, `LACM_SalesHandbook_Internal` (optional), `LACM_PrioritizedInnovationInitiatives_Current` (optional), other user-created performance summary TIP documents.
    2.  **AI Does:** Generates `LACM_Q[CurrentQuarter]_[Year]_ReviewPreparation_DraftOKRs_Q[NextQuarter]`.
    3.  **You Do:** Use AI prep doc for strategic discussion. Manually create/finalize the official `LACM_Goals_Quarter_Q[NextQuarter]_[Year]` using `LACM_QuarterlyGoals`. Update `LACM_Strategy_Current` if major shifts. Save all documents.
* **Artifacts:** `LACM_Q[CurrentQuarter]_[Year]_ReviewPreparation_DraftOKRs_Q[NextQuarter]`, new `LACM_Goals_Quarter_Q[NextQuarter]_[Year]`, potentially updated `LACM_Strategy_Current`.
* **Value:** Data-driven quarterly planning, strategic alignment, clear 90-day direction.

### 8.2. Innovation Management: Idea Generation & Evaluation

* **Purpose:** Systematically foster, capture, evaluate, and prioritize new ideas.
* **Cadence & Format:** Quarterly, or ad-hoc.
* **Participants:** All Team Members, Innovation Lead, AI (via TIP Workflow for idea generation).
* **Process in TIP:**
    1.  **How (User - Idea Generation - AI Processing):**
        * Select `LACM_Workflow_InnovationIdeaGeneration`.
        * Inputs: Recent analysis TIP documents, `LACM_Competitors_Current`, `LACM_CustomerFeedback_Log`, `LACM_IdeaBacklog`, `LACM_Strategy_Current`.
    2.  **AI Does:** Generates `LACM_NewIdeas_Q[CurrentQuarter]_YYYY-MM-DD`.
    3.  **You Do (Manual Evaluation & Prioritization):**
        * Review AI-generated ideas and add any human-generated ideas to the `LACM_IdeaBacklog` TIP Document (using `LACM_IdeaBacklog`).
        * Periodically evaluate ideas in the backlog.
        * Update the `LACM_PrioritizedInnovationInitiatives_Current` TIP Document (using `LACM_PrioritizedInnovationInitiatives`) with promising initiatives. Save all documents.
* **Artifacts:** `LACM_NewIdeas_Q[CurrentQuarter]_YYYY-MM-DD`, updated `LACM_IdeaBacklog`, updated `LACM_PrioritizedInnovationInitiatives_Current`.
* **Value:** Structured approach to innovation.

### 8.3. Annual Strategy Review & Long-Term Planning

* **Purpose:** Thorough review of overall strategy, vision, and long-term objectives. Sets direction for the upcoming year.
* **Cadence & Format:** Once per year (significant strategic workshop).
* **Participants:** Management/Strategy Lead(s), AI (via TIP Workflow for analysis support).
* **Process in TIP:**
    1.  **How (User - AI Processing):**
        * Select `LACM_Workflow_AnnualStrategyAnalysisPrep`.
        * Inputs: All `LACM_Q*_ReviewPreparation_*` files for the year, any annual financial/market summary TIP documents, expiring `LACM_Strategy_Current`.
    2.  **AI Does:** Generates `LACM_[Year]_AnnualStrategyAnalysisInput`.
    3.  **You Do (Strategic Review & Documentation):**
        * Use AI analysis for deep strategic discussions.
        * Make fundamental decisions about vision, mission, strategy.
        * Manually create/update the main `LACM_Strategy_Current` for the *next year*. This is a critical manual step.
        * Optionally create a `LACM_YYYY_AnnualReport_Strategy` to summarize the review. Save all documents.
* **Artifacts:** `LACM_[Year]_AnnualStrategyAnalysisInput`, significantly updated `LACM_Strategy_NextYear` (renaming current to previous year, and new one becomes current).
* **Value:** Ensures long-term strategic relevance and direction.

---

## **9. Ad-hoc AI Pair Working in TIP**

* **Purpose:** To leverage AI (via general-purpose TIP Workflows) for specific, focused tasks like drafting content, brainstorming, or analyzing text segments as part of daily work or other rituals.
* **Cadence & Format:** As needed by individual team members.
* **Process in TIP:**
    1.  **Prepare Input:** Create a new TIP Document (e.g., `LACM_PairInput_[TaskDescription]_[Date]`). In this document, clearly state your request for the AI and provide any necessary context, text to be analyzed, or keywords. Use a simple structure (e.g., "Request: Draft an introduction for X.", "Text to Analyze: ...").
    2.  **Select Workflow:** In TIP, go to "Run Workflows" and choose an appropriate general-purpose workflow like:
        * `LACM_Workflow_DraftSection`
        * `LACM_Workflow_BrainstormIdeas`
        * `LACM_Workflow_AnalyzeTextSegment`
    3.  **Execute & Review:** Select your prepared input TIP Document and run the workflow. Review the AI-generated output TIP Document.
    4.  **Iterate & Refine:** If the output isn't perfect, you can:
        * Edit your input TIP Document (`LACM_PairInput_...`) with more specific instructions or refined context and re-run the workflow.
        * Directly edit the AI's output TIP Document.
    5.  **Log & Document (Optional but Recommended):**
        * Consider using `LACM_PairWorkingSessionLog` (from `LACM Templates Library for TIP`) to create a `LACM_PairLog_[TaskDescription]_[Date]` to note effective prompts/inputs and AI responses for future reference or to share patterns.
* **Value:** Accelerates specific tasks, helps overcome writer's block, provides analytical assistance.

---

## **10. Implementation Notes for TIP Users**

### 10.1. Document Naming Conventions

Consistent naming of TIP Documents is crucial for organization and for the `inputDocumentSelectors` in TIP Workflows to function correctly. Adopt conventions like:
* `LACM_[Purpose]_[Date/Period/Identifier]`
* Examples: `LACM_Strategy_Current`, `LACM_ManualNewsInput_2025-05-11`, `LACM_DailyLog_2025-05-11`, `LACM_Goals_Q2_2025`, `LACM_KW20_WeeklyAnalysis_2025-W20`.
* Keep "Current" documents (like Strategy, TaskList) as single, living documents, frequently updated (TIP's versioning will track history). Dated documents are created for each instance (e.g., each day's log).

### 10.2. Using TIP Workflows

* Familiarize yourself with the workflows available in the `LACM Workflow Library for TIP` (Admin-created).
* Understand the **Expected Input TIP Document(s)** for each workflow. Prepare these documents carefully with all necessary information, as the LLM only sees what's in these documents.
* When running a workflow, TIP will prompt you to select one or more input documents. Choose the correct, most up-to-date versions.
* The output will be a new TIP Document.

### 10.3. Reviewing and Editing AI Outputs

* **Always review AI-generated TIP Documents.** The AI is an assistant; the team is responsible for the final accuracy, relevance, and quality.
* Use the TIP editor to make necessary corrections, additions, or deletions.
* Saving an AI-generated document (or your edits to it) creates a new version in TIP, making it part of your official record.

---

## **11. Continuous Improvement of LACM Practices in TIP**

* **Regularly Discuss:** Use parts of your Weekly Retrospective or dedicated monthly sessions to discuss how the LACM rituals and TIP Workflows are working for your team.
* **Refine Inputs:** If a TIP Workflow isn't producing desired results, first check the quality and completeness of the input TIP Documents.
* **Suggest Workflow/Prompt Improvements:** If input documents are good but AI output is consistently suboptimal, provide feedback to your TIP Administrator. They can refine the prompts within the Process Workflow definitions. Document effective ad-hoc prompts or input strategies for general workflows in shared TIP Documents.
* **Adapt Templates:** Over time, your team may find that the standard `LACM Templates Library for TIP` needs adjustments. Discuss these with your Admin, who can update the master templates in TIP.

---

## **12. Appendices**

### 12.1. Referenced LACM Templates Library for TIP
This document assumes the availability of Document Templates within TIP as defined in the `LACM Templates Library for TIP`. Team users will select these Admin-created templates when creating new TIP Documents for the LACM process.

### 12.2. Referenced LACM Workflow Library for TIP
This document assumes that System Administrators have created Process Workflows in TIP as defined in the `LACM Workflow Library for TIP`. Team users will execute these named workflows.
