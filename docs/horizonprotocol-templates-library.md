# HORIZON Template Library

**Version:** 1.0
**Date:** May 18, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

*The HORIZON Protocol uses a set of standardized document templates (prefixed with `HORIZON_`) to ensure consistency and completeness of information. Below are the key templates provided in Markdown format, with their intended structure and content guidelines. Team administrators should import these into TIP as the starting point for building the knowledge base. Users will then fill in the specifics for their team. These templates cover everything from high-level strategy to daily operations.*

- [HORIZON Template Library](#horizon-template-library)
    - [HORIZON\_North\_Star\_Charter](#horizon_north_star_charter)
    - [HORIZON\_Quarterly\_OKRs](#horizon_quarterly_okrs)
    - [HORIZON\_Task\_Backlog](#horizon_task_backlog)
    - [HORIZON\_Idea\_Backlog](#horizon_idea_backlog)
    - [HORIZON\_Decision\_Log](#horizon_decision_log)
    - [HORIZON\_Meeting\_Notes](#horizon_meeting_notes)
    - [HORIZON\_Daily\_Log](#horizon_daily_log)
    - [HORIZON\_Daily\_Plan](#horizon_daily_plan)
    - [HORIZON\_Weekly\_Plan](#horizon_weekly_plan)
    - [HORIZON\_Weekly\_Review](#horizon_weekly_review)
    - [HORIZON\_Monthly\_Report](#horizon_monthly_report)
    - [HORIZON\_Quarterly\_Business\_Review](#horizon_quarterly_business_review)
    - [HORIZON\_Annual\_Strategic\_Plan](#horizon_annual_strategic_plan)
    - [HORIZON\_Team\_Updates](#horizon_team_updates)
    - [HORIZON\_External\_Context](#horizon_external_context)
    - [HORIZON\_Team\_Availability](#horizon_team_availability)
    - [HORIZON\_Metrics\_KPI\_Update](#horizon_metrics_kpi_update)
    - [HORIZON\_Customer\_Feedback\_Summary](#horizon_customer_feedback_summary)
    - [HORIZON\_Market\_Context\_Trends\_Summary](#horizon_market_context_trends_summary)
    - [HORIZON\_Raw\_Meeting\_Record](#horizon_raw_meeting_record)
    - [HORIZON\_Meeting\_Agenda](#horizon_meeting_agenda)
    - [HORIZON\_Prompt\_Analysis\_Input](#horizon_prompt_analysis_input)
    - [HORIZON\_Condensation\_Criteria](#horizon_condensation_criteria)

### HORIZON_North_Star_Charter

*Purpose:* Captures the enduring guiding information about the team or organization – its mission, vision, core values, and long-term strategic pillars. This is the cornerstone of the team’s **strategic memory**; many workflows will pull from this document to ensure alignment.

```
# North Star Charter

**Mission:** _<One sentence stating the fundamental purpose of the team or organization.>_

**Vision:** _<A short statement of what the team aspires to achieve or become in the long term.>_

**Core Values:**
- _Value 1:_ <Brief description of this core value in practice.>
- _Value 2:_ <Brief description...>
- _Value 3:_ <... list 3-5 fundamental values guiding the team’s culture and decisions._

**Strategic Pillars:**
1. **Pillar 1:** <Long-term strategic focus area or goal (e.g. Operational Excellence, Innovation in X, Customer Satisfaction). Describe what this means.>
2. **Pillar 2:** <Another key strategic priority...>
3. **Pillar 3:** <... up to 3-5 pillars that define the team's high-level strategy.>

**Team Identity & Scope:**
- **Who We Serve:** <Define the customers or stakeholders the team/organization serves.>
- **What We Offer:** <Briefly describe the main products, services, or value the team delivers.>
- **Unique Strengths:** <Bullet points of the team’s unique advantages or differentiators.>

*_(This charter should be reviewed at least annually. All major plans and decisions should reference this document to ensure alignment.)_*
```

### HORIZON_Quarterly_OKRs

*Purpose:* Defines the team’s Objectives and Key Results (OKRs) for the current quarter. This template ensures goals are clearly articulated and measurable, aligning short-term execution with the long-term North Star Charter. It is updated at the start of each quarter and referenced in weekly and monthly routines.

```
# Q<Quarter> <Year> Objectives & Key Results

**Objective 1:** <Objective statement – a qualitative goal for this quarter.>
- **KR 1.1:** <First Key Result with target metric or deliverable to achieve this objective.>
- **KR 1.2:** <Second Key Result (if any)...>
- (Add KRs as needed)

**Objective 2:** <Second major objective for the quarter.>
- **KR 2.1:** <Key Result for Objective 2.>
- **KR 2.2:** <Key Result...>

*(List 1-5 Objectives maximum. Each Objective should have 1-4 Key Results that are specific and measurable.)*

**Quarter Focus Theme:** <If the quarter has an overarching theme or slogan, note it here (optional). For example, “Expand Market Reach” or “Operational Efficiency.”>

**Baseline Metrics:**
- <List any starting metrics at beginning of quarter, like revenue, user count, etc., relevant to the objectives. This helps measure improvement.>

**Risks & Assumptions:**
- <List any known risks to achieving these objectives or assumptions being made. e.g., "Assumption: funding for project X will be approved by Q2".>
```

### HORIZON_Task_Backlog

*Purpose:* Serves as the master task list or backlog for the team. It tracks ongoing and upcoming tasks, ensuring nothing falls through the cracks. The backlog is referenced during daily and weekly planning to decide what to tackle next. (If the team uses an external task management tool, this document can be a simple pointer or summary, but maintaining a high-level backlog here keeps the AI aware of tasks.)

```
# Team Task Backlog

| **ID** | **Task**                   | **Owner**    | **Priority** | **Status**   | **Notes**             |
|--------|---------------------------|--------------|--------------|--------------|-----------------------|
| 1      | <Task description>        | <Person/Team>| High/Med/Low | Not Started/In Progress/Done | <Any relevant details or links> |
| 2      | <Task description>        | <Owner>      | High         | In Progress  | <Notes...>            |
| 3      | <Task description>        | <Owner>      | Medium       | Not Started  | <Notes...>            |
| ...    | ...                       | ...          | ...          | ...          | ...                   |

*Guidelines:*
- Prioritize tasks (High, Medium, Low) so the Daily Plan workflow knows what’s important.
- Update statuses daily or as progress is made (e.g., when a task is completed or blocked).
- Use the Notes field for any context the AI might need (e.g., "Waiting on client feedback" or links to specifications).
- Keep the list pruned: remove or archive tasks that are no longer relevant so the AI stays focused on current priorities.
```

### HORIZON_Idea_Backlog

*Purpose:* Provides a space to capture new ideas, innovations, or improvements the team wants to consider. This can include product ideas, process improvements, or any “wouldn’t it be nice if…” thoughts. The AI can use this during planning or strategy sessions to ensure good ideas are not forgotten. Reviewed during quarterly and annual planning.

```
# Idea Backlog

| **Idea**                           | **Potential Impact**    | **Status**        | **Notes**                  |
|------------------------------------|-------------------------|-------------------|----------------------------|
| <Short description of idea>       | High/Medium/Low         | Proposed / Under Review / Approved / Archived | <Additional details or rationale> |
| <Idea description>               | Medium                  | Proposed          | <Notes... e.g., origin of idea> |
| <Idea description>               | Low                     | Under Review      | <Notes...> |

*Guidelines:*
- Be concise in describing each idea, but enough to recall what it is.
- Estimate the potential impact (e.g., High = game-changer, Low = minor improvement).
- Status can move from Proposed -> Under Review -> Approved (if the team commits to it) or Archived (if decided not to pursue).
- Periodically, the team (or AI) can review this list to surface promising ideas during planning cycles.
```

### HORIZON_Decision_Log

*Purpose:* Archives major decisions made by the team along with context and rationale. This helps with strategic memory and accountability – anyone can look back and understand why a decision was made. The AI can reference this to avoid revisiting settled debates or to remind the team of past reasoning.

```
# Decision Log

| **Date**    | **Decision**                        | **Context & Rationale**                             | **Outcome/Follow-up**                  |
|------------|-------------------------------------|----------------------------------------------------|----------------------------------------|
| 2025-05-10 | Adopt HORIZON Protocol for Q3 Pilot | Context: Team workload was increasing, and missed deadlines were occurring. Rationale: HORIZON promises efficiency. | Outcome: Began onboarding team to HORIZON in May. Follow-up: full rollout by Q3 start. |
| 2025-05-17 | Strategy pivot to SMB market        | Context: Q2 sales flat in enterprise segment. Rationale: better traction with small businesses per feedback. | Outcome: Q3 marketing plan refocused on SMB. Follow-up: new messaging draft by June. |
| ...        | ...                                 | ...                                                | ...                                    |

*Guidelines:* For each major decision, record the date, a short description of what was decided, key context or reasoning that led to it (including options considered, if relevant), and what happened next (e.g., actions taken, or if the decision was later revisited). Keep entries brief but informative. This log can be updated via a quick note or using an AI workflow after a decision is made (for example, a Meeting Notes workflow might append decisions here).
```

### HORIZON_Meeting_Notes

*Purpose:* A template for documenting meetings (internal or external). Using a consistent format for agendas and notes ensures important information is captured and easily searchable. The AI can assist by summarizing raw meeting transcripts or notes into this format.

```
# Meeting Notes - <Meeting Name or Purpose>
**Date & Time:** <YYYY-MM-DD> <HH:MM>
**Attendees:** <List of attendees>

**Agenda:**
1. <Agenda point 1>
2. <Agenda point 2>
3. ...

**Discussion Summary:**
- *Agenda Item 1:* <Summary of discussion outcomes for item 1.>
- *Agenda Item 2:* <Summary for item 2...>
- *Additional Topics:* <Any other discussion points not on formal agenda.>

**Decisions Made:**
- <Decision 1 (if any) and brief rationale/context>
- <Decision 2 ...>

**Action Items:**
- <Action Item 1> – *Owner:* <Person> – *Due:* <Due date or ASAP>
- <Action Item 2> – *Owner:* <Person> – *Due:* <...>

*Notes:* Attach or link any relevant documents presented. For recurring meetings, compare with previous notes to track progress on past action items.
```

### HORIZON_Daily_Log

*Purpose:* Records the daily context and happenings. This is generated each day (often by the AI using this template) to summarize yesterday’s accomplishments, today’s plans at a high level, and any noteworthy external factors. It acts as a quick journal of the team's day-to-day trajectory, feeding into weekly reviews.

```
# Daily Log - <DATE>

**Yesterday’s Summary:**
_<Brief recap of what happened yesterday: completed tasks, milestones achieved, any blockers encountered.>_

**Today’s Focus:**
_<Summary of what the team is focusing on today: major tasks planned, goals for the day, who is doing what at a high level.>_

**Notable Updates/Context:**
- <Any important context for today: e.g., "Client X meeting at 3pm", "Deployment of version 2.0 planned", or "Mark is OOO".>
- <External factors if any: e.g., "Industry news Y might impact our marketing strategy" (optional, include only if relevant).>

**Blockers & Concerns:**
- <List any obstacles that could impede progress today, e.g., "Waiting for approval on budget", "Server downtime issue". If none, write "None".>

**Mood & Morale (Optional):**
- <If the team tracks morale or other subjective context, note it here, e.g., "Team is energized by yesterday’s success" or "A bit anxious about upcoming deadline".>

*_(This Daily Log is automatically generated each morning and reviewed by the team for accuracy. It should remain short—aim for a few paragraphs or bullet points under each section.)_*
```

### HORIZON_Daily_Plan

*Purpose:* Outlines the actionable plan for the day once the daily context is established. It pulls in the highest priority tasks from the backlog, assigns owners, and sets any micro-deadlines (like end-of-day targets). This ensures every team member knows what to focus on today. Typically generated right after the Daily Log and adjusted by the team if needed.

```
# Daily Plan - <DATE>

**Top Priorities Today:**
1. <Task 1> – *Owner:* <Person> – *Expected Outcome:* <What completing this task achieves by EOD.>
2. <Task 2> – *Owner:* <Person> – *Expected Outcome:* <...>
3. <Task 3> – *Owner:* <Person> – *Expected Outcome:* <...>
*(Limit to 3-5 major tasks across the team to maintain focus.)*

**Secondary Tasks (if time permits):**
- <Task 4> – <Owner>
- <Task 5> – <Owner>
*(These are lower priority; they can be picked up if capacity allows, or moved to tomorrow.)*

**Carry-overs from Yesterday:**
- <Task from yesterday that wasn’t finished> – *Plan:* <e.g., "Will complete by midday today.">
- ...
*(If all tasks from yesterday were completed, state "All tasks from yesterday completed ✅.")*

**Scheduled Events/Meetings:**
- <Time> - <Event> (Attendees: X, Y)
- <Time> - <Event>
*(Any meetings or significant time commitments that team members have today.)*

**End-of-Day Target Check:**
- <Reiterate any end-of-day deliverables to check, e.g., "Draft report ready for review by 5pm.">
- ...

*Notes:* This plan is a living document for the day. Team members can adjust it if priorities change (make sure to note changes). At day’s end, compare actual progress against this plan to feed into tomorrow’s Daily Log.
```

### HORIZON_Weekly_Plan

*Purpose:* Sets the course at the start of the week (often Monday). It is sometimes called a “Sprint Plan” if the team works in sprints. This template helps the team decide what the focus of the week is, which tasks or stories will be tackled, and how they connect to the larger goals. The Weekly Plan aligns the team on priorities and expectations for the week.

```
# Weekly Plan - Week <##> of <Year> (Starting <Start Date>)

**Week’s Theme/Focus:** _<A short phrase capturing the main focus of the week, e.g., “Stabilize v2.0 Release” or “Client Outreach Blitz”.>_

**Key Goals for the Week:**
- <Goal 1: e.g., Complete Feature X development for Project Y.>
- <Goal 2: e.g., Close 3 new deals from pipeline.>
- <Goal 3: e.g., Hire 1 new engineer.>
*(These should tie back to the Quarterly OKRs where possible.)*

**Planned Tasks/Deliverables:**
- <Task or Deliverable 1> – *Owner:* <Person> – *Due:* <Day or date if within the week>
- <Task/Deliverable 2> – *Owner:* <Person> – *Due:* <...>
- ... (List key tasks the team commits to finishing this week.)

**Resource Availability:**
- <Team member A>: <e.g., "Out Friday", or "50% on support duties">
- <Team member B>: <e.g., "Back from vacation on Wednesday">
- <Any noteworthy availability or capacity info affecting the plan.>

**Known Risks/Challenges This Week:**
- <Risk 1: e.g., "If client delays feedback, Feature X might slip.">
- <Risk 2: e.g., "New hire onboarding might slow team velocity early in week.">
- <...>

**Communication & Coordination:**
- <Any special coordination needed, e.g., "Daily 4pm check-in on launch readiness", or "Sales & Dev sync on Thursday".>
- <...>

*Notes:* This Weekly Plan is reviewed at week’s end (in the Weekly Review) to assess completion and carry-overs. It should be realistic – avoid overcommitting. If priorities change mid-week, update this doc so it remains a source of truth.
```

### HORIZON_Weekly_Review

*Purpose:* Captures the outcomes and learnings at the end of the week (often Friday). It’s an essential part of continuous improvement, forcing reflection on what went well, what didn’t, and what to do next. It also rolls up any key metrics or OKR progress for the week. The AI can draft this based on the week’s Daily Logs, completed tasks, and any metrics updates.

```
# Weekly Review - Week <##> of <Year> (Ending <End Date>)

**Highlights (Wins):**
- <Highlight 1: e.g., "Delivered the demo to Client X which was well received.">
- <Highlight 2: e.g., "Feature Y was completed 2 days ahead of schedule.">
- <... list major achievements or positive outcomes of the week.>

**Lowlights (Challenges):**
- <Challenge 1: e.g., "Encountered a production bug that took 3 days to fix, delaying other work.">
- <Challenge 2: e.g., "Team communication broke down on Wednesday, resulting in duplicate work.">
- <... include any setbacks, issues, or things that didn’t go well.>

**Key Metrics Update:**
- <Metric 1 (e.g., Website signups): start of week -> end of week (difference, % change)>
- <Metric 2 (e.g., Sprint burn-down or velocity): planned vs actual>
- <... include any KPI or OKR-related metric that is tracked weekly. Reference the KPI baseline or OKR doc.>

**Progress on Week’s Goals:**
- Goal 1: <Status (Achieved / Partially / Not Achieved)>. <Brief commentary if needed (e.g., "Feature X done, pending QA on Monday").>
- Goal 2: <Status ...>. <Commentary...>
- ... for each goal listed in the Weekly Plan, note outcome.

**Lessons Learned:**
- <Lesson 1: e.g., "Daily 10-min end-of-day sync helped catch issues early – continue this practice.">
- <Lesson 2: e.g., "Need better clarity on spec before development – will involve UX earlier.">
- <... any takeaways to improve process or teamwork going forward.>

**Adjustments for Next Week:**
- <Adjustment 1: e.g., "Allocate extra time for code review given last week’s bug.">
- <Adjustment 2: e.g., "Focus on Project Z as priority shifted (carry over incomplete tasks from this week).">
- <... changes in plan or focus for the upcoming week based on this review.>

*Notes:* Keep this review factual and constructive. Celebrate wins to boost morale, and address challenges openly but without blame. Share the Weekly Review with the team (and any stakeholders, if appropriate) to maintain transparency.
```

### HORIZON_Monthly_Report

*Purpose:* Provides a higher-level summary at the end of each month, reflecting on progress towards quarterly goals, major achievements, and any strategic shifts. Think of it as an expanded version of the Weekly Review that zooms out to a monthly perspective. This is useful for leadership reviews or as input to quarterly planning.

```
# Monthly Report - <Month Year>

**Major Achievements:**
- <Achievement 1: e.g., "Reached 10k users milestone for product, ahead of plan.">
- <Achievement 2: e.g., "Launched Project X on schedule and budget.">
- <... top accomplishments of the month.>

**Summary of Progress toward Quarterly OKRs:**
- Objective 1: <Progress summary (e.g., "On track: 70% of Key Results met so far").>
  - KR1.1: <Status/details>
  - KR1.2: <Status/details>
- Objective 2: <Progress summary (e.g., "At risk: behind on KR2.1 due to delays in...").>
  - KR2.1: <Status/details>
  - ... list each key result and status.
- (Repeat for each active Objective in the quarter)

**Notable Issues & Resolutions:**
- <Issue 1: e.g., "Supply chain delay affected deliveries. Resolution: switched to alternate supplier in Week 2.">
- <Issue 2: e.g., "Team member out for 2 weeks, caused workload spike. Resolution: temporarily reallocated tasks among team.">
- <... any big problems faced and how they were addressed.>

**Team Highlights:**
- <E.g., "Hired 2 new team members (Names) who joined this month.">
- <E.g., "Team training on AI tools completed.">
- <Culture or team-building events or notable changes internally.>

**Next Month Preview:**
- <Focus or theme for next month: e.g., "Prepare for Q4 product launch," or "Integration phase with new partner.">
- <Any expected challenges or needs: e.g., "Will need additional budget approval for marketing push.">

*Notes:* This report should be concise (1-2 pages max). It can be generated by compiling weekly reviews and adding a broader perspective. Use it to communicate up to management or to keep the team’s strategic picture clear.
```

### HORIZON_Quarterly_Business_Review

*Purpose:* A comprehensive review done at the end of a quarter (or start of the next) that evaluates the quarter’s performance and resets priorities for the next quarter. It builds on monthly reports and focuses on OKR outcomes, financial or performance metrics, and strategic adjustments. It often leads to updates in the North Star Charter or setting the next quarter’s OKRs.

```
# Quarterly Business Review - Q<Quarter> <Year>

**Overview of Quarter Performance:**
- **Overall Assessment:** <Summary of how the quarter went (e.g., "Exceeded targets" / "Met most objectives" / "Struggled in areas", etc.)>
- **Key Metrics:** <List critical metrics with quarterly targets vs actuals, e.g., revenue, user growth, NPS, etc.>

**Objective Outcomes:**
- Objective 1 (“<Objective name>”): <Did we achieve it? Summarize results of its KRs.>
  - KR1.1: <Achieved % or result>
  - KR1.2: <Achieved % or result>
- Objective 2 (“<Objective name>”): <Summary>
  - KR2.1: <result>
  - ...
*(Cover each Objective from the Quarterly OKRs doc, noting which KRs were hit or missed and any analysis.)*

**Highlights of Q<Quarter>:**
- <Highlight 1: significant success or milestone reached this quarter and its impact.>
- <Highlight 2: another key positive outcome.>
- ... (at least one per objective or functional area)

**Challenges of Q<Quarter>:**
- <Challenge 1: major hurdle or shortfall and how it affected outcomes.>
- <Challenge 2: ...>
- ... (anything that impeded success)

**Lessons & Insights:**
- <Insight 1: e.g., "Our new marketing channel yielded better results than expected, invest more here.">
- <Insight 2: e.g., "Product development was slowed by tech debt, need to allocate time to address that moving forward.">
- ... (strategic or operational lessons that inform the future)

**Next Quarter Plan Preview:**
- <If available, list the draft Objectives for next quarter or key focus areas. E.g., "Focus on scaling customer support for growth," or "Invest in feature Y based on demand.">
- <Any carry-over initiatives from this quarter that continue into the next.>

**Strategic Adjustments:**
- <Note any changes to the North Star Charter or overall strategy decided because of this review. E.g., "Shift target market from Enterprise to SMB," or "Expand partnerships strategy per QBR discussion.">
- <If none, state that current strategy remains consistent heading into next quarter.>

*Notes:* The QBR is often discussed in a meeting with stakeholders. Use this document as both the pre-read and the record of decisions made (you can append or annotate during the meeting). After finalizing, ensure any strategic changes are propagated: update the North Star Charter or create new Quarterly_OKRs as needed.
```

### HORIZON_Annual_Strategic_Plan

*Purpose:* Outlines the high-level plan for the upcoming year (or reviews the past year) in terms of strategy, major initiatives, and goals. It’s derived from the cumulative insights of quarterly reviews and sets the stage for writing new charters or adjusting the vision if needed. This template helps teams conduct an annual off-site or planning session in a structured way.

```
# Annual Strategic Plan - <Year>

**Executive Summary:**
_<One-paragraph summary of the year’s strategic direction and expected outcomes.>_

**Year in Review (if closing year):**
- **Achievements:** <Bullet list of the most significant accomplishments of the past year.>
- **Challenges:** <Bullet list of major challenges or failures and their lessons.>
- **Trend Analysis:** <Key trends observed in the industry, market, or internal operations over the year that influence future strategy.>

**Vision Refresh (if any):**
_<Note if the team’s Vision/Mission or North Star Charter is updated this year. If yes, summarize the changes or reaffirm the existing vision here._>

**Strategic Objectives for <Year>:**
1. **Objective A:** <Major objective or theme for the year>
   - *Description:* <Explain this objective and why it’s important this year.>
   - *Key Initiatives:* <List big projects or initiatives under this objective.>
2. **Objective B:** <Next major yearly objective>
   - *Description:* …
   - *Key Initiatives:* …
3. **Objective C:** <Another objective, if applicable>
   - *Description:* …
   - *Key Initiatives:* …
*(These are broad, annual objectives, often broken down into quarterly OKRs later. Align them with the Strategic Pillars from the North Star Charter.)*

**Key Metrics Targets:**
- <Metric 1: Target for end of year (e.g., "Reach $X in revenue by Q4", or "100k users by Dec").>
- <Metric 2: ...>
- <... any top-level KPIs and their targets for the year.>

**Budget & Resource Summary:**
- <High-level summary of budget or headcount changes for the year, if applicable.>
- <E.g., "Plan to hire 5 engineers and 2 sales reps by Q3", or "Increase marketing budget by 20% to support Objective A.">

**Risks & Dependencies:**
- <Risk 1: e.g., "Market regulation changes could impact product launch timeline.">
- <Risk 2: e.g., "Dependence on Partner X’s technology; any delay on their side affects our Q2 deliverables.">
- <... list major risks to the plan and external dependencies to monitor.>

**Action Plan & Timeline:**
- Q1: <Focus or major deliverables in Q1>
- Q2: <Focus in Q2>
- Q3: <Focus in Q3>
- Q4: <Focus in Q4>
*(This provides a rough breakdown of the year’s plan per quarter.)*

*Notes:* The Annual Strategic Plan should be revisited mid-year (or quarterly) to ensure it’s still on track. At year-end, use it to evaluate success. It complements the North Star Charter: where the Charter is timeless, this plan is specific to the year’s execution.
```

### HORIZON_Team_Updates

*Purpose:* To collect brief daily updates from team members about their previous day's work, progress, and any blockers. This information is a key input for the Daily Log Generation workflow.

```markdown
# Team Updates - {{Date YYYY-MM-DD}}

**Instructions:** Each team member should provide a brief update below. Focus on:
1.  What you accomplished yesterday.
2.  What you plan to work on today.
3.  Any blockers or impediments.

---

**Team Member: [Name/Alias]**
* **Yesterday's Accomplishments:**
    -   [Accomplishment 1]
    -   [Accomplishment 2]
* **Today's Plan:**
    -   [Task 1]
    -   [Task 2]
* **Blockers/Concerns:**
    -   [Blocker 1, if any]

---

**Team Member: [Name/Alias]**
* **Yesterday's Accomplishments:**
    -   [...]
* **Today's Plan:**
    -   [...]
* **Blockers/Concerns:**
    -   [...]

---

*(Add sections for each team member as needed)*
```

### HORIZON_External_Context

*Purpose:* To capture notable external news, events, or client updates relevant to the team's work for a specific day or period. This can optionally inform the Daily Log or other reports.

```markdown
# External Context - {{Date YYYY-MM-DD or Period}}

**Source/Date of Information:** <e.g., Industry News Digest, Client X Update Call - YYYY-MM-DD>

**Key Points:**
-   **Update/Event 1:** <Brief description of the external event, news, or client update.>
    * *Relevance/Impact:* <Why this is important for the team.>
    * *Source Link (Optional):* <URL if applicable>

-   **Update/Event 2:** <Brief description...>
    * *Relevance/Impact:* <...>
    * *Source Link (Optional):* <...>

-   **(Add more updates as necessary)**

**Overall Assessment/Implication for Today/This Week:**
_<Optional: A brief summary of how this external context might influence the team's focus or priorities.>_
```

### HORIZON_Team_Availability

*Purpose:* To document team member availability for a specific period (e.g., a week), noting any out-of-office days, holidays, or special assignments impacting capacity. This is an optional input for Weekly Planning.

```markdown
# Team Availability - Week {{WeekNumber}} of {{Year}} ({{DateRange YYYY-MM-DD to YYYY-MM-DD}})

**General Notes:** <e.g., Company-wide holiday on Friday, Reduced hours due to X>

---

**Team Member: [Name/Alias]**
* **Availability:** <e.g., Fully Available, Partially Available (details below)>
* **Out of Office (OOO):** <List any OOO days/times, e.g., "Monday (All Day)", "Wednesday PM">
* **Special Assignments/Focus:** <e.g., "Dedicated to Project X support", "Onboarding new hire">
* **Notes:** <Any other relevant availability information>

---

**Team Member: [Name/Alias]**
* **Availability:** <...>
* **Out of Office (OOO):** <...>
* **Special Assignments/Focus:** <...>
* **Notes:** <...>

---

*(Add sections for each team member as needed)*

**Summary of Capacity Impact (Optional):**
_<A brief note on overall team capacity for the week, e.g., "Team at ~80% capacity due to OOO.">_
```

### HORIZON_Metrics_KPI_Update

*Purpose:* To provide a snapshot or update of key performance indicators (KPIs) and other metrics relevant to the team's goals. This document can be used as input for Weekly Review Synthesis and Monthly Report Compilation.

```markdown
# Metrics/KPI Update - {{Date YYYY-MM-DD or Period Ending YYYY-MM-DD}}

**Reporting Period:** <e.g., Week {{WeekNumber}} YYYY, Month of {{Month}} YYYY>

---

**Metric/KPI: [Metric Name 1]**
* **Current Value:** <Value>
* **Previous Value (Optional):** <Value from last period>
* **Target (Optional):** <Target value for this metric>
* **Change (Optional):** <e.g., +X%, -Y units>
* **Notes/Context:** <Brief explanation of any significant changes, trends, or context.>

---

**Metric/KPI: [Metric Name 2]**
* **Current Value:** <Value>
* **Previous Value (Optional):** <Value>
* **Target (Optional):** <Value>
* **Change (Optional):** <...>
* **Notes/Context:** <...>

---

*(Add sections for each relevant metric/KPI)*

**Overall Summary/Observations (Optional):**
_<A brief summary of overall performance based on these metrics, highlighting any key trends or areas needing attention.>_
```

### HORIZON_Customer_Feedback_Summary

*Purpose:* To consolidate and summarize key themes, specific praises, and critical concerns from customer feedback received over a period. This document serves as an optional input for Quarterly Business Reviews and Annual Strategic Planning.

```markdown
# Customer Feedback Summary - {{Period Covered, e.g., QX YYYY or Year YYYY}}

**Data Sources:** <e.g., Support Tickets, Survey Results (Link/Date), User Interviews, App Store Reviews>
**Period Covered:** <Start Date> to <End Date>

---

**Overall Sentiment (Optional):** <e.g., Positive, Neutral, Mixed, Negative - with brief justification>

---

**Key Positive Themes:**
1.  **Theme:** <e.g., Ease of Use for Feature X>
    * *Supporting Feedback Examples (Anonymized if necessary):*
        -   "<Quote or paraphrased feedback 1>"
        -   "<Quote or paraphrased feedback 2>"
    * *Frequency/Impact:* <e.g., Mentioned by ~X% of respondents, High impact on satisfaction>

2.  **Theme:** <e.g., Quality of Customer Support>
    * *Supporting Feedback Examples:*
        -   [...]
    * *Frequency/Impact:* <...>

*(Add more positive themes as identified)*

---

**Key Areas for Improvement/Concerns:**
1.  **Concern/Theme:** <e.g., Performance Issues on Y Platform>
    * *Supporting Feedback Examples (Anonymized if necessary):*
        -   "<Quote or paraphrased feedback 1>"
        -   "<Quote or paraphrased feedback 2>"
    * *Frequency/Impact:* <e.g., Reported by X users, Leading cause of frustration>

2.  **Concern/Theme:** <e.g., Missing Feature Z>
    * *Supporting Feedback Examples:*
        -   [...]
    * *Frequency/Impact:* <...>

*(Add more concerns/themes as identified)*

---

**Specific Feature Requests (Top 3-5):**
-   [Feature Request 1] - *Rationale/Benefit:* <Why customers want this>
-   [Feature Request 2] - *Rationale/Benefit:* <...>
-   [Feature Request 3] - *Rationale/Benefit:* <...>

---

**Actionable Insights/Recommendations (Optional):**
-   <Insight 1 and suggested action>
-   <Insight 2 and suggested action>
```

### HORIZON_Market_Context_Trends_Summary

*Purpose:* To summarize relevant market conditions, competitor activities, and industry trends that might impact the team's strategy or operations. This is an optional input for Quarterly Business Reviews and Annual Strategic Planning.

```markdown
# Market Context & Trends Summary - {{Period Covered, e.g., QX YYYY or Year YYYY}}

**Date of Analysis:** {{YYYY-MM-DD}}
**Information Sources:** <e.g., Industry Reports (Name/Link), News Articles, Competitor Announcements, Market Research Subscriptions>

---

**Overall Market Environment:**
* **Current State:** <Brief overview of the current market conditions - e.g., growing, contracting, stable, volatile.>
* **Key Drivers:** <Factors influencing the market - e.g., technological advancements, economic shifts, regulatory changes.>

---

**Key Industry Trends:**
1.  **Trend:** <Description of a significant trend, e.g., "Adoption of AI in X industry segment">
    * *Impact/Opportunity for Us:* <How this trend affects or could affect the team/product.>
    * *Observed Evidence:* <Specific examples or data points supporting this trend.>

2.  **Trend:** <Description of another trend, e.g., "Shift towards Y business model">
    * *Impact/Opportunity for Us:* <...>
    * *Observed Evidence:* <...>

*(Add more key trends as identified)*

---

**Competitor Landscape:**
* **Major Competitors:** <List 2-3 key competitors>
* **Competitor A ([Name]):**
    * *Recent Activities/Announcements:* <e.g., New product launch, strategic partnership, pricing changes.>
    * *Perceived Strengths/Weaknesses (relative to us):* <Brief analysis.>
* **Competitor B ([Name]):**
    * *Recent Activities/Announcements:* <...>
    * *Perceived Strengths/Weaknesses:* <...>

*(Add more competitors as relevant)*

---

**Emerging Opportunities:**
-   <Opportunity 1 based on market analysis.>
-   <Opportunity 2 based on market analysis.>

**Potential Threats/Risks:**
-   <Threat 1 based on market analysis.>
-   <Threat 2 based on market analysis.>

---

**Strategic Implications/Recommendations (Optional):**
_<How this market context should inform the team's strategy, product development, or positioning.>_
```

### HORIZON_Raw_Meeting_Record

*Purpose:* To capture the unprocessed output of a meeting, such as a raw transcript from a recording or very rough, unorganized notes taken during the meeting. This serves as the primary input for the Meeting Notes Summarization workflow. The content is expected to be free-form.

```markdown
# Raw Meeting Record - {{Meeting Name/Subject}} - {{Date YYYY-MM-DD}}

**Meeting Details (if known):**
* **Subject:** <Meeting Subject Line>
* **Date & Time:** <YYYY-MM-DD HH:MM>
* **Attendees (if noted):** <Names or groups present>
* **Recording Source (if applicable):** <e.g., Zoom transcript, Otter.ai export, manual notes>

---

**Raw Content Start:**

[Paste raw transcript, copied notes, or free-form text here. No specific structure is enforced at this stage. The AI summarization workflow will process this.]

Example of what might be here:

"Okay, so first on the agenda... John, did you have an update on the Q3 numbers? John: Yes, they're looking good, up 5%. We decided to move forward with the Alpha project. Sarah will own the next steps for that, due next Friday. Any questions? Mike: What about the budget for Alpha? John: We'll discuss that offline. Next item: marketing campaign. Lisa mentioned we need new creatives. Lisa: That's right, the old ones are stale. Agreed to brainstorm new ideas by Wednesday. Bob volunteered to set up the meeting. Okay, anything else? No? Meeting adjourned."

... or ...

- Q3 numbers up 5% (John)
- Alpha project GO
    - Sarah next steps EOW Friday
- Budget for Alpha?? -> offline discussion
- Marketing campaign - new creatives needed (Lisa)
    - Brainstorm by Wed
    - Bob to setup meeting.

**Raw Content End:**
```

### HORIZON_Meeting_Agenda

*Purpose:* To outline the topics to be discussed in a meeting, often prepared beforehand. This can be used as an optional input to the Meeting Notes Summarization workflow to help structure the summarized notes.

```markdown
# Meeting Agenda - {{Meeting Name/Purpose}}

**Date & Time:** <YYYY-MM-DD> <HH:MM>
**Location/Call Link:** <Physical location or virtual meeting URL>
**Attendees (Optional Invitees List):** <List of expected attendees>

**Meeting Goal(s):**
-   <Primary objective 1 of the meeting>
-   <Primary objective 2 of the meeting, if any>

---

**Agenda Items:**

1.  **Topic 1:** <Brief description of the first agenda item>
    * *Presenter/Lead (Optional):* <Name>
    * *Time Allotted (Optional):* <e.g., 15 mins>
    * *Desired Outcome:* <What needs to be achieved for this item>

2.  **Topic 2:** <Brief description of the second agenda item>
    * *Presenter/Lead (Optional):* <Name>
    * *Time Allotted (Optional):* <e.g., 20 mins>
    * *Desired Outcome:* <...>

3.  **(Add more agenda items as necessary)**

---

**Pre-Reading/Preparation (Optional):**
-   <Link to document 1> - <Brief description of what to review>
-   <Task to complete before meeting>

**Post-Meeting Next Steps (Placeholder):**
-   <e.g., Decisions to be logged, Actions to be assigned>
```

### HORIZON_Prompt_Analysis_Input

*Purpose:* To consolidate all necessary information for the "AI Prompt Refinement (Prompt Workshop)" workflow. This document bundles the problematic prompt, examples of its unsatisfactory output, a description of the desired outcome, and any relevant prompt design guidelines for the AI to analyze.

````markdown
# Prompt Analysis Input - {{Workflow Name or Prompt Subject}}

**Date of Analysis:** {{YYYY-MM-DD}}
**Target Workflow/Prompt Being Analyzed:** <Name of the HORIZON workflow or a description of the prompt's purpose>

---

**1. Current Prompt Text:**

```text
[Paste the full text of the current prompt that needs improvement here.]
```

-----

**2. Examples of Bad/Unsatisfactory Output (with annotations):**

  * **Example 1:**

      * *Input Snippet (if relevant to show what produced the bad output):*
        ```text
        [Relevant portion of input that led to this bad output]
        ```
      * *Actual Output from Current Prompt:*
        ```text
        [Paste the problematic output here]
        ```
      * *Annotation (What was wrong/missing/incorrect?):*
          - [Specific issue 1, e.g., "Output was too verbose here."]
          - [Specific issue 2, e.g., "Missed a key blocker mentioned in the input."]

  * **Example 2 (Optional, if more are needed):**

      * *Input Snippet:*
        ```text
        [...]
        ```
      * *Actual Output from Current Prompt:*
        ```text
        [...]
        ```
      * *Annotation:*
          - [...]

-----

**3. Desired Outcome Description:**

  * **What should an ideal output look like?**
    \<Describe the characteristics of a good output. e.g., "The output should be a concise summary under 200 words," or "It must extract all action items with owners and due dates."\>

  * **How should the ideal output differ from the bad examples?**
    \<Explain the key differences expected.\>

  * **Specific elements that MUST be included/excluded:**

      - Must include: [Element A, Element B]
      - Must exclude: [Element C, Element D]

-----

**4. Prompt Design Guidelines/Constraints (Optional):**

\<Reference any relevant best practices or rules that the revised prompt should adhere to. This could be from a team's internal prompt engineering guide or general principles.\>

  * Guideline 1: \<e.g., "Prompts should clearly define the AI's role."\>
  * Guideline 2: \<e.g., "Use few-shot examples if output structure is critical."\>
  * Guideline 3: \<e.g., "Ensure prompts are within context limits of the LLM."\>

-----

**5. Any Other Relevant Context:**

\<Provide any other information that might help the "Prompt Engineer Assistant" AI understand the problem and suggest better solutions.\>

````

### HORIZON_Condensation_Criteria

*Purpose:* To provide specific instructions and criteria for the "Knowledge Archive Summarization (Context Condenser)" workflow. This guides the AI on focus areas, desired length, and what to retain or discard when summarizing a collection of older documents.

```markdown
# Condensation Criteria for Archival Summary

**Criteria Set Name (Optional):** <e.g., "Monthly Log Condensation Rules", "Project Alpha Archive Specs">
**Date Created:** {{YYYY-MM-DD}}
**Intended For Document Types:** <e.g., Daily Logs, Weekly Reviews, Meeting Notes for Project X>
**Target Condensation Period (if applicable):** <e.g., Documents older than 90 days, Q1 YYYY Daily Logs>

---

**1. Desired Summary Length/Granularity:**
* <Specify desired output compactness. Examples:>
    * "Produce a one-paragraph summary per week of input."
    * "Limit the total summary to approximately 500 words."
    * "Extract no more than 5 key bullet points per input document."
    * "Generate a narrative summary, focusing on a high-level overview."

---

**2. Key Information to Retain/Prioritize:**
* **Strategic Decisions & Rationale:** <e.g., "Must retain all formally logged decisions and their stated reasons.">
* **Major Achievements/Milestones:** <e.g., "Focus on significant project completions, major feature releases, key targets met.">
* **Significant Challenges/Blockers & Resolutions:** <e.g., "Include recurring major issues, critical incidents, and how they were resolved.">
* **Key Learnings/Insights with Enduring Value:** <e.g., "Preserve lessons learned that led to process changes or strategic shifts.">
* **Numerical Results/Metrics:** <e.g., "Retain final figures for key metrics, budget variances, or performance indicators.">
* **Changes in Strategy/Direction:** <e.g., "Capture any pivots or re-prioritizations.">
* **(Add other specific categories relevant to the documents being condensed)**

---

**3. Information to Omit/De-prioritize:**
* **Routine Updates/Minor Details:** <e.g., "Omit day-to-day minor task updates unless they led to a major outcome.">
* **Transient Operational Details:** <e.g., "Exclude temporary system glitches if resolved quickly without impact.">
* **Redundant Information:** <e.g., "If multiple inputs cover the same event, synthesize it once.">
* **Informal Chatter/Non-Essential Dialogue (from meeting notes, etc.):** <e.g., "Focus on outcomes, not verbatim discussions unless a quote is critical.">
* **(Add other specific categories of information to exclude)**

---

**4. Desired Output Structure/Format (Optional):**
* <Suggest headings or a structure for the condensed output document. Examples:>
    * "Structure by month, then by key themes (Achievements, Challenges, Decisions)."
    * "Use top-level headings: Key Events, Major Decisions, Learnings."
    * "Provide output as a list of bullet points under pre-defined categories."

---

**5. Any Other Specific Instructions:**
* <e.g., "Maintain a neutral and factual tone." >
* <e.g., "If source documents have conflicting information, note the discrepancy." >
* <e.g., "Ensure all dates for key events are preserved accurately." >
```
