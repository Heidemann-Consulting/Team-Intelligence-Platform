# HORIZON Workflow Library

**Version:** 1.0
**Date:** May 18, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

*This section defines the key workflows that drive the HORIZON Protocol. Each workflow is implemented in TIP’s process automation and involves the local LLM using the context of various documents to produce a new or updated document. Inputs and outputs are named (without the `HORIZON_` prefix for brevity). Workflows are designed to chain together seamlessly – for example, the output of the Daily Log workflow is used as input to the Daily Plan workflow, and so on. They also include design considerations to ensure they run within the model’s context limits and play to its strengths (e.g., summarizing content when needed, using few-shot examples, etc.).*

- [HORIZON Workflow Library](#horizon-workflow-library)
  - [Workflow: Daily Log Generation](#workflow-daily-log-generation)
  - [Workflow: Daily Plan Generation](#workflow-daily-plan-generation)
  - [Workflow: Weekly Planning (Kick-off)](#workflow-weekly-planning-kick-off)
  - [Workflow: Weekly Review Synthesis](#workflow-weekly-review-synthesis)
  - [Workflow: Monthly Report Compilation](#workflow-monthly-report-compilation)
  - [Workflow: Quarterly Business Review (QBR) Generation](#workflow-quarterly-business-review-qbr-generation)
  - [Workflow: Annual Strategic Planning Assistant](#workflow-annual-strategic-planning-assistant)
  - [Workflow: Meeting Notes Summarization](#workflow-meeting-notes-summarization)
  - [Workflow: AI Prompt Refinement (Prompt Workshop)](#workflow-ai-prompt-refinement-prompt-workshop)
  - [Workflow: Knowledge Archive Summarization (Context Condenser)](#workflow-knowledge-archive-summarization-context-condenser)
- [Additional Workflows](#additional-workflows)
  - [Workflow: HORIZON\_NorthStarAlignmentCheck](#workflow-horizon_northstaralignmentcheck)
  - [Workflow: HORIZON\_AdaptiveMeetingAgenda](#workflow-horizon_adaptivemeetingagenda)
  - [Workflow: HORIZON\_DecisionLogRetro](#workflow-horizon_decisionlogretro)
  - [Workflow: HORIZON\_OKRPrioritisation](#workflow-horizon_okrprioritisation)
  - [Workflow: HORIZON\_RiskHeatmap](#workflow-horizon_riskheatmap)

## Workflow: Daily Log Generation

* **Purpose:** Every morning, summarize the latest team context into a Daily Log. This workflow collates what happened yesterday and the plan for today into a concise narrative (using the **Daily Log** template). It preserves strategic memory day-to-day and primes the team for action.
* **Trigger:** Manual (each morning after gathering team updates) or Scheduled (automated at a set time, e.g., 9:10 AM).
* **Inputs:**

  * **Team Updates:** Brief notes on what each team member did yesterday and any blockers (e.g., collected via a quick stand-up or chat, can be provided as a small text document or direct input).
  * **Task Backlog:** The current Task Backlog document (to see status of tasks: which were completed yesterday, which remain, new tasks).
  * **Weekly Plan:** The current Week’s Plan (to understand what the goals for this week are, providing context for what’s important today).
  * *(Optional)* **External Context:** If the team maintains any external news or context file (e.g., notable industry news or client updates relevant to today), that can be included so the Daily Log notes those if relevant.
* **Outputs:**

  * **Daily_Log_<Date>:** A new Daily Log document for today (named with today’s date). It follows the Daily Log template (sections for yesterday’s summary, today’s focus, etc.). This output will later be referenced by the Daily Plan workflow.
* **Process Overview:** The AI is prompted as a "Daily Chronicle Assistant" to draft the Daily Log. The prompt provides yesterday’s key points (from Team Updates and any completed tasks in the backlog), and asks the AI to summarize them under “Yesterday’s Summary”. It then provides the week’s goals and today’s date, instructing the AI to draft “Today’s Focus” – essentially forecasting what needs attention today, aligning with weekly goals. Any blockers noted by the team are inserted for the AI to list under “Blockers & Concerns”. If external context is provided, the prompt instructs the AI to add a bullet under Notable Updates for it. The result is a draft Daily Log, which the team’s **Navigator** reviews quickly (to ensure accuracy) before saving.
* **Design Considerations:** This workflow keeps input size small by using bullet summaries rather than dumping entire documents. For example, instead of giving the AI the entire backlog, a pre-processing step (or the prompt itself) might say “Completed tasks: X, Y; Ongoing high-priority tasks: A, B; New tasks: none” gleaned from the backlog. This way, the context stays within a few hundred tokens. The prompt uses the Daily Log template structure as a few-shot pattern so the AI knows the expected format (e.g., providing an example Daily Log from a previous day or a template ghost outline). This maximizes output quality and consistency.

````yaml
# Workflow Name: HORIZON_DailyLogGeneration
# Description: Collates yesterday's events and today's plan into a Daily Log.
# Ritual Relevance: Daily Log Generation (Morning)
# Template Origin: Outputs based on HORIZON_Daily_Log template structure.

inputDocumentSelectors:
  - "Team_Updates*"
  - "Task_Backlog*"
  - "Weekly_Plan*"
  - "External_Context*"
inputDateSelector: null
outputName: "Daily_Log_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are a Daily Chronicle Assistant. Your task is to draft the Daily Log document.
  **Goal:** Create a concise narrative summarizing what happened yesterday and the plan for today, based on the provided input documents. The output should follow the structure of the HORIZON_Daily_Log template.
  **Context:**
  The DocumentContext contains concatenated text from the following documents. Identify them by likely content or sections:
  1.  **Team Updates Document (e.g., "Team_Updates_YYYY-MM-DD"):** Contains notes on what team members did yesterday and any blockers.
  2.  **Task Backlog Document (e.g., "Task_Backlog*"):** Shows the status of tasks (completed, ongoing, new).
  3.  **Weekly Plan Document (e.g., "Weekly_Plan*"):** Outlines goals for the current week.
  4.  **External Context Document (Optional, e.g., "External_Context_YYYY-MM-DD"):** Contains notable industry news or client updates.

  Today's Date: {{Year}}-{{Month}}-{{Day}}.

  **Task:**
  1.  **Analyze Inputs:** Carefully review all provided documents within DocumentContext.
  2.  **Draft "Yesterday’s Summary":**
      * From "Team Updates" and "Task Backlog" (completed tasks), summarize key accomplishments and events from yesterday.
      * Use bullet points for clarity.
  3.  **Draft "Today’s Focus":**
      * Based on the "Weekly Plan" and any carry-over tasks from "Team Updates" or "Task Backlog", outline what needs attention today.
      * Align with weekly goals.
  4.  **Draft "Blockers & Concerns":**
      * Extract any blockers noted in "Team Updates" and list them. If none, state "None".
  5.  **Draft "Notable Updates/Context":**
      * If an "External Context" document is provided and relevant, include a bullet point for any significant update.
      * Include any other critical context for the day mentioned in inputs.
  6. **Constraints:**
      * Use only the information provided in the DocumentContext. Do not invent or assume details.
      * Be concise and factual.
      * Prioritize information directly impacting the team's work for the day and week.
      * If specific input document names are not determinable from DocumentContext structure, synthesize based on the nature of the content found (e.g., look for lists of tasks for the backlog, daily updates for team progress).
  7.  **Structure Output:** Format the entire output strictly according to the template provided in the TEMPLATE section.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
  # Daily Log - {{Year}}-{{Month}}-{{Day}}

  **Yesterday’s Summary:**
  - [Summary of yesterday's key accomplishments and completed tasks based on inputs]
  - [...]

  **Today’s Focus:**
  - [Forecast of what needs attention today, aligned with weekly goals and ongoing tasks, based on inputs]
  - [...]

  **Notable Updates/Context:**
  - [Important context for today from inputs, including external context if provided and relevant]
  - [...]

  **Blockers & Concerns:**
  - [List of blockers from inputs. If none, state "None".]
  - [...]
  ---END TEMPLATE---
````

## Workflow: Daily Plan Generation

* **Purpose:** Right after the Daily Log, generate a focused plan for the current day. The workflow uses the fresh Daily Log and the backlog to select top priorities and assign them, producing a Daily Plan document. This ensures every team member has clear tasks for the day, aligned with ongoing priorities.
* **Trigger:** Manual (each morning, after Daily Log is confirmed) or Scheduled (e.g., 9:20 AM each workday).
* **Inputs:**

  * **Daily_Log:** Today’s Daily Log (the one generated just prior). It provides context on what’s happening today and any blockers.
  * **Task Backlog:** The Task Backlog document (so the AI knows all open tasks and their priority/status).
  * **Weekly Plan:** The current Weekly Plan (to ensure the day’s plan contributes to the week’s goals).
  * **Quarterly OKRs:** (Optional, if needed) The quarterly objectives, so the AI can prefer tasks that advance key results (though the Weekly Plan usually already reflects this).
* **Outputs:**

  * **Daily_Plan_<Date>:** A new Daily Plan for today, listing the top tasks, secondary tasks, and any scheduled events (following the Daily Plan template).
* **Process Overview:** The AI is prompted as a "Planning Assistant". First, it’s given the Weekly Plan’s key goals and told “these are the goals for the week, we are on Day X of 5”. Next, it’s given a snapshot of the Task Backlog – specifically the highest priority tasks and their status. The prompt may filter or explicitly mention tasks that are ready to work on (e.g., those not started or in progress that are High priority). It also includes any carry-over tasks from yesterday (from the Daily Log’s “Yesterday” or backlog status). The AI is asked to choose 3-5 top priorities for today, ensuring each relates to the weekly goals or urgent deadlines, and assign them to owners (the prompt knows team members’ names/roles from the backlog or Weekly Plan). The AI also lists a couple of secondary tasks in case time permits. If the Weekly Plan or Daily Log mentions any meetings or events today, the prompt tells the AI to include them in the schedule section. The output is a draft Daily Plan which the **Navigator** or team lead checks and adjusts (e.g., maybe swapping a task due to human insight). Once confirmed, the Daily Plan is saved and shared.
* **Design Considerations:** Keeping within context limits, the workflow might not feed the entire backlog verbatim. Instead, a pre-step can rank or filter tasks. If needed, the Task Backlog could have a view or query to pull just today-relevant items (some TIP systems might allow queries, or an admin could maintain a short “Today’s Candidates” list). The prompt uses imperative language – e.g., “Select the most important tasks for today from the provided list” and provides examples (“E.g., if a task is nearly done, finish it; if a deadline is tomorrow, include it.”). We also guard against the AI picking too many tasks: the prompt explicitly limits count and reminds the model of human time constraints (the model doesn’t truly know time, but the guideline “3-5 tasks” helps). If the model output includes tasks that are too many or not aligned, the navigator will correct it and retrain the prompt accordingly (e.g., by adding a rule in the prompt next time like “Do not include more than 5 tasks.”). Over time, this workflow learns to consistently produce a realistic daily plan.

````yaml
# Workflow Name: HORIZON_DailyPlanGeneration
# Description: Generates a focused plan for the current day.
# Ritual Relevance: Daily Plan Creation (Morning)
# Template Origin: Outputs based on HORIZON_Daily_Plan template structure.

inputDocumentSelectors:
  - "Daily_Log*"
  - "Task_Backlog*"
  - "Weekly_Plan*"
  - "Quarterly_OKRs*"
inputDateSelector: null
outputName: "Daily_Plan_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are a Planning Assistant. Your task is to draft the Daily Plan document.
  **Goal:** Generate a focused, actionable plan for today, selecting top priorities from the Task Backlog that align with the Weekly Plan and Quarterly OKRs, using context from the Daily Log.
  **Context:**
  The DocumentContext contains concatenated text from:
  1.  **Daily Log (e.g., "Daily_Log_YYYY-MM-DD"):** Provides today's context, blockers, and yesterday's carry-overs.
  2.  **Task Backlog Document (e.g., "Task_Backlog*"):** Lists all open tasks, their priority, and status.
  3.  **Weekly Plan Document (e.g., "Weekly_Plan*"):** Outlines key goals for the week. (Assume Day X of 5 for this week, if not specified, assume mid-week).
  4.  **Quarterly OKRs (Optional, e.g., "Quarterly_OKRs*"):** Provides high-level objectives.

  Today's Date: {{Year}}-{{Month}}-{{Day}}.

  **Task:**
  1.  **Analyze Inputs:** Review all documents in DocumentContext.
  2.  **Identify Top Priorities:**
      * From the "Task Backlog", select 3-5 top priority tasks for today.
      * Ensure these tasks contribute to the "Weekly Plan" goals and, if applicable, "Quarterly OKRs".
      * Consider any carry-over tasks or blockers mentioned in the "Daily Log".
      * Assign owners if clear from backlog or weekly plan context.
  3.  **List Secondary Tasks:** Identify 1-2 secondary tasks from the "Task Backlog" that can be addressed if time permits.
  4.  **Schedule Events/Meetings:** If the "Weekly Plan" or "Daily Log" mentions specific meetings or events for today, list them.
  5.  **Constraints:**
      * Use only information from DocumentContext.
      * The plan must be realistic. Explicitly limit "Top Priorities Today" to 3-5 tasks.
      * If task owners are not specified in the input, leave as "[Unassigned]".
      * Expected outcomes should be inferred from task descriptions and goals.
  6.  **Structure Output:** Format the entire output strictly according to the template provided in the TEMPLATE section.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
  # Daily Plan - {{Year}}-{{Month}}-{{Day}}

  **Top Priorities Today:**
  1.  <Task 1 from backlog> – *Owner:* <Person/Team if known from inputs> – *Expected Outcome:* <Briefly describe what completing this achieves today based on inputs>
  2.  <Task 2 from backlog> – *Owner:* <Person/Team if known from inputs> – *Expected Outcome:* <...>
  3.  <Task 3 from backlog> – *Owner:* <Person/Team if known from inputs> – *Expected Outcome:* <...>
  *(Limit to 3-5 major tasks)*

  **Secondary Tasks (if time permits):**
  - <Task 4 from backlog> – *Owner:* <Person/Team if known from inputs>
  - <Task 5 from backlog> – *Owner:* <Person/Team if known from inputs>

  **Carry-overs from Yesterday:**
  - <Task from Daily Log or backlog not finished yesterday> – *Plan:* <e.g., "Complete by midday today.">
  *(If all tasks from yesterday were completed per Daily Log, state "All tasks from yesterday completed ✅.")*

  **Scheduled Events/Meetings:**
  - <Time (if known)> - <Event from Daily Log or Weekly Plan> (Attendees: <If known>)
  - <...>

  **End-of-Day Target Check:**
  - <Reiterate any specific end-of-day deliverables implied by top priority tasks>
  ---END TEMPLATE---
````

## Workflow: Weekly Planning (Kick-off)

* **Purpose:** At the start of each week, synthesize a Weekly Plan that outlines what the team aims to achieve in the coming days. It ensures alignment with quarterly objectives and accounts for any carry-overs or new priorities. This workflow essentially sets up the “sprint” for the week.
* **Trigger:** Scheduled (e.g., Monday 9:00 AM) or manual when the team is ready to plan the week.
* **Inputs:**

  * **North Star Charter:** The team’s North Star Charter (specifically the Strategic Pillars and possibly mission, to frame the context of why these weekly goals matter).
  * **Quarterly OKRs:** The current quarter’s OKRs, to pick goals to push on this week.
  * **Last Weekly Review:** The Weekly Review from the end of the previous week (to see what was completed or what issues arose that might need attention).
  * **Task Backlog:** The up-to-date Task Backlog (so available tasks can be chosen for this week).
  * **Idea Backlog:** (Optional) The Idea Backlog, in case the team wants to pull in an improvement or innovation item into this week’s work.
  * **Team Availability Info:** (Optional) Any notes about this week’s staffing (e.g., someone on vacation, or particular focus areas for certain team members). If not a separate document, the human planner can input this info into the prompt manually.
* **Outputs:**

  * **Weekly_Plan_<WeekNumber>:** A Weekly Plan document for the new week, following the template (with theme, key goals, tasks, etc.).
* **Process Overview:** The AI (as a "Sprint Planner") is prompted with a high-level context first: a quick recap of where we stand in the quarter (like “Quarter Q2: Objective 1 is 50% done, Objective 2 on track, etc.” possibly from the OKR doc), and any notable shift in strategy (maybe from Charter if relevant, or last week’s lesson “we need to focus on quality this week”). Then it’s given the key outcomes from last week’s review (especially incomplete goals or new issues). With that context, it’s given the Task Backlog’s top items and asked to propose what to tackle this week to advance the objectives. The AI will draft the “Key Goals for the Week” as 2-5 bullet points (likely influenced by the quarter goals and last week’s carry-overs), then list specific tasks/deliverables under each or in the tasks section, assign owners and tentative due days (which would be within the week). It will also fill in any known events (from context or if provided manually, e.g., “Thursday: client demo”). The output Weekly Plan is then reviewed in a short team meeting; minor edits can be made (this is where the team might adjust an AI suggestion or add a missing item). The final plan is saved and sets the stage for the daily plans.
* **Design Considerations:** The prompt needs to balance ambition with realism. We handle this by giving the AI a sense of capacity: e.g., telling it how many big tasks can usually fit in a week for this team (maybe mention “Assume the team can complete 5-7 significant tasks in a week” or use last week’s output as a guide). We also include the team’s roles or specialties, so the AI assigns tasks appropriately (for example, identify who is likely to do which task based on prior assignments, as seen in backlog or previous plans). To keep context tight, not every document is fed in full: the Quarterly OKRs might be summarized to just the objectives and any KRs that are lagging, and the backlog might be filtered to high priority items or those tagged for “this week” (one trick is to maintain a field in the backlog for “Target Week” and just feed those entries). By structuring the prompt with sections (e.g., “Context: <last week summary>”, “Goals to consider: <quarter goals>”, “Tasks available: <list>”, then “Now produce a plan…”), the model can systematically use each part. If the model tends to omit something (say it forgot a carry-over task), the facilitator will tweak the prompt or just add that task manually. Generally, this workflow sets up a strong starting plan that humans fine-tune slightly.

````yaml
# Workflow Name: HORIZON_WeeklyPlanningKickoff
# Description: Synthesizes a Weekly Plan for the upcoming week.
# Ritual Relevance: Weekly Kick-off Planning (Mondays)
# Template Origin: Outputs based on HORIZON_Weekly_Plan template structure.

inputDocumentSelectors:
  - "North_Star_Charter"
  - "Quarterly_OKRs*"
  - "Weekly_Review*"
  - "Task_Backlog*"
  - "Idea_Backlog*"
  - "Team_Availability*"
inputDateSelector: null
outputName: "Weekly_Plan_W{{CurrentWeekNumber}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are a Sprint Planner AI. Your task is to draft the Weekly Plan for the upcoming week.
  **Goal:** Create a Weekly Plan that outlines key goals and tasks, aligned with the North Star Charter and Quarterly OKRs, considering last week's review, current backlogs, and team availability.
  **Context:**
  The DocumentContext contains concatenated text from:
  1.  **North Star Charter:** Team's mission, vision, strategic pillars.
  2.  **Quarterly OKRs (e.g., "Quarterly_OKRs*"):** Current quarter's objectives. (Assume "Quarter QX: Objective 1 is Y% done..." summary is available or can be inferred).
  3.  **Last Weekly Review (e.g., "Weekly_Review*"):** Outcomes, incomplete goals, issues from the previous week.
  4.  **Task Backlog (e.g., "Task_Backlog*"):** Top available tasks.
  5.  **Idea Backlog (Optional, e.g., "Idea_Backlog*"):** Potential new items.
  6.  **Team Availability (Optional, e.g., "Team_Availability*"):** Staffing notes for the week.

  Current Date: {{Year}}-{{Month}}-{{Day}}. Assume this is the start of the new week.

  **Task:**
  1.  **Analyze Inputs:** Review all documents. Synthesize high-level context (e.g., progress in quarter, strategic focus needed based on last week's review).
  2.  **Draft "Week’s Theme/Focus":** Propose a short theme for the week based on the most pressing objectives or carry-overs.
  3.  **Draft "Key Goals for the Week":**
      * Propose 2-5 key goals for the week. These should advance "Quarterly OKRs" and address items from "Last Weekly Review" (e.g., incomplete goals).
  4.  **Draft "Planned Tasks/Deliverables":**
      * From "Task Backlog" (and "Idea Backlog" if relevant), list specific tasks/deliverables that support the weekly goals.
      * Assign owners and tentative due days (within the week) if information is available in inputs (e.g., team roles or typical assignments from backlog).
      * Consider team capacity: "Assume the team can complete 5-7 significant tasks in a week" or use "Team Availability" if provided.
  5.  **Populate "Resource Availability":** Summarize from "Team_Availability*" document if provided. Otherwise, state "Standard availability assumed."
  6.  **Identify "Known Risks/Challenges This Week":** Based on "Last Weekly Review" or task complexities.
  7.  **Suggest "Communication & Coordination":** Note any meetings from inputs or imply standard coordination needs.
  8.  **Constraints:**
      * Use only information from DocumentContext.
      * The plan should be ambitious but realistic given a typical week's capacity.
      * Please respect the team availability for everything you plan and give a reasoning for why you think that what you plan for the week fits into the given availability.
      * Prioritize tasks that advance quarterly goals or address carry-overs.
  9.  **Structure Output:** Format the entire output strictly according to the template provided in the TEMPLATE section.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
  # Weekly Plan - Week <Number> of {{Year}} (Starting {{Year}}-{{Month}}-{{Day}})

  **Week’s Theme/Focus:** _<Proposed theme based on inputs>_

  **Key Goals for the Week:**
  - <Proposed Goal 1 based on inputs, linked to OKRs/last week>
  - <Proposed Goal 2 based on inputs, linked to OKRs/last week>
  - [...] *(2-5 goals)*

  **Planned Tasks/Deliverables:**
  - <Task/Deliverable 1 from backlog/ideas> – *Owner:* <Person/Team if known> – *Due:* <Day/Date within week>
  - <Task/Deliverable 2 from backlog/ideas> – *Owner:* <Person/Team if known> – *Due:* <Day/Date within week>
  - [...] *(Consider 5-7 significant tasks)*

  **Resource Availability:**
  - <Summary from Team_Availability*, or "Standard availability assumed.">

  **Known Risks/Challenges This Week:**
  - <Risk 1 based on inputs>
  - <Risk 2 based on inputs>

  **Communication & Coordination:**
  - <Coordination notes based on inputs>
  ---END TEMPLATE---
````

## Workflow: Weekly Review Synthesis

* **Purpose:** At week’s end, produce a Weekly Review document that summarizes what happened, evaluates against the Weekly Plan, and captures lessons. This gives the team situational awareness and input for continuous improvement. It’s also a key input for monthly and quarterly reviews.
* **Trigger:** Scheduled (e.g., Friday 4:00 PM or last day of the workweek) or manual when ready to review.
* **Inputs:**

  * **Weekly Plan:** The Weekly Plan for this ending week (to compare planned vs actual outcomes).
  * **Daily Logs:** All Daily Logs from this week (to gather details of what occurred each day).
  * **Task Backlog:** The Task Backlog (to see which tasks moved to Done during the week, and which didn’t).
  * **Quarterly OKRs:** (Optional) The OKR document, to update any progress metrics (the metrics steward might have updated some numbers at week’s end).
  * **Decision Log:** (Optional) Check if any major decisions were made during the week to mention in highlights or challenges.
  * **Any Metrics/KPI Source:** (Optional) If there’s a separate KPI tracker or if metrics are embedded in an OKR doc, include the latest figures so the AI can incorporate them in the review.
* **Outputs:**

  * **Weekly_Review_<WeekNumber>:** A Weekly Review document for this week.
* **Process Overview:** The AI is prompted as a "Retrospective Analyst". It is given the Weekly Plan and asked to identify each goal’s status (the human could even annotate the plan with done/not done, or the AI can infer from backlog and daily logs). Next, the prompt feeds in highlights from daily logs (the easiest way is to concatenate each day’s highlights or a list of what got done each day). The model is asked to compile the top wins (things that were accomplished or went well), and the top challenges (things that didn’t go as planned or issues that arose). Because daily logs already contain a “Yesterday’s Summary” and “Blockers” each day, the model can aggregate common themes (the prompt may explicitly say “From the logs, identify any recurring blocker or a significant event”). It uses the completed tasks info to list achievements. For metrics, the prompt includes any updates (e.g., “KPI X was Y last week and Z now”). The AI then drafts the Weekly Review: populating highlights, lowlights, metrics changes, progress on each weekly goal (e.g., achieved or not, with a reason), lessons learned (this part might come from an analysis of what challenges were faced and how they were resolved, possibly also scanning the Decision Log for any changes in approach). Finally, it suggests adjustments or recommendations for next week (this can be derived from any unfinished tasks or lessons, e.g., “carry Task A to next week”, “spend more time on testing next week given bug issues”). The draft review is then reviewed by the **Editor-in-Chief** role (or any team member assigned to finalize it), who makes sure it’s accurate and not missing context. The finalized Weekly Review is saved.
* **Design Considerations:** The input could be large if we naively dump all daily logs in full. To stay within context, the workflow can first compress the daily logs: e.g., instruct the model to read all daily logs and extract only the key bullet points from each (this could even be done in a preliminary prompt or by having the prompt itself say: “Here are 5 daily summaries, extract 3 key points from each”). By summarizing each day, the model reduces the info to a manageable size and then can analyze it. Alternatively, the workflow might run in two stages with the TIP engine: Stage 1 uses the model to summarize daily logs into a short weekly events list; Stage 2 uses that summary plus plan & metrics to create the review. Such chaining ensures even a 4K token model can handle a week’s info. We also embed some few-shot style in the prompt: perhaps include the format or an example snippet of a good Weekly Review (maybe from a past week) so the AI mirrors the style (like including a lesson learned, etc.). Moreover, to mitigate any hallucination, the prompt emphasizes to stick to the facts from the logs and tasks: e.g., “If a metric is not mentioned, don’t invent it.” The human reviewer will catch if any detail looks off (like claiming a win that didn’t happen) and can correct it. As the team uses HORIZON, the AI will get better because it can also be given last week’s review as an example to follow for structure and even to understand ongoing story (context of what happened before).

````yaml
# Workflow Name: HORIZON_WeeklyReviewSynthesis
# Description: Produces a Weekly Review document summarizing the week's events and performance.
# Ritual Relevance: Weekly Review & Retro (Fridays)
# Template Origin: Outputs based on HORIZON_Weekly_Review template structure.

inputDocumentSelectors:
  - "Weekly_Plan*"
  - "Daily_Log*"
  - "Task_Backlog*"
  - "Quarterly_OKRs*"
  - "Decision_Log*"
  - "Metrics_KPI_Update*"
inputDateSelector: null
outputName: "Weekly_Review_W{{CurrentWeekNumber}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are a Retrospective Analyst AI. Your task is to draft the Weekly Review.
  **Goal:** Summarize the week's accomplishments, challenges, and progress against the Weekly Plan. Identify lessons learned and suggest adjustments for next week.
  **Context:**
  The DocumentContext contains concatenated text from:
  1.  **Weekly Plan (e.g., "Weekly_Plan*"):** The goals and tasks planned for this week.
  2.  **Daily Logs (e.g., "Daily_Log*"):** Details of what occurred each day this week (accomplishments, blockers).
  3.  **Task Backlog (e.g., "Task_Backlog*"):** Status of tasks (Done, In Progress).
  4.  **Quarterly OKRs (Optional):** For context on metrics.
  5.  **Decision Log (Optional):** For any major decisions made.
  6.  **Metrics/KPI Update (Optional, e.g., "Metrics_KPI_Update*"):** Latest figures for key metrics.

  Current Date: {{Year}}-{{Month}}-{{Day}}. Assume this is the end of the week being reviewed.

  **Task:**
  1.  **Analyze Inputs:** Review all documents. To manage context size, focus on summarizing key bullet points from daily logs rather than full text.
  2.  **Draft "Highlights (Wins)":**
      * From "Daily Logs" (accomplishments) and "Task Backlog" (completed tasks), compile top wins.
  3.  **Draft "Lowlights (Challenges)":**
      * From "Daily Logs" (blockers, issues) and "Task Backlog" (unfinished/delayed tasks), list key challenges.
  4.  **Draft "Key Metrics Update":**
      * If "Metrics_KPI_Update*" or relevant data in "Quarterly_OKRs" is provided, summarize changes in key metrics. State if data is unavailable.
  5.  **Draft "Progress on Week’s Goals":**
      * For each goal in the "Weekly Plan", assess its status (Achieved, Partially Achieved, Not Achieved) based on "Daily Logs" and "Task Backlog". Provide brief commentary.
  6.  **Draft "Lessons Learned":**
      * Analyze challenges and wins. Infer 1-2 key lessons. Check "Decision Log" for process changes.
  7.  **Draft "Adjustments for Next Week":**
      * Suggest 1-2 adjustments or carry-over focuses based on unfinished tasks or lessons learned.
  8.  **Constraints:**
      * Use only information from DocumentContext.
      * Be factual. If a metric is not mentioned, state "Data unavailable".
      * Prioritize impactful wins, challenges, and lessons.
      * Prompt emphasizes summarizing daily logs: "focus on summarizing key bullet points from daily logs rather than full text."
  9.  **Structure Output:** Format the entire output strictly according to the template provided in the TEMPLATE section.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
  # Weekly Review - Week <Number> of {{Year}} (Ending {{Year}}-{{Month}}-{{Day}})

  **Highlights (Wins):**
  - <Win 1 from inputs>
  - <Win 2 from inputs>
  - [...]

  **Lowlights (Challenges):**
  - <Challenge 1 from inputs>
  - <Challenge 2 from inputs>
  - [...]

  **Key Metrics Update:**
  - <Metric 1: Start -> End (Change), based on inputs or "Data unavailable">
  - <Metric 2: Start -> End (Change), based on inputs or "Data unavailable">
  - [...]

  **Progress on Week’s Goals:**
  - Goal 1 (<from Weekly Plan>): <Status (Achieved/Partially/Not Achieved)>. <Commentary based on inputs.>
  - Goal 2 (<from Weekly Plan>): <Status...>. <Commentary based on inputs.>
  - [...]

  **Lessons Learned:**
  - <Lesson 1 based on inputs' analysis>
  - <Lesson 2 based on inputs' analysis>
  - [...]

  **Adjustments for Next Week:**
  - <Adjustment 1 based on inputs' analysis (e.g., carry over task, focus area)>
  - <Adjustment 2 based on inputs' analysis>
  - [...]
  ---END TEMPLATE---
````

## Workflow: Monthly Report Compilation

* **Purpose:** At the end of each month, generate a Monthly Report that aggregates the higher-level view of progress and issues over that month. This helps in strategic adjustment and is a stepping stone to quarterly reviews.
* **Trigger:** Scheduled (e.g., last working day of the month) or manual.
* **Inputs:**

  * **Weekly Reviews:** All Weekly Review docs for that month (typically four).
  * **Quarterly OKRs:** The OKR document (to gauge how far along the team is in the quarter after this month).
  * **North Star Charter:** (Optional) The Charter, in case any strategic re-alignment needs noting or to ensure consistency in language.
  * **Idea Backlog & Decision Log:** (Optional) These can be scanned to see if any major innovations were implemented or decisions made this month that should be highlighted.
  * **Metrics/KPI Update:** If there’s a KPI or metrics document updated monthly or at month-end, include that data for the AI.
* **Outputs:**

  * **Monthly_Report_<MonthYear>:** A Monthly Report document.
* **Process Overview:** The AI acts as a "Report Aggregator". It is given each Weekly Review’s highlights and lowlights (which can be extracted from those docs) and asked to merge them into a coherent monthly perspective. The prompt might outline: “Looking at the four weeks: what were the major achievements overall? What patterns do you see in challenges? Summarize key metric trends.” It also references the quarterly OKRs to say “We are 2/3 through Q and Objective1 is tracking ahead (or behind) based on KRs.” The AI drafts the sections: Achievements (it might list the biggest ones that were repeated or significant in weekly reports), Progress on OKRs (taking data from KRs after two months of quarter, for example 66% time gone, are KRs ~66% done?), Issues/Resolutions (any challenge that spanned multiple weeks or a significant event, e.g., “Outage in week 2 impacted deliverables, but recovered by week 3”), Team updates (if any, maybe from Decision Log: “added 2 new clients” or “new hire joined”), and a Preview for next month (likely drawn from anything mentioned in Weekly Reviews about upcoming plans or simply the fact that if next month is end of quarter, focus will be on closing OKRs). The draft is then reviewed by the team leadership (e.g., manager or Editor-in-Chief) for accuracy and completeness.
* **Design Considerations:** Summarizing across weeks means the AI must not double-count or list every single weekly item. The prompt guides it to be selective: “Only include the most noteworthy accomplishments (e.g., those that had a big impact or were mentioned multiple times)” and likewise for challenges. The context might be slightly over 4k tokens if weekly reviews are long, so summarization is key. Possibly, the workflow leverages the already summarized Weekly Reviews rather than raw daily data. If not, a preliminary step might ask the AI to summarize the month in bullets from weekly data, but using monthly chunking is more straightforward. Another technique: feed the OKR doc and ask the AI to base the structure around those objectives (ensuring it doesn’t skip any). Also, given the strategic nature, the prompt may encourage an analytical tone: e.g., “For each objective, briefly analyze why it was or wasn’t achieved.” This pushes the model to incorporate reasons (from decision log or challenges input). By dividing the prompt into clear sections (maybe use headings in the system message like “### Objectives Outcome ### – \[OKR data] – Write analysis here; ### Highlights ### – \[some input] – Summarize here,” etc.), the model will format the output accordingly. Human oversight for this workflow is a must – the team will adjust any strategic recommendations and confirm the analysis – but the AI greatly speeds up the compilation of the baseline QBR document.

````yaml
# Workflow Name: HORIZON_MonthlyReportCompilation
# Description: Generates a Monthly Report aggregating weekly reviews and progress.
# Ritual Relevance: Monthly Strategy Check
# Template Origin: Outputs based on HORIZON_Monthly_Report template structure.

inputDocumentSelectors:
  - "Weekly_Review_W*"
  - "Quarterly_OKRs*"
  - "North_Star_Charter"
  - "Idea_Backlog*"
  - "Decision_Log*"
  - "Metrics_KPI_Update*"
inputDateSelector: null
outputName: "Monthly_Report_{{Year}}-{{Month}}"
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are a Report Aggregator AI. Your task is to draft the Monthly Report.
  **Goal:** Aggregate information from the month's Weekly Reviews to provide a higher-level view of progress, achievements, issues, and alignment with Quarterly OKRs.
  **Context:**
  The DocumentContext contains concatenated text from:
  1.  **Weekly Reviews (e.g., "Weekly_Review_W*"):** Highlights, lowlights, metrics, and lessons from each week of the month.
  2.  **Quarterly OKRs (e.g., "Quarterly_OKRs*"):** To assess progress.
  3.  **North Star Charter (Optional):** For strategic context.
  4.  **Idea Backlog & Decision Log (Optional):** For innovations or major decisions.
  5.  **Metrics/KPI Update (Optional, e.g., "Metrics_KPI_Update*"):** Month-end metric data.

  Current Date: {{Year}}-{{Month}}-{{Day}}. Assume this is for the month ending.

  **Task:**
  1.  **Analyze Inputs:** Review all documents. Focus on extracting major themes from weekly reviews, not minor details.
  2.  **Draft "Major Achievements":**
      * From "Weekly Reviews" (Highlights sections), synthesize the most significant accomplishments of the month. Avoid simple repetition; group related wins.
  3.  **Draft "Summary of Progress toward Quarterly OKRs":**
      * For each Objective in "Quarterly_OKRs", assess progress based on cumulative data from "Weekly Reviews" and "Metrics/KPI Update". Note if on track, at risk, or lagging.
  4.  **Draft "Notable Issues & Resolutions":**
      * From "Weekly Reviews" (Lowlights/Challenges sections), identify recurring or major issues. Note resolutions if mentioned.
  5.  **Draft "Team Highlights":**
      * From "Weekly Reviews", "Decision_Log", or other inputs, note any significant team changes, hires, or major internal events.
  6.  **Draft "Next Month Preview":**
      * Based on unfinished work from "Weekly Reviews" (Adjustments sections) or upcoming items in "Quarterly_OKRs", suggest a focus for the next month.
  7.  **Constraints:**
      * Use only information from DocumentContext.
      * Synthesize, do not just list. Focus on the monthly perspective.
      * Be selective: "Only include the most noteworthy accomplishments".
  8.  **Structure Output:** Format the entire output strictly according to the template provided in the TEMPLATE section.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
  # Monthly Report - {{Month}} {{Year}}

  **Major Achievements:**
  - <Synthesized Achievement 1 from weekly reviews>
  - <Synthesized Achievement 2 from weekly reviews>
  - [...]

  **Summary of Progress toward Quarterly OKRs:**
  - Objective 1 (<from Quarterly_OKRs>): <Progress summary (e.g., On track: X% of KRs met) based on inputs.>
    - KR1.1 (<from Quarterly_OKRs>): <Status/details based on inputs>
    - KR1.2 (<from Quarterly_OKRs>): <Status/details based on inputs>
  - Objective 2 (<from Quarterly_OKRs>): <Progress summary...>
    - [...]
  *(Repeat for each active Objective)*

  **Notable Issues & Resolutions:**
  - <Issue 1 from weekly reviews and its resolution if stated>
  - <Issue 2 from weekly reviews and its resolution if stated>
  - [...]

  **Team Highlights:**
  - <Team update 1 from inputs>
  - <Team update 2 from inputs>

  **Next Month Preview:**
  - <Focus/theme for next month based on inputs>
  - <Expected challenges/needs based on inputs>
  ---END TEMPLATE---
````

## Workflow: Quarterly Business Review (QBR) Generation

* **Purpose:** Generate the Quarterly Business Review document at quarter-end. This is a comprehensive analysis of the quarter’s performance and a crucial input to planning the next quarter (and sometimes presented to stakeholders). It collates info from weekly/monthly docs and OKRs.
* **Trigger:** Manual (e.g., on the last day of the quarter or first week of the new quarter, when the team is ready to review).
* **Inputs:**

  * **Quarterly OKRs:** The OKR document for the quarter (with final statuses of each Key Result).
  * **Weekly Reviews:** All Weekly Reviews from the quarter (or Monthly Reports, if those were thorough, to reduce volume).
  * **Monthly Reports:** (Optional) If available, these give a summary of each month.
  * **North Star Charter:** (Optional) for reference to long-term vision when assessing strategy.
  * **Decision Log:** (Optional) to see any major pivots or strategic decisions in the quarter.
  * **Customer Feedback / Market context:** (Optional) If the team has documents for customer feedback or market trends, include anything relevant that might have impacted the quarter outcomes or should influence next steps.
* **Outputs:**

  * **Quarterly_Business_Review_Q<Quarter>_<Year>:** The QBR document.
* **Process Overview:** The AI (as an "Executive Analyst") is tasked with creating a structured, high-level review. The prompt likely starts by stating the quarter’s objectives and asking the AI to state whether each was achieved, partially achieved, or missed, using the OKR data (which might indicate percentages or yes/no). Then, it includes the main highlights and challenges from the quarter. This is drawn from either the monthly reports or an aggregate of weekly reviews – possibly we give it the Monthly Reports to keep it succinct, or if not, we feed a short summary of each quarter’s months. The AI then populates sections: Overall Assessment (it might conclude something like “Q2 was a strong quarter with most goals met except in area X”), Key Metrics vs Targets (comparing planned vs actual for any numeric goals), Objective Outcomes (listing each objective and outcome), Highlights (could be the top 3-5 achievements, perhaps one per month or per objective), Challenges (major impediments or risks encountered), and Lessons & Insights. Finally, the prompt asks it to draft the preview for next quarter and strategic adjustments. The content here might be minimal if planning isn’t finalized; the AI could suggest some obvious next steps (like “Objective 2 will carry into next quarter since it wasn’t finished” or “Given the success in launching X, next quarter might focus on scaling it”). The human team will finalize these forward-looking parts, but the AI’s summary ensures nothing is forgotten. The QBR draft is reviewed typically by the leadership team who might tweak language or add commentary, then it’s finalized.
* **Design Considerations:** The QBR is an important document so accuracy is crucial. The workflow should ensure that any quantitative data (like KR percentages or revenue numbers) are provided either by feeding the OKR doc values or having a human insert them into the prompt. We include caution in the prompt: “Do not make assumptions about numbers that are not given.” The context will be large (a quarter’s worth of info), so again summarization is key. Possibly, the workflow leverages the already summarized Monthly Reports rather than raw weekly data. If not, a preliminary step might ask the AI to summarize the quarter in bullets from weekly data, but using monthly chunking is more straightforward. Another technique: feed the OKR doc and ask the AI to base the structure around those objectives (ensuring it doesn’t skip any). Also, given the strategic nature, the prompt may encourage an analytical tone: e.g., “For each objective, briefly analyze why it was or wasn’t achieved.” This pushes the model to incorporate reasons (from decision log or challenges input). By dividing the prompt into clear sections (maybe use headings in the system message like “### Objectives Outcome ### – \[OKR data] – Write analysis here; ### Highlights ### – \[some input] – Summarize here,” etc.), the model will format the output accordingly. Human oversight for this workflow is a must – the team will adjust any strategic recommendations and confirm the analysis – but the AI greatly speeds up the compilation of the baseline QBR document.

````yaml
# Workflow Name: HORIZON_QBRGeneration
# Description: Generates the Quarterly Business Review document.
# Ritual Relevance: Quarterly Business Review (Quarter's end)
# Template Origin: Outputs based on HORIZON_Quarterly_Business_Review template structure.

inputDocumentSelectors:
  - "Quarterly_OKRs*"
  - "Monthly_Report*"
  - "Weekly_Review_W*"
  - "North_Star_Charter"
  - "Decision_Log*"
  - "Customer_Feedback_Summary*"
  - "Market_Context_Summary*"
inputDateSelector: null
outputName: "Quarterly_Business_Review_Q{{WorkflowName | placeholder_for_quarter_number_logic}}_{{Year}}"
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are an Executive Analyst AI. Your task is to draft the Quarterly Business Review (QBR).
  **Goal:** Create a comprehensive, structured QBR analyzing the quarter's performance against OKRs, summarizing highlights, challenges, lessons, and suggesting strategic adjustments.
  **Context:**
  The DocumentContext contains concatenated text from:
  1.  **Quarterly OKRs (e.g., "Quarterly_OKRs*"):** With final status for each Key Result.
  2.  **Monthly Reports (e.g., "Monthly_Report_*") OR Weekly Reviews (e.g., "Weekly_Review_W*"):** Covering the quarter. Prefer Monthly Reports if available for conciseness.
  3.  **North Star Charter (Optional):** For long-term strategic reference.
  4.  **Decision Log (Optional, e.g., "Decision_Log*"):** Major decisions made.
  5.  **Customer Feedback / Market Context (Optional, e.g., "Customer_Feedback_Summary*"):** External factors.

  Assume this QBR is for the quarter just ended. Current Date: {{Year}}-{{Month}}-{{Day}}.

  **Task:**
  1.  **Analyze Inputs:** Review all documents. If using Weekly Reviews, synthesize monthly themes first if Monthly Reports are absent.
  2.  **Draft "Overview of Quarter Performance":**
      * Write an "Overall Assessment" of the quarter.
      * List "Key Metrics" (targets vs. actuals) if data is available in inputs.
  3.  **Draft "Objective Outcomes":**
      * For each Objective in "Quarterly_OKRs", state if achieved, partially, or missed. Summarize KR results and provide brief analysis using monthly/weekly report data.
  4.  **Draft "Highlights of QX":**
      * Synthesize the top 3-5 achievements from monthly/weekly reports.
  5.  **Draft "Challenges of QX":**
      * Synthesize major impediments or shortfalls from monthly/weekly reports.
  6.  **Draft "Lessons & Insights":**
      * Infer strategic or operational lessons based on objective outcomes and challenges. Check "Decision Log".
  7.  **Draft "Next Quarter Plan Preview":**
      * Suggest obvious next steps or carry-overs. If specific next-quarter plans are mentioned in inputs, include them.
  8.  **Draft "Strategic Adjustments":**
      * Based on the review, note any suggested changes to strategy or the "North Star Charter".
  9.  **Constraints:**
      * Use only information from DocumentContext.
      * Maintain an analytical and strategic tone. "For each objective, briefly analyze why it was or wasn’t achieved.".
      * Quantitative data for KRs must come from inputs. "Do not make assumptions about numbers that are not given.".
      * Prioritize summarizing from Monthly Reports if available.
  10. **Structure Output:** Format the entire output strictly according to the template provided in the TEMPLATE section.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
  # Quarterly Business Review - Q<Number> {{Year}}

  **Overview of Quarter Performance:**
  - **Overall Assessment:** <Summary of quarter performance based on inputs>
  - **Key Metrics:** <List critical metrics (target vs actual) from inputs, or "Data unavailable">

  **Objective Outcomes:**
  - Objective 1 ("<from OKRs doc>"): <Achieved/Partially/Missed>. <Summary of KR results & analysis from inputs.>
    - KR1.1 ("<from OKRs doc>"): <Result from inputs>
    - KR1.2 ("<from OKRs doc>"): <Result from inputs>
  - Objective 2 ("<from OKRs doc>"): <Summary...>
    - [...]
  *(Cover all Objectives from the OKRs document)*

  **Highlights of Q<Number>:**
  - <Highlight 1 synthesized from inputs>
  - <Highlight 2 synthesized from inputs>
  - [...] *(3-5 highlights)*

  **Challenges of Q<Number>:**
  - <Challenge 1 synthesized from inputs>
  - <Challenge 2 synthesized from inputs>
  - [...]

  **Lessons & Insights:**
  - <Insight 1 based on inputs>
  - <Insight 2 based on inputs>
  - [...]

  **Next Quarter Plan Preview:**
  - <Focus areas/carry-overs for next quarter, from inputs>
  - [...]

  **Strategic Adjustments:**
  - <Suggested changes to strategy/Charter based on inputs>
  - [...]
  ---END TEMPLATE---
````

## Workflow: Annual Strategic Planning Assistant

* **Purpose:** Assist in creating the Annual Strategic Plan by summarizing the past year and drafting goals for the next year. It uses accumulated knowledge to provide a first draft that the leadership can refine during annual planning.
* **Trigger:** Manual (during annual planning period, e.g., end of Q4).
* **Inputs:**

  * **North Star Charter:** The current North Star Charter (to see mission, vision, strategic pillars – in case the team wants to adjust them).
  * **All Quarterly Reviews (past year):** The QBR documents for each quarter of the year that’s ending (this provides the accomplishments and challenges per quarter).
  * **Annual Plan (previous year):** (If available) the plan that was set at the start of the year now ending, to evaluate what was expected vs what happened.
  * **Idea Backlog:** (Optional) to surface any big ideas that were deferred or emerged during the year as potential initiatives for next year.
  * **Customer Feedback / Market Trends:** (Optional) any summary of external changes (market trend doc or major customer feedback themes) to inform new strategy.
* **Outputs:**

  * **Annual_Strategic_Plan_\<Year+1>:** A draft of the Annual Strategic Plan for the upcoming year.
* **Process Overview:** The AI (as a "Strategic Planner") is given a broad prompt. First, it may be asked to summarize the year in review: reading the four QBRs and extracting the main achievements and challenges of the year (the prompt can provide these in chronological order). Then it’s asked to consider whether the vision or strategic pillars need update (this might be left more open-ended; perhaps the human will manually decide that part, but the AI could suggest based on patterns, e.g., “The team consistently struggled with X, consider adding a strategic focus on X next year”). Next, the prompt includes any known high-level direction for next year (if leadership has already brainstormed objectives, those can be input). Otherwise, the AI might propose objectives based on the idea backlog or unfinished business from this year. For example, if a big initiative was started but not finished, the AI might suggest “Complete rollout of Project Y in Q1” as an objective. The AI drafts sections of the Annual Plan: Achievements of last year (a short recap), strategic objectives for next year (with some rationale and possible key initiatives under each), and key metrics targets (it can propose something like “increase by 20%” if not given, but likely a human will adjust actual numbers). It may also list major known risks (pulling from the challenges of last year as hints). The human leadership team will definitely fine-tune this output – it’s more of a thought-starter to frame the conversation in the annual offsite or meeting. Once refined, the Annual Strategic Plan becomes final.
* **Design Considerations:** The volume of input (multiple QBRs) is significant. To avoid overloading the model, an initial summarization step is useful: the workflow could first ask the model to produce a “Year Summary” from QBRs (e.g., list the top 5 accomplishments of the year and top 5 challenges, gleaned from each quarter). With that summary plus reference to any existing strategy documents, the final prompt can be more focused. This two-step approach reduces context and also helps the model not to regurgitate all details. Few-shot examples might include showing it a snippet of a previous Annual Plan (if one exists) so it knows the style (structured by objectives, etc.). The prompt will emphasize that the output is a draft and that some sections might need human input (especially vision changes or budget figures). The AI should avoid making firm commitments that haven’t been decided (for example, it shouldn’t randomly say “increase budget by X%” unless input suggests it). We mitigate this by telling it to propose but mark uncertain things as “(to be confirmed)” or simply leave them general. The result is a comprehensive draft covering all template sections, which the team can then adjust in their planning session. It saves a lot of time by pre-populating data and even making creative suggestions that the team might not have thought of, based on the year’s analysis.

````yaml
# Workflow Name: HORIZON_AnnualStrategicPlanningAssistant
# Description: Assists in creating the Annual Strategic Plan by summarizing the past year and drafting future goals.
# Ritual Relevance: Annual Planning Retreat
# Template Origin: Outputs based on HORIZON_Annual_Strategic_Plan template structure.

inputDocumentSelectors:
  - "North_Star_Charter"
  - "Quarterly_Business_Review_Q*"
  - "Annual_Strategic_Plan*"
  - "Idea_Backlog_CurrentYear"
  - "Customer_Feedback_Summary_Annual"
  - "Market_Trends_Summary_Annual"
inputDateSelector: null
outputName: "Annual_Strategic_Plan_Draft_{{Year + 1}}"
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are a Strategic Planner AI. Your task is to assist in drafting the Annual Strategic Plan for next year ({{Year + 1}}).
  **Goal:** Summarize the performance of the current year ({{Year}}) using the provided QBRs and other inputs. Then, based on this analysis, the North Star Charter, and any ideas/trends, draft proposed strategic objectives, key initiatives, and metrics for the upcoming year.
  **Context:**
  The DocumentContext contains concatenated text from:
  1.  **North Star Charter:** Current mission, vision, strategic pillars.
  2.  **Quarterly Business Reviews (QBRs):** For all four quarters of the year {{Year}}. These are the primary source for the "Year in Review".
  3.  **Annual Strategic Plan for {{Year}} (Optional):** To compare expected vs. actual for {{Year}}.
  4.  **Idea Backlog for {{Year}} (Optional):** Potential initiatives.
  5.  **Customer Feedback / Market Trends for {{Year}} (Optional):** External context.

  Current Year (being reviewed): {{Year}}. Upcoming Year (being planned): {{Year + 1}}.

  **Task:**
  1.  **Analyze Inputs:** Review all documents. Focus on synthesizing themes from the four QBRs for the "Year in Review". An initial summarization of QBRs might be needed if context is too large: "produce a 'Year Summary' from QBRs (e.g., list the top 5 accomplishments of the year and top 5 challenges, gleaned from each quarter)".
  2.  **Draft "Year in Review ({{Year}})":**
      * Synthesize "Achievements" (top 5) and "Challenges" (top 5) from the QBRs.
      * Identify "Trend Analysis" based on patterns in QBRs or specific market trend documents.
  3.  **Draft "Vision Refresh (if any)":**
      * Based on the year's performance and the "North Star Charter", suggest if any aspect of the vision or strategic pillars might need discussion or reaffirmation. This should be a suggestion for human discussion.
  4.  **Draft "Strategic Objectives for {{Year + 1}}":**
      * Propose 2-3 major strategic objectives for the next year. These should align with "North Star Charter" and address insights from "Year in Review", "Idea Backlog", or market trends. For each, explain its importance and list potential "Key Initiatives".
  5.  **Draft "Key Metrics Targets":**
      * For the proposed objectives, suggest 1-2 high-level key metrics and placeholder targets (e.g., "Increase X by Y% (target TBD)").
  6.  **Draft "Budget & Resource Summary":**
      * Suggest high-level resource implications if evident from objectives (e.g., "Objective A may require new hires in Z"). Mark as "(to be confirmed)".
  7.  **Draft "Risks & Dependencies":**
      * List major risks based on challenges from {{Year}} or new initiatives.
  8.  **Draft "Action Plan & Timeline (Quarterly Focus)":**
      * For {{Year + 1}}, suggest a high-level focus for each quarter, distributing the proposed objectives/initiatives.
  9.  **Constraints:**
      * Use only information from DocumentContext.
      * Emphasize that output is a draft for human leadership refinement. "The AI should avoid making firm commitments that haven’t been decided". Mark uncertain financial/budget figures as "(to be confirmed)".
      * Focus on summarizing QBRs effectively for the "Year in Review".
  10. **Structure Output:** Format the entire output strictly according to the template provided in the TEMPLATE section.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
  # Annual Strategic Plan - {{Year + 1}}

  **Executive Summary:**
  _<One-paragraph summary of the proposed strategic direction for {{Year + 1}} based on inputs.>_

  **Year in Review ({{Year}}):**
  - **Achievements:** <Bullet list of top 5 significant accomplishments of {{Year}} from QBRs.>
  - **Challenges:** <Bullet list of top 5 major challenges of {{Year}} from QBRs.>
  - **Trend Analysis:** <Key trends observed in {{Year}} from QBRs/market docs.>

  **Vision Refresh (if any):**
  _<Suggest if vision/pillars from North Star Charter need review based on {{Year}}'s performance, or reaffirm existing vision. Frame as a point for discussion.>_

  **Strategic Objectives for {{Year + 1}}:**
  1.  **Objective A:** <Proposed major objective for {{Year + 1}}>
      - *Description:* <Explanation and importance based on inputs.>
      - *Key Initiatives:* <Potential projects from inputs.>
  2.  **Objective B:** <Proposed major objective for {{Year + 1}}>
      - *Description:* ...
      - *Key Initiatives:* ...
  *(2-3 objectives)*

  **Key Metrics Targets:**
  - <Metric 1 for Objective A: Target (e.g., "Increase X by Y% (target TBD)")>
  - <Metric 2 for Objective B: Target ...>

  **Budget & Resource Summary:**
  - <High-level resource implications, e.g., "Potential need for X resources (to be confirmed).">

  **Risks & Dependencies:**
  - <Risk 1 based on inputs>
  - <Risk 2 based on inputs>

  **Action Plan & Timeline:**
  - Q1 {{Year + 1}}: <Focus/major deliverables for Q1>
  - Q2 {{Year + 1}}: <Focus/major deliverables for Q2>
  - Q3 {{Year + 1}}: <Focus/major deliverables for Q3>
  - Q4 {{Year + 1}}: <Focus/major deliverables for Q4>
  ---END TEMPLATE---
````

## Workflow: Meeting Notes Summarization

* **Purpose:** Convert raw meeting inputs (like a transcript or bullet notes) into a clean Meeting Notes document. This workflow helps maintain the knowledge repository of meetings without requiring someone to manually write up minutes.
* **Trigger:** Manual (immediately after a meeting, someone initiates it).
* **Inputs:**

  * **Raw Meeting Record:** This could be a transcript (if a recording was transcribed) or rough notes from the meeting organizer. It might be provided as a plain text or markdown file with the dialogue or key points.
  * **Meeting Agenda:** (Optional) If an agenda doc exists or was prepared in the Meeting Notes template beforehand, include it so the AI can organize the summary by agenda topics.
  * **Decision Log:** (Optional) So the AI knows what decisions format looks like, or to cross-check if a decision in this meeting is new (though likely not needed if the raw record is clear).
* **Outputs:**

  * **Meeting_Notes_<MeetingName>_<Date>:** A formatted Meeting Notes document (using the Meeting Notes template).
* **Process Overview:** The AI is set as a "Meeting Scribe". The prompt might include the meeting title and date to output appropriately. If an agenda is provided, the AI will structure the summary under each agenda point. If not, it will structure by topics it detects. It scans the raw text for key points of discussion, conclusions, and action items. The model outputs a filled-in Meeting Notes doc: listing attendees (if not provided, it might glean names from transcript), summarizing discussion per topic, clearly listing any decisions made (sometimes signaled by words like “we decided” in the raw text), and extracting action items with owners and due dates (the prompt might specifically say “Look for phrases where someone volunteers or is assigned a task – list those as action items”). The human note-taker or facilitator then reviews this output, corrects any misinterpretation (especially if the model mis-identifies who said what or confuses content), and then finalizes the document.
* **Design Considerations:** A transcript can be long, so we might either truncate less important parts or instruct the model: “Focus on summarizing, do not include trivial chit-chat or tangents.” The model is good at summarizing if explicitly told. Also, names can be tricky (the model might not know them unless they appear in transcript). Likely the input notes have at least first names; the AI can use them. We ensure no hallucination by telling the AI “If unsure about a detail (e.g., exact decision wording), just provide a best-effort summary but do not fabricate any specifics.” If a meeting is very important (like with exact quotes needed), a human might do more editing, but for routine meetings this workflow speeds up the documentation a lot. It's also good to save the raw transcript separately if needed for reference (outside scope of AI). Over time, as the AI gets to know recurring meeting structures (e.g., weekly team syncs vs client calls), we could even have slight variations or few-shot examples by meeting type for even more tailored summaries.

````yaml
# Workflow Name: HORIZON_MeetingNotesSummarization
# Description: Converts raw meeting inputs into a structured Meeting Notes document.
# Ritual Relevance: Ad-hoc Meeting Notes Summarization
# Template Origin: Outputs based on HORIZON_Meeting_Notes template structure.

inputDocumentSelectors:
  - "Raw_Meeting_Record*"
  - "Meeting_Agenda*"
inputDateSelector: null
outputName: "Meeting_Notes_{{InputFileNames}}"
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are a Meeting Scribe AI. Your task is to process raw meeting records and generate structured Meeting Notes.
  **Goal:** Convert the provided raw meeting input (transcript or notes) into a clean, summarized Meeting Notes document, following the HORIZON_Meeting_Notes template structure.
  **Context:**
  The DocumentContext contains concatenated text from:
  1.  **Raw Meeting Record (e.g., "Raw_Meeting_Record_MeetingName_YYYY-MM-DD"):** The transcript or rough notes from the meeting. This is the primary source.
  2.  **Meeting Agenda (Optional, e.g., "Meeting_Agenda_MeetingName_YYYY-MM-DD"):** If provided, use its structure (Agenda points) to organize the summary. If not provided, infer topics from the raw record.

  Assume the meeting name and date can be inferred from `{{InputFileName}}` or are present in the raw record.

  **Task:**
  1.  **Analyze Inputs:** Review all documents. Prioritize the "Raw Meeting Record".
  2.  **Identify Attendees:** List attendees if mentioned in the raw record or agenda.
  3.  **Structure Agenda:** Use agenda from "Meeting_Agenda" if provided. Otherwise, list main topics discussed from "Raw Meeting Record".
  4.  **Draft "Discussion Summary":**
      * For each agenda point or identified topic, summarize the key discussion points and outcomes from the "Raw Meeting Record". Focus on decisions and conclusions, not verbatim dialogue.
  5.  **Draft "Decisions Made":**
      * Clearly list any decisions made, looking for phrases like "we decided", "agreed to", etc., in the "Raw Meeting Record". Include brief rationale if stated.
  6.  **Draft "Action Items":**
      * Extract action items. Look for phrases assigning tasks or responsibilities (e.g., "X will do Y by Z"). List action, owner, and due date if specified.
  7.  **Constraints:**
      * Use only information from DocumentContext.
      * Summarize concisely. "Focus on summarizing, do not include trivial chit-chat or tangents.".
      * If unsure about a detail (e.g., exact decision wording, owner), state "Summary based on notes, clarification may be needed" or provide best effort from text. Do not fabricate.
  8.  **Structure Output:** Format the entire output strictly according to the template provided in the TEMPLATE section.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
  # Meeting Notes - <Inferred Meeting Name from {{InputFileName}} or raw record>
  **Date & Time:** <Inferred Date & Time from {{InputFileName}} or raw record>
  **Attendees:** <List attendees from inputs, or "Not specified">

  **Agenda:**
  1.  <Agenda point 1 from inputs, or inferred topic 1>
  2.  <Agenda point 2 from inputs, or inferred topic 2>
  3.  ...

  **Discussion Summary:**
  - *Agenda Item 1:* <Summary of discussion for item 1 from raw record.>
  - *Agenda Item 2:* <Summary for item 2 from raw record...>
  - *Additional Topics:* <Any other discussion points not on formal agenda, from raw record.>

  **Decisions Made:**
  - <Decision 1 from raw record (if any) and brief rationale/context>
  - <Decision 2 from raw record ...>

  **Action Items:**
  - <Action Item 1 from raw record> – *Owner:* <Person from raw record> – *Due:* <Due date from raw record or ASAP>
  - <Action Item 2 from raw record> – *Owner:* <Person from raw record> – *Due:* <...>
  ---END TEMPLATE---
````

## Workflow: AI Prompt Refinement (Prompt Workshop)

* **Purpose:** Helps improve a workflow’s prompt or template by analyzing where the current prompt might be failing and suggesting enhancements. Essentially, it uses the AI to meta-improve itself, guided by human feedback.
* **Trigger:** Manual, ad-hoc (whenever the team notices an AI workflow output is consistently not meeting quality expectations, e.g., hallucinating, or off-tone).
* **Inputs:**

  * **Target Prompt/Workflow Description:** The text of the current prompt or a description of the workflow to improve.
  * **Examples of Bad Output:** One or more instances of the AI’s output that were unsatisfactory, with notes on what was wrong (e.g., “The daily plan was too verbose here” or “It missed a key blocker”).
  * **Desired Outcome Description:** Human description of what an ideal output should include or how it should differ from the bad output.
  * **Prompt Design Guidelines:** (Optional) The best practices and rules (possibly from the Concept & Design document) for reference.
* **Outputs:**

  * **Revised Prompt Suggestions:** This might not be a standard TIP document, but rather an output text with either a new prompt or specific recommended changes (e.g., “Add an instruction to focus on X”, or a fully rewritten prompt template). The team can then update the actual workflow’s prompt accordingly.
* **Process Overview:** The AI is put in the role of a "Prompt Engineer Assistant". The input prompt to the model may say something like: “We have a prompt that produces X, but it’s not doing Y correctly. Here is the prompt and an example of the output. Identify weaknesses and suggest improvements.” The model then analyzes – for example, it might point out “The prompt does not explicitly instruct brevity, so the output was verbose” – and then propose a revised prompt snippet. It could also suggest adding a few-shot example or a constraint. The human (maybe the Navigator or a designated AI Maintainer role) reviews the suggestions. Often, multiple iterations may be done: the team might test the new prompt with the AI, see if it fixes the issue, and if not, call this workflow again or refine manually. Over time, this leads to high-quality prompts for all workflows.
* **Design Considerations:** This is a more conversational workflow and might not always yield a perfect answer from the model (since it is critiquing itself). However, local models can often identify obvious omissions if given examples. The process should be done carefully because the AI might also suggest changes that need human judgment (for instance, it might over-correct or make the prompt too specific, losing flexibility). As a safeguard, treat the AI’s suggestion as exactly that – a suggestion. The team should apply their understanding to decide what to implement. Logging these changes (perhaps in a changelog or the Decision Log) can help track how prompts evolve. TIP’s versioning means if a new prompt version performs worse, you can roll back. This workflow reinforces the **continuous learning** principle of HORIZON, using AI to help fine-tune the system itself with minimal extra effort.

````yaml
# Workflow Name: HORIZON_AIPromptRefinement
# Description: Suggests improvements for an existing workflow prompt.
# Ritual Relevance: Prompt Workshop (Ad-hoc)
# Template Origin: N/A - output is textual suggestions.

inputDocumentSelectors:
  - "Prompt_Analysis_Input*"
inputDateSelector: null
outputName: "Prompt_Refinement_Suggestions_for_{{InputFileNames}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are a Prompt Engineer Assistant. Your task is to analyze an existing AI prompt and suggest improvements.
  **Goal:** Based on the provided current prompt, examples of its bad output, and a description of the desired outcome, identify weaknesses in the current prompt and suggest specific revisions or additions to improve its performance.
  **Context:**
  The DocumentContext (from a file like "Prompt_Analysis_Input_*") contains:
  1.  **Current Prompt Text:** The prompt that needs improvement.
  2.  **Examples of Bad Output:** Instances where the current prompt failed.
  3.  **Desired Outcome Description:** What the ideal output should look like.
  4.  **Prompt Design Guidelines (Optional):** Best practices for reference.

  **Task:**
  1.  **Analyze Inputs:** Carefully review the current prompt, bad outputs, and desired outcomes.
  2.  **Identify Weaknesses:** Pinpoint specific reasons why the current prompt might be leading to unsatisfactory results (e.g., lack of clarity, missing constraints, poor role priming, no few-shot example).
  3.  **Suggest Improvements:** Propose concrete changes to the prompt. This could include:
      * Rewording instructions for clarity.
      * Adding or refining constraints.
      * Suggesting a better role prompt.
      * Advising the inclusion of a few-shot example (and what that might look like).
      * Modifying the output structure instructions.
  4.  **Provide Revised Prompt (Optional but Preferred):** If feasible, provide a revised version of the prompt incorporating your suggestions.
  5.  **Constraints:**
      * Suggestions must be actionable and specific.
      * Base your analysis solely on the provided input document.
      * If providing a revised prompt, ensure it adheres to general prompt engineering best practices suitable for a local LLM.
  6.  **Structure Output:** Format the entire output strictly according to the template provided in the TEMPLATE section.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
  # Prompt Refinement Suggestions

  ## Analysis of Current Prompt Weaknesses
  - [Weakness 1 and explanation]
  - [Weakness 2 and explanation]

  ## Specific Recommendations for Improvement
  - Recommendation 1: [e.g., "Clarify the instruction for X by changing Y to Z."]
  - Recommendation 2: [e.g., "Add a constraint: 'Limit output to 3 bullet points.'"]
  - Recommendation 3: [e.g., "Consider adding a few-shot example for the output format, like this: ..."]

  ## (Optional) Proposed Revised Prompt Text:
  \<If you are providing a full revised prompt, include it here in a code block or as plain text.\>
  ---END TEMPLATE---
````

## Workflow: Knowledge Archive Summarization (Context Condenser)

* **Purpose:** Manage the growing volume of context by summarizing or archiving older documents. For instance, condense older Daily Logs or Weekly Reviews after some time into a shorter summary file, so they remain available in memory but take up less space. This ensures the AI’s context window isn’t overwhelmed by historical data, while preserving long-term knowledge.
* **Trigger:** Ad-hoc, or Scheduled periodically (e.g., monthly or quarterly).
* **Inputs:**

  * **Date Range or Topic Selection:** Criteria of what to summarize (e.g., “All Daily Logs from more than 30 days ago” or “All project X notes now that the project is done”).
  * **Documents to Condense:** The actual content of those source documents (could be a list of files or a merged content).
  * **Desired Summary Length:** (Optional) Guidance on how compact the summary should be (e.g., one paragraph per week, or a fixed number of bullet points).
* **Outputs:**

  * **Condensed Document:** e.g., a file like **Monthly_Summary_<MonthYear>** or **Archive_Summary_Q<Quarter><Year>**, capturing the essence of the input docs.
  * Optionally, an update to the original documents: e.g., one might append a note to old docs like “Archived in summary X” or even remove them from active use (depending on retention policies).
* **Process Overview:** The AI (as an "Archivist Assistant") is prompted with instructions such as: “Summarize the following 20 daily logs into a single monthly summary. Focus on key events, recurring themes, and any data points that would be relevant for future reference.” The input might be chunked if too large (processing 20 documents in one go might require splitting into weeks). The model produces a condensed version, often structured by time (like week-by-week or a narrative of the month). The human quickly checks that nothing critical was lost. The new summary document is saved. Subsequently, the team might decide to delete or move the original daily logs out of the main workspace (since their content is now in the summary and also the Weekly reviews cover some of it). However, version history in TIP means nothing is truly lost. This workflow can also be applied to things like a long research document or an ongoing meeting notes thread, etc., creating a concise reference version.
* **Design Considerations:** Summarization is a strength of many LLMs, including local ones, as long as the instruction is clear about what to keep. The prompt may need to specify, for example, “Preserve any numerical results or decisions mentioned, but you can omit day-to-day minor details.” And if multiple sources are fed in, instruct the model to not confuse timelines. If needed, do it stepwise: summary of each week then summary of summaries. Also, ensure the output clearly states the period it covers, so later users know the summary’s scope. By regularly condensing, the team ensures that the active context the AI deals with remains relevant and not beyond the token limit. This improves performance and keeps the knowledge base from bloating. The act of summarizing also surfaces patterns (maybe the AI or human notices a trend like “we had 5 days of outages last month” when seeing them all together). Those insights can feed into future planning.

````yaml
# Workflow Name: HORIZON_KnowledgeArchiveSummarization
# Description: Condenses older documents into a shorter summary, preserving key knowledge.
# Ritual Relevance: Knowledge Cleanup (Ad-hoc/Scheduled)
# Template Origin: N/A - output is a new summary document.

inputDocumentSelectors:
  - "*"
inputDateSelector: null
outputName: "Archive_Summary_of_{{InputFileNames}}_{{Year}}-{{Month}}-{{Day}}" # Topic extraction might need user input or smarter placeholder
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are an Archivist Assistant. Your task is to summarize and condense a collection of older documents.
  **Goal:** From the provided set of documents ({{InputFileNames}}), extract and synthesize the most critical long-term events, decisions, trends, and insights. Discard transient operational details and routine updates not relevant for future reference (e.g., 6-12+ months from now). If a "Condensation_Criteria" document is part of the input, adhere to its specified summary length or focus areas.
  **Context:**
  The DocumentContext contains concatenated text from multiple older documents selected by the user. It may also include a "Condensation_Criteria_*" document with specific instructions.

  **Task:**
  1.  **Analyze Inputs:** Review all provided documents. If a "Condensation_Criteria_*" document exists, prioritize its instructions for focus and length.
  2.  **Identify Core Content for Archival:** From all other documents, extract points discussing:
      * Major strategic events, decisions (and rationale if stated).
      * Significant trends with long-term implications.
      * Outcomes that directly impacted long-term goals or required strategic shifts.
      * Unique learnings that changed fundamental approaches or understanding.
  3.  **Synthesize and Condense:** Rewrite the extracted core content into an integrated summary. Use clear headings (e.g., Key Events, Major Decisions, Learnings). Use bullet points for clarity. Eliminate redundancy.
  4.  **Adhere to Criteria (if provided):** If "Condensation_Criteria" specifies length (e.g., "one paragraph per week", "max 500 words"), try to meet it. If it specifies focus areas, prioritize those.
  5.  **Constraints:**
      * Use only information from DocumentContext.
      * Primary goal is concise preservation of strategically important information. "Preserve any numerical results or decisions mentioned, but you can omit day-to-day minor details.".
      * If multiple documents cover the same event, synthesize it once.
      * If `Condensation_Criteria*` is provided, its instructions take precedence for focus/length.
  6.  **Structure Output:** Format the entire output strictly according to the template provided in the TEMPLATE section.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
  # Archive Summary - Covering documents like: {{InputFileNames}}
  *(Condensed on: {{Year}}-{{Month}}-{{Day}})*

  ## Key Strategic Events & Decisions
  - [Summary of major event/decision 1 from the period, synthesized from inputs]
  - [...]

  ## Significant Long-Term Trends Identified
  - [Summary of major trend 1 observed during the period, synthesized from inputs]
  - [...]

  ## Major Challenges/Outcomes Impacting Strategy
  - [Summary of significant challenge or outcome, synthesized from inputs]
  - [...]

  ## Key Learnings with Enduring Value
  - [A significant learning, synthesized from inputs]
  - [...]
  ---END TEMPLATE---
````

*(Note: The above workflows cover the core co-management loop. Teams can develop additional specialized workflows (e.g., a "Decision Analysis" workflow that assists with complex decision-making by weighing options using the Decision Log and Values, or a "Content Drafting" workflow for turning ideas into blog posts using the knowledge base). All workflows should follow the design principles of clear inputs/outputs, staying within context limits, and requiring minimal human effort for maximum gain. The listed workflows are designed to interlock – outputs from daily routines feed into weekly, which feed into monthly, and so on – creating a cohesive system that the AI helps run.)*

# Additional Workflows

## Workflow: HORIZON_NorthStarAlignmentCheck

* **Purpose**: Validate that any major proposal or decision aligns with the team’s North-Star Charter and active Quarterly OKRs. Generates a short Alignment Report that lists fit / mis-fit signals plus a go / refine / reject recommendation.
* **Daily Log**: N/A – ad-hoc; typically invoked before approving a big decision or project charter.
* **Trigger**: Manual via TIP “Run Workflow” button on a draft Decision document.
* **Inputs**:
  * The draft **Decision Proposal** (free-text, usually Meeting Notes or a proposal doc).
  * **North Star Charter**
  * **Quarterly OKRs**
  * *(Optional)* last **Decision Log_Retrospective** for context.
* **Outputs**:
  * **Alignment_Report_<InputFileName>_<YYYY-MM-DD>**
* **Process Overview**:
  * 1. Pull Charter pillars + active Objectives/KRs.
  * 2. Extract key intent from the draft decision.
  * 3. Score strategic fit (High / Medium / Low) and list rationale bullets.
  * 4. Recommend “Proceed”, “Refine”, or “Reject” with next-step hints.
* **Design Considerations**:
  * Keep context short: embed only pillar/KR text, not full docs.
  * Use explicit “If a detail is missing, state ‘Unknown’” guardrail

````yaml
# Workflow Name: HORIZON_NorthStarAlignmentCheck
# Description: LLM checks big decisions regarding strategic fit
# Ritual Relevance: Use on a draft Decision document
# Template Origin: N/A

inputDocumentSelectors:
  - "Decision_Proposal*"
  - "North_Star_Charter*"
  - "Quarterly_OKRs*"
  - "Decision_Log_Retrospective*"
outputName: "Alignment_Report_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are a Strategic Alignment Analyst.
  **Goal:** Produce an Alignment Report that scores the proposal’s fit to
  the North-Star Charter pillars and active Quarterly OKRs.

  **Instructions:**
  1. Read the Decision Proposal section <Proposal>.
  2. Compare against Charter pillars <Charter> and KRs <OKRs>.
  3. For each pillar & KR, state “Supports / Neutral / Conflicts” with 1-line reason.
  4. Conclude with one of:
       * ✅ Proceed
       * ✏️  Refine (list what to address)
       * ❌ Reject (list critical conflicts)
  5.  **Structure Output:** Format the entire output strictly according to the template provided in the TEMPLATE section.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
  # Alignment Report – *{{DecisionTitle}}* ({{Date}})

  ## 1 Strategic Fit Matrix

  ### 1.1 North-Star Charter Pillars
  | Pillar | Fit Rating* | Rationale |
  |--------|-------------|-----------|
  | Pillar 1 | Supports / Neutral / Conflicts | <one-line reason> |
  | Pillar 2 | … | … |
  | Pillar 3 | … | … |

  ### 1.2 Quarterly Key Results
  | Objective / KR | Fit Rating* | Rationale |
  |----------------|-------------|-----------|
  | O1 / KR 1.1 | Supports / Neutral / Conflicts | <one-line reason> |
  | O2 / KR 2.3 | … | … |

  > *Rating scale:*
  > **Supports** – strong positive contribution
  > **Neutral** – little or no impact
  > **Conflicts** – likely to hinder or contradict

  ---

  ## 2 Overall Alignment Score
  **{{Score / 10}}**
  _(0 = no strategic fit, 10 = perfect fit)_

  ---

  ## 3 Recommendation
  | Decision | Reasoning |
  |----------|-----------|
  | ✅ Proceed / ✏️ Refine / ❌ Reject | <concise justification> |

  ---

  ## 4 Risks & Dependencies
  - **Risk 1:** <description> → *Mitigation:* <action / owner>
  - **Risk 2:** …

  ---

  ## 5 Next-Step Actions
  1. <Action 1 – owner – due date>
  2. <Action 2 – owner – due date>

  ---

  ### Template Guidelines
  - **Brevity:** keep total length ≤ 2 pages.
  - **Objectivity:** base ratings only on the provided documents; state “Unknown” when data is missing.
  - **Actionability:** every “Refine” or “Reject” outcome must list concrete follow-ups.
  ---END TEMPLATE---
````

## Workflow: HORIZON_AdaptiveMeetingAgenda

* **Purpose**: Auto-build a focused agenda by mining open action items, blockers, and pending decisions so that live meetings stay short & outcome-driven.
* **Daily Log**: Yes – Navigator typically runs it 5-10 min before each standing meeting.
* **Trigger**: Manual or Calendar-linked “5 min before event” automation.
* **Inputs**:
  * **Daily_Log** (latest)
  * **Task_Backlog**
  * **Decision_Log** (to surface open questions)
  * *(Optional)* raw meeting request text.
* **Outputs**:
  * **Meeting_Agenda_<MeetingName>_<YYYY-MM-DD>** (uses existing template)
* **Process Overview**:
  * 1. Parse Daily Log → today’s blockers & goals.
  * 2. Scan Task Backlog for high-priority items “In Progress/Blocked”.
  * 3. Pull Decision Log rows with empty “Outcome/Follow-up”.
  * 4. Rank topics by impact & urgency; stop at 5-7 items.
* **Design Considerations**:
  * Cap agenda length to fit 30 min meeting rule of thumb
  * Provide “Suggested Timebox” per topic (mins) using simple heuristic (impact × complexity).

````yaml
# Workflow Name: HORIZON_AdaptiveMeetingAgenda
# Description: LLM creates an agenda from open topics from logs and blockers
# Ritual Relevance: 5 min before event
# Template Origin: HORIZON_Meeting_Agenda

inputDocumentSelectors:
  - "Daily_Log*"
  - "Task_Backlog*"
  - "Decision_Log*"
  - "Meeting_Request*"
outputName: "Meeting_Agenda_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are a Meeting Navigator AI.
  **Goal:** Draft a crisp agenda that will let the team resolve blockers and
  make key decisions within 30 minutes.

  **Steps**
  1. Pull max 3 critical blockers from Daily Log.
  2. Pull top 3 high-priority tasks still unresolved.
  3. Include any Decision Log entries without outcomes.
  4. Order by (Blocker → Decision → Task). For each, suggest owner & mins.
  5. Use bullet lists, be concise, no redundant context.
  6. Format the entire output strictly according to the template provided in the TEMPLATE section.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
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
  ---END TEMPLATE---
````

## Workflow: HORIZON_DecisionLogRetro

* **Purpose**: Generate a monthly Decision Log Retrospective document that scores the success of past decisions and extracts lessons learned.
* **Daily Log**: N/A – runs once per month, typically by Metrics Steward.
* **Trigger**: Scheduled on the first work-day each month.
* **Inputs**:
  * **Decision_Log**
  * *(Optional)* relevant KPI Update documents.
* **Outputs**:
  * **Decision_Log_Retrospective_<YYYY-MM>**
* **Process Overview**:
  * 1. Filter Decision Log rows within past calendar month.
  * 2. For each, compare “Outcome / Follow-up” against intent keywords.
  * 3. Classify Success / Partial / Fail.
  * 4. Aggregate common success factors & pitfalls.
  * 5. Fill new template sections (Scorecard, Patterns, Recommendations).
* **Design Considerations**:
  * Summarise numeric impact only when KPI doc available; else qualitative.
  * Keep output ≤ 1 k words to stay within context for Quarterly reviews.

````yaml
# Workflow Name: HORIZON_DecisionLogRetro
# Description: Monthly Lessons-Learned Synthesis
# Ritual Relevance: On the first work-day each month
# Template Origin: N/A

inputDocumentSelectors:
  - "Decision_Log*"
  - "Metrics_KPI_Update*"
outputName: "Decision_Log_Retrospective_{{Year}}-{{Month}}"
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are a Decision Retrospective Analyst.
  **Window:** {{Year}}-{{Month}}-01 to end-of-month.

  **Tasks**
  1. Load decisions in that window.
  2. Assess outcome vs. stated intent. Rate ✅ / ⚠️ / ❌.
  3. Populate the template mentioned below in section Output Format.
  4. End with 2-3 actionable recommendations.
  5. Constraints:
     * Use only data from Decision Log and KPI updates provided.
     * If metrics absent, state “No KPI data”.
     * Be concise; aim <1000 words.
  6. Format the entire output strictly according to the template provided in the TEMPLATE section.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
  # Decision_Log_Retrospective_{{Year}}-{{Month}}

  ## 1. Synopsis of Reviewed Period
  _<e.g., “2025-04-01 to 2025-04-30 – total 12 decisions logged”>_

  ## 2. Outcome Scorecard
  | Decision | Intended Outcome | Actual Result | Status | Notes |
  |----------|------------------|---------------|--------|-------|
  | *Adopt HORIZON Protocol* | Improve on-time delivery | +18 % on-time, 0 missed deadlines | ✅  Successful | — |
  | *Pivot to SMB Market* | +20 % leads in SMB segment | +22 % leads | ✅ | Larger TAM than forecast |

  *(Add rows as needed)*

  ## 3. Patterns & Insights
  - **High-confidence calls:** <bullet 1>
  - **Missed assumptions:** <bullet 2>

  ## 4. Recommendations
  1. <Recommendation 1>
  2. <Recommendation 2>

  ---

  *Guidelines:* Limit to 1-2 pages; focus on transferable insights, not recounting every detail. Cite Decision Log entries via dates for traceability.
  ---END TEMPLATE---
````

## Workflow: HORIZON_OKRPrioritisation

* **Purpose**: Re-score all open tasks against active Quarterly OKRs, surface the top-impact items, and suggest keep / accelerate / deprioritise actions for the coming week.
* **Daily Log**: N/A – typically run every Monday after Weekly Plan draft.
* **Trigger**: Manual (“Run Workflow”) or calendar 09:00 each Monday.
* **Inputs**:
  * **Quarterly_OKRs**    – active objectives & key results
  * **Task_Backlog**      – full backlog with status & tags
  * **Weekly_Plan**     – (optional) draft plan to cross-check commitment
* **Outputs**:
  * **OKR_Prioritisation_Summary_<YYYY-W##>**
* **Process Overview**:
  * 1. Parse each Task → map to the Objective/KR it best supports.
  * 2. Compute *Impact Score* = (KR importance × task leverage) ÷ effort using simple heuristics (High=3, Med=2, Low=1 for each factor).
  * 3. Rank tasks > Impact Score 6 as **Accelerate**, 3-6 as **Keep**, < 3 as **Deprioritise**.
  * 4. Generate summary table + recommendations section.
* **Design Considerations**:
  * Cap output to 25 top-ranked tasks to stay within context window.
  * Use consistent scoring rubric so scores are comparable week to week.
  * Respect the 30 min/day overhead rule—analysis should finish in seconds.

````yaml
# Workflow Name: HORIZON_OKRPrioritisation
# Description: Impact Scoring of Tasks
# Ritual Relevance: Run each Monday morning
# Template Origin: N/A

inputDocumentSelectors:
  - "Quarterly_OKRs*"
  - "Task_Backlog*"
  - "Weekly_Plan*"
outputName: "OKR_Prioritisation_Summary_{{Year}}-W{{CurrentWeekNumber}}"
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are an OKR Impact Analyst AI.
  **Goal:** Score backlog tasks for their contribution to current OKRs and
  recommend which to accelerate, keep, or deprioritise this week.

  **Steps**
  1. For each task, identify the most relevant Objective & KR.
  2. Assign Importance (High/Med/Low) from the KR text.
  3. Infer Effort (High/Med/Low) from task size tag or description length.
  4. Calculate Impact Score = (Importance * Leverage) / Effort
     (H=3 | M=2 | L=1). Round to one decimal.
  5. Constraints:
     * Do NOT invent Objectives/KRs or tasks not in inputs.
     * If a task has no clear OKR link, mark Importance = 1.
     * Keep narrative sections <300 words total.
  6. Format the entire output strictly according to the template provided in the TEMPLATE section and consider these points:
     * Table of the 25 highest-scoring tasks
     * Insight bullets (e.g., gaps, over-commitment signals)
     * Suggested next steps.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
  # OKR Prioritisation Summary – Week {{CurrentWeekNumber}} {{Year}}

  ## Top-Impact Tasks
  | Rank | Task ID & Title | Owner | Linked Objective / KR | Impact Score | Action |
  |------|-----------------|-------|-----------------------|--------------|--------|
  | 1 | <ID – Title> | <Name> | O1 / KR1.2 | 8.5 | Accelerate |
  | 2 | … | … | … | … | Keep |
  | … | … | … | … | … | … |

  *Scoring rubric:* High = 3, Medium = 2, Low = 1 for Importance, Leverage, Effort
  Impact Score = (Importance × Leverage) / Effort

  ## Insights
  - **Coverage gaps:** _<e.g., “Objective 3 has no high-impact tasks in flight.”>_
  - **Over-commitment alerts:** _<e.g., “Owner X holds 40 % of top tasks.”>_
  - **Quick wins (<1 pt effort) worth acceleration:** _<list>_

  ## Recommendations for Weekly Plan
  1. _<e.g., “Move Task #123 to this week’s Top Priorities.”>_
  2. _<e.g., “Deprioritise Task #98; low impact vs. KR progress.”>_

  ---

  *Guidelines:* Limit table to 25 rows. Keep Insights ≤5 bullets and Recommendations ≤3 actions to preserve clarity.
  ---END TEMPLATE---
````

## Workflow: HORIZON_RiskHeatmap

* **Purpose**: Aggregate blockers & warnings from the past week, cluster them into risk themes, and output a RAG-rated heatmap with mitigation actions.
* **Daily Log**: Yes – Metrics Steward runs every Friday before Weekly Review.
* **Trigger**: Manual or scheduled (Friday 16:00).
* **Inputs**:
  * Daily_Log*        – last 5-7 daily logs (for blockers)
  * Task_Backlog*      – tasks flagged “Blocked” or “At-Risk”
  * Metrics_KPI_Update* – (optional) KPI anomalies to correlate
* **Outputs**:
  * Risk_Heatmap_Report_<YYYY-W##>
* **Process Overview**:
  * 1. Extract all blocker lines & at-risk tags.
  * 2. Cluster by keyword similarity into ≤ 7 risk themes.
  * 3. For each theme, score *Likelihood* and *Impact* (High/Med/Low).
  * 4. Map to RAG rating (H/H = Red, H/M or M/H = Amber, else Green).
  * 5. Suggest one mitigation or owner per Red/Amber cluster.
* **Design Considerations**:
  * Heuristic: Likelihood = frequency of mentions; Impact = severity tags or KPI deviation size.
  * Output fits the new Risk Heatmap template and remains ≤ 800 words.

````yaml
# Workflow Name: HORIZON_RiskHeatmap
# Description: LLM clusters Blocker and  proposes countermeasures
# Ritual Relevance: Run each Friday afternoon before Weekly Review
# Template Origin: N/A

inputDocumentSelectors:
  - "Daily_Log*"
  - "Task_Backlog*"
  - "Metrics_KPI_Update*"
outputName: "Risk_Heatmap_Report_{{Year}}-W{{CurrentWeekNumber}}"
prompt: |
  **STRICT MODE ON** — Strictly follow the instructions in the INSTRUCTIONS section below using the context provided in the CONTEXT section below. For your output strictly adhere to the template specified in the TEMPLATE section below and provide the output in markdown format.

  ---BEGIN CONTEXT---
  {{DocumentContext}}
  ---END CONTEXT---

  ---BEGIN INSTRUCTIONS---
  **Role:** You are a Risk Analyst AI.
  **Goal:** Produce a weekly heatmap of operational risks plus mitigation
  advice that helps the team act before issues escalate.

  **Method**
  1. Collect blockers/risks from Daily Logs + flagged tasks.
  2. Cluster into themes (≤7) with concise names.
  3. Determine Likelihood (High > 3 mentions, Med = 2, Low = 1) and
     Impact (High = could stop objective, Med = delays, Low = minor).
  4. Assign RAG colour.
  5. Recommend mitigations for Red & Amber themes.
  6. Constraints:
     * No speculative risks; base only on supplied data.
     * Keep full report under 6 k tokens (~800 words).
  7. Format the entire output strictly according to the template provided in the TEMPLATE section.
  ---END INSTRUCTIONS---

  ---BEGIN TEMPLATE---
  # Weekly Risk Heatmap – Week {{CurrentWeekNumber}} {{Year}}

  | Risk Theme | Likelihood | Impact | RAG Rating | Proposed Mitigation & Owner |
  |------------|------------|--------|------------|-----------------------------|
  | <Theme A> | High | High | 🔴 Red | <Mitigation – Owner> |
  | <Theme B> | Medium | High | 🟠 Amber | <Mitigation – Owner> |
  | <Theme C> | Low | Medium | 🟢 Green | <Monitor only> |
  | … | … | … | … | … |

  **Key Observations**
  - Theme **<A>** poses the highest combined risk; immediate action required.
  - Theme **<B>** likely tied to KPI dip in <Metric>; monitor after fix.
  - No critical new risks emerged beyond known areas.

  **Next-Step Actions (Top 3)**
  1. _<e.g., “Assign two devs to unblock Deployment Pipeline issues (Theme A).”>_
  2. _<e.g., “Schedule customer call to clarify Scope creep (Theme B).”>_
  3. _<e.g., “Add automated alert for <Metric> deviation > 5 %.”>_

  ---

  *Guidelines:* Use concise language; RAG emojis improve skim-readability. Mitigation owners must be real team members or “Unassigned”.
  ---END TEMPLATE---
````
