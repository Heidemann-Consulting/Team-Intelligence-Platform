# **Lean AI Co-Management (LACM) Templates Library for TIP**

**Version:** 1.0
**Date:** May 11, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

## **Table of Contents**

- [**Lean AI Co-Management (LACM) Templates Library for TIP**](#lean-ai-co-management-lacm-templates-library-for-tip)
  - [**Table of Contents**](#table-of-contents)
  - [**Introduction**](#introduction)
  - [**Phase 0: Initial Setup Document Templates**](#phase-0-initial-setup-document-templates)
    - [1. `LACM_Strategy`](#1-lacm_strategy)
    - [2. `LACM_ManualNewsInput`](#2-lacm_manualnewsinput)
    - [3. `LACM_Competitors`](#3-lacm_competitors)
    - [4. `LACM_TargetMarkets`](#4-lacm_targetmarkets)
    - [5. `LACM_QuarterlyGoals`](#5-lacm_quarterlygoals)
    - [6. `LACM_WeeklyPlanPreview_Initial`](#6-lacm_weeklyplanpreview_initial)
    - [7. `LACM_TaskList`](#7-lacm_tasklist)
    - [8. `LACM_AvailableTime`](#8-lacm_availabletime)
    - [9. `LACM_Processes`](#9-lacm_processes)
    - [10. `LACM_IdeaBacklog`](#10-lacm_ideabacklog)
    - [11. `LACM_PrioritizedInnovationInitiatives`](#11-lacm_prioritizedinnovationinitiatives)
    - [12. `LACM_CustomerFeedback`](#12-lacm_customerfeedback)
    - [13. `LACM_SalesHandbook`](#13-lacm_saleshandbook)
    - [2. `LACM_DailyPlanReview`](#2-lacm_dailyplanreview)
  - [**Phase 2: Weekly Routine Document Templates**](#phase-2-weekly-routine-document-templates)
    - [1. `LACM_WeeklyRetroSummary`](#1-lacm_weeklyretrosummary)
  - [**General Purpose Templates**](#general-purpose-templates)
    - [1. `LACM_MeetingSummary`](#1-lacm_meetingsummary)
    - [2. `LACM_DecisionLog`](#2-lacm_decisionlog)

## **Introduction**

This library provides standard templates for creating and managing documents within the Team Intelligence Platform (TIP) as part of the Lean AI Co-Management (LACM) process. These templates are designed to be set up by a TIP Administrator. Team Users will then use these Admin-created "Document Templates" to create new TIP Documents.

The naming convention for documents created from these templates would typically be: `LACM_[TemplatePurpose]_[Date/Identifier]` (e.g., `LACM_Strategy_2025-05-11`, `LACM_DailyLogInput_2025-05-11`). Consistent naming is crucial in TIP due to the absence of a user-managed folder structure.

**Note on AI Interaction:** Since LLMs in TIP cannot access the internet or external tools, any information required by an AI Process Workflow (e.g., news, specific data) must be manually gathered by the user and placed into a TIP Document using an appropriate template (like `LACM_ManualNewsInput`). The AI workflow then processes this document.

---

## **Phase 0: Initial Setup Document Templates**

These templates are for foundational documents that provide context to the AI and the team. They should be created once at the beginning and updated as per the LACM cycle definitions (e.g., Strategy updated annually/quarterly).

### 1. `LACM_Strategy`
* **Purpose:** Defines the high-level direction, goals, and operational context. Primary input for AI analysis and planning.
* **TIP Document Name Example:** `LACM_Strategy_YYYY-MM-DD`

```markdown
# LACM Strategy - Effective Date: {{CurrentDate_YYYY-MM-DD}}

## 1. Vision
*Where are you going long-term?*
-

## 2. Mission
*What do you do day-to-day?*
-

## 3. Core Values
*What principles guide your actions?*
-
-

## 4. Strategic Pillars / Themes
*What are the 3-5 major areas of focus to achieve your vision?*
- Pillar 1:
- Pillar 2:

## 5. Key Goals (Long-Term / Annual)
*What major objectives support your pillars for the next 12-24 months?*
- Goal A:
- Goal B:

## 6. Target Audience / Market Segments
*Who are your primary customers/users?*
- Primary Segment:
  - Characteristics:
- Secondary Segment (Optional):
  - Characteristics:

## 7. Core Offerings / Value Proposition
*What products/services do you provide and what unique value do they offer?*
- Offering 1:
  - Value:
- Offering 2:
  - Value:

## 8. Competitive Landscape Overview
*Who are your main competitors and what is your general positioning against them? (Detailed analysis in `LACM_Competitors_YYYY-MM-DD`)*
- Competitor A:
- Competitor B:

## 9. Key Success Metrics (Strategic Level)
*How will you measure the success of this strategy?*
- Metric 1:
- Metric 2:

## 10. Assumptions
*What key assumptions underpin this strategy?*
-
```

### 2. `LACM_ManualNewsInput`
* **Purpose:** For users to manually input news summaries, articles, or links that will serve as the primary source for the "Daily News & Environment Analysis" AI workflow.
* **TIP Document Name Example:** `LACM_ManualNewsInput_YYYY-MM-DD`

```markdown
# LACM Manual News & External Information Input - {{CurrentDate_YYYY-MM-DD}}

## Instructions for User:
* Manually research and gather relevant news, articles, blog posts, social media trends, or other external information from the last 24-48 hours.
* Focus on items potentially impacting your strategy, competitors, target markets, or ongoing projects.
* For each item, provide a source (if applicable), a brief summary or the full text if concise, and optionally, your initial thoughts on its relevance.
* This document will be processed by an AI workflow to generate the `LACM_DailyNewsAnalysis_YYYY-MM-DD`.

---

## Item 1
- **Source (URL/Name):**
- **Date Published:**
- **Summary / Key Points / Pasted Text:**
- **Initial Relevance Assessment (Optional):**

## Item 2
- **Source (URL/Name):**
- **Date Published:**
- **Summary / Key Points / Pasted Text:**
- **Initial Relevance Assessment (Optional):**

## Item 3
- **Source (URL/Name):**
- **Date Published:**
- **Summary / Key Points / Pasted Text:**
- **Initial Relevance Assessment (Optional):**

*(Add more items as needed)*
```

### 3. `LACM_Competitors`
* **Purpose:** Provides context about main competitors for analysis and strategic reviews.
* **TIP Document Name Example:** `LACM_Competitors_YYYY-MM-DD` (updated periodically)

```markdown
# LACM Competitor Analysis - Last Updated: {{CurrentDate_YYYY-MM-DD}}

## Competitor 1: [Name]
- **Website:**
- **Main Focus / Offerings:**
- **Perceived Strengths:**
  -
- **Perceived Weaknesses:**
  -
- **Recent Activities / News (Manual Entry - Link to `LACM_ManualNewsInput` if source):**
  -
- **Strategic Notes:**

## Competitor 2: [Name]
- **Website:**
- **Main Focus / Offerings:**
- **Perceived Strengths:**
  -
- **Perceived Weaknesses:**
  -
- **Recent Activities / News (Manual Entry):**
  -
- **Strategic Notes:**

*(Add more competitors as needed)*
```

### 4. `LACM_TargetMarkets`
* **Purpose:** Defines target customers/users to inform AI analysis relevance.
* **TIP Document Name Example:** `LACM_TargetMarkets_YYYY-MM-DD` (updated periodically)

```markdown
# LACM Target Market Analysis - Last Updated: {{CurrentDate_YYYY-MM-DD}}

## Primary Market Segment 1: [e.g., Small Manufacturing Businesses, Germany]
- **Description:**
- **Key Characteristics / Demographics:**
- **Needs / Pain Points:**
- **Size / Potential (Estimate):**
- **Trends Affecting This Segment (Manual Entry):**

## Secondary Market Segment 2 (Optional): [e.g., Freelance Consultants in Tech]
- **Description:**
- **Key Characteristics / Demographics:**
- **Needs / Pain Points:**
- **Size / Potential (Estimate):**
- **Trends Affecting This Segment (Manual Entry):**

*(Add more segments as needed)*
```

### 5. `LACM_QuarterlyGoals`
* **Purpose:** Defines specific, measurable Objectives and Key Results (OKRs) for the current quarter.
* **TIP Document Name Example:** `LACM_Goals_Q[Number]_[Year]` (e.g., `LACM_Goals_Q2_2025`)

```markdown
# LACM Quarterly Goals - Q{{CurrentQuarterNumber}} / {{CurrentYear}}

## Objective 1: [Clear, Ambitious, Qualitative Objective Title]
*Alignment: Links to Strategic Pillar/Goal X from `LACM_Strategy_YYYY-MM-DD`*
- **Key Result 1.1:** [Specific, Measurable, Achievable, Relevant, Time-bound (SMART) Key Result]
  - Target:
  - Current:
- **Key Result 1.2:** [SMART Key Result]
  - Target:
  - Current:
- **Key Result 1.3:** [SMART Key Result]
  - Target:
  - Current:

## Objective 2: [Clear, Ambitious, Qualitative Objective Title]
*Alignment: Links to Strategic Pillar/Goal Y from `LACM_Strategy_YYYY-MM-DD`*
- **Key Result 2.1:** [SMART Key Result]
  - Target:
  - Current:
- **Key Result 2.2:** [SMART Key Result]
  - Target:
  - Current:

*(Add 1-3 more Objectives for the quarter, each with 2-4 Key Results)*

## Overall Confidence Score for this Quarter's Goals (Manual Assessment):
* [e.g., 7/10 - Provide brief rationale]
```

### 6. `LACM_WeeklyPlanPreview_Initial`
* **Purpose:** Sets the focus for the *very first week* of using LACM, guiding Daily Planning. This is a bridging document until the first full weekly planning cycle.
* **TIP Document Name Example:** `LACM_KW[WeekNo]_WeeklyPlanPreview_YYYY-MM-DD`

```markdown
# LACM Weekly Plan Preview - Week {{CurrentWeekNumber}} / {{CurrentYear}} (Initial Setup Focus)

*Initial plan for starting with and setting up the LACM process.*

## Main Objectives for Week {{CurrentWeekNumber}} (Aligned with Q{{CurrentQuarterNumber}} Initial Goals)

1.  **Objective:** Complete LACM Initial Document Setup
    *Why:* Prerequisite for starting daily cycles (links to Q{{CurrentQuarterNumber}} Objective 1).
2.  **Objective:** Begin Daily LACM Cycle Execution
    *Why:* Start integrating the process into routine (links to Q{{CurrentQuarterNumber}} Objective 1).
3.  **Objective (If Applicable):** [Another key early setup goal]
    *Why:*

## Key Tasks / Projects Requiring Focus in Week {{CurrentWeekNumber}}
- **Task/Project:** Create initial versions of all required LACM setup documents (Strategy, Competitors, Target Markets, Initial Quarterly Goals, etc.).
  *Related Objective(s):* 1
- **Task/Project:** Populate `LACM_ManualNewsInput_YYYY-MM-DD` with relevant information for the first AI-driven Daily Analysis.
  *Related Objective(s):* 2
- **Task/Project:** Execute the "Daily News & Environment Analysis" AI Workflow for the first time on [Target Day].
  *Related Objective(s):* 2
- **Task/Project:** Conduct the "Daily Review & Context Capture" (manual input to `LACM_DailyLogInput_YYYY-MM-DD`, then AI processing) for the first time on [Target Day].
  *Related Objective(s):* 2
- **Task/Project:** Conduct "Daily Planning" (using AI Workflow based on logs, analysis, this weekly plan) for the first time on [Target Day].
  *Related Objective(s):* 2

## Notes for the Week
- Focus on understanding the inputs and outputs of each daily step.
- Don't aim for perfection in documents; aim for completion of the initial setup.
```

### 7. `LACM_TaskList`
* **Purpose:** Central list of tasks or backlog. Input for AI-assisted daily planning.
* **TIP Document Name Example:** `LACM_TaskList_YYYY-MM-DD` (can be one persistent document, frequently updated)

```markdown
# LACM Task List - Last Updated: {{CurrentDate_YYYY-MM-DD}}

## Instructions:
* Add new tasks with a description, priority, status, and optionally an owner and due date.
* Update status as tasks progress.
* The AI Daily Planning workflow will consider "To Do" and "In Progress" tasks.

---

## Task ID: [Unique ID, e.g., TSK-001]
- **Description:**
- **Priority:** [High / Medium / Low]
- **Status:** [To Do / In Progress / Blocked / Done / Archived]
- **Owner (Optional):**
- **Due Date (Optional):**
- **Related Goal/Objective (Optional):** [e.g., Q2 Objective 1.1, Strategy Pillar A]
- **Notes:**

## Task ID: [TSK-002]
- **Description:**
- **Priority:**
- **Status:**
- **Owner (Optional):**
- **Due Date (Optional):**
- **Related Goal/Objective (Optional):**
- **Notes:**

*(Add more tasks as needed)*
```

### 8. `LACM_AvailableTime`
* **Purpose:** Helps AI propose realistic daily plans by considering estimated available focused work time.
* **TIP Document Name Example:** `LACM_AvailableTime_YYYY-MM-DD` (updated daily or weekly)

```markdown
# LACM Estimated Available Focused Work Time - Updated: {{CurrentDate_YYYY-MM-DD}}

## Next 24 Hours (for {{TomorrowDate_YYYY-MM-DD}})
- **Total Team Focused Hours Available:** [e.g., 6] hours
- **Breakdown (if team):**
  - Member A: [e.g., 3] hours
  - Member B: [e.g., 3] hours
- **Key Commitments / Blockers of Time:**
  - [e.g., Meeting X from 10-11 AM]
  - [e.g., Member A unavailable PM]

## Next 7 Days (Week starting {{NextMondayDate_YYYY-MM-DD}})
- **Total Team Focused Hours Available:** [e.g., 25] hours
- **Breakdown (if team):**
  - Member A: [e.g., 15] hours
  - Member B: [e.g., 10] hours
- **Known Absences / Major Time Commitments:**
  -
```

### 9. `LACM_Processes`
* **Purpose:** Documents key operational processes, steps, roles, and KPIs. Basis for process retrospectives and improvements.
* **TIP Document Name Example:** `LACM_Processes_Internal` (a living document)

```markdown
# LACM Key Operational Processes - Last Updated: {{CurrentDate_YYYY-MM-DD}}

## Process 1: [Name of Process, e.g., New Feature Development Cycle]
- **Owner:**
- **Objective:**
- **Key Steps:**
  1.
  2.
  3.
- **Roles Involved & Responsibilities:**
  -
- **Key Performance Indicators (KPIs):**
  -
- **Associated TIP Workflows (if any):**
  - [Workflow Name in TIP] - Purpose:
- **Improvement Notes (from Retrospectives):**
  -

## Process 2: [Name of Process, e.g., Customer Support Ticket Handling]
- **Owner:**
- **Objective:**
- **Key Steps:**
  1.
  2.
- **Roles Involved & Responsibilities:**
  -
- **Key Performance Indicators (KPIs):**
  -
- **Associated TIP Workflows (if any):**
  -
- **Improvement Notes:**
  -

*(Add more processes as they are defined/refined)*
```

### 10. `LACM_IdeaBacklog`
* **Purpose:** Captures new ideas, their status, potential, and feasibility. Input for innovation management.
* **TIP Document Name Example:** `LACM_IdeaBacklog` (a living document)

```markdown
# LACM Idea Backlog - Last Updated: {{CurrentDate_YYYY-MM-DD}}

## Idea ID: [Unique ID, e.g., IDEA-001]
- **Idea Title/Summary:**
- **Problem Solved / Opportunity Addressed:**
- **Source / Inspiration:**
- **Date Captured:** {{CurrentDate_YYYY-MM-DD}}
- **Proposer (Optional):**
- **Initial Assessment:**
  - Strategic Fit (High/Medium/Low):
  - Potential Impact (High/Medium/Low):
  - Feasibility (High/Medium/Low):
- **Status:** [New / Under Review / Prioritized / Archived / Implemented]
- **Next Steps / Notes:**

## Idea ID: [IDEA-002]
- **Idea Title/Summary:**
- **Problem Solved / Opportunity Addressed:**
- **Source / Inspiration:**
- **Date Captured:**
- **Proposer (Optional):**
- **Initial Assessment:**
  - Strategic Fit:
  - Potential Impact:
  - Feasibility:
- **Status:**
- **Next Steps / Notes:**

*(Add more ideas as they arise)*
```

### 11. `LACM_PrioritizedInnovationInitiatives`
* **Purpose:** Lists innovation ideas that have been evaluated and prioritized for potential inclusion in quarterly planning.
* **TIP Document Name Example:** `LACM_PrioritizedInnovationInitiatives_YYYY-MM-DD` (updated quarterly or as needed)

```markdown
# LACM Prioritized Innovation Initiatives - As of: {{CurrentDate_YYYY-MM-DD}}

## Prioritized Initiative 1: [Title from Idea Backlog]
- **Idea ID:** [Link to `LACM_IdeaBacklog` entry]
- **Brief Description:**
- **Strategic Rationale for Prioritization:**
- **Key Success Metrics (if defined):**
- **Potential Next Steps / Resources Needed:**
- **Target Quarter for Consideration:** Q[Number] / [Year]

## Prioritized Initiative 2: [Title from Idea Backlog]
- **Idea ID:**
- **Brief Description:**
- **Strategic Rationale for Prioritization:**
- **Key Success Metrics (if defined):**
- **Potential Next Steps / Resources Needed:**
- **Target Quarter for Consideration:**

*(Add more prioritized initiatives)*
```

### 12. `LACM_CustomerFeedback`
* **Purpose:** Collects and structures feedback from customers for service/product improvement and strategic review.
* **TIP Document Name Example:** `LACM_CustomerFeedback_Log` (a living document)

```markdown
# LACM Customer Feedback Log - Last Updated: {{CurrentDate_YYYY-MM-DD}}

## Feedback Entry 1
- **Date Received:** {{CurrentDate_YYYY-MM-DD}}
- **Source:** [e.g., Email, Survey, Call, Meeting with Client X]
- **Customer (Optional):** [Name/Company]
- **Product/Service:** [If specific]
- **Feedback Type:** [Positive / Negative / Suggestion / Bug Report / Question]
- **Summary of Feedback:**
- **Key Quotes (if applicable):**
- **Sentiment (Manual Assessment):** [Positive/Neutral/Negative/Mixed]
- **Actionable Insights / Themes Identified:**
- **Follow-up Action Taken / Planned (Optional):**
  - Action:
  - Owner:
  - Status:

## Feedback Entry 2
- **Date Received:**
- **Source:**
- **Customer (Optional):**
- **Product/Service:**
- **Feedback Type:**
- **Summary of Feedback:**
- **Key Quotes (if applicable):**
- **Sentiment (Manual Assessment):**
- **Actionable Insights / Themes Identified:**
- **Follow-up Action Taken / Planned (Optional):**

*(Add more feedback entries)*
```

### 13. `LACM_SalesHandbook`
* **Purpose:** Details sales philosophy, targets, processes, pricing, etc. Relevant for market-facing activities.
* **TIP Document Name Example:** `LACM_SalesHandbook_Internal` (a living document)

```markdown
# LACM Sales Handbook - Last Updated: {{CurrentDate_YYYY-MM-DD}}

## 1. Sales Philosophy & Approach
-

## 2. Target Customers & Ideal Customer Profile (ICP)
*(Reference `LACM_TargetMarkets_YYYY-MM-DD`)*
-

## 3. Product/Service Offerings & Pricing
*(Reference Core Offerings in `LACM_Strategy_YYYY-MM-DD`)*
- **Offering A:**
  - Description:
  - Key Benefits:
  - Pricing:
- **Offering B:**
  - Description:
  - Key Benefits:
  - Pricing:

## 4. Sales Process Overview
- Lead Generation:
- Qualification:
- Needs Analysis:
- Proposal:
- Closing:
- Onboarding:

## 5. Key Sales Metrics & Targets
- [e.g., Monthly Recurring Revenue (MRR)]
- [e.g., Customer Acquisition Cost (CAC)]
- [e.g., Sales Cycle Length]

## 6. Sales Tools & Resources
- CRM:
- Proposal Templates: [Link to TIP Document name if applicable]
- Marketing Materials: [Link to TIP Document name if applicable]

## 7. Handling Objections
- Objection 1:
  - Response:
- Objection 2:
  - Response:

## 8. Competitive Positioning (Sales Focused)
*(Reference `LACM_Competitors_YYYY-MM-DD`)*
- How we differentiate from Competitor X:
- Key selling points against Competitor Y:

## 9. Sales Team Structure & Roles (If applicable)
-

---

## **Phase 1: Daily Routine Document Templates**

These templates support the daily operational cycle.

### 1. `LACM_DailyLogInput`
* **Purpose:** For team members to manually input their daily review information (accomplishments, challenges, learnings, etc.) before it's processed by an AI workflow into the structured `LACM_DailyLog_YYYY-MM-DD`.
* **TIP Document Name Example:** `LACM_DailyLogInput_TeamMemberA_YYYY-MM-DD` (or a combined one for the team)

```markdown
# LACM Daily Log - Input Data for {{CurrentDate_YYYY-MM-DD}}

## Team Member (Optional, if individual inputs): [Your Name]

## 1. Key Accomplishments (Since last log)
*What did you complete or make significant progress on?*
-
-

## 2. Challenges & Blockers Encountered
*What issues did you face? What's preventing progress?*
-
-

## 3. Key Interactions (Internal/External Meetings, Calls, Emails)
*Summarize important communications and their outcomes.*
- Interaction with [Person/Team/Client] regarding [Topic]:
  - Outcome/Decision:
  - Action Items (if any):
-

## 4. Learnings & Insights
*What did you learn? Any new ideas or observations?*
-
-

## 5. Open Points / Questions / Items for Next 24h Focus
*What needs immediate attention or is top of mind for tomorrow?*
-
-

## 6. Relevant External Context Items (from `LACM_DailyNewsAnalysis_YYYY-MM-DD` or manual input)
*Any specific news or external factors that influenced your day or plans?*
-
```

### 2. `LACM_DailyPlanReview`
* **Purpose:** For human review and adjustment of the AI-generated `LACM_DailyPlan_YYYY-MM-DD`. This template isn't used to create a new document from scratch, but rather as a mental checklist or structure if one were to manually draft/override the AI's plan. The AI's output format is defined by its prompt.
* **This template serves more as a "Standard Structure for Daily Plan Output" which an Admin would configure in the relevant AI Workflow prompt.**

```markdown
# LACM Daily Plan - {{CurrentDate_YYYY-MM-DD}} (Structure for AI Output & Human Review)

## Plan Next 24h (Aligned with KW{{CurrentWeekNumber}} Objectives)

| Priority | Task Description                      | Who    | Effort | Notes / Dependency |
| :------- | :------------------------------------ | :----- | :----- | :----------------- |
| High     | [Specific, actionable task 1]         | [Name] | [S/M/L]| [e.g., Blocked by X]|
| High     | [Specific, actionable task 2]         | [Name] | [S/M/L]|                    |
| Medium   | [Specific, actionable task 3]         | [Name] | [S/M/L]|                    |
| Low      | [Specific, actionable task 4]         | [Name] | [S/M/L]|                    |
*Feasibility Check: Proposed effort roughly aligns with `LACM_AvailableTime_YYYY-MM-DD`.*

## Outlook Next 7 Days (Focus on KW{{CurrentWeekNumber}} Objectives from `LACM_KW[Num]_WeeklyPlanPreview`)
- [Key Task/Theme 1 from Weekly Plan Preview]
- [Key Task/Theme 2 from Weekly Plan Preview]

## Outlook Next 31 Days (Strategic Focus from `LACM_Goals_Q[Num]_[Year]` or `LACM_Strategy`)
- [Key Strategic Theme/Milestone 1]

## Review Notes (Human):
* [Any adjustments made to the AI-proposed plan and why]
* [Confirm alignment with available time and weekly objectives]
```

---

## **Phase 2: Weekly Routine Document Templates**

### 1. `LACM_WeeklyRetroSummary`
* **Purpose:** For the team to manually summarize the outcomes of their Weekly Retrospective discussion. This is human-generated, potentially after reviewing AI-prepared data.
* **TIP Document Name Example:** `LACM_KW[WeekNo]_WeeklyRetroSummary_YYYY-MM-DD`

```markdown
# LACM Weekly Retrospective Summary - Week {{CurrentWeekNumber}} ({{DateRangeOfWeek}})

## Date of Retrospective: {{CurrentDate_YYYY-MM-DD}}
## Participants:
-

## 1. What Went Well This Week?
-
-

## 2. What Were the Main Challenges / Could Be Improved?
-
-

## 3. Key Learnings & Insights from This Week
-
-

## 4. Action Items for Improvement (To be added to `LACM_TaskList`)
- **Action 1:**
  - Owner:
  - Due Date:
  - Success Metric (Optional):
- **Action 2:**
  - Owner:
  - Due Date:
  - Success Metric (Optional):

## 5. Process Improvement Notes (Potential updates for `LACM_Processes_Internal`)
-

## Overall Mood / Sentiment for the Week:
- [Briefly describe, e.g., Positive, Challenging but Productive, Stressed]
```

---

## **General Purpose Templates**

These can be used ad-hoc as needed.

### 1. `LACM_MeetingSummary`
* **Purpose:** Standard format for summarizing meetings. Can be used as input for an AI workflow that helps draft it, or filled manually.
* **TIP Document Name Example:** `LACM_MeetingSummary_[Topic]_[YYYY-MM-DD]`

```markdown
# LACM Meeting Summary - {{CurrentDate_YYYY-MM-DD}}

**Meeting Topic:**
**Date & Time:**
**Attendees:**
-
**Apologies:**
-

## 1. Agenda / Purpose of Meeting
-

## 2. Key Discussion Points
-
-
-

## 3. Decisions Made
- Decision 1:
  - Rationale:
  - Agreed by:
- Decision 2:

## 4. Action Items
| Action Description | Owner | Due Date | Status   | Notes |
| :----------------- | :---- | :------- | :------- | :---- |
|                    |       |          | To Do    |       |
|                    |       |          |          |       |

## 5. Other Notes / Open Questions
-

## 6. Next Meeting (If applicable)
- Date/Time:
- Tentative Agenda:
```

### 2. `LACM_DecisionLog`
* **Purpose:** To log important decisions made by the team for future reference and traceability.
* **TIP Document Name Example:** `LACM_DecisionLog_TeamX` (a living document for a team)

```markdown
# LACM Team Decision Log - Last Updated: {{CurrentDate_YYYY-MM-DD}}

## Decision ID: [Unique ID, e.g., DEC-2025-001]
- **Date of Decision:**
- **Decision Made:** [Clear statement of the decision]
- **Problem / Context:** [Briefly describe the issue or situation leading to the decision]
- **Options Considered (Optional):**
  - Option A:
  - Option B:
- **Rationale for Decision:**
- **Key Stakeholders / People Involved in Decision:**
- **Expected Outcome / Impact:**
- **Follow-up Actions (if any, link to Task List):**
  - [Task ID from `LACM_TaskList`]
- **Review Date (Optional):**

## Decision ID: [DEC-2025-002]
- **Date of Decision:**
- **Decision Made:**
- **Problem / Context:**
- **Options Considered (Optional):**
- **Rationale for Decision:**
- **Key Stakeholders / People Involved in Decision:**
- **Expected Outcome / Impact:**
- **Follow-up Actions (if any, link to Task List):**
- **Review Date (Optional):**

*(Add more decisions as they are made)*
```
