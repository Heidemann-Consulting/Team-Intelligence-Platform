--
-- PostgreSQL database dump
--

-- Dumped from database version 15.12
-- Dumped by pg_dump version 15.12

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;

-- Install pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: content_item_type_enum; Type: TYPE; Schema: public; Owner: ulacm_user
--

CREATE TYPE public.content_item_type_enum AS ENUM (
    'DOCUMENT',
    'TEMPLATE',
    'WORKFLOW'
);


ALTER TYPE public.content_item_type_enum OWNER TO ulacm_user;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: ulacm_user
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
   NEW.updated_at = now();
   RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO ulacm_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: teams; Type: TABLE; Schema: public; Owner: ulacm_user
--

CREATE TABLE public.teams (
    team_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    team_name character varying(100) NOT NULL,
    username character varying(50) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.teams OWNER TO ulacm_user;

--
-- Name: content_items; Type: TABLE; Schema: public; Owner: ulacm_user
--

CREATE TABLE public.content_items (
    item_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    team_id uuid NOT NULL,
    item_type public.content_item_type_enum NOT NULL,
    name character varying(255) NOT NULL,
    is_globally_visible boolean DEFAULT false NOT NULL,
    current_version_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.content_items OWNER TO ulacm_user;

--
-- Name: content_versions; Type: TABLE; Schema: public; Owner: ulacm_user
--

CREATE TABLE public.content_versions (
    version_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    item_id uuid NOT NULL,
    markdown_content text NOT NULL,
    version_number integer NOT NULL,
    saved_by_team_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    content_tsv tsvector,
    content_vector vector(384),
    vector vector(384)
);


ALTER TABLE public.content_versions OWNER TO ulacm_user;

--
-- Data for Name: teams; Type: TABLE DATA; Schema: public; Owner: ulacm_user
--

COPY public.teams (team_id, team_name, username, hashed_password, is_active, created_at, updated_at) FROM stdin;
04a9a4ec-18d8-4cfd-bead-d0ef99199e17	ULACM System Administrators	_ulacm_admin_system_team_	$2b$12$DUMMYHASHFORADMINSYSTEMTEAMACCOUNTDONTUSEME	t	2025-05-11 05:01:45.325693+00	2025-05-11 05:01:45.325693+00
\.

--
-- Delete existing documents, templates and workflows
--
DELETE FROM public.content_versions WHERE item_id IN (SELECT item_id FROM public.content_items WHERE item_type = 'DOCUMENT');
DELETE FROM public.content_items WHERE item_type = 'DOCUMENT';
DELETE FROM public.content_versions WHERE item_id IN (SELECT item_id FROM public.content_items WHERE item_type = 'TEMPLATE');
DELETE FROM public.content_items WHERE item_type = 'TEMPLATE';
DELETE FROM public.content_versions WHERE item_id IN (SELECT item_id FROM public.content_items WHERE item_type = 'WORKFLOW');
DELETE FROM public.content_items WHERE item_type = 'WORKFLOW';

--
-- Inserting Empty Template
--
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'A blank Template', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'This is deliberately empty so that you can realize all your ideas with it.',
    1, admin_team_id, NOW());
END $$;

--
-- Inserting Empty Workflow
--
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: A blank Workflow\n# Description: This is deliberately empty to allow for execution of just the "Additional input for the AI"\n\ninputDocumentSelectors:\n  - "*" # Allows user to select any one document visible to them at runtime.\ninputDateSelector: null # No specific date filter by default for this generic workflow.\noutputName: "AI_Response_{{Year}}-{{Month}}-{{Day}}.md"\nprompt: |\n  Please execute the "Additional AI Input" request on the following document(s):\n\n  DOCUMENT CONTENT(s):\n  ```\n  {{DocumentContext}}\n  ```';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'A blank Workflow', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

--
-- Inserting HORIZON Protocol Templates
--

-- Template: HORIZON_North_Star_Charter
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_North_Star_Charter', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# North Star Charter\n\n**Mission:** _<One sentence stating the fundamental purpose of the team or organization.>_\n\n**Vision:** _<A short statement of what the team aspires to achieve or become in the long term.>_\n\n**Core Values:**\n- _Value 1:_ <Brief description of this core value in practice.>\n- _Value 2:_ <Brief description...>\n- _Value 3:_ <... list 3-5 fundamental values guiding the team''s culture and decisions._\n\n**Strategic Pillars:**\n1. **Pillar 1:** <Long-term strategic focus area or goal (e.g. Operational Excellence, Innovation in X, Customer Satisfaction). Describe what this means.>\n2. **Pillar 2:** <Another key strategic priority...>\n3. **Pillar 3:** <... up to 3-5 pillars that define the team''s high-level strategy.>\n\n**Team Identity & Scope:**\n- **Who We Serve:** <Define the customers or stakeholders the team/organization serves.>\n- **What We Offer:** <Briefly describe the main products, services, or value the team delivers.>\n- **Unique Strengths:** <Bullet points of the team''s unique advantages or differentiators.>\n\n*_(This charter should be reviewed at least annually. All major plans and decisions should reference this document to ensure alignment.)_*',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Quarterly_OKRs
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Quarterly_OKRs', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Q<Quarter> <Year> Objectives & Key Results\n\n**Objective 1:** <Objective statement – a qualitative goal for this quarter.>\n- **KR 1.1:** <First Key Result with target metric or deliverable to achieve this objective.>\n- **KR 1.2:** <Second Key Result (if any)...>\n- (Add KRs as needed)\n\n**Objective 2:** <Second major objective for the quarter.>\n- **KR 2.1:** <Key Result for Objective 2.>\n- **KR 2.2:** <Key Result...>\n\n*(List 1-5 Objectives maximum. Each Objective should have 1-4 Key Results that are specific and measurable.)*\n\n**Quarter Focus Theme:** <If the quarter has an overarching theme or slogan, note it here (optional). For example, “Expand Market Reach” or “Operational Efficiency.”>\n\n**Baseline Metrics:**\n- <List any starting metrics at beginning of quarter, like revenue, user count, etc., relevant to the objectives. This helps measure improvement.>\n\n**Risks & Assumptions:**\n- <List any known risks to achieving these objectives or assumptions being made. e.g., "Assumption: funding for project X will be approved by Q2".>',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Task_Backlog
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Task_Backlog', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Team Task Backlog\n\n| **ID** | **Task** | **Owner** | **Priority** | **Status** | **Notes** |\n|--------|---------------------------|--------------|--------------|--------------|-----------------------|\n| 1      | <Task description>        | <Person/Team>| High/Med/Low | Not Started/In Progress/Done | <Any relevant details or links> |\n| 2      | <Task description>        | <Owner>      | High         | In Progress  | <Notes...>            |\n| 3      | <Task description>        | <Owner>      | Medium       | Not Started  | <Notes...>            |\n| ...    | ...                       | ...          | ...          | ...          | ...                   |\n\n*Guidelines:*\n- Prioritize tasks (High, Medium, Low) so the Daily Plan workflow knows what''s important.\n- Update statuses daily or as progress is made (e.g., when a task is completed or blocked).\n- Use the Notes field for any context the AI might need (e.g., "Waiting on client feedback" or links to specifications).\n- Keep the list pruned: remove or archive tasks that are no longer relevant so the AI stays focused on current priorities.',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Idea_Backlog
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Idea_Backlog', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Idea Backlog\n\n| **Idea** | **Potential Impact** | **Status** | **Notes** |\n|------------------------------------|-------------------------|-------------------|----------------------------|\n| <Short description of idea>       | High/Medium/Low         | Proposed / Under Review / Approved / Archived | <Additional details or rationale> |\n| <Idea description>               | Medium                  | Proposed          | <Notes... e.g., origin of idea> |\n| <Idea description>               | Low                     | Under Review      | <Notes...> |\n\n*Guidelines:*\n- Be concise in describing each idea, but enough to recall what it is.\n- Estimate the potential impact (e.g., High = game-changer, Low = minor improvement).\n- Status can move from Proposed -> Under Review -> Approved (if the team commits to it) or Archived (if decided not to pursue).\n- Periodically, the team (or AI) can review this list to surface promising ideas during planning cycles.',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Decision_Log
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Decision_Log', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Decision Log\n\n| **Date** | **Decision** | **Context & Rationale** | **Outcome/Follow-up** |\n|------------|-------------------------------------|----------------------------------------------------|----------------------------------------|\n| 2025-05-10 | Adopt HORIZON Protocol for Q3 Pilot | Context: Team workload was increasing, and missed deadlines were occurring. Rationale: HORIZON promises efficiency. | Outcome: Began onboarding team to HORIZON in May. Follow-up: full rollout by Q3 start. |\n| 2025-05-17 | Strategy pivot to SMB market        | Context: Q2 sales flat in enterprise segment. Rationale: better traction with small businesses per feedback. | Outcome: Q3 marketing plan refocused on SMB. Follow-up: new messaging draft by June. |\n| ...        | ...                                 | ...                                                | ...                                    |\n\n*Guidelines:* For each major decision, record the date, a short description of what was decided, key context or reasoning that led to it (including options considered, if relevant), and what happened next (e.g., actions taken, or if the decision was later revisited). Keep entries brief but informative. This log can be updated via a quick note or using an AI workflow after a decision is made (for example, a Meeting Notes workflow might append decisions here).',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Meeting_Notes
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Meeting_Notes', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Meeting Notes - <Meeting Name or Purpose>\n**Date & Time:** <YYYY-MM-DD> <HH:MM>\n**Attendees:** <List of attendees>\n\n**Agenda:**\n1. <Agenda point 1>\n2. <Agenda point 2>\n3. ...\n\n**Discussion Summary:**\n- *Agenda Item 1:* <Summary of discussion outcomes for item 1.>\n- *Agenda Item 2:* <Summary for item 2...>\n- *Additional Topics:* <Any other discussion points not on formal agenda.>\n\n**Decisions Made:**\n- <Decision 1 (if any) and brief rationale/context>\n- <Decision 2 ...>\n\n**Action Items:**\n- <Action Item 1> – *Owner:* <Person> – *Due:* <Due date or ASAP>\n- <Action Item 2> – *Owner:* <Person> – *Due:* <...>\n\n*Notes:* Attach or link any relevant documents presented. For recurring meetings, compare with previous notes to track progress on past action items.',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Daily_Log
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Daily_Log', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Daily Log - <DATE>\n\n**Yesterday’s Summary:**\n_<Brief recap of what happened yesterday: completed tasks, milestones achieved, any blockers encountered.>_\n\n**Today’s Focus:**\n_<Summary of what the team is focusing on today: major tasks planned, goals for the day, who is doing what at a high level.>_\n\n**Notable Updates/Context:**\n- <Any important context for today: e.g., "Client X meeting at 3pm", "Deployment of version 2.0 planned", or "Mark is OOO".>\n- <External factors if any: e.g., "Industry news Y might impact our marketing strategy" (optional, include only if relevant).>\n\n**Blockers & Concerns:**\n- <List any obstacles that could impede progress today, e.g., "Waiting for approval on budget", "Server downtime issue". If none, write "None".>\n\n**Mood & Morale (Optional):**\n- <If the team tracks morale or other subjective context, note it here, e.g., "Team is energized by yesterday''s success" or "A bit anxious about upcoming deadline".>\n\n*_(This Daily Log is automatically generated each morning and reviewed by the team for accuracy. It should remain short—aim for a few paragraphs or bullet points under each section.)_*',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Daily_Plan
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Daily_Plan', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Daily Plan - <DATE>\n\n**Top Priorities Today:**\n1. <Task 1> – *Owner:* <Person> – *Expected Outcome:* <What completing this task achieves by EOD.>\n2. <Task 2> – *Owner:* <Person> – *Expected Outcome:* <...>\n3. <Task 3> – *Owner:* <Person> – *Expected Outcome:* <...>\n*(Limit to 3-5 major tasks across the team to maintain focus.)*\n\n**Secondary Tasks (if time permits):**\n- <Task 4> – <Owner>\n- <Task 5> – <Owner>\n*(These are lower priority; they can be picked up if capacity allows, or moved to tomorrow.)*\n\n**Carry-overs from Yesterday:**\n- <Task from yesterday that wasn''t finished> – *Plan:* <e.g., "Will complete by midday today.">\n- ...\n*(If all tasks from yesterday were completed, state "All tasks from yesterday completed ✅.")*\n\n**Scheduled Events/Meetings:**\n- <Time> - <Event> (Attendees: X, Y)\n- <Time> - <Event>\n*(Any meetings or significant time commitments that team members have today.)*\n\n**End-of-Day Target Check:**\n- <Reiterate any end-of-day deliverables to check, e.g., "Draft report ready for review by 5pm.">\n- ...\n\n*Notes:* This plan is a living document for the day. Team members can adjust it if priorities change (make sure to note changes). At day''s end, compare actual progress against this plan to feed into tomorrow''s Daily Log.',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Weekly_Plan
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Weekly_Plan', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Weekly Plan - Week <##> of <Year> (Starting <Start Date>)\n\n**Week’s Theme/Focus:** _<A short phrase capturing the main focus of the week, e.g., “Stabilize v2.0 Release” or “Client Outreach Blitz”.>_\n\n**Key Goals for the Week:**\n- <Goal 1: e.g., Complete Feature X development for Project Y.>\n- <Goal 2: e.g., Close 3 new deals from pipeline.>\n- <Goal 3: e.g., Hire 1 new engineer.>\n*(These should tie back to the Quarterly OKRs where possible.)*\n\n**Planned Tasks/Deliverables:**\n- <Task or Deliverable 1> – *Owner:* <Person> – *Due:* <Day or date if within the week>\n- <Task/Deliverable 2> – *Owner:* <Person> – *Due:* <...>\n- ... (List key tasks the team commits to finishing this week.)\n\n**Resource Availability:**\n- <Team member A>: <e.g., "Out Friday", or "50% on support duties">\n- <Team member B>: <e.g., "Back from vacation on Wednesday">\n- <Any noteworthy availability or capacity info affecting the plan.>\n\n**Known Risks/Challenges This Week:**\n- <Risk 1: e.g., "If client delays feedback, Feature X might slip.">\n- <Risk 2: e.g., "New hire onboarding might slow team velocity early in week.">\n- <...>\n\n**Communication & Coordination:**\n- <Any special coordination needed, e.g., "Daily 4pm check-in on launch readiness", or "Sales & Dev sync on Thursday".>\n- <...>\n\n*Notes:* This Weekly Plan is reviewed at week''s end (in the Weekly Review) to assess completion and carry-overs. It should be realistic – avoid overcommitting. If priorities change mid-week, update this doc so it remains a source of truth.',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Weekly_Review
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Weekly_Review', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Weekly Review - Week <##> of <Year> (Ending <End Date>)\n\n**Highlights (Wins):**\n- <Highlight 1: e.g., "Delivered the demo to Client X which was well received.">\n- <Highlight 2: e.g., "Feature Y was completed 2 days ahead of schedule.">\n- <... list major achievements or positive outcomes of the week.>\n\n**Lowlights (Challenges):**\n- <Challenge 1: e.g., "Encountered a production bug that took 3 days to fix, delaying other work.">\n- <Challenge 2: e.g., "Team communication broke down on Wednesday, resulting in duplicate work.">\n- <... include any setbacks, issues, or things that didn''t go well.>\n\n**Key Metrics Update:**\n- <Metric 1 (e.g., Website signups): start of week -> end of week (difference, % change)>\n- <Metric 2 (e.g., Sprint burn-down or velocity): planned vs actual>\n- <... include any KPI or OKR-related metric that is tracked weekly. Reference the KPI baseline or OKR doc.>\n\n**Progress on Week’s Goals:**\n- Goal 1: <Status (Achieved / Partially / Not Achieved)>. <Brief commentary if needed (e.g., "Feature X done, pending QA on Monday").>\n- Goal 2: <Status ...>. <Commentary...>\n- ... for each goal listed in the Weekly Plan, note outcome.\n\n**Lessons Learned:**\n- <Lesson 1: e.g., "Daily 10-min end-of-day sync helped catch issues early – continue this practice.">\n- <Lesson 2: e.g., "Need better clarity on spec before development – will involve UX earlier.">\n- <... any takeaways to improve process or teamwork going forward.>\n\n**Adjustments for Next Week:**\n- <Adjustment 1: e.g., "Allocate extra time for code review given last week''s bug.">\n- <Adjustment 2: e.g., "Focus on Project Z as priority shifted (carry over incomplete tasks from this week).">\n- <... changes in plan or focus for the upcoming week based on this review.>\n\n*Notes:* Keep this review factual and constructive. Celebrate wins to boost morale, and address challenges openly but without blame. Share the Weekly Review with the team (and any stakeholders, if appropriate) to maintain transparency.',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Monthly_Report
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Monthly_Report', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Monthly Report - <Month Year>\n\n**Major Achievements:**\n- <Achievement 1: e.g., "Reached 10k users milestone for product, ahead of plan.">\n- <Achievement 2: e.g., "Launched Project X on schedule and budget.">\n- <... top accomplishments of the month.>\n\n**Summary of Progress toward Quarterly OKRs:**\n- Objective 1: <Progress summary (e.g., "On track: 70% of Key Results met so far").>\n  - KR1.1: <Status/details>\n  - KR1.2: <Status/details>\n- Objective 2: <Progress summary (e.g., "At risk: behind on KR2.1 due to delays in...").>\n  - KR2.1: <Status/details>\n  - ... list each key result and status.\n- (Repeat for each active Objective in the quarter)\n\n**Notable Issues & Resolutions:**\n- <Issue 1: e.g., "Supply chain delay affected deliveries. Resolution: switched to alternate supplier in Week 2.">\n- <Issue 2: e.g., "Team member out for 2 weeks, caused workload spike. Resolution: temporarily reallocated tasks among team.">\n- <... any big problems faced and how they were addressed.>\n\n**Team Highlights:**\n- <E.g., "Hired 2 new team members (Names) who joined this month.">\n- <E.g., "Team training on AI tools completed.">\n- <Culture or team-building events or notable changes internally.>\n\n**Next Month Preview:**\n- <Focus or theme for next month: e.g., "Prepare for Q4 product launch," or "Integration phase with new partner.">\n- <Any expected challenges or needs: e.g., "Will need additional budget approval for marketing push.">\n\n*Notes:* This report should be concise (1-2 pages max). It can be generated by compiling weekly reviews and adding a broader perspective. Use it to communicate up to management or to keep the team''s strategic picture clear.',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Quarterly_Business_Review
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Quarterly_Business_Review', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Quarterly Business Review - Q<Quarter> <Year>\n\n**Overview of Quarter Performance:**\n- **Overall Assessment:** <Summary of how the quarter went (e.g., "Exceeded targets" / "Met most objectives" / "Struggled in areas", etc.)>\n- **Key Metrics:** <List critical metrics with quarterly targets vs actuals, e.g., revenue, user growth, NPS, etc.>\n\n**Objective Outcomes:**\n- Objective 1 (“<Objective name>”): <Did we achieve it? Summarize results of its KRs.>\n  - KR1.1: <Achieved % or result>\n  - KR1.2: <Achieved % or result>\n- Objective 2 (“<Objective name>”): <Summary>\n  - KR2.1: <result>\n  - ...\n*(Cover each Objective from the Quarterly OKRs doc, noting which KRs were hit or missed and any analysis.)*\n\n**Highlights of Q<Quarter>:**\n- <Highlight 1: significant success or milestone reached this quarter and its impact.>\n- <Highlight 2: another key positive outcome.>\n- ... (at least one per objective or functional area)\n\n**Challenges of Q<Quarter>:**\n- <Challenge 1: major hurdle or shortfall and how it affected outcomes.>\n- <Challenge 2: ...>\n- ... (anything that impeded success)\n\n**Lessons & Insights:**\n- <Insight 1: e.g., "Our new marketing channel yielded better results than expected, invest more here.">\n- <Insight 2: e.g., "Product development was slowed by tech debt, need to allocate time to address that moving forward.">\n- ... (strategic or operational lessons that inform the future)\n\n**Next Quarter Plan Preview:**\n- <If available, list the draft Objectives for next quarter or key focus areas. E.g., "Focus on scaling customer support for growth," or "Invest in feature Y based on demand.">\n- <Any carry-over initiatives from this quarter that continue into the next.>\n\n**Strategic Adjustments:**\n- <Note any changes to the North Star Charter or overall strategy decided because of this review. E.g., "Shift target market from Enterprise to SMB," or "Expand partnerships strategy per QBR discussion.">\n- <If none, state that current strategy remains consistent heading into next quarter.>\n\n*Notes:* The QBR is often discussed in a meeting with stakeholders. Use this document as both the pre-read and the record of decisions made (you can append or annotate during the meeting). After finalizing, ensure any strategic changes are propagated: update the North Star Charter or create new Quarterly_OKRs as needed.',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Annual_Strategic_Plan
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Annual_Strategic_Plan', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Annual Strategic Plan - <Year>\n\n**Executive Summary:**\n_<One-paragraph summary of the year’s strategic direction and expected outcomes.>_\n\n**Year in Review (if closing year):**\n- **Achievements:** <Bullet list of the most significant accomplishments of the past year.>\n- **Challenges:** <Bullet list of major challenges or failures and their lessons.>\n- **Trend Analysis:** <Key trends observed in the industry, market, or internal operations over the year that influence future strategy.>\n\n**Vision Refresh (if any):**\n_<Note if the team’s Vision/Mission or North Star Charter is updated this year. If yes, summarize the changes or reaffirm the existing vision here._>\n\n**Strategic Objectives for <Year>:**\n1. **Objective A:** <Major objective or theme for the year>\n   - *Description:* <Explain this objective and why it’s important this year.>\n   - *Key Initiatives:* <List big projects or initiatives under this objective.>\n2. **Objective B:** <Next major yearly objective>\n   - *Description:* …\n   - *Key Initiatives:* …\n3. **Objective C:** <Another objective, if applicable>\n   - *Description:* …\n   - *Key Initiatives:* …\n*(These are broad, annual objectives, often broken down into quarterly OKRs later. Align them with the Strategic Pillars from the North Star Charter.)*\n\n**Key Metrics Targets:**\n- <Metric 1: Target for end of year (e.g., "Reach $X in revenue by Q4", or "100k users by Dec").>\n- <Metric 2: ...>\n- <... any top-level KPIs and their targets for the year.>\n\n**Budget & Resource Summary:**\n- <High-level summary of budget or headcount changes for the year, if applicable.>\n- <E.g., "Plan to hire 5 engineers and 2 sales reps by Q3", or "Increase marketing budget by 20% to support Objective A.">\n\n**Risks & Dependencies:**\n- <Risk 1: e.g., "Market regulation changes could impact product launch timeline.">\n- <Risk 2: e.g., "Dependence on Partner X’s technology; any delay on their side affects our Q2 deliverables.">\n- <... list major risks to the plan and external dependencies to monitor.>\n\n**Action Plan & Timeline:**\n- Q1: <Focus or major deliverables in Q1>\n- Q2: <Focus in Q2>\n- Q3: <Focus in Q3>\n- Q4: <Focus in Q4>\n*(This provides a rough breakdown of the year’s plan per quarter.)*\n\n*Notes:* The Annual Strategic Plan should be revisited mid-year (or quarterly) to ensure it’s still on track. At year-end, use it to evaluate success. It complements the North Star Charter: where the Charter is timeless, this plan is specific to the year’s execution.',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Team_Updates
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Team_Updates', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Team Updates - {{Date YYYY-MM-DD}}\n\n**Instructions:** Each team member should provide a brief update below. Focus on:\n1.  What you accomplished yesterday.\n2.  What you plan to work on today.\n3.  Any blockers or impediments.\n\n---\n\n**Team Member: [Name/Alias]**\n* **Yesterday''s Accomplishments:**\n    -   [Accomplishment 1]\n    -   [Accomplishment 2]\n* **Today''s Plan:**\n    -   [Task 1]\n    -   [Task 2]\n* **Blockers/Concerns:**\n    -   [Blocker 1, if any]\n\n---\n\n**Team Member: [Name/Alias]**\n* **Yesterday''s Accomplishments:**\n    -   [...]\n* **Today''s Plan:**\n    -   [...]\n* **Blockers/Concerns:**\n    -   [...]\n\n---\n\n*(Add sections for each team member as needed)*',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_External_Context
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_External_Context', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# External Context - {{Date YYYY-MM-DD or Period}}\n\n**Source/Date of Information:** <e.g., Industry News Digest, Client X Update Call - YYYY-MM-DD>\n\n**Key Points:**\n-   **Update/Event 1:** <Brief description of the external event, news, or client update.>\n    * *Relevance/Impact:* <Why this is important for the team.>\n    * *Source Link (Optional):* <URL if applicable>\n\n-   **Update/Event 2:** <Brief description...>\n    * *Relevance/Impact:* <...>\n    * *Source Link (Optional):* <...>\n\n-   **(Add more updates as necessary)**\n\n**Overall Assessment/Implication for Today/This Week:**\n_<Optional: A brief summary of how this external context might influence the team''s focus or priorities.>_',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Team_Availability
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Team_Availability', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Team Availability - Week {{WeekNumber}} of {{Year}} ({{DateRange YYYY-MM-DD to YYYY-MM-DD}})\n\n**General Notes:** <e.g., Company-wide holiday on Friday, Reduced hours due to X>\n\n---\n\n**Team Member: [Name/Alias]**\n* **Availability:** <e.g., Fully Available, Partially Available (details below)>\n* **Out of Office (OOO):** <List any OOO days/times, e.g., "Monday (All Day)", "Wednesday PM">\n* **Special Assignments/Focus:** <e.g., "Dedicated to Project X support", "Onboarding new hire">\n* **Notes:** <Any other relevant availability information>\n\n---\n\n**Team Member: [Name/Alias]**\n* **Availability:** <...>\n* **Out of Office (OOO):** <...>\n* **Special Assignments/Focus:** <...>\n* **Notes:** <...>\n\n---\n\n*(Add sections for each team member as needed)*\n\n**Summary of Capacity Impact (Optional):**\n_<A brief note on overall team capacity for the week, e.g., "Team at ~80% capacity due to OOO.">_',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Metrics_KPI_Update
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Metrics_KPI_Update', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Metrics/KPI Update - {{Date YYYY-MM-DD or Period Ending YYYY-MM-DD}}\n\n**Reporting Period:** <e.g., Week {{WeekNumber}} YYYY, Month of {{Month}} YYYY>\n\n---\n\n**Metric/KPI: [Metric Name 1]**\n* **Current Value:** <Value>\n* **Previous Value (Optional):** <Value from last period>\n* **Target (Optional):** <Target value for this metric>\n* **Change (Optional):** <e.g., +X%, -Y units>\n* **Notes/Context:** <Brief explanation of any significant changes, trends, or context.>\n\n---\n\n**Metric/KPI: [Metric Name 2]**\n* **Current Value:** <Value>\n* **Previous Value (Optional):** <Value>\n* **Target (Optional):** <Value>\n* **Change (Optional):** <...>\n* **Notes/Context:** <...>\n\n---\n\n*(Add sections for each relevant metric/KPI)*\n\n**Overall Summary/Observations (Optional):**\n_<A brief summary of overall performance based on these metrics, highlighting any key trends or areas needing attention.>_',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Customer_Feedback_Summary
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Customer_Feedback_Summary', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Customer Feedback Summary - {{Period Covered, e.g., QX YYYY or Year YYYY}}\n\n**Data Sources:** <e.g., Support Tickets, Survey Results (Link/Date), User Interviews, App Store Reviews>\n**Period Covered:** <Start Date> to <End Date>\n\n---\n\n**Overall Sentiment (Optional):** <e.g., Positive, Neutral, Mixed, Negative - with brief justification>\n\n---\n\n**Key Positive Themes:**\n1.  **Theme:** <e.g., Ease of Use for Feature X>\n    * *Supporting Feedback Examples (Anonymized if necessary):*\n        -   "<Quote or paraphrased feedback 1>"\n        -   "<Quote or paraphrased feedback 2>"\n    * *Frequency/Impact:* <e.g., Mentioned by ~X% of respondents, High impact on satisfaction>\n\n2.  **Theme:** <e.g., Quality of Customer Support>\n    * *Supporting Feedback Examples:*\n        -   [...]\n    * *Frequency/Impact:* <...>\n\n*(Add more positive themes as identified)*\n\n---\n\n**Key Areas for Improvement/Concerns:**\n1.  **Concern/Theme:** <e.g., Performance Issues on Y Platform>\n    * *Supporting Feedback Examples (Anonymized if necessary):*\n        -   "<Quote or paraphrased feedback 1>"\n        -   "<Quote or paraphrased feedback 2>"\n    * *Frequency/Impact:* <e.g., Reported by X users, Leading cause of frustration>\n\n2.  **Concern/Theme:** <e.g., Missing Feature Z>\n    * *Supporting Feedback Examples:*\n        -   [...]\n    * *Frequency/Impact:* <...>\n\n*(Add more concerns/themes as identified)*\n\n---\n\n**Specific Feature Requests (Top 3-5):**\n-   [Feature Request 1] - *Rationale/Benefit:* <Why customers want this>\n-   [Feature Request 2] - *Rationale/Benefit:* <...>\n-   [Feature Request 3] - *Rationale/Benefit:* <...>\n\n---\n\n**Actionable Insights/Recommendations (Optional):**\n-   <Insight 1 and suggested action>\n-   <Insight 2 and suggested action>',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Market_Context_Trends_Summary
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Market_Context_Trends_Summary', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Market Context & Trends Summary - {{Period Covered, e.g., QX YYYY or Year YYYY}}\n\n**Date of Analysis:** {{YYYY-MM-DD}}\n**Information Sources:** <e.g., Industry Reports (Name/Link), News Articles, Competitor Announcements, Market Research Subscriptions>\n\n---\n\n**Overall Market Environment:**\n* **Current State:** <Brief overview of the current market conditions - e.g., growing, contracting, stable, volatile.>\n* **Key Drivers:** <Factors influencing the market - e.g., technological advancements, economic shifts, regulatory changes.>\n\n---\n\n**Key Industry Trends:**\n1.  **Trend:** <Description of a significant trend, e.g., "Adoption of AI in X industry segment">\n    * *Impact/Opportunity for Us:* <How this trend affects or could affect the team/product.>\n    * *Observed Evidence:* <Specific examples or data points supporting this trend.>\n\n2.  **Trend:** <Description of another trend, e.g., "Shift towards Y business model">\n    * *Impact/Opportunity for Us:* <...>\n    * *Observed Evidence:* <...>\n\n*(Add more key trends as identified)*\n\n---\n\n**Competitor Landscape:**\n* **Major Competitors:** <List 2-3 key competitors>\n* **Competitor A ([Name]):**\n    * *Recent Activities/Announcements:* <e.g., New product launch, strategic partnership, pricing changes.>\n    * *Perceived Strengths/Weaknesses (relative to us):* <Brief analysis.>\n* **Competitor B ([Name]):**\n    * *Recent Activities/Announcements:* <...>\n    * *Perceived Strengths/Weaknesses:* <...>\n\n*(Add more competitors as relevant)*\n\n---\n\n**Emerging Opportunities:**\n-   <Opportunity 1 based on market analysis.>\n-   <Opportunity 2 based on market analysis.>\n\n**Potential Threats/Risks:**\n-   <Threat 1 based on market analysis.>\n-   <Threat 2 based on market analysis.>\n\n---\n\n**Strategic Implications/Recommendations (Optional):**\n_<How this market context should inform the team''s strategy, product development, or positioning.>_',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Raw_Meeting_Record
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Raw_Meeting_Record', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Raw Meeting Record - {{Meeting Name/Subject}} - {{Date YYYY-MM-DD}}\n\n**Meeting Details (if known):**\n* **Subject:** <Meeting Subject Line>\n* **Date & Time:** <YYYY-MM-DD HH:MM>\n* **Attendees (if noted):** <Names or groups present>\n* **Recording Source (if applicable):** <e.g., Zoom transcript, Otter.ai export, manual notes>\n\n---\n\n**Raw Content Start:**\n\n[Paste raw transcript, copied notes, or free-form text here. No specific structure is enforced at this stage. The AI summarization workflow will process this.]\n\nExample of what might be here:\n\n"Okay, so first on the agenda... John, did you have an update on the Q3 numbers? John: Yes, they''re looking good, up 5%. We decided to move forward with the Alpha project. Sarah will own the next steps for that, due next Friday. Any questions? Mike: What about the budget for Alpha? John: We''ll discuss that offline. Next item: marketing campaign. Lisa mentioned we need new creatives. Lisa: That''s right, the old ones are stale. Agreed to brainstorm new ideas by Wednesday. Bob volunteered to set up the meeting. Okay, anything else? No? Meeting adjourned."\n\n... or ...\n\n- Q3 numbers up 5% (John)\n- Alpha project GO\n    - Sarah next steps EOW Friday\n- Budget for Alpha?? -> offline discussion\n- Marketing campaign - new creatives needed (Lisa)\n    - Brainstorm by Wed\n    - Bob to setup meeting.\n\n**Raw Content End:**',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Meeting_Agenda
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Meeting_Agenda', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Meeting Agenda - {{Meeting Name/Purpose}}\n\n**Date & Time:** <YYYY-MM-DD> <HH:MM>\n**Location/Call Link:** <Physical location or virtual meeting URL>\n**Attendees (Optional Invitees List):** <List of expected attendees>\n\n**Meeting Goal(s):**\n-   <Primary objective 1 of the meeting>\n-   <Primary objective 2 of the meeting, if any>\n\n---\n\n**Agenda Items:**\n\n1.  **Topic 1:** <Brief description of the first agenda item>\n    * *Presenter/Lead (Optional):* <Name>\n    * *Time Allotted (Optional):* <e.g., 15 mins>\n    * *Desired Outcome:* <What needs to be achieved for this item>\n\n2.  **Topic 2:** <Brief description of the second agenda item>\n    * *Presenter/Lead (Optional):* <Name>\n    * *Time Allotted (Optional):* <e.g., 20 mins>\n    * *Desired Outcome:* <...>\n\n3.  **(Add more agenda items as necessary)**\n\n---\n\n**Pre-Reading/Preparation (Optional):**\n-   <Link to document 1> - <Brief description of what to review>\n-   <Task to complete before meeting>\n\n**Post-Meeting Next Steps (Placeholder):**\n-   <e.g., Decisions to be logged, Actions to be assigned>',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Prompt_Analysis_Input
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Prompt_Analysis_Input', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Prompt Analysis Input - {{Workflow Name or Prompt Subject}}\n\n**Date of Analysis:** {{YYYY-MM-DD}}\n**Target Workflow/Prompt Being Analyzed:** <Name of the HORIZON workflow or a description of the prompt''s purpose>\n\n---\n\n**1. Current Prompt Text:**\n\n```text\n[Paste the full text of the current prompt that needs improvement here.]\n```\n\n---\n\n**2. Examples of Bad/Unsatisfactory Output (with annotations):**\n\n* **Example 1:**\n    * *Input Snippet (if relevant to show what produced the bad output):*\n        ```text\n        [Relevant portion of input that led to this bad output]\n        ```\n    * *Actual Output from Current Prompt:*\n        ```text\n        [Paste the problematic output here]\n        ```\n    * *Annotation (What was wrong/missing/incorrect?):*\n        -   [Specific issue 1, e.g., "Output was too verbose here."]\n        -   [Specific issue 2, e.g., "Missed a key blocker mentioned in the input."]\n\n* **Example 2 (Optional, if more are needed):**\n    * *Input Snippet:*\n        ```text\n        [...]\n        ```\n    * *Actual Output from Current Prompt:*\n        ```text\n        [...]\n        ```\n    * *Annotation:*\n        -   [...]\n\n---\n\n**3. Desired Outcome Description:**\n\n* **What should an ideal output look like?**\n    <Describe the characteristics of a good output. e.g., "The output should be a concise summary under 200 words," or "It must extract all action items with owners and due dates.">\n\n* **How should the ideal output differ from the bad examples?**\n    <Explain the key differences expected.>\n\n* **Specific elements that MUST be included/excluded:**\n    -   Must include: [Element A, Element B]\n    -   Must exclude: [Element C, Element D]\n\n---\n\n**4. Prompt Design Guidelines/Constraints (Optional):**\n\n<Reference any relevant best practices or rules that the revised prompt should adhere to. This could be from a team''s internal prompt engineering guide or general principles.>\n\n* Guideline 1: <e.g., "Prompts should clearly define the AI''s role.">\n* Guideline 2: <e.g., "Use few-shot examples if output structure is critical.">\n* Guideline 3: <e.g., "Ensure prompts are within context limits of the LLM.">\n\n---\n\n**5. Any Other Relevant Context:**\n\n<Provide any other information that might help the "Prompt Engineer Assistant" AI understand the problem and suggest better solutions.>',
    1, admin_team_id, NOW());
END $$;

-- Template: HORIZON_Condensation_Criteria
DO $$
DECLARE
    template_item_id uuid := public.uuid_generate_v4();
    template_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'HORIZON_Condensation_Criteria', true, template_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (template_version_id, template_item_id,
E'# Condensation Criteria for Archival Summary\n\n**Criteria Set Name (Optional):** <e.g., "Monthly Log Condensation Rules", "Project Alpha Archive Specs">\n**Date Created:** {{YYYY-MM-DD}}\n**Intended For Document Types:** <e.g., Daily Logs, Weekly Reviews, Meeting Notes for Project X>\n**Target Condensation Period (if applicable):** <e.g., Documents older than 90 days, Q1 YYYY Daily Logs>\n\n---\n\n**1. Desired Summary Length/Granularity:**\n* <Specify desired output compactness. Examples:>\n    * "Produce a one-paragraph summary per week of input."\n    * "Limit the total summary to approximately 500 words."\n    * "Extract no more than 5 key bullet points per input document."\n    * "Generate a narrative summary, focusing on a high-level overview."\n\n---\n\n**2. Key Information to Retain/Prioritize:**\n* **Strategic Decisions & Rationale:** <e.g., "Must retain all formally logged decisions and their stated reasons.">\n* **Major Achievements/Milestones:** <e.g., "Focus on significant project completions, major feature releases, key targets met.">\n* **Significant Challenges/Blockers & Resolutions:** <e.g., "Include recurring major issues, critical incidents, and how they were resolved.">\n* **Key Learnings/Insights with Enduring Value:** <e.g., "Preserve lessons learned that led to process changes or strategic shifts.">\n* **Numerical Results/Metrics:** <e.g., "Retain final figures for key metrics, budget variances, or performance indicators.">\n* **Changes in Strategy/Direction:** <e.g., "Capture any pivots or re-prioritizations.">\n* **(Add other specific categories relevant to the documents being condensed)**\n\n---\n\n**3. Information to Omit/De-prioritize:**\n* **Routine Updates/Minor Details:** <e.g., "Omit day-to-day minor task updates unless they led to a major outcome.">\n* **Transient Operational Details:** <e.g., "Exclude temporary system glitches if resolved quickly without impact.">\n* **Redundant Information:** <e.g., "If multiple inputs cover the same event, synthesize it once.">\n* **Informal Chatter/Non-Essential Dialogue (from meeting notes, etc.):** <e.g., "Focus on outcomes, not verbatim discussions unless a quote is critical.">\n* **(Add other specific categories of information to exclude)**\n\n---\n\n**4. Desired Output Structure/Format (Optional):**\n* <Suggest headings or a structure for the condensed output document. Examples:>\n    * "Structure by month, then by key themes (Achievements, Challenges, Decisions)."\n    * "Use top-level headings: Key Events, Major Decisions, Learnings."\n    * "Provide output as a list of bullet points under pre-defined categories."\n\n---\n\n**5. Any Other Specific Instructions:**\n* <e.g., "Maintain a neutral and factual tone." >\n* <e.g., "If source documents have conflicting information, note the discrepancy." >\n* <e.g., "Ensure all dates for key events are preserved accurately." >',
    1, admin_team_id, NOW());
END $$;

--
-- End of HORIZON Protocol Templates
--

--
-- Inserting HORIZON Protocol Workflows
--

-- Workflow: HORIZON_DailyLogGeneration
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_DailyLogGeneration\n# Description: Collates yesterday''s events and today''s plan into a Daily Log.\n# Ritual Relevance: Daily Log Generation (Morning)\n# Template Origin: Outputs based on HORIZON_Daily_Log template structure.\n\ninputDocumentSelectors:\n  - "Team_Updates*"\n  - "Task_Backlog*"\n  - "Weekly_Plan*"\n  - "External_Context*"\ninputDateSelector: null\noutputName: "Daily_Log_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  **Role:** You are a Daily Chronicle Assistant. Your task is to draft the Daily Log document.\n  **Goal:** Create a concise narrative summarizing what happened yesterday and the plan for today, based on the provided input documents. The output should follow the structure of the HORIZON_Daily_Log template.\n  **Context:**\n  The DocumentContext contains concatenated text from the following documents. Identify them by likely content or sections:\n  1.  **Team Updates Document (e.g., "Team_Updates_YYYY-MM-DD"):** Contains notes on what team members did yesterday and any blockers.\n  2.  **Task Backlog Document (e.g., "Task_Backlog*"):** Shows the status of tasks (completed, ongoing, new).\n  3.  **Weekly Plan Document (e.g., "Weekly_Plan*"):** Outlines goals for the current week.\n  4.  **External Context Document (Optional, e.g., "External_Context_YYYY-MM-DD"):** Contains notable industry news or client updates.\n\n  Today''s Date: {{Year}}-{{Month}}-{{Day}}.\n\n  **Task:**\n  1.  **Analyze Inputs:** Carefully review all provided documents within DocumentContext.\n  2.  **Draft "Yesterday’s Summary":**\n      * From "Team Updates" and "Task Backlog" (completed tasks), summarize key accomplishments and events from yesterday.\n      * Use bullet points for clarity.\n  3.  **Draft "Today’s Focus":**\n      * Based on the "Weekly Plan" and any carry-over tasks from "Team Updates" or "Task Backlog", outline what needs attention today.\n      * Align with weekly goals.\n  4.  **Draft "Blockers & Concerns":**\n      * Extract any blockers noted in "Team Updates" and list them. If none, state "None".\n  5.  **Draft "Notable Updates/Context":**\n      * If an "External Context" document is provided and relevant, include a bullet point for any significant update.\n      * Include any other critical context for the day mentioned in inputs.\n  6.  **Structure Output:** Format the entire output strictly according to the HORIZON_Daily_Log template structure (headings: Yesterday''s Summary, Today''s Focus, Notable Updates/Context, Blockers & Concerns).\n\n  **Output Format (Strictly Adhere):**\n  ```markdown\n  # Daily Log - {{Year}}-{{Month}}-{{Day}}\n\n  **Yesterday’s Summary:**\n  - [Summary of yesterday''s key accomplishments and completed tasks based on inputs]\n  - [...]\n\n  **Today’s Focus:**\n  - [Forecast of what needs attention today, aligned with weekly goals and ongoing tasks, based on inputs]\n  - [...]\n\n  **Notable Updates/Context:**\n  - [Important context for today from inputs, including external context if provided and relevant]\n  - [...]\n\n  **Blockers & Concerns:**\n  - [List of blockers from inputs. If none, state "None".]\n  - [...]\n  ```\n\n  **Constraints:**\n  - Use only the information provided in the DocumentContext. Do not invent or assume details.\n  - Be concise and factual.\n  - Prioritize information directly impacting the team''s work for the day and week.\n  - If specific input document names are not determinable from DocumentContext structure, synthesize based on the nature of the content found (e.g., look for lists of tasks for the backlog, daily updates for team progress).\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_DailyLogGeneration', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

-- Workflow: HORIZON_DailyPlanGeneration
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_DailyPlanGeneration\n# Description: Generates a focused plan for the current day.\n# Ritual Relevance: Daily Plan Creation (Morning)\n# Template Origin: Outputs based on HORIZON_Daily_Plan template structure.\n\ninputDocumentSelectors:\n  - "Daily_Log*"\n  - "Task_Backlog*"\n  - "Weekly_Plan*"\n  - "Quarterly_OKRs*"\ninputDateSelector: null\noutputName: "Daily_Plan_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  **Role:** You are a Planning Assistant. Your task is to draft the Daily Plan document.\n  **Goal:** Generate a focused, actionable plan for today, selecting top priorities from the Task Backlog that align with the Weekly Plan and Quarterly OKRs, using context from the Daily Log.\n  **Context:**\n  The DocumentContext contains concatenated text from:\n  1.  **Daily Log (e.g., "Daily_Log_YYYY-MM-DD"):** Provides today''s context, blockers, and yesterday''s carry-overs.\n  2.  **Task Backlog Document (e.g., "Task_Backlog*"):** Lists all open tasks, their priority, and status.\n  3.  **Weekly Plan Document (e.g., "Weekly_Plan*"):** Outlines key goals for the week. (Assume Day X of 5 for this week, if not specified, assume mid-week).\n  4.  **Quarterly OKRs (Optional, e.g., "Quarterly_OKRs*"):** Provides high-level objectives.\n\n  Today''s Date: {{Year}}-{{Month}}-{{Day}}.\n\n  **Task:**\n  1.  **Analyze Inputs:** Review all documents in DocumentContext.\n  2.  **Identify Top Priorities:**\n      * From the "Task Backlog", select 3-5 top priority tasks for today.\n      * Ensure these tasks contribute to the "Weekly Plan" goals and, if applicable, "Quarterly OKRs".\n      * Consider any carry-over tasks or blockers mentioned in the "Daily Log".\n      * Assign owners if clear from backlog or weekly plan context.\n  3.  **List Secondary Tasks:** Identify 1-2 secondary tasks from the "Task Backlog" that can be addressed if time permits.\n  4.  **Schedule Events/Meetings:** If the "Weekly Plan" or "Daily Log" mentions specific meetings or events for today, list them.\n  5.  **Structure Output:** Format the output strictly according to the HORIZON_Daily_Plan template structure.\n\n  **Output Format (Strictly Adhere):**\n  ```markdown\n  # Daily Plan - {{Year}}-{{Month}}-{{Day}}\n\n  **Top Priorities Today:**\n  1.  <Task 1 from backlog> – *Owner:* <Person/Team if known from inputs> – *Expected Outcome:* <Briefly describe what completing this achieves today based on inputs>\n  2.  <Task 2 from backlog> – *Owner:* <Person/Team if known from inputs> – *Expected Outcome:* <...>\n  3.  <Task 3 from backlog> – *Owner:* <Person/Team if known from inputs> – *Expected Outcome:* <...>\n  *(Limit to 3-5 major tasks)*\n\n  **Secondary Tasks (if time permits):**\n  - <Task 4 from backlog> – *Owner:* <Person/Team if known from inputs>\n  - <Task 5 from backlog> – *Owner:* <Person/Team if known from inputs>\n\n  **Carry-overs from Yesterday:**\n  - <Task from Daily Log or backlog not finished yesterday> – *Plan:* <e.g., "Complete by midday today.">\n  *(If all tasks from yesterday were completed per Daily Log, state "All tasks from yesterday completed ✅.")*\n\n  **Scheduled Events/Meetings:**\n  - <Time (if known)> - <Event from Daily Log or Weekly Plan> (Attendees: <If known>)\n  - <...>\n\n  **End-of-Day Target Check:**\n  - <Reiterate any specific end-of-day deliverables implied by top priority tasks>\n  ```\n\n  **Constraints:**\n  - Use only information from DocumentContext.\n  - The plan must be realistic. Explicitly limit "Top Priorities Today" to 3-5 tasks.\n  - If task owners are not specified in the input, leave as "[Unassigned]".\n  - Expected outcomes should be inferred from task descriptions and goals.\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_DailyPlanGeneration', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

-- Workflow: HORIZON_WeeklyPlanningKickoff
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_WeeklyPlanningKickoff\n# Description: Synthesizes a Weekly Plan for the upcoming week.\n# Ritual Relevance: Weekly Kick-off Planning (Mondays)\n# Template Origin: Outputs based on HORIZON_Weekly_Plan template structure.\n\ninputDocumentSelectors:\n  - "North_Star_Charter"\n  - "Quarterly_OKRs*"\n  - "Weekly_Review*"\n  - "Task_Backlog*"\n  - "Idea_Backlog*"\n  - "Team_Availability*"\ninputDateSelector: null\noutputName: "Weekly_Plan_W{{CurrentWeekNumber}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  **Role:** You are a Sprint Planner AI. Your task is to draft the Weekly Plan for the upcoming week.\n  **Goal:** Create a Weekly Plan that outlines key goals and tasks, aligned with the North Star Charter and Quarterly OKRs, considering last week''s review, current backlogs, and team availability.\n  **Context:**\n  The DocumentContext contains concatenated text from:\n  1.  **North Star Charter:** Team''s mission, vision, strategic pillars.\n  2.  **Quarterly OKRs (e.g., "Quarterly_OKRs*"):** Current quarter''s objectives. (Assume "Quarter QX: Objective 1 is Y% done..." summary is available or can be inferred).\n  3.  **Last Weekly Review (e.g., "Weekly_Review*"):** Outcomes, incomplete goals, issues from the previous week.\n  4.  **Task Backlog (e.g., "Task_Backlog*"):** Top available tasks.\n  5.  **Idea Backlog (Optional, e.g., "Idea_Backlog*"):** Potential new items.\n  6.  **Team Availability (Optional, e.g., "Team_Availability*"):** Staffing notes for the week.\n\n  Current Date: {{Year}}-{{Month}}-{{Day}}. Assume this is the start of the new week.\n\n  **Task:**\n  1.  **Analyze Inputs:** Review all documents. Synthesize high-level context (e.g., progress in quarter, strategic focus needed based on last week''s review).\n  2.  **Draft "Week’s Theme/Focus":** Propose a short theme for the week based on the most pressing objectives or carry-overs.\n  3.  **Draft "Key Goals for the Week":**\n      * Propose 2-5 key goals for the week. These should advance "Quarterly OKRs" and address items from "Last Weekly Review" (e.g., incomplete goals).\n  4.  **Draft "Planned Tasks/Deliverables":**\n      * From "Task Backlog" (and "Idea Backlog" if relevant), list specific tasks/deliverables that support the weekly goals.\n      * Assign owners and tentative due days (within the week) if information is available in inputs (e.g., team roles or typical assignments from backlog).\n      * Consider team capacity: "Assume the team can complete 5-7 significant tasks in a week" or use "Team Availability" if provided.\n  5.  **Populate "Resource Availability":** Summarize from "Team_Availability*" document if provided. Otherwise, state "Standard availability assumed."\n  6.  **Identify "Known Risks/Challenges This Week":** Based on "Last Weekly Review" or task complexities.\n  7.  **Suggest "Communication & Coordination":** Note any meetings from inputs or imply standard coordination needs.\n  8.  **Structure Output:** Format according to the HORIZON_Weekly_Plan template.\n\n  **Output Format (Strictly Adhere):**\n  ```markdown\n  # Weekly Plan - Week <Number> of {{Year}} (Starting {{Year}}-{{Month}}-{{Day}})\n\n  **Week’s Theme/Focus:** _<Proposed theme based on inputs>_\n\n  **Key Goals for the Week:**\n  - <Proposed Goal 1 based on inputs, linked to OKRs/last week>\n  - <Proposed Goal 2 based on inputs, linked to OKRs/last week>\n  - [...] *(2-5 goals)*\n\n  **Planned Tasks/Deliverables:**\n  - <Task/Deliverable 1 from backlog/ideas> – *Owner:* <Person/Team if known> – *Due:* <Day/Date within week>\n  - <Task/Deliverable 2 from backlog/ideas> – *Owner:* <Person/Team if known> – *Due:* <Day/Date within week>\n  - [...] *(Consider 5-7 significant tasks)*\n\n  **Resource Availability:**\n  - <Summary from Team_Availability*, or "Standard availability assumed.">\n\n  **Known Risks/Challenges This Week:**\n  - <Risk 1 based on inputs>\n  - <Risk 2 based on inputs>\n\n  **Communication & Coordination:**\n  - <Coordination notes based on inputs>\n  ```\n\n  **Constraints:**\n  - Use only information from DocumentContext.\n  - The plan should be ambitious but realistic given a typical week''s capacity.\n  - Please respect the team availability for everything you plan and give a reasoning for why you think that what you plan for the week fits into the given availability.\n  - Prioritize tasks that advance quarterly goals or address carry-overs.\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_WeeklyPlanningKickoff', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

-- Workflow: HORIZON_WeeklyReviewSynthesis
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_WeeklyReviewSynthesis\n# Description: Produces a Weekly Review document summarizing the week''s events and performance.\n# Ritual Relevance: Weekly Review & Retro (Fridays)\n# Template Origin: Outputs based on HORIZON_Weekly_Review template structure.\n\ninputDocumentSelectors:\n  - "Weekly_Plan*"\n  - "Daily_Log*"\n  - "Task_Backlog*"\n  - "Quarterly_OKRs*"\n  - "Decision_Log*"\n  - "Metrics_KPI_Update*"\ninputDateSelector: null\noutputName: "Weekly_Review_W{{CurrentWeekNumber}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  **Role:** You are a Retrospective Analyst AI. Your task is to draft the Weekly Review.\n  **Goal:** Summarize the week''s accomplishments, challenges, and progress against the Weekly Plan. Identify lessons learned and suggest adjustments for next week.\n  **Context:**\n  The DocumentContext contains concatenated text from:\n  1.  **Weekly Plan (e.g., "Weekly_Plan*"):** The goals and tasks planned for this week.\n  2.  **Daily Logs (e.g., "Daily_Log_*"):** Details of what occurred each day this week (accomplishments, blockers).\n  3.  **Task Backlog (e.g., "Task_Backlog*"):** Status of tasks (Done, In Progress).\n  4.  **Quarterly OKRs (Optional):** For context on metrics.\n  5.  **Decision Log (Optional):** For any major decisions made.\n  6.  **Metrics/KPI Update (Optional, e.g., "Metrics_KPI_Update*"):** Latest figures for key metrics.\n\n  Current Date: {{Year}}-{{Month}}-{{Day}}. Assume this is the end of the week being reviewed.\n\n  **Task:**\n  1.  **Analyze Inputs:** Review all documents. To manage context size, focus on summarizing key bullet points from daily logs rather than full text.\n  2.  **Draft "Highlights (Wins)":**\n      * From "Daily Logs" (accomplishments) and "Task Backlog" (completed tasks), compile top wins.\n  3.  **Draft "Lowlights (Challenges)":**\n      * From "Daily Logs" (blockers, issues) and "Task Backlog" (unfinished/delayed tasks), list key challenges.\n  4.  **Draft "Key Metrics Update":**\n      * If "Metrics_KPI_Update*" or relevant data in "Quarterly_OKRs" is provided, summarize changes in key metrics. State if data is unavailable.\n  5.  **Draft "Progress on Week’s Goals":**\n      * For each goal in the "Weekly Plan", assess its status (Achieved, Partially Achieved, Not Achieved) based on "Daily Logs" and "Task Backlog". Provide brief commentary.\n  6.  **Draft "Lessons Learned":**\n      * Analyze challenges and wins. Infer 1-2 key lessons. Check "Decision Log" for process changes.\n  7.  **Draft "Adjustments for Next Week":**\n      * Suggest 1-2 adjustments or carry-over focuses based on unfinished tasks or lessons learned.\n  8.  **Structure Output:** Format according to the HORIZON_Weekly_Review template.\n\n  **Output Format (Strictly Adhere):**\n  ```markdown\n  # Weekly Review - Week <Number> of {{Year}} (Ending {{Year}}-{{Month}}-{{Day}})\n\n  **Highlights (Wins):**\n  - <Win 1 from inputs>\n  - <Win 2 from inputs>\n  - [...]\n\n  **Lowlights (Challenges):**\n  - <Challenge 1 from inputs>\n  - <Challenge 2 from inputs>\n  - [...]\n\n  **Key Metrics Update:**\n  - <Metric 1: Start -> End (Change), based on inputs or "Data unavailable">\n  - <Metric 2: Start -> End (Change), based on inputs or "Data unavailable">\n  - [...]\n\n  **Progress on Week’s Goals:**\n  - Goal 1 (<from Weekly Plan>): <Status (Achieved/Partially/Not Achieved)>. <Commentary based on inputs.>\n  - Goal 2 (<from Weekly Plan>): <Status...>. <Commentary based on inputs.>\n  - [...]\n\n  **Lessons Learned:**\n  - <Lesson 1 based on inputs'' analysis>\n  - <Lesson 2 based on inputs'' analysis>\n  - [...]\n\n  **Adjustments for Next Week:**\n  - <Adjustment 1 based on inputs'' analysis (e.g., carry over task, focus area)>\n  - <Adjustment 2 based on inputs'' analysis>\n  - [...]\n  ```\n\n  **Constraints:**\n  - Use only information from DocumentContext.\n  - Be factual. If a metric is not mentioned, state "Data unavailable".\n  - Prioritize impactful wins, challenges, and lessons.\n  - Prompt emphasizes summarizing daily logs: "focus on summarizing key bullet points from daily logs rather than full text."\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_WeeklyReviewSynthesis', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

-- Workflow: HORIZON_MonthlyReportCompilation
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_MonthlyReportCompilation\n# Description: Generates a Monthly Report aggregating weekly reviews and progress.\n# Ritual Relevance: Monthly Strategy Check\n# Template Origin: Outputs based on HORIZON_Monthly_Report template structure.\n\ninputDocumentSelectors:\n  - "Weekly_Review_W*"\n  - "Quarterly_OKRs*"\n  - "North_Star_Charter"\n  - "Idea_Backlog*"\n  - "Decision_Log*"\n  - "Metrics_KPI_Update*"\ninputDateSelector: null\noutputName: "Monthly_Report_{{Year}}-{{Month}}"\nprompt: |\n  **Role:** You are a Report Aggregator AI. Your task is to draft the Monthly Report.\n  **Goal:** Aggregate information from the month''s Weekly Reviews to provide a higher-level view of progress, achievements, issues, and alignment with Quarterly OKRs.\n  **Context:**\n  The DocumentContext contains concatenated text from:\n  1.  **Weekly Reviews (e.g., "Weekly_Review_W*"):** Highlights, lowlights, metrics, and lessons from each week of the month.\n  2.  **Quarterly OKRs (e.g., "Quarterly_OKRs*"):** To assess progress.\n  3.  **North Star Charter (Optional):** For strategic context.\n  4.  **Idea Backlog & Decision Log (Optional):** For innovations or major decisions.\n  5.  **Metrics/KPI Update (Optional, e.g., "Metrics_KPI_Update*"):** Month-end metric data.\n\n  Current Date: {{Year}}-{{Month}}-{{Day}}. Assume this is for the month ending.\n\n  **Task:**\n  1.  **Analyze Inputs:** Review all documents. Focus on extracting major themes from weekly reviews, not minor details.\n  2.  **Draft "Major Achievements":**\n      * From "Weekly Reviews" (Highlights sections), synthesize the most significant accomplishments of the month. Avoid simple repetition; group related wins.\n  3.  **Draft "Summary of Progress toward Quarterly OKRs":**\n      * For each Objective in "Quarterly_OKRs", assess progress based on cumulative data from "Weekly Reviews" and "Metrics/KPI Update". Note if on track, at risk, or lagging.\n  4.  **Draft "Notable Issues & Resolutions":**\n      * From "Weekly Reviews" (Lowlights/Challenges sections), identify recurring or major issues. Note resolutions if mentioned.\n  5.  **Draft "Team Highlights":**\n      * From "Weekly Reviews", "Decision_Log", or other inputs, note any significant team changes, hires, or major internal events.\n  6.  **Draft "Next Month Preview":**\n      * Based on unfinished work from "Weekly Reviews" (Adjustments sections) or upcoming items in "Quarterly_OKRs", suggest a focus for the next month.\n  7.  **Structure Output:** Format according to the HORIZON_Monthly_Report template.\n\n  **Output Format (Strictly Adhere):**\n  ```markdown\n  # Monthly Report - {{Month}} {{Year}}\n\n  **Major Achievements:**\n  - <Synthesized Achievement 1 from weekly reviews>\n  - <Synthesized Achievement 2 from weekly reviews>\n  - [...]\n\n  **Summary of Progress toward Quarterly OKRs:**\n  - Objective 1 (<from Quarterly_OKRs>): <Progress summary (e.g., On track: X% of KRs met) based on inputs.>\n    - KR1.1 (<from Quarterly_OKRs>): <Status/details based on inputs>\n    - KR1.2 (<from Quarterly_OKRs>): <Status/details based on inputs>\n  - Objective 2 (<from Quarterly_OKRs>): <Progress summary...>\n    - [...]\n  *(Repeat for each active Objective)*\n\n  **Notable Issues & Resolutions:**\n  - <Issue 1 from weekly reviews and its resolution if stated>\n  - <Issue 2 from weekly reviews and its resolution if stated>\n  - [...]\n\n  **Team Highlights:**\n  - <Team update 1 from inputs>\n  - <Team update 2 from inputs>\n\n  **Next Month Preview:**\n  - <Focus/theme for next month based on inputs>\n  - <Expected challenges/needs based on inputs>\n  ```\n\n  **Constraints:**\n  - Use only information from DocumentContext.\n  - Synthesize, do not just list. Focus on the monthly perspective.\n  - Be selective: "Only include the most noteworthy accomplishments".\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_MonthlyReportCompilation', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

-- Workflow: HORIZON_QBRGeneration
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_QBRGeneration\n# Description: Generates the Quarterly Business Review document.\n# Ritual Relevance: Quarterly Business Review (Quarter''s end)\n# Template Origin: Outputs based on HORIZON_Quarterly_Business_Review template structure.\n\ninputDocumentSelectors:\n  - "Quarterly_OKRs*"\n  - "Monthly_Report*"\n  - "Weekly_Review_W*"\n  - "North_Star_Charter"\n  - "Decision_Log*"\n  - "Customer_Feedback_Summary*"\n  - "Market_Context_Summary*"\ninputDateSelector: null\noutputName: "Quarterly_Business_Review_Q{{WorkflowName | placeholder_for_quarter_number_logic}}_{{Year}}"\nprompt: |\n  **Role:** You are an Executive Analyst AI. Your task is to draft the Quarterly Business Review (QBR).\n  **Goal:** Create a comprehensive, structured QBR analyzing the quarter''s performance against OKRs, summarizing highlights, challenges, lessons, and suggesting strategic adjustments.\n  **Context:**\n  The DocumentContext contains concatenated text from:\n  1.  **Quarterly OKRs (e.g., "Quarterly_OKRs*"):** With final status for each Key Result.\n  2.  **Monthly Reports (e.g., "Monthly_Report_*") OR Weekly Reviews (e.g., "Weekly_Review_W*"):** Covering the quarter. Prefer Monthly Reports if available for conciseness.\n  3.  **North Star Charter (Optional):** For long-term strategic reference.\n  4.  **Decision Log (Optional, e.g., "Decision_Log*"):** Major decisions made.\n  5.  **Customer Feedback / Market Context (Optional, e.g., "Customer_Feedback_Summary*"):** External factors.\n\n  Assume this QBR is for the quarter just ended. Current Date: {{Year}}-{{Month}}-{{Day}}.\n\n  **Task:**\n  1.  **Analyze Inputs:** Review all documents. If using Weekly Reviews, synthesize monthly themes first if Monthly Reports are absent.\n  2.  **Draft "Overview of Quarter Performance":**\n      * Write an "Overall Assessment" of the quarter.\n      * List "Key Metrics" (targets vs. actuals) if data is available in inputs.\n  3.  **Draft "Objective Outcomes":**\n      * For each Objective in "Quarterly_OKRs", state if achieved, partially, or missed. Summarize KR results and provide brief analysis using monthly/weekly report data.\n  4.  **Draft "Highlights of QX":**\n      * Synthesize the top 3-5 achievements from monthly/weekly reports.\n  5.  **Draft "Challenges of QX":**\n      * Synthesize major impediments or shortfalls from monthly/weekly reports.\n  6.  **Draft "Lessons & Insights":**\n      * Infer strategic or operational lessons based on objective outcomes and challenges. Check "Decision Log".\n  7.  **Draft "Next Quarter Plan Preview":**\n      * Suggest obvious next steps or carry-overs. If specific next-quarter plans are mentioned in inputs, include them.\n  8.  **Draft "Strategic Adjustments":**\n      * Based on the review, note any suggested changes to strategy or the "North Star Charter".\n  9.  **Structure Output:** Format according to the HORIZON_Quarterly_Business_Review template.\n\n  **Output Format (Strictly Adhere):**\n  ```markdown\n  # Quarterly Business Review - Q<Number> {{Year}}\n\n  **Overview of Quarter Performance:**\n  - **Overall Assessment:** <Summary of quarter performance based on inputs>\n  - **Key Metrics:** <List critical metrics (target vs actual) from inputs, or "Data unavailable">\n\n  **Objective Outcomes:**\n  - Objective 1 ("<from OKRs doc>"): <Achieved/Partially/Missed>. <Summary of KR results & analysis from inputs.>\n    - KR1.1 ("<from OKRs doc>"): <Result from inputs>\n    - KR1.2 ("<from OKRs doc>"): <Result from inputs>\n  - Objective 2 ("<from OKRs doc>"): <Summary...>\n    - [...]\n  *(Cover all Objectives from the OKRs document)*\n\n  **Highlights of Q<Number>:**\n  - <Highlight 1 synthesized from inputs>\n  - <Highlight 2 synthesized from inputs>\n  - [...] *(3-5 highlights)*\n\n  **Challenges of Q<Number>:**\n  - <Challenge 1 synthesized from inputs>\n  - <Challenge 2 synthesized from inputs>\n  - [...]\n\n  **Lessons & Insights:**\n  - <Insight 1 based on inputs>\n  - <Insight 2 based on inputs>\n  - [...]\n\n  **Next Quarter Plan Preview:**\n  - <Focus areas/carry-overs for next quarter, from inputs>\n  - [...]\n\n  **Strategic Adjustments:**\n  - <Suggested changes to strategy/Charter based on inputs>\n  - [...]\n  ```\n\n  **Constraints:**\n  - Use only information from DocumentContext.\n  - Maintain an analytical and strategic tone. "For each objective, briefly analyze why it was or wasn’t achieved.".\n  - Quantitative data for KRs must come from inputs. "Do not make assumptions about numbers that are not given.".\n  - Prioritize summarizing from Monthly Reports if available.\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_QBRGeneration', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

-- Workflow: HORIZON_AnnualStrategicPlanningAssistant
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_AnnualStrategicPlanningAssistant\n# Description: Assists in creating the Annual Strategic Plan by summarizing the past year and drafting future goals.\n# Ritual Relevance: Annual Planning Retreat\n# Template Origin: Outputs based on HORIZON_Annual_Strategic_Plan template structure.\n\ninputDocumentSelectors:\n  - "North_Star_Charter"\n  - "Quarterly_Business_Review_Q*"\n  - "Annual_Strategic_Plan*"\n  - "Idea_Backlog_CurrentYear"\n  - "Customer_Feedback_Summary_Annual"\n  - "Market_Trends_Summary_Annual"\ninputDateSelector: null\noutputName: "Annual_Strategic_Plan_Draft_{{Year + 1}}"\nprompt: |\n  **Role:** You are a Strategic Planner AI. Your task is to assist in drafting the Annual Strategic Plan for next year ({{Year + 1}}).\n  **Goal:** Summarize the performance of the current year ({{Year}}) using the provided QBRs and other inputs. Then, based on this analysis, the North Star Charter, and any ideas/trends, draft proposed strategic objectives, key initiatives, and metrics for the upcoming year.\n  **Context:**\n  The DocumentContext contains concatenated text from:\n  1.  **North Star Charter:** Current mission, vision, strategic pillars.\n  2.  **Quarterly Business Reviews (QBRs):** For all four quarters of the year {{Year}}. These are the primary source for the "Year in Review".\n  3.  **Annual Strategic Plan for {{Year}} (Optional):** To compare expected vs. actual for {{Year}}.\n  4.  **Idea Backlog for {{Year}} (Optional):** Potential initiatives.\n  5.  **Customer Feedback / Market Trends for {{Year}} (Optional):** External context.\n\n  Current Year (being reviewed): {{Year}}. Upcoming Year (being planned): {{Year + 1}}.\n\n  **Task:**\n  1.  **Analyze Inputs:** Review all documents. Focus on synthesizing themes from the four QBRs for the "Year in Review". An initial summarization of QBRs might be needed if context is too large: "produce a ''Year Summary'' from QBRs (e.g., list the top 5 accomplishments of the year and top 5 challenges, gleaned from each quarter)".\n  2.  **Draft "Year in Review ({{Year}})":**\n      * Synthesize "Achievements" (top 5) and "Challenges" (top 5) from the QBRs.\n      * Identify "Trend Analysis" based on patterns in QBRs or specific market trend documents.\n  3.  **Draft "Vision Refresh (if any)":**\n      * Based on the year''s performance and the "North Star Charter", suggest if any aspect of the vision or strategic pillars might need discussion or reaffirmation. This should be a suggestion for human discussion.\n  4.  **Draft "Strategic Objectives for {{Year + 1}}":**\n      * Propose 2-3 major strategic objectives for the next year. These should align with "North Star Charter" and address insights from "Year in Review", "Idea Backlog", or market trends. For each, explain its importance and list potential "Key Initiatives".\n  5.  **Draft "Key Metrics Targets":**\n      * For the proposed objectives, suggest 1-2 high-level key metrics and placeholder targets (e.g., "Increase X by Y% (target TBD)").\n  6.  **Draft "Budget & Resource Summary":**\n      * Suggest high-level resource implications if evident from objectives (e.g., "Objective A may require new hires in Z"). Mark as "(to be confirmed)".\n  7.  **Draft "Risks & Dependencies":**\n      * List major risks based on challenges from {{Year}} or new initiatives.\n  8.  **Draft "Action Plan & Timeline (Quarterly Focus)":**\n      * For {{Year + 1}}, suggest a high-level focus for each quarter, distributing the proposed objectives/initiatives.\n  9.  **Structure Output:** Format according to the HORIZON_Annual_Strategic_Plan template.\n\n  **Output Format (Strictly Adhere):**\n  ```markdown\n  # Annual Strategic Plan - {{Year + 1}}\n\n  **Executive Summary:**\n  _<One-paragraph summary of the proposed strategic direction for {{Year + 1}} based on inputs.>_\n\n  **Year in Review ({{Year}}):**\n  - **Achievements:** <Bullet list of top 5 significant accomplishments of {{Year}} from QBRs.>\n  - **Challenges:** <Bullet list of top 5 major challenges of {{Year}} from QBRs.>\n  - **Trend Analysis:** <Key trends observed in {{Year}} from QBRs/market docs.>\n\n  **Vision Refresh (if any):**\n  _<Suggest if vision/pillars from North Star Charter need review based on {{Year}}''s performance, or reaffirm existing vision. Frame as a point for discussion.>_\n\n  **Strategic Objectives for {{Year + 1}}:**\n  1.  **Objective A:** <Proposed major objective for {{Year + 1}}>\n      - *Description:* <Explanation and importance based on inputs.>\n      - *Key Initiatives:* <Potential projects from inputs.>\n  2.  **Objective B:** <Proposed major objective for {{Year + 1}}>\n      - *Description:* ...\n      - *Key Initiatives:* ...\n  *(2-3 objectives)*\n\n  **Key Metrics Targets:**\n  - <Metric 1 for Objective A: Target (e.g., "Increase X by Y% (target TBD)")>\n  - <Metric 2 for Objective B: Target ...>\n\n  **Budget & Resource Summary:**\n  - <High-level resource implications, e.g., "Potential need for X resources (to be confirmed).">\n\n  **Risks & Dependencies:**\n  - <Risk 1 based on inputs>\n  - <Risk 2 based on inputs>\n\n  **Action Plan & Timeline:**\n  - Q1 {{Year + 1}}: <Focus/major deliverables for Q1>\n  - Q2 {{Year + 1}}: <Focus/major deliverables for Q2>\n  - Q3 {{Year + 1}}: <Focus/major deliverables for Q3>\n  - Q4 {{Year + 1}}: <Focus/major deliverables for Q4>\n  ```\n\n  **Constraints:**\n  - Use only information from DocumentContext.\n  - Emphasize that output is a draft for human leadership refinement. "The AI should avoid making firm commitments that haven’t been decided". Mark uncertain financial/budget figures as "(to be confirmed)".\n  - Focus on summarizing QBRs effectively for the "Year in Review".\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_AnnualStrategicPlanningAssistant', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

-- Workflow: HORIZON_MeetingNotesSummarization
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_MeetingNotesSummarization\n# Description: Converts raw meeting inputs into a structured Meeting Notes document.\n# Ritual Relevance: Ad-hoc Meeting Notes Summarization\n# Template Origin: Outputs based on HORIZON_Meeting_Notes template structure.\n\ninputDocumentSelectors:\n  - "Raw_Meeting_Record*"\n  - "Meeting_Agenda*"\ninputDateSelector: null\noutputName: "Meeting_Notes_{{InputFileNames}}"\nprompt: |\n  **Role:** You are a Meeting Scribe AI. Your task is to process raw meeting records and generate structured Meeting Notes.\n  **Goal:** Convert the provided raw meeting input (transcript or notes) into a clean, summarized Meeting Notes document, following the HORIZON_Meeting_Notes template structure.\n  **Context:**\n  The DocumentContext contains concatenated text from:\n  1.  **Raw Meeting Record (e.g., "Raw_Meeting_Record_MeetingName_YYYY-MM-DD"):** The transcript or rough notes from the meeting. This is the primary source.\n  2.  **Meeting Agenda (Optional, e.g., "Meeting_Agenda_MeetingName_YYYY-MM-DD"):** If provided, use its structure (Agenda points) to organize the summary. If not provided, infer topics from the raw record.\n\n  Assume the meeting name and date can be inferred from `{{InputFileName}}` or are present in the raw record.\n\n  **Task:**\n  1.  **Analyze Inputs:** Review all documents. Prioritize the "Raw Meeting Record".\n  2.  **Identify Attendees:** List attendees if mentioned in the raw record or agenda.\n  3.  **Structure Agenda:** Use agenda from "Meeting_Agenda" if provided. Otherwise, list main topics discussed from "Raw Meeting Record".\n  4.  **Draft "Discussion Summary":**\n      * For each agenda point or identified topic, summarize the key discussion points and outcomes from the "Raw Meeting Record". Focus on decisions and conclusions, not verbatim dialogue.\n  5.  **Draft "Decisions Made":**\n      * Clearly list any decisions made, looking for phrases like "we decided", "agreed to", etc., in the "Raw Meeting Record". Include brief rationale if stated.\n  6.  **Draft "Action Items":**\n      * Extract action items. Look for phrases assigning tasks or responsibilities (e.g., "X will do Y by Z"). List action, owner, and due date if specified.\n  7.  **Structure Output:** Format according to the HORIZON_Meeting_Notes template.\n\n  **Output Format (Strictly Adhere - use HORIZON_Meeting_Notes structure):**\n  ```markdown\n  # Meeting Notes - <Inferred Meeting Name from {{InputFileName}} or raw record>\n  **Date & Time:** <Inferred Date & Time from {{InputFileName}} or raw record>\n  **Attendees:** <List attendees from inputs, or "Not specified">\n\n  **Agenda:**\n  1.  <Agenda point 1 from inputs, or inferred topic 1>\n  2.  <Agenda point 2 from inputs, or inferred topic 2>\n  3.  ...\n\n  **Discussion Summary:**\n  - *Agenda Item 1:* <Summary of discussion for item 1 from raw record.>\n  - *Agenda Item 2:* <Summary for item 2 from raw record...>\n  - *Additional Topics:* <Any other discussion points not on formal agenda, from raw record.>\n\n  **Decisions Made:**\n  - <Decision 1 from raw record (if any) and brief rationale/context>\n  - <Decision 2 from raw record ...>\n\n  **Action Items:**\n  - <Action Item 1 from raw record> – *Owner:* <Person from raw record> – *Due:* <Due date from raw record or ASAP>\n  - <Action Item 2 from raw record> – *Owner:* <Person from raw record> – *Due:* <...>\n  ```\n\n  **Constraints:**\n  - Use only information from DocumentContext.\n  - Summarize concisely. "Focus on summarizing, do not include trivial chit-chat or tangents.".\n  - If unsure about a detail (e.g., exact decision wording, owner), state "Summary based on notes, clarification may be needed" or provide best effort from text. Do not fabricate.\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_MeetingNotesSummarization', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

-- Workflow: HORIZON_AIPromptRefinement
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_AIPromptRefinement\n# Description: Suggests improvements for an existing workflow prompt.\n# Ritual Relevance: Prompt Workshop (Ad-hoc)\n# Template Origin: N/A - output is textual suggestions.\n\ninputDocumentSelectors:\n  - "Prompt_Analysis_Input*"\ninputDateSelector: null\noutputName: "Prompt_Refinement_Suggestions_for_{{InputFileNames}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  **Role:** You are a Prompt Engineer Assistant. Your task is to analyze an existing AI prompt and suggest improvements.\n  **Goal:** Based on the provided current prompt, examples of its bad output, and a description of the desired outcome, identify weaknesses in the current prompt and suggest specific revisions or additions to improve its performance.\n  **Context:**\n  The DocumentContext (from a file like "Prompt_Analysis_Input_*") contains:\n  1.  **Current Prompt Text:** The prompt that needs improvement.\n  2.  **Examples of Bad Output:** Instances where the current prompt failed.\n  3.  **Desired Outcome Description:** What the ideal output should look like.\n  4.  **Prompt Design Guidelines (Optional):** Best practices for reference.\n\n  **Task:**\n  1.  **Analyze Inputs:** Carefully review the current prompt, bad outputs, and desired outcomes.\n  2.  **Identify Weaknesses:** Pinpoint specific reasons why the current prompt might be leading to unsatisfactory results (e.g., lack of clarity, missing constraints, poor role priming, no few-shot example).\n  3.  **Suggest Improvements:** Propose concrete changes to the prompt. This could include:\n      * Rewording instructions for clarity.\n      * Adding or refining constraints.\n      * Suggesting a better role prompt.\n      * Advising the inclusion of a few-shot example (and what that might look like).\n      * Modifying the output structure instructions.\n  4.  **Provide Revised Prompt (Optional but Preferred):** If feasible, provide a revised version of the prompt incorporating your suggestions.\n\n  **Output Format:**\n  Structure your response with clear headings:\n  ```markdown\n  # Prompt Refinement Suggestions\n\n  ## Analysis of Current Prompt Weaknesses\n  - [Weakness 1 and explanation]\n  - [Weakness 2 and explanation]\n\n  ## Specific Recommendations for Improvement\n  - Recommendation 1: [e.g., "Clarify the instruction for X by changing Y to Z."]\n  - Recommendation 2: [e.g., "Add a constraint: ''Limit output to 3 bullet points.''"]\n  - Recommendation 3: [e.g., "Consider adding a few-shot example for the output format, like this: ..."]\n\n  ## (Optional) Proposed Revised Prompt Text:\n  \\<If you are providing a full revised prompt, include it here in a code block or as plain text.\\>\n  ```\n\n  **Constraints:**\n  - Suggestions must be actionable and specific.\n  - Base your analysis solely on the provided input document.\n  - If providing a revised prompt, ensure it adheres to general prompt engineering best practices suitable for a local LLM.\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_AIPromptRefinement', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

-- Workflow: HORIZON_KnowledgeArchiveSummarization
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_KnowledgeArchiveSummarization\n# Description: Condenses older documents into a shorter summary, preserving key knowledge.\n# Ritual Relevance: Knowledge Cleanup (Ad-hoc/Scheduled)\n# Template Origin: N/A - output is a new summary document.\n\ninputDocumentSelectors:\n  - "*"\ninputDateSelector: null\noutputName: "Archive_Summary_of_{{InputFileNames}}_{{Year}}-{{Month}}-{{Day}}" # Topic extraction might need user input or smarter placeholder\nprompt: |\n  **Role:** You are an Archivist Assistant. Your task is to summarize and condense a collection of older documents.\n  **Goal:** From the provided set of documents ({{InputFileNames}}), extract and synthesize the most critical long-term events, decisions, trends, and insights. Discard transient operational details and routine updates not relevant for future reference (e.g., 6-12+ months from now). If a "Condensation_Criteria" document is part of the input, adhere to its specified summary length or focus areas.\n  **Context:**\n  The DocumentContext contains concatenated text from multiple older documents selected by the user. It may also include a "Condensation_Criteria_*" document with specific instructions.\n\n  **Task:**\n  1.  **Analyze Inputs:** Review all provided documents. If a "Condensation_Criteria_*" document exists, prioritize its instructions for focus and length.\n  2.  **Identify Core Content for Archival:** From all other documents, extract points discussing:\n      * Major strategic events, decisions (and rationale if stated).\n      * Significant trends with long-term implications.\n      * Outcomes that directly impacted long-term goals or required strategic shifts.\n      * Unique learnings that changed fundamental approaches or understanding.\n  3.  **Synthesize and Condense:** Rewrite the extracted core content into an integrated summary. Use clear headings (e.g., Key Events, Major Decisions, Learnings). Use bullet points for clarity. Eliminate redundancy.\n  4.  **Adhere to Criteria (if provided):** If "Condensation_Criteria" specifies length (e.g., "one paragraph per week", "max 500 words"), try to meet it. If it specifies focus areas, prioritize those.\n  5.  **Structure Output:** Generate a clean Markdown summary.\n\n  **Output Format Suggestion (adapt based on content and criteria):**\n  ```markdown\n  # Archive Summary - Covering documents like: {{InputFileNames}}\n  *(Condensed on: {{Year}}-{{Month}}-{{Day}})*\n\n  ## Key Strategic Events & Decisions\n  - [Summary of major event/decision 1 from the period, synthesized from inputs]\n  - [...]\n\n  ## Significant Long-Term Trends Identified\n  - [Summary of major trend 1 observed during the period, synthesized from inputs]\n  - [...]\n\n  ## Major Challenges/Outcomes Impacting Strategy\n  - [Summary of significant challenge or outcome, synthesized from inputs]\n  - [...]\n\n  ## Key Learnings with Enduring Value\n  - [A significant learning, synthesized from inputs]\n  - [...]\n  ```\n\n  **Constraints:**\n  - Use only information from DocumentContext.\n  - Primary goal is concise preservation of strategically important information. "Preserve any numerical results or decisions mentioned, but you can omit day-to-day minor details.".\n  - If multiple documents cover the same event, synthesize it once.\n  - If `Condensation_Criteria*` is provided, its instructions take precedence for focus/length.\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_KnowledgeArchiveSummarization', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

--
-- End of HORIZON Protocol Workflows
--

--
-- Inserting Additional HORIZON Protocol Workflows
--

-- Workflow: HORIZON_NorthStarAlignmentCheck
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_NorthStarAlignmentCheck\n# Description: LLM checks big decisions regarding strategic fit\n# Ritual Relevance: Use on a draft Decision document\n# Template Origin: N/A\n\ninputDocumentSelectors:\n  - "Decision_Proposal*"\n  - "North_Star_Charter*"\n  - "Quarterly_OKRs*"\n  - "Decision_Log_Retrospective*"\noutputName: "Alignment_Report_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  **Role:** You are a Strategic Alignment Analyst.\n  **Goal:** Produce an Alignment Report that scores the proposal’s fit to\n  the North-Star Charter pillars and active Quarterly OKRs.\n\n  **Instructions:**\n  1. Read the Decision Proposal section <Proposal>.\n  2. Compare against Charter pillars <Charter> and KRs <OKRs>.\n  3. For each pillar & KR, state “Supports / Neutral / Conflicts” with 1-line reason.\n  4. Conclude with one of:\n       * ✅ Proceed\n       * ✏️  Refine (list what to address)\n       * ❌ Reject (list critical conflicts)\n  5. Use the template mentioned below in section Output Format.\n\n  **Output Format:**\n  Structure your response with clear headings:\n  ```markdown\n  # Alignment Report – *{{DecisionTitle}}* ({{Date}})\n\n  ## 1 Strategic Fit Matrix\n\n  ### 1.1 North-Star Charter Pillars\n  | Pillar | Fit Rating* | Rationale |\n  |--------|-------------|-----------|\n  | Pillar 1 | Supports / Neutral / Conflicts | <one-line reason> |\n  | Pillar 2 | … | … |\n  | Pillar 3 | … | … |\n\n  ### 1.2 Quarterly Key Results\n  | Objective / KR | Fit Rating* | Rationale |\n  |----------------|-------------|-----------|\n  | O1 / KR 1.1 | Supports / Neutral / Conflicts | <one-line reason> |\n  | O2 / KR 2.3 | … | … |\n\n  > *Rating scale:*\n  > **Supports** – strong positive contribution\n  > **Neutral** – little or no impact\n  > **Conflicts** – likely to hinder or contradict\n\n  ---\n\n  ## 2 Overall Alignment Score\n  **{{Score / 10}}**\n  _(0 = no strategic fit, 10 = perfect fit)_\n\n  ---\n\n  ## 3 Recommendation\n  | Decision | Reasoning |\n  |----------|-----------|\n  | ✅ Proceed / ✏️ Refine / ❌ Reject | <concise justification> |\n\n  ---\n\n  ## 4 Risks & Dependencies\n  - **Risk 1:** <description> → *Mitigation:* <action / owner>\n  - **Risk 2:** …\n\n  ---\n\n  ## 5 Next-Step Actions\n  1. <Action 1 – owner – due date>\n  2. <Action 2 – owner – due date>\n\n  ---\n\n  ### Template Guidelines\n  - **Brevity:** keep total length ≤ 2 pages.\n  - **Objectivity:** base ratings only on the provided documents; state “Unknown” when data is missing.\n  - **Actionability:** every “Refine” or “Reject” outcome must list concrete follow-ups.\n  ```\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_NorthStarAlignmentCheck', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

-- Workflow: HORIZON_AdaptiveMeetingAgenda
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_AdaptiveMeetingAgenda\n# Description: LLM creates an agenda from open topics from logs and blockers\n# Ritual Relevance: 5 min before event\n# Template Origin: HORIZON_Meeting_Agenda\n\ninputDocumentSelectors:\n  - "Daily_Log*"\n  - "Task_Backlog*"\n  - "Decision_Log*"\n  - "Meeting_Request*"\noutputName: "Meeting_Agenda_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  **Role:** You are a Meeting Navigator AI.\n  **Goal:** Draft a crisp agenda that will let the team resolve blockers and\n  make key decisions within 30 minutes.\n\n  **Steps**\n  1. Pull max 3 critical blockers from Daily Log.\n  2. Pull top 3 high-priority tasks still unresolved.\n  3. Include any Decision Log entries without outcomes.\n  4. Order by (Blocker → Decision → Task). For each, suggest owner & mins.\n  5. Output using the template mentioned below in section Output Format.\n\n  **Output Format:**\n  Structure your response with clear headings:\n  ```markdown\n  # Meeting Agenda - {{Meeting Name/Purpose}}\n\n  **Date & Time:** <YYYY-MM-DD> <HH:MM>\n  **Location/Call Link:** <Physical location or virtual meeting URL>\n  **Attendees (Optional Invitees List):** <List of expected attendees>\n\n  **Meeting Goal(s):**\n  -   <Primary objective 1 of the meeting>\n  -   <Primary objective 2 of the meeting, if any>\n\n  ---\n\n  **Agenda Items:**\n\n  1.  **Topic 1:** <Brief description of the first agenda item>\n      * *Presenter/Lead (Optional):* <Name>\n      * *Time Allotted (Optional):* <e.g., 15 mins>\n      * *Desired Outcome:* <What needs to be achieved for this item>\n\n  2.  **Topic 2:** <Brief description of the second agenda item>\n      * *Presenter/Lead (Optional):* <Name>\n      * *Time Allotted (Optional):* <e.g., 20 mins>\n      * *Desired Outcome:* <...>\n\n  3.  **(Add more agenda items as necessary)**\n\n  ---\n\n  **Pre-Reading/Preparation (Optional):**\n  -   <Link to document 1> - <Brief description of what to review>\n  -   <Task to complete before meeting>\n\n  **Post-Meeting Next Steps (Placeholder):**\n  -   <e.g., Decisions to be logged, Actions to be assigned>\n  ```\n\n  Use bullet lists, be concise, no redundant context.\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_AdaptiveMeetingAgenda', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

-- Workflow: HORIZON_DecisionLogRetro
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_DecisionLogRetro\n# Description: Monthly Lessons-Learned Synthesis\n# Ritual Relevance: On the first work-day each month\n# Template Origin: N/A\n\ninputDocumentSelectors:\n  - "Decision_Log*"\n  - "Metrics_KPI_Update*"\noutputName: "Decision_Log_Retrospective_{{Year}}-{{Month}}"\nprompt: |\n  **Role:** You are a Decision Retrospective Analyst.\n  **Window:** {{Year}}-{{Month}}-01 to end-of-month.\n\n  **Tasks**\n  A. Load decisions in that window.\n  B. Assess outcome vs. stated intent. Rate ✅ / ⚠️ / ❌.\n  C. Populate the template mentioned below in section Output Format.\n  D. End with 2-3 actionable recommendations.\n\n  **Output Format:**\n  Structure your response with clear headings:\n  ```markdown\n  # Decision_Log_Retrospective_{{Year}}-{{Month}}\n\n  ## 1. Synopsis of Reviewed Period\n  _<e.g., “2025-04-01 to 2025-04-30 – total 12 decisions logged”>_\n\n  ## 2. Outcome Scorecard\n  | Decision | Intended Outcome | Actual Result | Status | Notes |\n  |----------|------------------|---------------|--------|-------|\n  | *Adopt HORIZON Protocol* | Improve on-time delivery | +18 % on-time, 0 missed deadlines | ✅  Successful | — |\n  | *Pivot to SMB Market* | +20 % leads in SMB segment | +22 % leads | ✅ | Larger TAM than forecast |\n\n  *(Add rows as needed)*\n\n  ## 3. Patterns & Insights\n  - **High-confidence calls:** <bullet 1>\n  - **Missed assumptions:** <bullet 2>\n\n  ## 4. Recommendations\n  1. <Recommendation 1>\n  2. <Recommendation 2>\n\n  ---\n\n  *Guidelines:* Limit to 1-2 pages; focus on transferable insights, not recounting every detail. Cite Decision Log entries via dates for traceability.\n  ```\n\n  **Constraints**\n  * Use only data from Decision Log and KPI updates provided.\n  * If metrics absent, state “No KPI data”.\n  * Be concise; aim <1000 words.\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_DecisionLogRetro', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

-- Workflow: HORIZON_OKRPrioritisation
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_OKRPrioritisation\n# Description: Impact Scoring of Tasks\n# Ritual Relevance: Run each Monday morning\n# Template Origin: N/A\n\ninputDocumentSelectors:\n  - "Quarterly_OKRs*"\n  - "Task_Backlog*"\n  - "Weekly_Plan*"\noutputName: "OKR_Prioritisation_Summary_{{Year}}-W{{CurrentWeekNumber}}"\nprompt: |\n  **Role:** You are an OKR Impact Analyst AI.\n  **Goal:** Score backlog tasks for their contribution to current OKRs and\n  recommend which to accelerate, keep, or deprioritise this week.\n\n  **Steps**\n  1. For each task, identify the most relevant Objective & KR.\n  2. Assign Importance (High/Med/Low) from the KR text.\n  3. Infer Effort (High/Med/Low) from task size tag or description length.\n  4. Calculate Impact Score = (Importance * Leverage) / Effort\n     (H=3 | M=2 | L=1). Round to one decimal.\n  5. Fill the template mentioned below in section Output Format:\n     * Table of the 25 highest-scoring tasks\n     * Insight bullets (e.g., gaps, over-commitment signals)\n     * Suggested next steps.\n\n  **Output Format:**\n  Structure your response with clear headings:\n  ```markdown\n  # OKR Prioritisation Summary – Week {{CurrentWeekNumber}} {{Year}}\n\n  ## Top-Impact Tasks\n  | Rank | Task ID & Title | Owner | Linked Objective / KR | Impact Score | Action |\n  |------|-----------------|-------|-----------------------|--------------|--------|\n  | 1 | <ID – Title> | <Name> | O1 / KR1.2 | 8.5 | Accelerate |\n  | 2 | … | … | … | … | Keep |\n  | … | … | … | … | … | … |\n\n  *Scoring rubric:* High = 3, Medium = 2, Low = 1 for Importance, Leverage, Effort\n  Impact Score = (Importance × Leverage) / Effort\n\n  ## Insights\n  - **Coverage gaps:** _<e.g., “Objective 3 has no high-impact tasks in flight.”>_\n  - **Over-commitment alerts:** _<e.g., “Owner X holds 40 % of top tasks.”>_\n  - **Quick wins (<1 pt effort) worth acceleration:** _<list>_\n\n  ## Recommendations for Weekly Plan\n  1. _<e.g., “Move Task #123 to this week’s Top Priorities.”>_\n  2. _<e.g., “Deprioritise Task #98; low impact vs. KR progress.”>_\n\n  ---\n\n  *Guidelines:* Limit table to 25 rows. Keep Insights ≤5 bullets and Recommendations ≤3 actions to preserve clarity.\n  ```\n\n  **Constraints**\n  * Do NOT invent Objectives/KRs or tasks not in inputs.\n  * If a task has no clear OKR link, mark Importance = 1.\n  * Keep narrative sections <300 words total.\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_OKRPrioritisation', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

-- Workflow: HORIZON_RiskHeatmap
DO $$
DECLARE
    workflow_item_id uuid := public.uuid_generate_v4();
    workflow_version_id uuid := public.uuid_generate_v4();
    admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
    workflow_content text := E'# Workflow Name: HORIZON_RiskHeatmap\n# Description: LLM clusters Blocker and  proposes countermeasures\n# Ritual Relevance: Run each Friday afternoon before Weekly Review\n# Template Origin: N/A\n\ninputDocumentSelectors:\n  - "Daily_Log*"\n  - "Task_Backlog*"\n  - "Metrics_KPI_Update*"\noutputName: "Risk_Heatmap_Report_{{Year}}-W{{CurrentWeekNumber}}"\nprompt: |\n  **Role:** You are a Risk Analyst AI.\n  **Goal:** Produce a weekly heatmap of operational risks plus mitigation\n  advice that helps the team act before issues escalate.\n\n  **Method**\n  1. Collect blockers/risks from Daily Logs + flagged tasks.\n  2. Cluster into themes (≤7) with concise names.\n  3. Determine Likelihood (High > 3 mentions, Med = 2, Low = 1) and\n     Impact (High = could stop objective, Med = delays, Low = minor).\n  4. Assign RAG colour.\n  5. Recommend mitigations for Red & Amber themes.\n\n  **Output Format:**\n  Structure your response with clear headings:\n  ```markdown\n  # Weekly Risk Heatmap – Week {{CurrentWeekNumber}} {{Year}}\n\n  | Risk Theme | Likelihood | Impact | RAG Rating | Proposed Mitigation & Owner |\n  |------------|------------|--------|------------|-----------------------------|\n  | <Theme A> | High | High | 🔴 Red | <Mitigation – Owner> |\n  | <Theme B> | Medium | High | 🟠 Amber | <Mitigation – Owner> |\n  | <Theme C> | Low | Medium | 🟢 Green | <Monitor only> |\n  | … | … | … | … | … |\n\n  **Key Observations**\n  - Theme **<A>** poses the highest combined risk; immediate action required.\n  - Theme **<B>** likely tied to KPI dip in <Metric>; monitor after fix.\n  - No critical new risks emerged beyond known areas.\n\n  **Next-Step Actions (Top 3)**\n  1. _<e.g., “Assign two devs to unblock Deployment Pipeline issues (Theme A).”>_\n  2. _<e.g., “Schedule customer call to clarify Scope creep (Theme B).”>_\n  3. _<e.g., “Add automated alert for <Metric> deviation > 5 %.”>_\n\n  ---\n\n  *Guidelines:* Use concise language; RAG emojis improve skim-readability. Mitigation owners must be real team members or “Unassigned”.\n  ```\n\n  **Constraints:**\n  - No speculative risks; base only on supplied data.\n  - Keep full report under 6 k tokens (~800 words).\n\n  Now follows the DocumentContext:\n  {{DocumentContext}}';
BEGIN
    INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
    VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'HORIZON_RiskHeatmap', true, workflow_version_id, NOW(), NOW());

    INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
    VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
END $$;

--
-- End of Additional HORIZON Protocol Workflows
--

-- --
-- -- Inserting A_Lean_Loop_ Templates
-- --

-- -- Template: A_Lean_Loop_North_Star_Charter
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'A_Lean_Loop_North_Star_Charter', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# North-Star Charter\n<-- 1-page evergreen mission & 3-year objectives -->\n\n## Mission\n-\n\n## 3-Year Objectives & KPIs\n| Objective | KPI | Target by <YYYY-MM> |\n|-----------|-----|---------------------|\n|\n\n## Success Metrics Definition\n- **Value Created:**\n- **Quality Bar:**\n- **Velocity Target:**\n\n## Last Charter Review\n<YYYY-MM-DD> — summary of changes',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: A_Lean_Loop_Working_Backlog
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'A_Lean_Loop_Working_Backlog', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Working Backlog  (rolling 12 weeks)\n<-- Ordered so top = next work item -->\n\n| Rank | Deliverable | Owner | Due | Status | Notes |\n|------|-------------|-------|-----|--------|-------|\n| 1 |  |  |  | ☐ To Do |  |',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: A_Lean_Loop_Decision_Log
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'A_Lean_Loop_Decision_Log', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Decision Log\n<-- When a consequential choice is made, add one row -->\n\n| When (UTC) | What we decided | Why | Next Action | Link(s) |\n|------------|-----------------|-----|-------------|---------|\n|            |                 |     |             |         |',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: A_Lean_Loop_Prompt_Packet
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'A_Lean_Loop_Prompt_Packet', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Prompt Packet {{CurrentDate}}\n<-- Filled daily by the Coordinator -->\n\n## Goal of the Day\n-\n\n## New Facts / Resources\n-\n\n## Questions Requiring Reasoning\n1.\n\n## Desired Output Format\nMarkdown bullets, ≤300 tokens\n\n## Capacity / Constraints (optional)\n| Person | Available hrs today | Key skills / notes |\n|--------|--------------------|--------------------|',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: A_Lean_Loop_Daily_Digest
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'A_Lean_Loop_Daily_Digest', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Daily Digest\n\n<-- Coordinator pastes the 150-token summary produced by the Digest Compressor.\nDelete entries older than 14 days to keep the context small. -->\n\n## {{CurrentDate}}\n…',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: A_Lean_Loop_Prompt_Library
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'A_Lean_Loop_Prompt_Library', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Prompt Library\n<-- Keep only prompts that scored ≥4/5 usefulness -->\n\n| Tag | Prompt Snippet | Use Case | Last Success Date |\n|-----|---------------|----------|-------------------|',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: A_Lean_Loop_Resource_Vault
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'A_Lean_Loop_Resource_Vault', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Resource Vault\n<-- Curated links, datasets, style guides, credentials, etc. -->\n\n## Docs & Specs\n-\n\n## Data Sources\n-\n\n## Style Guides / Reference\n-',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: A_Lean_Loop_Capacity_Snapshot
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'A_Lean_Loop_Capacity_Snapshot', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Capacity Snapshot {{CurrentDate}}\n\n| Person | Available hrs today | Key skills / notes |\n|--------|--------------------|--------------------|',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: A_Lean_Loop_Metrics_Dashboard
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'A_Lean_Loop_Metrics_Dashboard', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Lean-Loop KPI Dashboard\n\n| Week | Human minutes / deliverable | Accuracy (sample 5-pt) | NASA-TLX | Prompt reuse % |\n|------|----------------------------|------------------------|----------|----------------|\n|      |                            |                        |          |                |',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: A_Lean_Loop_Lean_Loop_Guide
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'A_Lean_Loop_Lean_Loop_Guide', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Lean-Loop Guide (Quick Reference)\n\n## Daily at a Glance\n1. Coordinator fills Prompt Packet (≤5 min).\n2. Run **Generate LLM Draft** workflow.\n3. Contributors comment 👍/👎 (async).\n4. Run **Incorporate Comments** workflow.\n5. Coordinator compresses into Daily Digest.\n\n## Weekly at a Glance\n- Monday Kick-off (15 min sync).\n- Friday Retro (LLM-led, 10 min async).\n\n## Artefact Locations\n- Charter: `North_Star_Charter`\n- Backlog: `Working_Backlog_Current`\n- Decision Log: `Decision_Log`\n- Digest: `Daily_Digest`\n- Prompt Library: `Prompt_Library`',
--     1, admin_team_id, NOW());
-- END $$;

-- --
-- -- End of A_Lean_Loop_ Templates
-- --

-- --
-- -- Inserting A_Lean_Loop_ Workflows
-- --

-- -- Workflow: A_Lean_Loop_Generate_LLM_Draft
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'inputDocumentSelectors:\n  - "Prompt_Packet*"\n  - "North_Star_Charter*"\n  - "Working_Backlog_Current*"\n  - "Daily_Digest*"\n  - "Decision_Log*"\ninputDateSelector: null\noutputName: "LLM_Draft_{{CurrentDate}}"\nprompt: |\n  You are the **LLM Facilitator** for our Lean-Loop team.\n\n  ### Context\n  <<<{{DocumentContext}}>>>\n\n  ### Goals\n  • Answer all items under **Questions Requiring Reasoning**.\n  • Propose **Next-Best-Steps** ranked by ROI per human-hour.\n\n  ### Expected Sections\n  1. **Draft** – coherent answer.\n  2. **Risks** – bullet list of potential pitfalls.\n  3. **Clarifying Questions** – what you still need.\n  4. **👍-Points / 👎-Points** – self-critique.\n  5. **Next-Best-Steps** – top 3 actions with 1-line rationales.\n\n  ### Output Format\n  Markdown only, ≤600 tokens.\n  Prefix any uncertain statement with `(LOW-CONF)`.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'A_Lean_Loop_Generate_LLM_Draft', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: A_Lean_Loop_Incorporate_Comments
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'inputDocumentSelectors:\n  - "LLM_Draft*"\n  - "Prompt_Packet*"\ninputDateSelector: null\noutputName: "LLM_Refined_{{CurrentDate}}"\nprompt: |\n  You are the **Reviser** responsible for integrating human feedback.\n\n  ### Context\n  <<<{{DocumentContext}}>>>\n\n  ### Instructions\n  1. Accept all inline 👍 comments and apply suggested edits.\n  2. Ignore 👎 sections unless replacement text is provided.\n  3. Compress the **Draft** section by ≈20 % while preserving meaning and bullet structure.\n  4. Retain **Risks**, **Clarifying Questions**, and **Next-Best-Steps**.\n\n  ### Output Format\n  Markdown, ≤480 tokens.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'A_Lean_Loop_Incorporate_Comments', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: A_Lean_Loop_Digest_Compressor
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'inputDocumentSelectors:\n  - "LLM_Refined*"\noutputName: "Digest_{{CurrentDate}}"\nprompt: |\n  You are the **Daily Digest Writer**.\n\n  ### Context\n  <<<{{DocumentContext}}>>>\n\n  ### Task\n  Summarise the key insights, decisions and action items in **≤150 tokens**.\n\n  ### Output Format\n  Exactly three bullets followed by a **Next Action** line.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'A_Lean_Loop_Digest_Compressor', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: A_Lean_Loop_Weekly_Kickoff
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'inputDocumentSelectors:\n  - "Working_Backlog*"\n  - "North_Star_Charter*"\n  - "Daily_Digest*"\ninputDateSelector: "olderThanDays 7"\noutputName: "Backlog_Reprioritization_{{CurrentDate}}"\nprompt: |\n  You are the **Planning Analyst** preparing today’s Kick-off.\n\n  ### Context\n  <<<{{DocumentContext}}>>>\n\n  ### Objectives\n  • Re-rank the backlog for the coming week.\n  • Estimate human vs LLM effort.\n  • Surface scope-creep risks.\n\n  ### Output Format\n  Sections – **Proposed Backlog** (ranked table), **Rationale**, **Risks**.\n  Limit to ≤550 tokens.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'A_Lean_Loop_Weekly_Kickoff', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: A_Lean_Loop_Retro_Analyzer
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'inputDocumentSelectors:\n  - "Decision_Log*"\n  - "LLM_Refined*"\ninputDateSelector: "olderThanDays 7"\noutputName: "Retro_Insights_Week_{{Year}}-W{{WeekNumber}}"\nprompt: |\n  You are the **Process Analyst**.\n\n  ### Context\n  <<<{{DocumentContext}}>>>\n\n  ### Tasks\n  1. Extract recurring **success** and **failure** patterns.\n  2. Recommend the two highest-ROI **process tweaks** (≤50 words each).\n  3. Cite concrete examples (link-style).\n\n  ### Output Format\n  Sections – **Patterns** / **Recommendations**.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'A_Lean_Loop_Retro_Analyzer', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: A_Lean_Loop_Metrics_Snapshot
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'inputDocumentSelectors:\n  - "Decision_Log*"\n  - "Daily_Digest*"\n  - "LLM_Refined*"\ninputDateSelector: "olderThanDays 30"\noutputName: "Metrics_Snapshot_{{Year}}-{{Month}}"\nprompt: |\n  You are the **Metrics Auditor**.\n\n  ### Context\n  <<<{{DocumentContext}}>>>\n\n  ### Tasks\n  • Compute: Human-minutes per deliverable, Accuracy (sample 10), NASA-TLX average, Prompt reuse %.\n  • Provide one-paragraph commentary.\n\n  ### Output Format\n  Markdown table of the four metrics followed by commentary. ≤400 tokens.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'A_Lean_Loop_Metrics_Snapshot', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: A_Lean_Loop_Context_Condensor
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'inputDocumentSelectors:\n  - "Daily_Digest*"\n  - "Decision_Log*"\ninputDateSelector: "olderThanDays 30"\noutputName: "Condensed_Context_{{Year}}-{{Month}}"\nprompt: |\n  You are the **Context Librarian**.\n\n  ### Context\n  <<<{{DocumentContext}}>>>\n\n  ### Goal\n  Produce a concise summary ≤1 500 tokens that preserves:\n  • Key decisions, reasons, outcomes.\n  • Enduring lessons learned.\n  • Links to artefacts still required.\n\n  ### Output Format\n  Sections – **Decisions**, **Lessons Learned**, **Archived Links**.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'A_Lean_Loop_Context_Condensor', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: A_Lean_Loop_Quarterly_Strategy_Review
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'inputDocumentSelectors:\n  - "North_Star_Charter*"\n  - "Metrics_Snapshot*"\n  - "Working_Backlog*"\n  - "Condensed_Context*"\ninputDateSelector: "olderThanDays 90"\noutputName: "Strategy_Review_{{Year}}-Q{{Quarter}}"\nprompt: |\n  You are the **Strategy Review Facilitator**.\n\n  ### Context\n  <<<{{DocumentContext}}>>>\n\n  ### Tasks\n  1. Evaluate KPI trajectory vs 3-year objectives.\n  2. Identify ≤3 strategic gaps or opportunities.\n  3. Draft updated **OKRs** for the next quarter.\n  4. Suggest backlog deletions or de-prioritisations.\n\n  ### Output Format\n  – **Executive Summary** (≤120 words)\n  – **Proposed OKRs** (table)\n  – **Backlog Changes** (bullets)';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'A_Lean_Loop_Quarterly_Strategy_Review', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- --
-- -- End of A_Lean_Loop_ Workflows
-- --

-- --
-- -- Inserting Phase 1 Templates
-- --

-- -- Template: Daily Quick Capture
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 1 Daily Quick Capture', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Daily Context Curation - [Date]\n\n## Participants\n- [List of team members present]\n\n## New Context Elements\n- [Team Member 1]: [Context element]\n- [Team Member 2]: [Context element]\n- [Team Member 3]: [Context element]\n\n## Decisions\n- Accept/Reject: [Context element] - [Rationale]\n- Accept with modification: [Context element] → [Modified version]\n\n## Action Items\n- [ ] [Action description] (@owner) (due: [date])\n- [ ] [Action description] (@owner) (due: [date])\n\n## Notes\n[Any additional notes or observations]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Weekly Structured Review
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 1 Weekly Structured Review', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Weekly Context Curation - [Date]\n\n## Participants\n- [List of team members present]\n\n## Context Health Assessment\n- Total knowledge items: [number]\n- New items this week: [number]\n- Accessed items this week: [number]\n- Coverage areas: [list key areas]\n- Identified gaps: [list gaps]\n\n## Priority Improvement Areas\n1. [Area 1] - [Specific improvements needed]\n2. [Area 2] - [Specific improvements needed]\n3. [Area 3] - [Specific improvements needed]\n\n## Action Items\n- [ ] [Action description] (@owner) (due: [date])\n- [ ] [Action description] (@owner) (due: [date])\n\n## Discussion Summary\n[Summary of key discussion points]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Prompt Workshop Preparation
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 1 Prompt Workshop Preparation', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Prompt Workshop Preparation - [Date]\n\n## Target Workflow\n[Description of workflow needing prompt improvement]\n\n## Current Prompt\n```\n[Exact text of current prompt]\n```\n\n## Current Limitations\n- [Limitation 1]\n- [Limitation 2]\n- [Limitation 3]\n\n## Example Outputs\n### Successful Example\n[Example of successful output]\n\n### Unsuccessful Example\n[Example of problematic output]\n\n## Desired Improvements\n- [Improvement 1]\n- [Improvement 2]\n- [Improvement 3]\n\n## References\n- [Link to relevant context]\n- [Link to related prompts]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Prompt Documentation
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 1 Prompt Documentation', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Prompt: [Name]\n\n## Version\n[Version number] - [Date]\n\n## Purpose\n[Clear description of what this prompt is designed to accomplish]\n\n## Use Cases\n- [Use case 1]\n- [Use case 2]\n- [Use case 3]\n\n## Prompt Text\n```\n[Full prompt text]\n```\n\n## Input Requirements\n- [Requirement 1]\n- [Requirement 2]\n\n## Expected Output\n[Description of expected output format and content]\n\n## Example Input/Output\n### Input\n[Example input]\n\n### Output\n[Example output]\n\n## Performance Notes\n- Success rate: [percentage]\n- Common issues: [list]\n- Best practices: [list]\n\n## Changelog\n- [Version] ([Date]): [Changes]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Meeting Notes
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 1 Meeting Notes', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# [Meeting Type] - [Date]\n\n## Participants\n- [List of attendees]\n\n## Agenda\n1. [Agenda item 1]\n2. [Agenda item 2]\n3. [Agenda item 3]\n\n## Discussion\n### [Agenda item 1]\n[Raw notes]\n#decision [Any decisions made]\n#action [Any actions identified]\n\n### [Agenda item 2]\n[Raw notes]\n#decision [Any decisions made]\n#action [Any actions identified]\n\n### [Agenda item 3]\n[Raw notes]\n#decision [Any decisions made]\n#action [Any actions identified]\n\n## Next Steps\n- [Next step 1]\n- [Next step 2]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: AI-Generated Summary
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 1 AI-Generated Summary', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Summary: [Meeting Type] - [Date]\n\n## Overview\n[Brief 1-2 sentence overview of the meeting purpose and outcome]\n\n## Key Decisions\n- [Decision 1 with context]\n- [Decision 2 with context]\n- [Decision 3 with context]\n\n## Action Items\n- [ ] [Action 1] (@owner) (due: [date])\n- [ ] [Action 2] (@owner) (due: [date])\n- [ ] [Action 3] (@owner) (due: [date])\n\n## Discussion Summary\n### [Topic 1]\n[Concise summary of discussion, key points, and context]\n\n### [Topic 2]\n[Concise summary of discussion, key points, and context]\n\n## Related Context\n- [Link to related knowledge item 1]\n- [Link to related knowledge item 2]\n\n## Follow-up Scheduled\n[Date and time of any follow-up meetings]',
--     1, admin_team_id, NOW());
-- END $$;

-- --
-- -- End of Phase 1 Templates
-- --

-- --
-- -- Inserting Phase 1 Workflows
-- --

-- -- Workflow: SummarizeTextWorkflow
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: SummarizeTextWorkflow\n# Description: Summarizes the content of a single input TIP document.\n\ninputDocumentSelectors:\n  - "*" # Allows user to select any one document visible to them at runtime.\ninputDateSelector: null # No specific date filter by default for this generic workflow.\noutputName: "Summary_of_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}.md"\nprompt: |\n  Please provide a concise summary of the following document:\n\n  DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```\n\n  Focus on the key points, main arguments, and any conclusions presented in the document.\n  The summary should be easy to understand and capture the essence of the original text.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 1 SummarizeTextWorkflow', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: GenerateMeetingSummaryWorkflow
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: GenerateMeetingSummaryWorkflow\n# Description: Generates a structured meeting summary from a meeting notes document.\n\ninputDocumentSelectors:\n  - "MeetingNotes*" # Designed for documents like MeetingNotes_ProjectAlpha_YYYY-MM-DD.md\n  - "Meeting_Notes*"\n  - "*MeetingNotes*"\ninputDateSelector: null # User will typically select a recent meeting notes document.\noutputName: "MeetingSummary_from_{{InputFileName}}_AI-Generated_{{Year}}-{{Month}}-{{Day}}.md"\nprompt: |\n  You are an AI assistant tasked with creating a structured summary from the provided meeting notes.\n\n  MEETING NOTES DOCUMENT:\n  ```\n  {{DocumentContext}}\n  ```\n\n  Please carefully read the meeting notes and generate a summary that includes the following sections:\n  1.  **Overview:** A brief 1-2 sentence overview of the meeting''s purpose and main outcome.\n  2.  **Key Decisions:** List all significant decisions made. Look for lines or sections marked with ''#decision''.\n  3.  **Action Items:** List all action items identified. Look for lines or sections marked with ''#action''. Try to identify the owner and due date if mentioned.\n  4.  **Discussion Summary:** For each main topic discussed, provide a concise summary of the key points.\n\n  Format the output clearly. For example:\n\n  # Summary: [Extract Meeting Name from InputFileName if possible] - {{CurrentDate}}\n\n  ## Overview\n  [Generated overview here]\n\n  ## Key Decisions\n  - [Decision 1 text]\n  - [Decision 2 text]\n\n  ## Action Items\n  - [ ] [Action 1 text] (Owner: @name) (Due: YYYY-MM-DD)\n  - [ ] [Action 2 text] (Owner: @name)\n\n  ## Discussion Summary\n  ### [Topic 1 Name]\n  [Summary of discussion for topic 1]\n  ### [Topic 2 Name]\n  [Summary of discussion for topic 2]\n\n  Current Date for reference: {{CurrentDate}}\n  Source Document Name: {{InputFileName}}';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 1 GenerateMeetingSummaryWorkflow', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- --
-- -- End of Phase 1 Workflows
-- --

-- --
-- -- Inserting Phase 2 Templates
-- --

-- -- Template: Daily Quick Capture Template (Phase 2)
-- -- This seems to be a duplicate name from Phase 1 ("Daily Quick Capture").
-- -- To avoid conflicts if names must be unique per admin_team_id and type,
-- -- I will name this "Daily Quick Capture P2" in the database.
-- -- If the original "Daily Quick Capture" should be overwritten or this is an evolution,
-- -- the logic would need adjustment (e.g., UPDATE existing or handle versioning).
-- -- For now, inserting as a new distinct template with a modified name.
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 2 Daily Quick Capture', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Daily Context Curation - [Date]\n\n## Participants\n- [List of team members present]\n- AI Role: Knowledge Assistant\n\n## Context Updates\n- [Team Member 1]: [Context element]\n- [Team Member 2]: [Context element]\n- [Team Member 3]: [Context element]\n\n## AI-Extracted Elements\n- [Extracted element 1] → Classification: [Category] → Related to: [Linked items]\n- [Extracted element 2] → Classification: [Category] → Related to: [Linked items]\n- [Extracted element 3] → Classification: [Category] → Related to: [Linked items]\n\n## Team Verification\n- Accept/Modify/Reject: [Element 1] - [Adjustment if needed]\n- Accept/Modify/Reject: [Element 2] - [Adjustment if needed]\n- Accept/Modify/Reject: [Element 3] - [Adjustment if needed]\n\n## Auto-Generated Connections\n- [New element] connects to [Existing element] because [Relationship rationale]\n- [New element] connects to [Existing element] because [Relationship rationale]\n\n## Action Items\n- [ ] [Action description] (@owner) (due: [date])\n- [ ] [Action description] (@owner) (due: [date])\n\n## Notes\n[Any additional notes or observations]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Weekly Structured Curation Template (Phase 2)
-- -- Similar to "Weekly Structured Review" from Phase 1. Naming "Weekly Structured Curation P2".
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 2 Weekly Structured Curation', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Weekly Context Curation - [Date]\n\n## Participants\n- [List of team members present]\n- AI Role: Knowledge Architect\n\n## Context Health Dashboard\n- Total knowledge items: [number]\n- New items this week: [number]\n- Relationship density: [number] connections per item (target: >3)\n- Orphaned items: [number] items with <2 connections\n- Aging items (not updated in >30 days): [number]\n- Most active areas: [list top 3 areas]\n- Least active areas: [list bottom 3 areas]\n\n## Identified Gaps & Inconsistencies\n1. [Gap 1] - Priority: [High/Medium/Low] - [Context]\n2. [Gap 2] - Priority: [High/Medium/Low] - [Context]\n3. [Gap 3] - Priority: [High/Medium/Low] - [Context]\n\n## AI-Suggested Improvements\n1. [Suggestion 1] - Addresses: [Gap/Issue] - [Rationale]\n2. [Suggestion 2] - Addresses: [Gap/Issue] - [Rationale]\n3. [Suggestion 3] - Addresses: [Gap/Issue] - [Rationale]\n\n## Prioritized Actions\n- [ ] [Improvement action] (@owner) (due: [date])\n- [ ] [Improvement action] (@owner) (due: [date])\n- [ ] [Improvement action] (@owner) (due: [date])\n\n## Relationship Mapping Session\n- Area of focus: [knowledge area]\n- New connections identified:\n  - [Item 1] → [Item 2]: [Relationship type]\n  - [Item 3] → [Item 4]: [Relationship type]\n  - [Item 5] → [Item 6]: [Relationship type]\n\n## Discussion Notes\n[Summary of key discussion points and decisions]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Monthly Context Architecture Review Template
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 2 Monthly Context Architecture Review', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Monthly Context Architecture Review - [Date]\n\n## Participants\n- [List of team members present]\n- AI Role: Knowledge Architect\n- Context Steward: [Name]\n\n## Knowledge Base Health Assessment\n- Total knowledge items: [number]\n- Relationship density: [metric]\n- Dead ends / orphaned items: [number]\n- Average knowledge depth: [metric]\n- Coverage index: [percentage]\n- Usage metrics:\n  - Most accessed items: [list]\n  - Least accessed items: [list]\n  - Search success rate: [percentage]\n\n## Knowledge Structure Evaluation\n- Current classification system effectiveness: [Rating 1-5]\n- Navigation friction points: [list]\n- Content duplication issues: [list]\n- Content inconsistency issues: [list]\n\n## AI Pattern Analysis\n### Observed Usage Patterns\n- [Pattern 1] - Frequency: [metric] - Impact: [analysis]\n- [Pattern 2] - Frequency: [metric] - Impact: [analysis]\n- [Pattern 3] - Frequency: [metric] - Impact: [analysis]\n\n### Content Gap Analysis\n- [Gap area 1] - Evidence: [data] - Impact: [analysis]\n- [Gap area 2] - Evidence: [data] - Impact: [analysis]\n- [Gap area 3] - Evidence: [data] - Impact: [analysis]\n\n## Strategic Improvement Plan\n### Classification Refinements\n- [ ] [Refinement action] (@owner) (due: [date])\n- [ ] [Refinement action] (@owner) (due: [date])\n\n### Structure Reorganization\n- [ ] [Reorganization action] (@owner) (due: [date])\n- [ ] [Reorganization action] (@owner) (due: [date])\n\n### Content Development Initiatives\n- [ ] [Content initiative] (@owner) (due: [date])\n- [ ] [Content initiative] (@owner) (due: [date])\n\n### Automation Enhancements\n- [ ] [Automation enhancement] (@owner) (due: [date])\n- [ ] [Automation enhancement] (@owner) (due: [date])\n\n## Next Review Focus Areas\n- Primary focus: [Area]\n- Secondary focus: [Area]\n- Key metrics to improve: [Metrics]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Pre-Retrospective Analysis Report Template
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 2 Pre-Retrospective Analysis Report', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Pre-Retrospective Analysis - [Sprint/Iteration]\n\n## Sprint/Iteration Overview\n- Sprint/Iteration: [Name/Number]\n- Duration: [Start date] to [End date]\n- Team: [Team name]\n\n## Metrics Analysis\n### Quantitative Performance\n- Planned story points: [number]\n- Completed story points: [number] ([percentage]%)\n- Story point velocity trend: [Up/Down/Stable] by [percentage]% from previous sprints\n- Cycle time: [Average in days] ([Up/Down/Stable] by [percentage]% from baseline)\n- Defects introduced: [number] ([Up/Down/Stable] by [percentage]% from baseline)\n- Technical debt addressed: [number of items] ([percentage]% of planned)\n\n### Process Indicators\n- Sprint scope changes: [number] ([Impact assessment])\n- Blockers encountered: [number] - Average resolution time: [time]\n- Code review cycle time: [Average in hours]\n- Testing coverage: [percentage]\n- Documentation completeness: [percentage]\n\n## Communication Pattern Analysis\n- Meeting efficiency: [Assessment based on duration vs. outcomes]\n- Collaboration hotspots: [Areas with highest interaction]\n- Collaboration gaps: [Areas with limited interaction]\n- Decision clarity index: [Assessment of decision documentation quality]\n\n## Historical Pattern Identification\n### Recurring Themes\n- [Theme 1]: Evidence: [data points] - Appears in [number] previous retrospectives\n- [Theme 2]: Evidence: [data points] - Appears in [number] previous retrospectives\n- [Theme 3]: Evidence: [data points] - Appears in [number] previous retrospectives\n\n### Action Item Completion Patterns\n- Previous retrospective actions completed: [percentage]\n- Action effectiveness rating: [Assessment of impact]\n- Common action failure patterns: [Observations]\n\n## Insight Summary\n### Strengths to Leverage\n1. [Strength 1] - Evidence: [data points]\n2. [Strength 2] - Evidence: [data points]\n3. [Strength 3] - Evidence: [data points]\n\n### Opportunities for Improvement\n1. [Opportunity 1] - Evidence: [data points]\n2. [Opportunity 2] - Evidence: [data points]\n3. [Opportunity 3] - Evidence: [data points]\n\n### Systemic Patterns\n1. [Pattern 1] - Manifestation: [description] - Potential root causes: [hypotheses]\n2. [Pattern 2] - Manifestation: [description] - Potential root causes: [hypotheses]\n3. [Pattern 3] - Manifestation: [description] - Potential root causes: [hypotheses]\n\n## Suggested Discussion Prompts\n1. [Thought-provoking question related to key pattern 1]\n2. [Thought-provoking question related to key pattern 2]\n3. [Thought-provoking question related to key pattern 3]\n4. [General improvement-focused question]\n5. [Team dynamics/health question]\n\n## Contextual Relationship to Team Knowledge\n- Related context elements: [list of links to relevant knowledge items]\n- Relevant previous retrospective learnings: [list of links]\n- Applicable team goals/OKRs: [list of links]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Retrospective Session Template
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 2 Retrospective Session', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# AI-Enhanced Retrospective - [Sprint/Iteration]\n\n## Participants\n- [List of team members present]\n- AI Roles: Analyst, Challenger, Documentarian\n- Facilitator: [Name]\n\n## Agenda\n1. AI Insights Review (15 min)\n2. Key Pattern Discussion (20 min)\n3. Root Cause Exploration (20 min)\n4. Improvement Options (15 min)\n5. Action Planning (15 min)\n\n## AI Insights Summary\n[Brief summary of the key points from the pre-retrospective analysis]\n\n### Team Response to Insights\n- [Agreement points]\n- [Disagreement points]\n- [Additional perspectives]\n\n## Key Pattern Discussion\n### Pattern 1: [Name]\n- Observations: [Discussion notes]\n- Impact: [Assessment]\n- Context: [Additional information]\n\n### Pattern 2: [Name]\n- Observations: [Discussion notes]\n- Impact: [Assessment]\n- Context: [Additional information]\n\n### Pattern 3: [Name]\n- Observations: [Discussion notes]\n- Impact: [Assessment]\n- Context: [Additional information]\n\n## Root Cause Exploration\n### Pattern 1 Root Causes\n- [Root cause 1] - Evidence: [Discussion points]\n- [Root cause 2] - Evidence: [Discussion points]\n\n### Pattern 2 Root Causes\n- [Root cause 1] - Evidence: [Discussion points]\n- [Root cause 2] - Evidence: [Discussion points]\n\n### Pattern 3 Root Causes\n- [Root cause 1] - Evidence: [Discussion points]\n- [Root cause 2] - Evidence: [Discussion points]\n\n### AI Challenge Questions & Team Responses\n- [Challenge question 1]:\n  - [Team response]\n- [Challenge question 2]:\n  - [Team response]\n- [Challenge question 3]:\n  - [Team response]\n\n## Improvement Options\n### For Root Cause [X]\n- Option 1: [Description] - Pros: [list] - Cons: [list]\n- Option 2: [Description] - Pros: [list] - Cons: [list]\n- Option 3: [Description] - Pros: [list] - Cons: [list]\n\n### For Root Cause [Y]\n- Option 1: [Description] - Pros: [list] - Cons: [list]\n- Option 2: [Description] - Pros: [list] - Cons: [list]\n\n### AI Suggestions & Team Response\n- [AI suggestion 1]:\n  - [Team assessment]\n- [AI suggestion 2]:\n  - [Team assessment]\n\n## Action Planning\n### High Priority Actions\n- [ ] [Action description] (@owner) (due: [date]) (success metric: [description])\n- [ ] [Action description] (@owner) (due: [date]) (success metric: [description])\n\n### Medium Priority Actions\n- [ ] [Action description] (@owner) (due: [date]) (success metric: [description])\n- [ ] [Action description] (@owner) (due: [date]) (success metric: [description])\n\n### Experiment Actions\n- [ ] [Experiment description] (@owner) (due: [date]) (hypothesis: [description]) (measurement: [description])\n\n## Meta-Retrospective\n- What worked well in this retrospective format: [notes]\n- What could be improved for next time: [notes]\n- AI contribution effectiveness: [assessment]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Retrospective Summary Template
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 2 Retrospective Summary', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# AI-Enhanced Retrospective Summary - [Sprint/Iteration]\n\n## Overview\n- Sprint/Iteration: [Name/Number]\n- Date of Retrospective: [Date]\n- Duration: [Length of meeting]\n- Participants: [Names]\n\n## Executive Summary\n[1-2 paragraph summary of the key outcomes, insights, and actions from the retrospective]\n\n## Key Insights\n1. [Key insight 1 with supporting data and discussion context]\n2. [Key insight 2 with supporting data and discussion context]\n3. [Key insight 3 with supporting data and discussion context]\n\n## Root Causes Identified\n1. [Root cause 1] - Impact: [High/Medium/Low] - Evidence: [Summary]\n2. [Root cause 2] - Impact: [High/Medium/Low] - Evidence: [Summary]\n3. [Root cause 3] - Impact: [High/Medium/Low] - Evidence: [Summary]\n\n## Action Plan\n### High Priority Actions (Must address)\n- [ ] [Action description] (@owner) (due: [date]) (success metric: [description])\n- [ ] [Action description] (@owner) (due: [date]) (success metric: [description])\n\n### Medium Priority Actions (Should address)\n- [ ] [Action description] (@owner) (due: [date]) (success metric: [description])\n- [ ] [Action description] (@owner) (due: [date]) (success metric: [description])\n\n### Experimental Actions (Learning opportunities)\n- [ ] [Experiment description] (@owner) (due: [date]) (hypothesis: [description]) (measurement: [description])\n\n## Team Celebration Points\n- [Achievement/positive aspect to recognize]\n- [Achievement/positive aspect to recognize]\n\n## Knowledge Base Updates\nThe following items should be added or updated in our knowledge base:\n- [ ] [Knowledge item] (@owner)\n- [ ] [Knowledge item] (@owner)\n\n## Continuous Improvement Metrics\n- Retrospective effectiveness rating: [Score 1-5]\n- Action completion rate from previous retrospective: [Percentage]\n- Impact assessment of completed actions: [Brief assessment]\n\n## Follow-up Schedule\n- Action review checkpoint: [Date]\n- Integration with next planning session: [Notes on approach]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Pre-Planning Analysis Template
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 2 Pre-Planning Analysis', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Pre-Planning Analysis - [Sprint/Iteration]\n\n## Planning Context\n- Sprint/Iteration: [Name/Number]\n- Duration: [Start date] to [End date]\n- Team: [Team name]\n- Team capacity: [Available person-days]\n\n## Historical Performance Analysis\n### Velocity Metrics\n- Average velocity (last 3 sprints): [number] story points\n- Velocity trend: [Up/Down/Stable] by [percentage]%\n- Velocity variation: [Standard deviation] (indicating predictability)\n- Velocity confidence interval: [range] (85% confidence)\n\n### Estimation Accuracy\n- Average estimation error (last 3 sprints): [percentage]%\n- Over-estimation pattern: [Analysis of tasks consistently over-estimated]\n- Under-estimation pattern: [Analysis of tasks consistently under-estimated]\n- Complexity correlation: [Analysis of how accuracy varies with complexity]\n\n### Delivery Patterns\n- Average cycle time: [days]\n- Cycle time by work type:\n  - Feature: [days]\n  - Bug: [days]\n  - Technical Debt: [days]\n- Lead time analysis: [findings on bottlenecks or wait states]\n- WIP correlation: [findings on relationship between WIP and throughput]\n\n## Candidate Work Item Analysis\n### Backlog Composition\n- Total candidate items: [number]\n- Total estimated story points: [number]\n- Distribution by type:\n  - Features: [number] items ([percentage]%)\n  - Bugs: [number] items ([percentage]%)\n  - Technical Debt: [number] items ([percentage]%)\n  - Other: [number] items ([percentage]%)\n\n### Key Work Items\n1. [Item ID/Name]:\n   - Historical comparison: [Similar past items and their actual effort]\n   - Complexity factors: [List of identified complexity factors]\n   - Risk factors: [List of identified risk factors]\n   - Dependencies: [List of dependencies]\n   - Suggested estimate range: [range] story points (based on historical data)\n\n2. [Item ID/Name]:\n   - Historical comparison: [Similar past items and their actual effort]\n   - Complexity factors: [List of identified complexity factors]\n   - Risk factors: [List of identified risk factors]\n   - Dependencies: [List of dependencies]\n   - Suggested estimate range: [range] story points (based on historical data)\n\n[Repeat for 3-5 key work items]\n\n## Risk Analysis\n### Team Risk Factors\n- Capacity risk: [Assessment based on planned time off, training, etc.]\n- Skill coverage risk: [Assessment of skill requirements vs. availability]\n- Context switching risk: [Assessment based on planned parallel work]\n\n### Technical Risk Factors\n- [Technical risk 1] - Probability: [High/Medium/Low] - Impact: [High/Medium/Low]\n- [Technical risk 2] - Probability: [High/Medium/Low] - Impact: [High/Medium/Low]\n- [Technical risk 3] - Probability: [High/Medium/Low] - Impact: [High/Medium/Low]\n\n### External Risk Factors\n- [External risk 1] - Probability: [High/Medium/Low] - Impact: [High/Medium/Low]\n- [External risk 2] - Probability: [High/Medium/Low] - Impact: [High/Medium/Low]\n\n## Relevant Knowledge Context\n- [Link to relevant context item 1] - Relevance: [Brief explanation]\n- [Link to relevant context item 2] - Relevance: [Brief explanation]\n- [Link to relevant context item 3] - Relevance: [Brief explanation]\n\n## Planning Recommendations\n### Suggested Sprint Scope\n- Recommended story point range: [min]-[max] points\n- Confidence level at [max] points: [percentage]%\n- Risk-adjusted recommendation: [number] points\n\n### Focus Areas\n- Suggested priority focus: [Area with rationale]\n- Risk mitigation focus: [Specific risks to address]\n- Technical debt consideration: [Recommendation]\n\n### Planning Session Discussion Prompts\n1. [Question related to specific work item estimation]\n2. [Question related to risk management]\n3. [Question related to dependencies]\n4. [Question related to team capacity]\n5. [Question related to priority trade-offs]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Planning Session Template
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 2 Planning Session', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Context-Aware Planning Session - [Sprint/Iteration]\n\n## Participants\n- [List of team members present]\n- Product Owner: [Name]\n- AI Roles: Analyst, Advisor\n- Facilitator: [Name]\n\n## Agenda\n1. Context & Analysis Review (15 min)\n2. Work Item Discussion (20-30 min)\n3. AI-Enhanced Estimation (20-30 min)\n4. Risk/Dependency Analysis (15 min)\n5. Final Capacity Alignment (10 min)\n\n## Context Frame\n[Brief summary of the key points from the pre-planning analysis]\n\n### Team Response to Analysis\n- [Agreement points]\n- [Disagreement points]\n- [Additional perspectives]\n\n## Work Item Discussion\n### [Item ID/Name 1]\n- Business value: [notes]\n- Technical approach: [notes]\n- Relevant context: [reference to knowledge items]\n- Complexity factors: [discussion notes]\n- AI insights: [notes on historical comparisons]\n- Decision: [Include/Exclude/Defer] - Rationale: [notes]\n\n### [Item ID/Name 2]\n- Business value: [notes]\n- Technical approach: [notes]\n- Relevant context: [reference to knowledge items]\n- Complexity factors: [discussion notes]\n- AI insights: [notes on historical comparisons]\n- Decision: [Include/Exclude/Defer] - Rationale: [notes]\n\n[Repeat for each work item discussed]\n\n## AI-Enhanced Estimation\n### [Item ID/Name 1]\n- Initial team estimate: [points/range]\n- Historical comparison data: [summary]\n- Discussion points: [notes]\n- Final estimate: [points] - Confidence: [High/Medium/Low]\n\n### [Item ID/Name 2]\n- Initial team estimate: [points/range]\n- Historical comparison data: [summary]\n- Discussion points: [notes]\n- Final estimate: [points] - Confidence: [High/Medium/Low]\n\n[Repeat for each work item estimated]\n\n### Estimation Summary\n- Total story points: [number]\n- Comparison to velocity: [percentage] of average\n- Confidence assessment: [AI-generated confidence level with rationale]\n\n## Risk & Dependency Analysis\n### Identified Risks\n- [Risk 1] - Probability: [H/M/L] - Impact: [H/M/L] - Mitigation: [strategy]\n- [Risk 2] - Probability: [H/M/L] - Impact: [H/M/L] - Mitigation: [strategy]\n- [Risk 3] - Probability: [H/M/L] - Impact: [H/M/L] - Mitigation: [strategy]\n\n### Dependencies\n- [Dependency 1] - Status: [Resolved/Pending/Blocked] - Plan: [approach]\n- [Dependency 2] - Status: [Resolved/Pending/Blocked] - Plan: [approach]\n\n### AI Risk Suggestions & Team Response\n- [AI suggestion 1]:\n  - [Team response]\n- [AI suggestion 2]:\n  - [Team response]\n\n## Final Capacity Alignment\n- Team capacity: [available person-days]\n- Planned work capacity: [estimated person-days]\n- Buffer/margin: [percentage]\n- Confidence in delivery: [High/Medium/Low]\n- Adjustments made: [list of scope adjustments]\n\n## Sprint/Iteration Goal\n[Clear, concise statement of the goal for this sprint/iteration]\n\n## Success Criteria\n- [Measurable success criterion 1]\n- [Measurable success criterion 2]\n- [Measurable success criterion 3]\n\n## Planning Meta-Assessment\n- Planning efficiency rating: [1-5]\n- Value of AI analysis: [1-5]\n- Areas to improve for next planning: [notes]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Planning Documentation Template
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 2 Planning Documentation', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Sprint/Iteration Plan - [Sprint/Iteration]\n\n## Plan Overview\n- Sprint/Iteration: [Name/Number]\n- Duration: [Start date] to [End date]\n- Team: [Team name]\n- Total story points: [number]\n\n## Sprint/Iteration Goal\n[Clear, concise statement of the goal for this sprint/iteration]\n\n## Success Criteria\n- [Measurable success criterion 1]\n- [Measurable success criterion 2]\n- [Measurable success criterion 3]\n\n## Work Item Summary\n- Total work items: [number]\n- Features: [number] ([percentage]% of points)\n- Bugs: [number] ([percentage]% of points)\n- Technical Debt: [number] ([percentage]% of points)\n- Other: [number] ([percentage]% of points)\n\n## Committed Work Items\n| ID | Title | Type | Story Points | Confidence | Owner | Dependencies |\n|----|-------|------|-------------|------------|-------|--------------|\n| [ID] | [Title] | [Type] | [Points] | [H/M/L] | [Name] | [IDs] |\n| [ID] | [Title] | [Type] | [Points] | [H/M/L] | [Name] | [IDs] |\n| [ID] | [Title] | [Type] | [Points] | [H/M/L] | [Name] | [IDs] |\n[Additional rows as needed]\n\n## Planning Context & Rationale\n### Capacity Considerations\n- Available capacity: [person-days]\n- Planned capacity utilization: [percentage]\n- Buffer allocation: [percentage]\n- Confidence assessment: [AI-generated analysis]\n\n### Scope Selection Rationale\n[Explanation of why these specific items were selected, including business value, technical considerations, risk balancing, etc.]\n\n### Estimation Approach\n[Summary of how estimates were generated, including historical data leveraged and confidence factors]\n\n## Risk Management Plan\n### Key Risks\n- [Risk 1] - Probability: [H/M/L] - Impact: [H/M/L]\n  - Mitigation: [strategy]\n  - Owner: [name]\n- [Risk 2] - Probability: [H/M/L] - Impact: [H/M/L]\n  - Mitigation: [strategy]\n  - Owner: [name]\n- [Risk 3] - Probability: [H/M/L] - Impact: [H/M/L]\n  - Mitigation: [strategy]\n  - Owner: [name]\n\n### Contingency Plan\n[Description of how the team will handle unexpected issues, scope changes, or capacity changes]\n\n## Dependencies\n### Internal Dependencies\n- [Dependency 1] - Status: [Resolved/Pending/Blocked] - Resolution plan: [description]\n- [Dependency 2] - Status: [Resolved/Pending/Blocked] - Resolution plan: [description]\n\n### External Dependencies\n- [Dependency 1] - Status: [Resolved/Pending/Blocked] - Resolution plan: [description]\n- [Dependency 2] - Status: [Resolved/Pending/Blocked] - Resolution plan: [description]\n\n## Knowledge Context Links\n- [Link to relevant context item 1] - Relevance: [Brief explanation]\n- [Link to relevant context item 2] - Relevance: [Brief explanation]\n- [Link to relevant context item 3] - Relevance: [Brief explanation]\n\n## Communication Plan\n- Daily status updates: [approach]\n- Mid-sprint review: [date and focus]\n- Stakeholder communication: [approach and frequency]\n\n## Approval\n- Product Owner: [Name] - Status: [Approved/Pending]\n- Team: [Consensus achieved: Yes/No]\n- Date: [Approval date]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Pair Working Initialization Template
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 2 Pair Working Initialization', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# AI Pair Working Session - Initialization\n\n## Session Information\n- Date: [Date]\n- Team Member: [Name]\n- Task Type: [Coding/Design/Analysis/Writing/Other]\n- Expected Duration: [Estimated time]\n- AI Model/Assistant: [Name/Configuration]\n\n## Task Definition\n### Objective\n[Clear, specific statement of what this session aims to accomplish]\n\n### Success Criteria\n- [Measurable criterion 1]\n- [Measurable criterion 2]\n- [Measurable criterion 3]\n\n### Constraints\n- [Technical constraint]\n- [Business constraint]\n- [Time constraint]\n- [Quality constraint]\n\n## Relevant Context\n### Knowledge Base References\n- [Link to context item 1] - Relevance: [Brief explanation]\n- [Link to context item 2] - Relevance: [Brief explanation]\n- [Link to context item 3] - Relevance: [Brief explanation]\n\n### Related Work\n- [Link to previous/related work 1]\n- [Link to previous/related work 2]\n\n## AI Configuration\n### Role Definition\n- Primary AI Role: [Analyst/Advisor/Challenger/Co-Creator/Other]\n- Role Description: [Detailed description of the AI''s responsibilities]\n- Boundaries: [Clear delineation of what AI should not do]\n\n### Collaboration Model\n- [Turn-taking/Simultaneous/Interactive/Other]\n- [Specific process description]\n\n### Initial Prompt\n```\n[Copy of the initial instruction/prompt to configure the AI]\n```\n\n## Checkpoint Plan\n- First checkpoint: [Specific milestone] - Expected time: [Estimate]\n- Second checkpoint: [Specific milestone] - Expected time: [Estimate]\n- Final review: [Specific milestone] - Expected time: [Estimate]\n\n## Post-Session Plan\n- Documentation approach: [How will results be documented]\n- Integration plan: [How will output be integrated with other work]\n- Knowledge capture: [What learnings should be preserved]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Session Log Template
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 2 Session Log', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# AI Pair Working Session Log\n\n## Session Information\n- Date: [Date]\n- Duration: [Actual time]\n- Team Member: [Name]\n- Task: [Brief description]\n- AI Model/Assistant: [Name/Configuration]\n\n## Session Timeline\n### [Timestamp]: Session Start\n- Initial prompt/configuration: [Summary]\n- AI initial response: [Summary]\n\n### [Timestamp]: First Checkpoint\n- Progress: [Status against objectives]\n- Key decisions: [List of important decisions made]\n- Adjustments: [Any changes to approach]\n\n### [Timestamp]: Second Checkpoint\n- Progress: [Status against objectives]\n- Key decisions: [List of important decisions made]\n- Adjustments: [Any changes to approach]\n\n### [Timestamp]: Final Review\n- Completeness: [Assessment against success criteria]\n- Quality: [Assessment of output quality]\n- Final adjustments: [Last changes made]\n\n### [Timestamp]: Session End\n- Outcome summary: [Brief description of what was accomplished]\n\n## Key Decision Points\n1. [Decision 1]:\n   - Options considered: [List]\n   - Decision rationale: [Explanation]\n   - Human/AI contribution: [Who proposed/decided]\n\n2. [Decision 2]:\n   - Options considered: [List]\n   - Decision rationale: [Explanation]\n   - Human/AI contribution: [Who proposed/decided]\n\n3. [Decision 3]:\n   - Options considered: [List]\n   - Decision rationale: [Explanation]\n   - Human/AI contribution: [Who proposed/decided]\n\n## Challenges Encountered\n- [Challenge 1]:\n  - Solution approach: [Description]\n  - Resolution: [Outcome]\n\n- [Challenge 2]:\n  - Solution approach: [Description]\n  - Resolution: [Outcome]\n\n## Effective Interactions\n- [Interaction pattern 1]: [Description and why it was effective]\n- [Interaction pattern 2]: [Description and why it was effective]\n\n## Session Output\n[Summary or link to the session output, e.g., code, document, analysis]\n\n## Follow-up Actions\n- [ ] [Action description] (due: [date])\n- [ ] [Action description] (due: [date])\n\n## Meta-Reflection\n### What Worked Well\n- [Aspect 1]\n- [Aspect 2]\n\n### Areas for Improvement\n- [Area 1]\n- [Area 2]\n\n### For Next Time\n- [ ] [Improvement to try]\n- [ ] [Improvement to try]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Pattern Documentation Template
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 2 Pattern Documentation', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# AI Pair Working Pattern\n\n## Pattern Identification\n- Name: [Descriptive name]\n- Version: [Version number]\n- Created by: [Team member]\n- Date: [Date documented]\n- Task types: [Coding/Design/Analysis/Writing/Other]\n\n## Pattern Description\n### Purpose\n[Clear description of what this collaboration pattern aims to accomplish]\n\n### When to Use\n- [Situation or task type 1]\n- [Situation or task type 2]\n- [Situation or task type 3]\n\n### Roles and Responsibilities\n- Human role: [Specific responsibilities]\n- AI role: [Specific responsibilities]\n\n## Pattern Structure\n### Initialization\n1. [Step 1]\n2. [Step 2]\n3. [Step 3]\n\n### Workflow\n1. [Step 1]\n2. [Step 2]\n3. [Step 3]\n\n### Checkpoints\n- [Checkpoint 1]: [Purpose and process]\n- [Checkpoint 2]: [Purpose and process]\n- [Final review]: [Purpose and process]\n\n## Implementation Guide\n### Initial Prompt Template\n```\n[Template text for configuring the AI with placeholders]\n```\n\n### Example Exchange\n**Human:** [Example input]\n\n**AI:** [Example response]\n\n**Human:** [Example follow-up]\n\n**AI:** [Example response]\n\n### Tips for Effective Implementation\n- [Tip 1]\n- [Tip 2]\n- [Tip 3]\n\n## Success Factors and Metrics\n### Success Indicators\n- [Indicator 1]\n- [Indicator 2]\n- [Indicator 3]\n\n### Common Pitfalls\n- [Pitfall 1] - Mitigation: [strategy]\n- [Pitfall 2] - Mitigation: [strategy]\n- [Pitfall 3] - Mitigation: [strategy]\n\n## Case Studies\n### Case 1: [Brief description]\n- Context: [Background]\n- Application: [How pattern was applied]\n- Outcome: [Results achieved]\n- Learnings: [Key takeaways]\n\n### Case 2: [Brief description]\n- Context: [Background]\n- Application: [How pattern was applied]\n- Outcome: [Results achieved]\n- Learnings: [Key takeaways]\n\n## Related Patterns\n- [Related pattern 1]: [Relationship description]\n- [Related pattern 2]: [Relationship description]\n\n## Evolution History\n- [Version] ([Date]): [Changes]\n- [Version] ([Date]): [Changes]',
--     1, admin_team_id, NOW());
-- END $$;

-- --
-- -- End of Phase 2 Templates
-- --

-- --
-- -- Inserting Phase 2 Workflows
-- --

-- -- Workflow: ExtractContextElements
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: ExtractContextElements\n# Description: Extracts key elements, suggests classifications, and potential relations from daily context updates.\n\ninputDocumentSelectors:\n  - "DailyContextCuration*" # Designed for documents like DailyContextCuration_YYYY-MM-DD\ninputDateSelector: null\noutputName: "ExtractedElements_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Review the following daily context updates from the document titled "{{InputFileName}}".\n  For each team member''s update, identify 3-5 key informational elements (e.g., decisions, findings, new terms, project updates, risks identified).\n\n  For each extracted element:\n  1.  Suggest a brief, relevant CATEGORY (e.g., Decision, Finding, Risk, New Term, Project Update, Technical Debt).\n  2.  If the element seems related to common project themes or other items mentioned in the input, briefly note a "Potential Relation" (e.g., "Related to: Feature X Rollout", "Related to: Sprint Goal Y").\n\n  Format your output clearly for each team member. Example:\n\n  Team Member: [Name]\n  - Extracted Element: [Element text]\n    - Suggested Category: [Category]\n    - Potential Relation: [Relation text or N/A]\n  - Extracted Element: [...]\n    - Suggested Category: [...]\n    - Potential Relation: [...]\n\n  DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```\n\n  Provide only the extracted elements, categories, and potential relations as requested.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 2 ExtractContextElements', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: AnalyzeContextMetrics
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: AnalyzeContextMetrics\n# Description: Analyzes a list of TIP documents and their metadata to generate context health metrics.\n\ninputDocumentSelectors:\n  - "Input_ContextMetrics*" # Designed for manually compiled documents listing other documents\ninputDateSelector: null\noutputName: "Output_ContextHealthDashboard_Data_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}.md"\nprompt: |\n  **Role:** You are an AI Knowledge Management Assistant. Your task is to analyze the provided list of documents and their metadata to identify basic context health metrics.\n  **Goal:** Generate a structured report based ONLY on the information within the input document titled "{{InputFileName}}". This report will serve as data for a Context Health Dashboard.\n\n  **Context:**\n  - The input document contains a list of other TIP document names and may include metadata such as "LastModified" dates and "Keywords".\n  - It may also contain an "Analysis Focus" section specifying what the user wants to identify.\n  - Today''s Date for reference: {{CurrentDate_YYYY-MM-DD}}.\n\n  **Task:**\n  Based *only* on the content of the input document "{{InputFileName}}":\n\n  1.  **Document Count:**\n      - Report the total number of documents listed in the input.\n\n  2.  **Activity Summary (if "LastModified" dates are provided):**\n      - Identify and list any documents not modified in the last 30 days (calculate based on {{CurrentDate_YYYY-MM-DD}} and the provided "LastModified" dates).\n      - Identify and list documents modified in the last 7 days.\n\n  3.  **Keyword Analysis (if "Keywords" are provided):**\n      - If keywords are present for each document, count the occurrences of the top 3-5 most frequent primary keywords across all listed documents.\n      - List documents associated with each of these top keywords.\n\n  4.  **User-Defined Analysis Focus (if "Analysis Focus" section is provided in the input):**\n      - Address any specific requests made in the "Analysis Focus" section of the input document, using the provided data.\n\n  5.  **Potential Issues (General Observations):**\n      - Briefly note any obvious potential issues based *only* on the provided list, e.g., a high number of very old documents, or very few recent documents if that context is inferable from document names/dates.\n\n  **Format Output Clearly:**\n  Structure your output with clear headings for each section (e.g., "Document Count", "Activity Summary", "Keyword Analysis", "User-Defined Analysis", "Potential Issues").\n\n  **Constraint:** Base your entire analysis strictly on the information explicitly provided within the "{{InputFileName}}" document. Do not make assumptions or infer information beyond what is written.\n\n  INPUT DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 2 AnalyzeContextMetrics', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: AnalyzeRetroData
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: AnalyzeRetroData\n# Description: Analyzes pre-compiled retrospective data to identify patterns and suggest discussion prompts.\n\ninputDocumentSelectors:\n  - "PreRetroData*" # Designed for documents like PreRetroData_SprintX_YYYY-MM-DD\ninputDateSelector: null\noutputName: "AI_RetroInsights_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Based on the content of the Pre-Retrospective Analysis document titled "{{InputFileName}}", perform the following analysis. The input document contains sections like "Metrics Analysis", "Communication Pattern Analysis", and "Historical Pattern Identification".\n\n  1.  **Insight Summary:**\n      - Identify 2-3 key strengths to leverage from the data.\n      - Identify 2-3 significant opportunities for improvement.\n      - Identify 1-2 potential systemic patterns or recurring themes.\n  2.  **Suggested Discussion Prompts:**\n      - Generate 3-4 thought-provoking questions based on your analysis of the "Systemic Patterns", "Opportunities for Improvement", or "Historical Pattern Identification" sections of the input document. These questions should help the team explore root causes or potential solutions.\n\n  Format your output clearly.\n\n  Pre-Retrospective Analysis Document Content:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 2 AnalyzeRetroData', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: SuggestRetroActions
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: SuggestRetroActions\n# Description: Suggests potential action items based on retrospective session notes.\n\ninputDocumentSelectors:\n  - "RetroSessionNotes*" # Designed for documents from the Retrospective Session Template\ninputDateSelector: null\noutputName: "SuggestedActions_for_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Review the Retrospective Session Notes from the document titled "{{InputFileName}}".\n  Based on the "Key Pattern Discussion", "Root Cause Exploration", and "Improvement Options" sections, suggest 3-5 concrete, actionable, and measurable (if possible) improvement actions the team could take.\n\n  For each suggested action, provide:\n  - A clear description of the action.\n  - A brief rationale linking it to the discussion in the notes.\n\n  Example Format:\n  **Suggested Action 1:**\n  - Description: [Action description]\n  - Rationale: [Rationale based on notes]\n\n  **Suggested Action 2:**\n  - Description: [Action description]\n  - Rationale: [Rationale based on notes]\n\n  Retrospective Session Notes Document Content:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 2 SuggestRetroActions', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: AnalyzePlanningData
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: AnalyzePlanningData\n# Description: Analyzes pre-compiled planning data to provide insights for sprint planning.\n\ninputDocumentSelectors:\n  - "PrePlanningData*" # Designed for documents like PrePlanningData_SprintY_YYYY-MM-DD\ninputDateSelector: null\noutputName: "AI_PlanningInsights_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Based on the content of the Pre-Planning Analysis document titled "{{InputFileName}}", provide the following:\n\n  1.  **Historical Performance Summary (from input data):**\n      - Briefly summarize any trends in velocity or cycle time mentioned in the "Historical Performance Analysis" section.\n      - Highlight any significant estimation patterns (over/under estimation) noted.\n  2.  **Key Work Item Considerations (from input data):**\n      - For up to 3 "Key Work Items" listed, summarize their complexity and risk factors as presented in the input.\n  3.  **Risk Profile Summary (from input data):**\n      - List the top 2-3 "Technical Risk Factors" and "External Risk Factors" with their probability/impact if provided in the input.\n  4.  **Suggested Planning Focus Areas:**\n      - Based on the overall input data, suggest 1-2 areas the team might want to focus on during their planning session (e.g., addressing a specific risk, considering capacity against a complex item).\n\n  Format your output clearly under these headings.\n\n  Pre-Planning Analysis Document Content:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 2 AnalyzePlanningData', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: DraftSection-PairWorking
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: DraftSection-PairWorking\n# Description: Drafts a text section based on a topic, keywords, or outline provided in the input document.\n\ninputDocumentSelectors:\n  - "PairInput*" # User prepares a document with their specific input, e.g., PairInput_DraftFeatureX_YYYY-MM-DD\ninputDateSelector: null\noutputName: "DraftOutput_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  The following input document "{{InputFileName}}" contains a request to draft a text section.\n  The request might include a topic, keywords, a brief outline, or some source material.\n\n  Based **only** on the information provided in the input document below, please draft the requested text section.\n  Aim for clarity, conciseness, and adhere to any specified tone or style if mentioned in the input.\n  If the input is an outline, expand on each point.\n  If keywords are provided, weave them naturally into the text.\n\n  Input Document Content:\n  ```\n  {{DocumentContext}}\n  ```\n\n  Begin your response directly with the drafted section. Do not add any prefatory remarks.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 2 DraftSection-PairWorking', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: BrainstormIdeas-PairWorking
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: BrainstormIdeas-PairWorking\n# Description: Brainstorms ideas based on a problem statement or topic from an input document.\n\ninputDocumentSelectors:\n  - "PairInput*" # User prepares a document with their specific input\ninputDateSelector: null\noutputName: "BrainstormOutput_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  The input document "{{InputFileName}}" contains a request for brainstorming ideas.\n  This request could be a problem statement, a question, or a topic.\n\n  Based **only** on the information and request provided in the input document below, generate a list of 5-10 distinct ideas related to the core request.\n  Present the ideas as a bulleted list.\n\n  Input Document Content:\n  ```\n  {{DocumentContext}}\n  ```\n\n  Begin your response directly with the list of brainstormed ideas.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 2 BrainstormIdeas-PairWorking', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: AnalyzeTextSegment-PairWorking
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: AnalyzeTextSegment-PairWorking\n# Description: Analyzes a provided text segment based on instructions in the input document.\n\ninputDocumentSelectors:\n  - "PairInput*" # User prepares a document with text and analysis instructions\ninputDateSelector: null\noutputName: "AnalysisOutput_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  The input document "{{InputFileName}}" contains a segment of text and a specific request for how to analyze that text.\n  Carefully read the "Analysis Request" and the "Text to Analyze" sections within the input document.\n\n  Perform **only** the requested analysis on the provided text.\n  Structure your output clearly based on the nature of the analysis requested. For example, if asked for pros and cons, use those headings. If asked for themes, list them.\n\n  Input Document Content:\n  ```\n  {{DocumentContext}}\n  ```\n\n  Begin your response directly with the results of your analysis.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 2 AnalyzeTextSegment-PairWorking', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- --
-- -- End of Phase 2 Workflows
-- --

-- --
-- -- Inserting Phase 3 Templates
-- --

-- -- Template: Continuous Context Evolution Configuration
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Continuous Context Evolution Configuration', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Continuous Context Evolution Configuration\n\n## General Settings\n- Team Identifier: [Team Name/ID]\n- Repository Federation Links: [List of connected repositories]\n- Context Steward: [Primary responsible person]\n- AI Knowledge Architect: [Configuration name]\n\n## Automated Extraction Settings\n### Communication Channels\n- [ ] Team Chat ([Integration configuration])\n- [ ] Email ([Integration configuration])\n- [ ] Video Meetings ([Integration configuration])\n- [ ] Documents ([Integration configuration])\n- [ ] Code Repositories ([Integration configuration])\n- [ ] Project Management ([Integration configuration])\n\n### Classification Rules\n- Domain: [Primary knowledge domain]\n  - Categories: [List of primary categories]\n  - Auto-classification rules: [Rules configuration]\n  - Relationship mapping heuristics: [Mapping configuration]\n\n### Privacy & Security Settings\n- Classification levels: [List of sensitivity levels]\n- Access control groups: [List of access roles]\n- Content filtering rules: [List of exclusion patterns]\n\n## Cross-Team Connections\n- Connected Teams: [List of teams with federated repositories]\n- Boundary Areas: [List of shared knowledge domains]\n- Cross-reference patterns: [Configuration for cross-repository linking]\n\n## AI Processing Configuration\n- Extraction model: [Model configuration]\n- Classification workflow: [LangFlow workflow reference]\n- Relationship mapping workflow: [LangFlow workflow reference]\n- Health monitoring workflow: [LangFlow workflow reference]\n\n## Notification Settings\n- Immediate notification triggers: [List of high-priority events]\n- Daily digest configuration: [Settings for daily updates]\n- Weekly summary configuration: [Settings for weekly reports]\n\n## Automation Rules\n- Auto-commit rules: [When changes are automatically committed]\n- Human review thresholds: [Confidence levels requiring review]\n- Escalation paths: [Who to notify for different scenarios]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Weekly Team Curation Template (30 min)
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Weekly Team Curation Template (30 min)', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Weekly Context Curation - [Date]\n\n## Participants\n- [List of team members present]\n- AI Knowledge Architect: [Configuration name]\n- Context Steward: [Name]\n- Cross-team representatives: [Names, if applicable]\n\n## Context Health Dashboard\n### Quantitative Metrics\n- Total knowledge items: [number]\n- New items this week: [number]\n- Items updated/modified: [number]\n- Relationship density: [average connections per item]\n- Cross-team references: [number]\n- Orphaned items: [number] items with <2 connections\n- Aging areas: [number] knowledge areas not updated in >30 days\n\n### Qualitative Assessment\n- Overall health score: [1-10]\n- Areas of excellence: [List knowledge areas with high health]\n- Areas requiring attention: [List knowledge areas with poor health]\n- Cross-team integration quality: [Assessment]\n\n## AI-Identified Health Issues\n1. [Issue 1] - Priority: [High/Medium/Low]\n   - Evidence: [Data supporting the issue]\n   - Recommendation: [AI-suggested improvement]\n   - Impact if addressed: [Expected benefit]\n\n2. [Issue 2] - Priority: [High/Medium/Low]\n   - Evidence: [Data supporting the issue]\n   - Recommendation: [AI-suggested improvement]\n   - Impact if addressed: [Expected benefit]\n\n3. [Issue 3] - Priority: [High/Medium/Low]\n   - Evidence: [Data supporting the issue]\n   - Recommendation: [AI-suggested improvement]\n   - Impact if addressed: [Expected benefit]\n\n## Strategic Knowledge Decisions\n1. [Knowledge area 1]:\n   - Current state: [Description]\n   - Evolution direction: [Strategic decision]\n   - Rationale: [Justification]\n   - Implementation: [Immediate actions]\n\n2. [Knowledge area 2]:\n   - Current state: [Description]\n   - Evolution direction: [Strategic decision]\n   - Rationale: [Justification]\n   - Implementation: [Immediate actions]\n\n## Cross-Team Knowledge Needs\n- Requested from [Team A]: [Knowledge element needed]\n- Offering to [Team B]: [Knowledge element to share]\n- Joint development with [Team C]: [Shared knowledge element]\n\n## Automated Classification Review\n- Classifications to verify: [List of items with uncertain classification]\n- Decision: [Accept/Modify for each] with [Rationale]\n- Classification rule updates: [Any patterns requiring rule changes]\n\n## Priority Actions\n- [ ] [Action description] (@owner) (due: [date])\n- [ ] [Action description] (@owner) (due: [date])\n- [ ] [Action description] (@owner) (due: [date])\n\n## Notes\n[Any additional notes or observations]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Monthly Cross-Team Alignment Template (60 min)
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Monthly Cross-Team Alignment Template (60 min)', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Monthly Cross-Team Alignment - [Date]\n\n## Participants\n- Context Stewards: [List of stewards from each team]\n- AI Knowledge Architect(s): [Configuration names]\n- Knowledge Management Lead: [Name]\n- Facilitator: [Name]\n- Executives/Stakeholders: [Names, if applicable]\n\n## Organizational Knowledge Map\n- [Visualization/link to current knowledge map]\n- Key changes since last alignment: [Summary of major evolutions]\n- Strategic importance areas: [Areas aligned with business priorities]\n\n## Boundary Areas Analysis\n### [Boundary Area 1]\n- Connected teams: [List of teams sharing this boundary]\n- Knowledge elements: [Key shared knowledge items]\n- Integration quality: [Assessment of how well integrated]\n- Pain points: [Issues with current connection]\n- Opportunities: [Potential for enhanced integration]\n\n### [Boundary Area 2]\n- Connected teams: [List of teams sharing this boundary]\n- Knowledge elements: [Key shared knowledge items]\n- Integration quality: [Assessment of how well integrated]\n- Pain points: [Issues with current connection]\n- Opportunities: [Potential for enhanced integration]\n\n## Knowledge Domain Harmonization\n### [Overlapping Domain 1]\n- Current state: [Description of overlap/conflict]\n- Teams involved: [List of teams]\n- Harmonization approach: [Agreement on handling]\n- Implementation plan: [Steps to resolve]\n- Success criteria: [How we''ll measure improvement]\n\n### [Overlapping Domain 2]\n- Current state: [Description of overlap/conflict]\n- Teams involved: [List of teams]\n- Harmonization approach: [Agreement on handling]\n- Implementation plan: [Steps to resolve]\n- Success criteria: [How we''ll measure improvement]\n\n## Strategic Knowledge Planning\n### Organizational Priorities\n- [Priority 1]: [Relevance to knowledge strategy]\n- [Priority 2]: [Relevance to knowledge strategy]\n- [Priority 3]: [Relevance to knowledge strategy]\n\n### Future Knowledge Needs\n- Anticipated in next quarter: [Upcoming knowledge requirements]\n- Long-term strategic elements: [Knowledge to develop for future]\n- Innovation areas: [Where knowledge can drive innovation]\n\n### Knowledge Gap Strategy\n- Identified gaps: [Areas where knowledge is insufficient]\n- Development approach: [How gaps will be addressed]\n- Ownership: [Who will drive this development]\n- Timeline: [When knowledge should be developed]\n\n## Cross-Team Initiatives\n- [ ] [Initiative description] (Teams: [teams involved], Lead: [@owner], due: [date])\n- [ ] [Initiative description] (Teams: [teams involved], Lead: [@owner], due: [date])\n- [ ] [Initiative description] (Teams: [teams involved], Lead: [@owner], due: [date])\n\n## Standards and Governance Updates\n- Classification system changes: [Any updates to taxonomy]\n- Access control adjustments: [Changes to who can access what]\n- Quality standard updates: [New or revised quality metrics]\n- Tool/integration enhancements: [Technical improvements]\n\n## Follow-up Schedule\n- Next alignment session: [Date]\n- Interim checkpoints: [Dates for any interim reviews]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Decision Initialization Template (15-30 min)
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Decision Initialization Template (15-30 min)', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Decision Initialization - [Decision ID]\n\n## Decision Metadata\n- Decision ID: [Unique identifier]\n- Date initiated: [Date]\n- Decision owner: [Primary responsible person]\n- Decision type: [Strategic/Tactical/Operational]\n- Decision complexity: [High/Medium/Low]\n- Deadline: [Required by date]\n- Impact scope: [Team/Department/Organization]\n\n## Decision Context\n### Problem Statement\n[Clear, concise description of the problem or opportunity requiring a decision]\n\n### Strategic Alignment\n- Organizational goals: [Relevant organizational objectives]\n- Team objectives: [Relevant team objectives]\n- Previous related decisions: [Links to relevant past decisions]\n\n### Current Situation\n[Detailed description of the current state, including relevant background and circumstances]\n\n## Decision Criteria\n| Criterion | Weight (1-10) | Description | Measurement Approach |\n|-----------|---------------|-------------|----------------------|\n| [Criterion 1] | [Weight] | [Description] | [How it will be assessed] |\n| [Criterion 2] | [Weight] | [Description] | [How it will be assessed] |\n| [Criterion 3] | [Weight] | [Description] | [How it will be assessed] |\n| [Criterion 4] | [Weight] | [Description] | [How it will be assessed] |\n| [Criterion 5] | [Weight] | [Description] | [How it will be assessed] |\n\n## Stakeholder Perspectives\n| Stakeholder | Interests | Success Looks Like | Concerns | Involvement Level |\n|-------------|-----------|-------------------|----------|-------------------|\n| [Stakeholder 1] | [Key interests] | [Desired outcome] | [Potential issues] | [Decision-maker/Consulted/Informed] |\n| [Stakeholder 2] | [Key interests] | [Desired outcome] | [Potential issues] | [Decision-maker/Consulted/Informed] |\n| [Stakeholder 3] | [Key interests] | [Desired outcome] | [Potential issues] | [Decision-maker/Consulted/Informed] |\n\n## Constraints\n- Time constraints: [Deadlines or timing limitations]\n- Resource constraints: [Budget, people, technology limitations]\n- Technical constraints: [Technical limitations or requirements]\n- Legal/Policy constraints: [Any legal or policy restrictions]\n- Risk tolerance: [Level of acceptable risk]\n\n## Historical Context (AI-Retrieved)\n### Similar Past Decisions\n1. [Decision reference]: [Outcome and relevance]\n2. [Decision reference]: [Outcome and relevance]\n3. [Decision reference]: [Outcome and relevance]\n\n### Lessons Learned\n- [Key lesson 1]\n- [Key lesson 2]\n- [Key lesson 3]\n\n## Decision Process Plan\n- Option development approach: [How options will be generated]\n- Evaluation methodology: [How options will be assessed]\n- Decision-making approach: [How final decision will be made]\n- Implementation planning: [How execution will be approached]\n- Success measurement: [How outcomes will be evaluated]\n\n## Initial Hypotheses (Optional)\n- [Initial hypothesis 1]\n- [Initial hypothesis 2]\n- [Initial hypothesis 3]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Option Development Template (30-45 min)
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Option Development Template (30-45 min)', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Option Development - [Decision ID]\n\n## Decision Summary\n- Decision ID: [Reference to initialization document]\n- Decision focus: [Brief description of the decision focus]\n- Key criteria: [Quick list of top decision criteria]\n\n## Option Generation\n### Collaborative Brainstorming Results\n- [Option 1]: [Brief description]\n- [Option 2]: [Brief description]\n- [Option 3]: [Brief description]\n- [Option 4]: [Brief description]\n- [Option 5]: [Brief description]\n- [Option 6+]: [Brief description]\n\n### AI-Generated Options\n- [AI Option 1]: [Brief description] - [Generation rationale]\n- [AI Option 2]: [Brief description] - [Generation rationale]\n- [AI Option 3]: [Brief description] - [Generation rationale]\n\n### Historical Pattern Matches\n- [Historical parallel 1]: [Description and relevance]\n- [Historical parallel 2]: [Description and relevance]\n- [Historical parallel 3]: [Description and relevance]\n\n## Option Development\n\n### Option 1: [Name]\n**Description:**\n[Detailed description of what this option entails]\n\n**Key Components:**\n- [Component 1]\n- [Component 2]\n- [Component 3]\n\n**Implementation Approach:**\n[How this option would be implemented]\n\n**Resource Requirements:**\n- Time: [Estimated time requirements]\n- Cost: [Estimated financial requirements]\n- People: [Staffing/skill requirements]\n- Technology: [Technology requirements]\n\n**Preliminary Assessment:**\n- Strengths: [Key strengths]\n- Weaknesses: [Key weaknesses]\n- Opportunities: [Potential upsides]\n- Threats: [Potential risks]\n\n### Option 2: [Name]\n**Description:**\n[Detailed description of what this option entails]\n\n**Key Components:**\n- [Component 1]\n- [Component 2]\n- [Component 3]\n\n**Implementation Approach:**\n[How this option would be implemented]\n\n**Resource Requirements:**\n- Time: [Estimated time requirements]\n- Cost: [Estimated financial requirements]\n- People: [Staffing/skill requirements]\n- Technology: [Technology requirements]\n\n**Preliminary Assessment:**\n- Strengths: [Key strengths]\n- Weaknesses: [Key weaknesses]\n- Opportunities: [Potential upsides]\n- Threats: [Potential risks]\n\n[Repeat for additional options]\n\n## Cross-Impact Analysis\n| Decision | Interaction with Option 1 | Interaction with Option 2 | Interaction with Option 3 |\n|----------|---------------------------|---------------------------|---------------------------|\n| [Related Decision 1] | [Impact description] | [Impact description] | [Impact description] |\n| [Related Decision 2] | [Impact description] | [Impact description] | [Impact description] |\n| [Related Decision 3] | [Impact description] | [Impact description] | [Impact description] |\n\n## Next Steps\n- Options to advance for detailed evaluation: [List selected options]\n- Additional information needed: [List information gaps]\n- Analysis to perform: [Specific analyses required]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Structured Evaluation Template (30-45 min)
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Structured Evaluation Template (30-45 min)', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Structured Evaluation - [Decision ID]\n\n## Decision Summary\n- Decision ID: [Reference to initialization document]\n- Decision focus: [Brief description of the decision focus]\n- Options being evaluated: [List of options from the Option Development]\n\n## Multi-Criteria Analysis\n### Criteria Weighting Confirmation\n| Criterion | Weight (1-10) | Rationale for Weight |\n|-----------|---------------|----------------------|\n| [Criterion 1] | [Final weight] | [Explanation] |\n| [Criterion 2] | [Final weight] | [Explanation] |\n| [Criterion 3] | [Final weight] | [Explanation] |\n| [Criterion 4] | [Final weight] | [Explanation] |\n| [Criterion 5] | [Final weight] | [Explanation] |\n\n### Detailed Option Scoring\n\n#### Option 1: [Name]\n| Criterion | Score (1-10) | Justification | Weighted Score |\n|-----------|--------------|---------------|---------------|\n| [Criterion 1] | [Score] | [Justification] | [Weight × Score] |\n| [Criterion 2] | [Score] | [Justification] | [Weight × Score] |\n| [Criterion 3] | [Score] | [Justification] | [Weight × Score] |\n| [Criterion 4] | [Score] | [Justification] | [Weight × Score] |\n| [Criterion 5] | [Score] | [Justification] | [Weight × Score] |\n| **TOTAL** | | | [Sum of weighted scores] |\n\n#### Option 2: [Name]\n| Criterion | Score (1-10) | Justification | Weighted Score |\n|-----------|--------------|---------------|---------------|\n| [Criterion 1] | [Score] | [Justification] | [Weight × Score] |\n| [Criterion 2] | [Score] | [Justification] | [Weight × Score] |\n| [Criterion 3] | [Score] | [Justification] | [Weight × Score] |\n| [Criterion 4] | [Score] | [Justification] | [Weight × Score] |\n| [Criterion 5] | [Score] | [Justification] | [Weight × Score] |\n| **TOTAL** | | | [Sum of weighted scores] |\n\n[Repeat for additional options]\n\n## Bias Identification\n### Potential Biases Identified\n- [Bias 1]: [Description of how this bias might be influencing evaluation]\n- [Bias 2]: [Description of how this bias might be influencing evaluation]\n- [Bias 3]: [Description of how this bias might be influencing evaluation]\n\n### Bias Mitigation Approaches\n- [Approach 1]: [How this was addressed in the evaluation]\n- [Approach 2]: [How this was addressed in the evaluation]\n- [Approach 3]: [How this was addressed in the evaluation]\n\n## Sensitivity Analysis\n### Key Assumptions\n1. [Assumption 1]\n2. [Assumption 2]\n3. [Assumption 3]\n\n### Sensitivity Testing Results\n| Assumption | Variation | Impact on Option 1 | Impact on Option 2 | Impact on Option 3 |\n|------------|-----------|---------------------|---------------------|---------------------|\n| [Assumption 1] | [Change] | [Impact] | [Impact] | [Impact] |\n| [Assumption 2] | [Change] | [Impact] | [Impact] | [Impact] |\n| [Assumption 3] | [Change] | [Impact] | [Impact] | [Impact] |\n\n### Robustness Assessment\n- Most robust option: [Option]\n- Most sensitive option: [Option]\n- Critical threshold(s): [Describe any critical assumption thresholds]\n\n## Stakeholder Impact Modeling\n| Stakeholder | Option 1 Impact | Option 2 Impact | Option 3 Impact | Stakeholder Preference |\n|-------------|-----------------|-----------------|-----------------|------------------------|\n| [Stakeholder 1] | [Impact] | [Impact] | [Impact] | [Preference] |\n| [Stakeholder 2] | [Impact] | [Impact] | [Impact] | [Preference] |\n| [Stakeholder 3] | [Impact] | [Impact] | [Impact] | [Preference] |\n\n### Stakeholder Alignment\n- Areas of stakeholder agreement: [Describe]\n- Areas of stakeholder divergence: [Describe]\n- Approaches to address misalignment: [Strategies]\n\n## Risk Assessment\n| Risk | Probability | Impact | Option 1 Exposure | Option 2 Exposure | Option 3 Exposure | Mitigation Approach |\n|------|------------|--------|-------------------|-------------------|-------------------|---------------------|\n| [Risk 1] | [H/M/L] | [H/M/L] | [Exposure] | [Exposure] | [Exposure] | [Mitigation] |\n| [Risk 2] | [H/M/L] | [H/M/L] | [Exposure] | [Exposure] | [Exposure] | [Mitigation] |\n| [Risk 3] | [H/M/L] | [H/M/L] | [Exposure] | [Exposure] | [Exposure] | [Mitigation] |\n\n## Evaluation Summary\n- Highest scoring option: [Option name] ([Score])\n- Most robust option: [Option name]\n- Stakeholder preferred option: [Option name]\n- Lowest risk option: [Option name]\n- Recommendation for final decision: [Option name]\n- Rationale for recommendation: [Summary of key factors]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Decision Finalization Template (15-30 min)
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Decision Finalization Template (15-30 min)', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Decision Finalization - [Decision ID]\n\n## Decision Summary\n- Decision ID: [Reference to initialization document]\n- Decision Title: [Descriptive title]\n- Date of Decision: [Date finalized]\n- Decision Owner: [Primary responsible person]\n- Decision Type: [Strategic/Tactical/Operational]\n- Impact Scope: [Team/Department/Organization]\n\n## Final Decision\n**Selected Option: [Name of chosen option]**\n\n**Key Components:**\n- [Component 1]\n- [Component 2]\n- [Component 3]\n\n## Comprehensive Decision Rationale\n### Primary Decision Drivers\n1. [Key factor 1]\n2. [Key factor 2]\n3. [Key factor 3]\n\n### Alignment with Criteria\n| Criterion | Weight | Performance | Explanation |\n|-----------|--------|-------------|-------------|\n| [Criterion 1] | [Weight] | [Rating] | [Explanation] |\n| [Criterion 2] | [Weight] | [Rating] | [Explanation] |\n| [Criterion 3] | [Weight] | [Rating] | [Explanation] |\n| [Criterion 4] | [Weight] | [Rating] | [Explanation] |\n| [Criterion 5] | [Weight] | [Rating] | [Explanation] |\n\n### Options Considered\n| Option | Score | Key Strengths | Key Weaknesses | Why Selected/Rejected |\n|--------|-------|---------------|----------------|------------------------|\n| [Option 1] | [Score] | [Strengths] | [Weaknesses] | [Reasoning] |\n| [Option 2] | [Score] | [Strengths] | [Weaknesses] | [Reasoning] |\n| [Option 3] | [Score] | [Strengths] | [Weaknesses] | [Reasoning] |\n\n### Strategic Context Connection\n- [Explanation of how this decision supports broader strategic objectives]\n- [Links to related decisions and organizational priorities]\n- [Future implications and opportunities created]\n\n## Implementation Guidance\n### Implementation Roadmap\n1. [Phase 1]: [Key milestones and timing]\n2. [Phase 2]: [Key milestones and timing]\n3. [Phase 3]: [Key milestones and timing]\n\n### Critical Success Factors\n- [Success factor 1]\n- [Success factor 2]\n- [Success factor 3]\n\n### Risk Management\n| Risk | Probability | Impact | Mitigation Strategy | Owner | Monitoring Approach |\n|------|------------|--------|---------------------|-------|---------------------|\n| [Risk 1] | [H/M/L] | [H/M/L] | [Strategy] | [Owner] | [Monitoring] |\n| [Risk 2] | [H/M/L] | [H/M/L] | [Strategy] | [Owner] | [Monitoring] |\n| [Risk 3] | [H/M/L] | [H/M/L] | [Strategy] | [Owner] | [Monitoring] |\n\n### Resource Requirements\n- Personnel: [Staffing needs]\n- Budget: [Financial resources]\n- Time: [Time commitments]\n- Technology: [Technology requirements]\n- Training: [Skill development needs]\n\n## Learning Capture for Future Decisions\n### Process Effectiveness\n- What worked well: [Aspects of the decision process that were effective]\n- What could be improved: [Aspects of the decision process that could be enhanced]\n- Recommendations for future decisions: [Specific recommendations]\n\n### AI Contribution Assessment\n- Value added: [How AI enhanced the decision process]\n- Limitations: [Where AI input was less valuable]\n- Future enhancement opportunities: [How AI could better support future decisions]\n\n## Decision Communication Plan\n| Stakeholder Group | Key Message | Communication Channel | Timing | Responsible |\n|-------------------|-------------|----------------------|--------|-------------|\n| [Group 1] | [Message] | [Channel] | [When] | [Who] |\n| [Group 2] | [Message] | [Channel] | [When] | [Who] |\n| [Group 3] | [Message] | [Channel] | [When] | [Who] |\n\n## Approval and Commitment\n- Decision maker(s): [Names and roles]\n- Approver signature(s): _________________________\n- Date: [Approval date]\n\n## Decision Review and Adaptation\n- Review checkpoints: [When decision outcomes will be reviewed]\n- Adaptation triggers: [Conditions that would prompt reconsideration]\n- Learning documentation process: [How outcomes will be captured for future decisions]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Sprint Retrospective Analysis Template (Pre-work)
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Sprint Retrospective Analysis Template (Pre-work)', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Sprint Retrospective Analysis - [Sprint/Iteration]\n\n## Sprint Overview\n- Sprint/Iteration: [Name/Number]\n- Duration: [Start date] to [End date]\n- Team: [Team name]\n\n## Quantitative Performance Analysis\n### Velocity & Delivery Metrics\n- Planned story points: [number]\n- Completed story points: [number] ([percentage]%)\n- Velocity trend: [Up/Down/Stable] by [percentage]% (Last 5 sprints)\n- Cycle time: [Average in days] ([Up/Down/Stable] by [percentage]%)\n- Lead time: [Average in days] ([Up/Down/Stable] by [percentage]%)\n- WIP limits: [Adherence percentage]\n\n### Quality Metrics\n- Defects introduced: [number]\n- Defects resolved: [number]\n- Test coverage: [percentage]\n- Code review turnaround: [Average time]\n- Technical debt addressed: [Items/Points]\n- Production incidents: [number]\n\n### Process Metrics\n- Sprint scope changes: [number]\n- Blockers encountered: [number] - Average resolution time: [time]\n- Ceremony effectiveness ratings: [Planning/Daily/Review ratings]\n- Team capacity utilization: [percentage]\n\n## Deep Pattern Analysis\n### Performance Trends\n- Long-term velocity trend (10 sprints): [Chart/analysis]\n- Variance pattern analysis: [Observations about consistency/predictability]\n- Seasonal or cyclical patterns: [Any identified cycles]\n- Correlation with team composition changes: [Analysis]\n\n### Process Patterns\n- Meeting effectiveness pattern: [Analysis of meeting ROI]\n- Communication network analysis: [Key collaboration patterns]\n- Decision quality tracking: [Analysis of decision outcomes]\n- Knowledge flow analysis: [How information moved through team]\n\n### Systemic Patterns\n- Recurring blockers: [Patterns in impediments]\n- Structural constraints: [Organizational limitations identified]\n- Cross-team dependency patterns: [Analysis of external dependencies]\n- Environmental factors: [External influences on performance]\n\n## Previous Action Assessment\n- Actions from last retrospective: [List]\n- Completion rate: [percentage]\n- Impact assessment: [Analysis of effectiveness]\n- Continued relevance: [Ongoing importance of incomplete actions]\n\n## Strategic Alignment Analysis\n- Team objectives: [Current objectives]\n- Progress toward objectives: [Assessment]\n- Alignment with organizational priorities: [Assessment]\n- Value delivery assessment: [Business impact analysis]\n\n## Team Health Assessment\n- Engagement indicators: [Analysis of engagement metrics]\n- Collaboration quality: [Assessment of team interaction]\n- Learning and growth: [Skills development assessment]\n- Work-life balance: [Sustainability assessment]\n\n## AI-Generated Insights\n### Key Strengths to Leverage\n1. [Strength 1]: [Supporting evidence] - [Strategic importance]\n2. [Strength 2]: [Supporting evidence] - [Strategic importance]\n3. [Strength 3]: [Supporting evidence] - [Strategic importance]\n\n### Primary Improvement Opportunities\n1. [Opportunity 1]: [Supporting evidence] - [Potential impact]\n2. [Opportunity 2]: [Supporting evidence] - [Potential impact]\n3. [Opportunity 3]: [Supporting evidence] - [Potential impact]\n\n### Systemic Root Causes\n1. [Root cause 1]: [Pattern evidence] - [Verification approach]\n2. [Root cause 2]: [Pattern evidence] - [Verification approach]\n3. [Root cause 3]: [Pattern evidence] - [Verification approach]\n\n### Potential Experiments\n1. [Experiment 1]: [Hypothesis] - [Testing approach] - [Success measurement]\n2. [Experiment 2]: [Hypothesis] - [Testing approach] - [Success measurement]\n3. [Experiment 3]: [Hypothesis] - [Testing approach] - [Success measurement]\n\n## Discussion Prompts\n1. [Strategic question related to pattern 1]\n2. [Strategic question related to pattern 2]\n3. [Strategic question related to pattern 3]\n4. [Open-ended improvement question]\n5. [Team dynamics question]\n\n## Relevant Context Links\n- [Link to team objectives]\n- [Link to organizational priorities]\n- [Link to previous retrospective summaries]\n- [Link to related team knowledge]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Sprint Retrospective Session Template (60 min)
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Sprint Retrospective Session Template (60 min)', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Sprint Retrospective Session - [Sprint/Iteration]\n\n## Session Information\n- Date: [Date]\n- Facilitator: [Name]\n- Participants: [Names]\n- AI Roles: [Analyst, Challenger, Documentarian]\n\n## Agenda\n1. Analysis Review (10 min)\n2. Focused Pattern Exploration (15 min)\n3. Root Cause Investigation (15 min)\n4. Strategic Improvement Planning (15 min)\n5. Next Steps & Commitments (5 min)\n\n## Analysis Review\n### Key Metrics Summary\n- Velocity: [Quick summary]\n- Quality: [Quick summary]\n- Process: [Quick summary]\n- Team health: [Quick summary]\n\n### AI-Generated Insights Summary\n- Key patterns identified: [Brief list]\n- Primary improvement opportunities: [Brief list]\n- Systemic forces at play: [Brief list]\n\n### Team Response to Analysis\n- Agreements: [Points team aligned with]\n- Disagreements: [Points team disagreed with]\n- Additional perspectives: [Team additions]\n\n## Focused Pattern Exploration\n### Pattern 1: [Name]\n- Detailed description: [Extended explanation]\n- Impact assessment: [Business/team impact]\n- Team discussion notes: [Key points from discussion]\n- Priority assessment: [High/Medium/Low]\n\n### Pattern 2: [Name]\n- Detailed description: [Extended explanation]\n- Impact assessment: [Business/team impact]\n- Team discussion notes: [Key points from discussion]\n- Priority assessment: [High/Medium/Low]\n\n### Pattern 3: [Name]\n- Detailed description: [Extended explanation]\n- Impact assessment: [Business/team impact]\n- Team discussion notes: [Key points from discussion]\n- Priority assessment: [High/Medium/Low]\n\n## Root Cause Investigation\n### Priority Pattern: [Selected pattern]\n#### Root Cause Analysis\n- Why 1: [First level cause]\n  - Why 2: [Second level cause]\n    - Why 3: [Third level cause]\n      - Why 4: [Fourth level cause]\n        - Why 5: [Fifth level cause - root]\n\n#### Systemic Forces Identified\n- [Force 1]: [Description and influence]\n- [Force 2]: [Description and influence]\n- [Force 3]: [Description and influence]\n\n#### AI Challenge Questions & Team Responses\n- [Challenge 1]: [Team response]\n- [Challenge 2]: [Team response]\n- [Challenge 3]: [Team response]\n\n#### Validated Root Cause(s)\n1. [Root cause 1]: [Validation evidence]\n2. [Root cause 2]: [Validation evidence]\n\n## Strategic Improvement Planning\n### Improvement Initiatives\n1. [Initiative 1]:\n   - Target root cause: [Cause being addressed]\n   - Approach: [Description of improvement]\n   - Expected impact: [Anticipated benefits]\n   - Success measurement: [How success will be determined]\n   - Resources required: [What''s needed to implement]\n\n2. [Initiative 2]:\n   - Target root cause: [Cause being addressed]\n   - Approach: [Description of improvement]\n   - Expected impact: [Anticipated benefits]\n   - Success measurement: [How success will be determined]\n   - Resources required: [What''s needed to implement]\n\n### Experimental Approaches\n1. [Experiment 1]:\n   - Hypothesis: [What we believe]\n   - Test: [How we''ll test it]\n   - Duration: [How long we''ll run the experiment]\n   - Data collection: [What we''ll measure]\n   - Success criteria: [How we''ll evaluate results]\n\n### AI Effectiveness Predictions\n- Initiative 1 prediction: [AI-generated prediction with reasoning]\n- Initiative 2 prediction: [AI-generated prediction with reasoning]\n- Experiment 1 prediction: [AI-generated prediction with reasoning]\n\n## Next Steps & Commitments\n### Action Items\n- [ ] [Action description] (@owner) (due: [date]) (success: [measurement])\n- [ ] [Action description] (@owner) (due: [date]) (success: [measurement])\n- [ ] [Action description] (@owner) (due: [date]) (success: [measurement])\n\n### Follow-up Plan\n- Review checkpoint: [Date for mid-cycle check]\n- Next retrospective: [Date]\n- Integration with planning: [How this feeds into next sprint]\n\n## Session Effectiveness\n- Participant engagement: [Assessment]\n- Insight quality: [Assessment]\n- Action item clarity: [Assessment]\n- AI contribution value: [Assessment]\n- Improvement for next session: [Recommendation]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Quarterly Meta-Retrospective Template (120 min)
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Quarterly Meta-Retrospective Template (120 min)', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Quarterly Meta-Retrospective - [Quarter/Period]\n\n## Session Information\n- Date: [Date]\n- Facilitator: [Name]\n- Participants: [Names]\n- AI Roles: [Strategic Analyst, Systems Thinker, Futurist]\n- External Stakeholders: [Names, if applicable]\n\n## Agenda\n1. Performance Trend Analysis (20 min)\n2. System Dynamics Exploration (30 min)\n3. Capability Assessment & Development Planning (30 min)\n4. Practice Evolution (20 min)\n5. Strategic Alignment & Roadmap (20 min)\n\n## Performance Trend Analysis\n### Longitudinal Metrics Review\n- Velocity trends (last 6 sprints): [Chart and analysis]\n- Quality metrics evolution: [Chart and analysis]\n- Process effectiveness indicators: [Chart and analysis]\n- Team health trajectory: [Chart and analysis]\n\n### Pattern Identification Across Cycles\n- Recurring themes: [Patterns appearing in multiple retrospectives]\n- Oscillating patterns: [Patterns that appear, disappear, and reappear]\n- Gradual shifts: [Slow-moving changes over multiple cycles]\n- Breakthrough moments: [Step-changes in performance or practice]\n\n### Action Effectiveness Analysis\n- Categories of actions: [Types of actions taken]\n- Implementation rates by category: [Completion percentages]\n- Impact assessment by category: [Effectiveness ratings]\n- Sustainability of improvements: [Longevity of positive changes]\n\n### Team Discussion Notes\n- Key insights: [Important realizations]\n- Questions raised: [Areas for further exploration]\n- Disagreements: [Points of contention]\n- Consensus areas: [Points of agreement]\n\n## System Dynamics Exploration\n### Systemic Forces Mapping\n- [Diagram or description of system dynamics map]\n- Key reinforcing loops: [Virtuous/vicious cycles identified]\n- Key balancing loops: [Self-regulating mechanisms identified]\n- External variables: [Outside factors influencing the system]\n- Leverage points: [High-impact intervention opportunities]\n\n### Constraint Analysis\n- Primary constraints: [Most limiting factors]\n- Constraint evolution: [How constraints have changed over time]\n- Constraint interactions: [How constraints affect each other]\n- Constraint relaxation opportunities: [Ways to reduce limitations]\n\n### Organizational Context Factors\n- Leadership influences: [How leadership affects outcomes]\n- Structural enablers/barriers: [Organizational structures at play]\n- Cultural factors: [How culture impacts performance]\n- Resource dynamics: [How resource allocation affects outcomes]\n\n### AI-Generated System Insights\n1. [System insight 1]: [Supporting evidence] - [Implications]\n2. [System insight 2]: [Supporting evidence] - [Implications]\n3. [System insight 3]: [Supporting evidence] - [Implications]\n\n## Capability Assessment & Development Planning\n### Team Capability Model\n- Current capability profile: [Assessment of key capabilities]\n- Capability evolution: [How capabilities have changed]\n- Capability gaps: [Areas needing development]\n- Competitive differentiators: [Distinctive capabilities]\n\n### Growth Opportunity Identification\n1. [Growth area 1]:\n   - Current state: [Assessment]\n   - Target state: [Desired capability level]\n   - Development approach: [How to build this capability]\n   - Investment required: [Resources needed]\n   - Expected impact: [Benefits of this capability]\n\n2. [Growth area 2]:\n   - Current state: [Assessment]\n   - Target state: [Desired capability level]\n   - Development approach: [How to build this capability]\n   - Investment required: [Resources needed]\n   - Expected impact: [Benefits of this capability]\n\n3. [Growth area 3]:\n   - Current state: [Assessment]\n   - Target state: [Desired capability level]\n   - Development approach: [How to build this capability]\n   - Investment required: [Resources needed]\n   - Expected impact: [Benefits of this capability]\n\n### AI & Human Collaboration Evolution\n- Current collaboration patterns: [Assessment]\n- Collaboration effectiveness: [Evaluation]\n- Next-level opportunities: [Advanced collaboration possibilities]\n- Development roadmap: [Plan for enhancing collaboration]\n\n## Practice Evolution\n### Practice Assessment\n- Most effective practices: [What''s working well]\n- Practices needing refinement: [What could be improved]\n- Practices to retire: [What should be discontinued]\n- Practice gaps: [New practices needed]\n\n### Innovation Opportunities\n1. [Practice innovation 1]:\n   - Current pain point: [Problem being addressed]\n   - Innovative approach: [New practice description]\n   - Implementation plan: [How to adopt]\n   - Success criteria: [How to evaluate]\n\n2. [Practice innovation 2]:\n   - Current pain point: [Problem being addressed]\n   - Innovative approach: [New practice description]\n   - Implementation plan: [How to adopt]\n   - Success criteria: [How to evaluate]\n\n### Ritual Evolution Plan\n- Context Management evolution: [How to enhance]\n- Decision Framework evolution: [How to enhance]\n- Retrospective System evolution: [How to enhance]\n- Cross-Team Intelligence evolution: [How to enhance]\n- AI Pair Working evolution: [How to enhance]\n\n## Strategic Alignment & Roadmap\n### Strategic Priorities Alignment\n- Organizational priorities: [Key strategic objectives]\n- Alignment assessment: [How well team is aligned]\n- Alignment enhancement opportunities: [Ways to increase alignment]\n\n### Improvement Roadmap\n- Immediate actions (Next quarter):\n  - [ ] [Action item] (@owner) (due: [date]) (success: [criteria])\n  - [ ] [Action item] (@owner) (due: [date]) (success: [criteria])\n  - [ ] [Action item] (@owner) (due: [date]) (success: [criteria])\n\n- Medium-term initiatives (2-3 quarters):\n  - [ ] [Initiative] (@owner) (timeframe: [quarters]) (success: [criteria])\n  - [ ] [Initiative] (@owner) (timeframe: [quarters]) (success: [criteria])\n\n- Long-term transformations (3+ quarters):\n  - [ ] [Transformation] (@sponsor) (timeframe: [quarters]) (success: [criteria])\n  - [ ] [Transformation] (@sponsor) (timeframe: [quarters]) (success: [criteria])\n\n### Commitment & Resources\n- Executive sponsorship needs: [Required support]\n- Resource commitments: [Dedicated resources]\n- Enablement requirements: [Tools, training, etc.]\n- Tracking mechanism: [How progress will be monitored]\n\n## Session Summary\n- Key insights: [Most important realizations]\n- Transformative opportunities: [Highest impact possibilities]\n- Commitments made: [What the team is committing to]\n- Next checkpoint: [When progress will be reviewed]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Annual Strategic Retrospective Template (240 min)
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Annual Strategic Retrospective Template (240 min)', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Annual Strategic Retrospective - [Year]\n\n## Session Information\n- Date: [Date]\n- Facilitator: [Name]\n- Participants: [Names]\n- AI Roles: [Strategic Adviser, Futurist, Systemic Analyst]\n- Executive Stakeholders: [Names]\n\n## Agenda\n1. Annual Performance Review (40 min)\n2. Team Evolution Analysis (40 min)\n3. Business Impact Assessment (40 min)\n4. Capability Development Strategy (40 min)\n5. Strategic Alignment & Visioning (40 min)\n6. Long-term Roadmap Development (40 min)\n\n## Annual Performance Review\n### Comprehensive Metrics Analysis\n- Velocity trajectory (full year): [Chart and analysis]\n- Quality evolution: [Chart and analysis]\n- Predictability trends: [Chart and analysis]\n- Efficiency metrics: [Chart and analysis]\n- Innovation indicators: [Chart and analysis]\n\n### Critical Success & Challenge Analysis\n- Major achievements: [Significant accomplishments]\n- Notable challenges: [Significant obstacles]\n- Pivotal moments: [Key turning points]\n- Missed opportunities: [What could have been better leveraged]\n\n### Comparative Performance\n- Industry benchmarks: [How the team compares]\n- Organizational comparison: [How the team compares internally]\n- Historical performance: [Year-over-year comparison]\n- Target achievement: [Performance against goals]\n\n### AI-Generated Performance Insights\n1. [Performance insight 1]: [Supporting data] - [Strategic implication]\n2. [Performance insight 2]: [Supporting data] - [Strategic implication]\n3. [Performance insight 3]: [Supporting data] - [Strategic implication]\n\n## Team Evolution Analysis\n### Team Composition & Dynamics\n- Composition changes: [How the team has changed]\n- Skill profile evolution: [How capabilities have evolved]\n- Collaboration pattern changes: [How interaction has changed]\n- Team identity development: [How culture has evolved]\n\n### Working Practice Evolution\n- Process maturity progression: [How processes have evolved]\n- Tool usage sophistication: [How tool use has advanced]\n- Knowledge management advancement: [How knowledge practices have matured]\n- Ritual effectiveness trends: [How rituals have evolved]\n\n### Advanced Collaboration Assessment\n- Human-AI collaboration evolution: [How partnership has developed]\n- Cross-team collaboration maturity: [How external collaboration has evolved]\n- Stakeholder engagement effectiveness: [How stakeholder relationships have developed]\n- Remote/distributed work effectiveness: [How distributed work has evolved]\n\n### AI-Generated Evolution Insights\n1. [Evolution insight 1]: [Supporting evidence] - [Strategic implication]\n2. [Evolution insight 2]: [Supporting evidence] - [Strategic implication]\n3. [Evolution insight 3]: [Supporting evidence] - [Strategic implication]\n\n## Business Impact Assessment\n### Value Delivery Analysis\n- Direct business outcomes: [Measurable business impacts]\n- Customer/user impact: [Effects on end users]\n- Strategic initiative contributions: [Support for key initiatives]\n- Innovation impact: [New capabilities/opportunities created]\n\n### Economic Impact\n- Efficiency gains: [Cost/time savings]\n- Quality economics: [Reduced rework/defect costs]\n- Time-to-market impact: [Revenue/opportunity effects]\n- Investment efficiency: [ROI analysis]\n\n### Competitive Position Impact\n- Market differentiation: [Unique capabilities developed]\n- Time-to-market advantage: [Speed improvements]\n- Quality differentiation: [Quality advantages]\n- Innovation advantage: [Novel approaches/solutions]\n\n### Stakeholder Impact Analysis\n- Executive leadership: [Impact on executive goals]\n- Partner teams: [Impact on collaborators]\n- Customers/users: [Impact on end users]\n- Team members: [Impact on team satisfaction/growth]\n\n## Capability Development Strategy\n### Current Capability Assessment\n- Technical capabilities: [Assessment of technical skills]\n- Process capabilities: [Assessment of process maturity]\n- Collaboration capabilities: [Assessment of teamwork effectiveness]\n- Innovation capabilities: [Assessment of creative capacity]\n- Leadership capabilities: [Assessment of direction-setting]\n\n### Strategic Capability Needs\n- Market-driven needs: [Capabilities required by market]\n- Technology-driven needs: [Capabilities required by technology trends]\n- Organization-driven needs: [Capabilities required by organizational strategy]\n- Team aspiration-driven needs: [Capabilities aligned with team goals]\n\n### Capability Development Plan\n1. [Capability area 1]:\n   - Current state: [Assessment]\n   - Target state: [Goal]\n   - Development approach: [How to build]\n   - Investment requirements: [Resources needed]\n   - Timeline: [Development schedule]\n   - Success indicators: [How to measure progress]\n\n2. [Capability area 2]:\n   - Current state: [Assessment]\n   - Target state: [Goal]\n   - Development approach: [How to build]\n   - Investment requirements: [Resources needed]\n   - Timeline: [Development schedule]\n   - Success indicators: [How to measure progress]\n\n3. [Capability area 3]:\n   - Current state: [Assessment]\n   - Target state: [Goal]\n   - Development approach: [How to build]\n   - Investment requirements: [Resources needed]\n   - Timeline: [Development schedule]\n   - Success indicators: [How to measure progress]\n\n### Next-Generation Human-AI Collaboration Vision\n- Advanced collaboration patterns: [Future collaboration models]\n- AI role evolution: [How AI roles will develop]\n- Human skill evolution: [How human roles will develop]\n- Collaborative intelligence opportunities: [Synergistic possibilities]\n\n## Strategic Alignment & Visioning\n### Organizational Strategy Review\n- Key organizational objectives: [Primary organization goals]\n- Industry trends: [Relevant market/industry directions]\n- Competitive landscape: [Competitive positioning]\n- Technology disruption factors: [Emerging technology impacts]\n\n### Team Strategic Positioning\n- Current strategic positioning: [How team currently creates value]\n- Differentiation opportunities: [Unique value creation possibilities]\n- Core mission evolution: [How team purpose may evolve]\n- Value proposition development: [How team''s value will grow]\n\n### Future Vision Development\n- 1-year vision: [What success looks like in 1 year]\n- 3-year horizon: [What success looks like in 3 years]\n- 5-year aspirational state: [What success looks like in 5 years]\n- Transformative possibilities: [Game-changing opportunities]\n\n### Strategic Imperatives\n1. [Strategic imperative 1]: [Description] - [Rationale] - [Success criteria]\n2. [Strategic imperative 2]: [Description] - [Rationale] - [Success criteria]\n3. [Strategic imperative 3]: [Description] - [Rationale] - [Success criteria]\n\n## Long-term Roadmap Development\n### Transformation Initiatives\n1. [Transformation initiative 1]:\n   - Strategic alignment: [How it supports strategy]\n   - Scope: [What it encompasses]\n   - Timeline: [Implementation schedule]\n   - Resources: [What''s required]\n   - Key milestones: [Major checkpoints]\n   - Success measures: [How to evaluate]\n   - Ownership: [Who drives it]\n\n2. [Transformation initiative 2]:\n   - Strategic alignment: [How it supports strategy]\n   - Scope: [What it encompasses]\n   - Timeline: [Implementation schedule]\n   - Resources: [What''s required]\n   - Key milestones: [Major checkpoints]\n   - Success measures: [How to evaluate]\n   - Ownership: [Who drives it]\n\n3. [Transformation initiative 3]:\n   - Strategic alignment: [How it supports strategy]\n   - Scope: [What it encompasses]\n   - Timeline: [Implementation schedule]\n   - Resources: [What''s required]\n   - Key milestones: [Major checkpoints]\n   - Success measures: [How to evaluate]\n   - Ownership: [Who drives it]\n\n### Evolutionary Path\n- Phase 1 (Next quarter): [Focus and goals]\n- Phase 2 (Quarters 2-3): [Focus and goals]\n- Phase 3 (Quarter 4+): [Focus and goals]\n- Long-term transformation: [Ultimate destination]\n\n### Risk Assessment & Mitigation\n| Risk | Probability | Impact | Mitigation Strategy | Owner | Monitoring Approach |\n|------|------------|--------|---------------------|-------|---------------------|\n| [Risk 1] | [H/M/L] | [H/M/L] | [Strategy] | [Owner] | [Monitoring] |\n| [Risk 2] | [H/M/L] | [H/M/L] | [Strategy] | [Owner] | [Monitoring] |\n| [Risk 3] | [H/M/L] | [H/M/L] | [Strategy] | [Owner] | [Monitoring] |\n\n### Executive Alignment & Support\n- Executive sponsorship: [Required executive support]\n- Resource commitments: [Resources required]\n- Organizational enablers: [Needed organizational changes]\n- Strategic protection: [How to ensure continued focus]\n\n## Session Summary & Commitments\n- Breakthrough insights: [Game-changing realizations]\n- Strategic commitments: [High-level commitments made]\n- Immediate next steps: [Actions in next 30 days]\n- Accountability: [How progress will be tracked]\n- Next strategic review: [When the next session will occur]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Weekly Cross-Pollination Template (30 min)
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Weekly Cross-Pollination Template (30 min)', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Weekly Cross-Pollination Session - [Date]\n\n## Session Information\n- Date: [Date]\n- Facilitator: [Name]\n- Participants: [Names and teams]\n- AI Roles: [Connector, Synthesizer]\n\n## Curated Cross-Team Insights\n### Team A: [Team Name]\n- Key developments: [Notable recent activities]\n- Relevant learnings: [Insights that might benefit others]\n- Current challenges: [Problems that others might help with]\n- Success patterns: [Approaches that are working well]\n\n### Team B: [Team Name]\n- Key developments: [Notable recent activities]\n- Relevant learnings: [Insights that might benefit others]\n- Current challenges: [Problems that others might help with]\n- Success patterns: [Approaches that are working well]\n\n### Team C: [Team Name]\n- Key developments: [Notable recent activities]\n- Relevant learnings: [Insights that might benefit others]\n- Current challenges: [Problems that others might help with]\n- Success patterns: [Approaches that are working well]\n\n## AI-Identified Cross-Team Patterns\n### Pattern 1: [Name]\n- Description: [Pattern explanation]\n- Observed in: [Teams where pattern appears]\n- Potential impact: [Why this matters]\n- Exploration questions: [Questions to understand the pattern]\n\n### Pattern 2: [Name]\n- Description: [Pattern explanation]\n- Observed in: [Teams where pattern appears]\n- Potential impact: [Why this matters]\n- Exploration questions: [Questions to understand the pattern]\n\n### Pattern 3: [Name]\n- Description: [Pattern explanation]\n- Observed in: [Teams where pattern appears]\n- Potential impact: [Why this matters]\n- Exploration questions: [Questions to understand the pattern]\n\n## Knowledge Gap Analysis\n### Team A: [Team Name]\n- Knowledge needs: [Areas where this team needs insights]\n- Potential sources: [Teams that might have this knowledge]\n- Connection strategy: [How to facilitate knowledge transfer]\n\n### Team B: [Team Name]\n- Knowledge needs: [Areas where this team needs insights]\n- Potential sources: [Teams that might have this knowledge]\n- Connection strategy: [How to facilitate knowledge transfer]\n\n### Team C: [Team Name]\n- Knowledge needs: [Areas where this team needs insights]\n- Potential sources: [Teams that might have this knowledge]\n- Connection strategy: [How to facilitate knowledge transfer]\n\n## Practice Sharing Opportunities\n### Practice 1: [Name]\n- Originating team: [Where practice started]\n- Description: [What the practice entails]\n- Value demonstrated: [Benefits realized]\n- Teams that could benefit: [Who should consider adopting]\n- Adaptation considerations: [How to tailor for different contexts]\n\n### Practice 2: [Name]\n- Originating team: [Where practice started]\n- Description: [What the practice entails]\n- Value demonstrated: [Benefits realized]\n- Teams that could benefit: [Who should consider adopting]\n- Adaptation considerations: [How to tailor for different contexts]\n\n## Potential Collaboration Opportunities\n1. [Opportunity 1]:\n   - Relevant teams: [Who should be involved]\n   - Description: [What the collaboration entails]\n   - Potential value: [Expected benefits]\n   - Next steps: [How to move forward]\n\n2. [Opportunity 2]:\n   - Relevant teams: [Who should be involved]\n   - Description: [What the collaboration entails]\n   - Potential value: [Expected benefits]\n   - Next steps: [How to move forward]\n\n## Follow-up Actions\n- [ ] [Action description] (Teams: [teams], @owner) (due: [date])\n- [ ] [Action description] (Teams: [teams], @owner) (due: [date])\n- [ ] [Action description] (Teams: [teams], @owner) (due: [date])\n\n## Next Session\n- Date: [Next session date]\n- Focus areas: [Special topics for next session]\n- Preparation needed: [What participants should prepare]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Monthly Cross-Team Ritual Template (90 min)
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Monthly Cross-Team Ritual Template (90 min)', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Monthly Cross-Team Ritual - [Date]\n\n## Session Information\n- Date: [Date]\n- Facilitator: [Name]\n- Teams Represented: [List of teams]\n- Participants: [Names]\n- AI Roles: [Connector, Synthesizer, Strategist]\n\n## Agenda\n1. Cross-Team State of the Union (20 min)\n2. Common Challenge Exploration (25 min)\n3. Collaborative Practice Development (25 min)\n4. Strategic Alignment Reinforcement (10 min)\n5. Joint Commitments (10 min)\n\n## Cross-Team State of the Union\n### Team Status Updates\n- Team A: [Brief status, key achievements, current focus]\n- Team B: [Brief status, key achievements, current focus]\n- Team C: [Brief status, key achievements, current focus]\n\n### AI-Synthesized Cross-Team Landscape\n- Common themes: [Patterns across teams]\n- Divergent approaches: [Areas with different approaches]\n- Interconnection points: [How teams are impacting each other]\n- Collective progress: [Movement toward shared goals]\n\n### Ecosystem Health Indicators\n- Collaboration effectiveness: [Assessment]\n- Knowledge flow quality: [Assessment]\n- Alignment strength: [Assessment]\n- Collective capability growth: [Assessment]\n\n## Common Challenge Exploration\n### Challenge 1: [Name]\n- Description: [Detailed explanation]\n- Affected teams: [Who experiences this]\n- Impact assessment: [Business/team consequences]\n- Current approaches: [How teams are handling it]\n- Root cause hypotheses: [Potential underlying causes]\n- Discussion notes: [Key points from exploration]\n\n### Challenge 2: [Name]\n- Description: [Detailed explanation]\n- Affected teams: [Who experiences this]\n- Impact assessment: [Business/team consequences]\n- Current approaches: [How teams are handling it]\n- Root cause hypotheses: [Potential underlying causes]\n- Discussion notes: [Key points from exploration]\n\n### AI-Generated Challenge Insights\n- Systemic patterns: [Cross-challenge patterns]\n- Opportunity areas: [Where collaboration could help]\n- Innovation triggers: [Potential for creative solutions]\n- External factors: [Outside influences to consider]\n\n## Collaborative Practice Development\n### Practice Focus: [Selected practice area]\n#### Current State Across Teams\n- Team A approach: [Description]\n- Team B approach: [Description]\n- Team C approach: [Description]\n- Effectiveness comparison: [What''s working where]\n\n#### Best Practice Synthesis\n- Key elements of success: [What works well]\n- Context factors: [How context affects success]\n- Adaptation principles: [How to tailor to different teams]\n- Implementation considerations: [Adoption factors]\n\n#### Enhanced Practice Design\n- Practice description: [What the practice entails]\n- Expected benefits: [Anticipated improvements]\n- Required capabilities: [Skills/tools needed]\n- Implementation approach: [How to adopt]\n- Success measures: [How to evaluate effectiveness]\n\n#### Team Adaptation Plans\n- Team A: [How they''ll implement]\n- Team B: [How they''ll implement]\n- Team C: [How they''ll implement]\n- Shared resources: [What can be leveraged across teams]\n\n## Strategic Alignment Reinforcement\n### Organizational Priorities Review\n- Key strategic initiatives: [Major organizational priorities]\n- Recent directional changes: [Recent strategic shifts]\n- Success indicators: [How progress is measured]\n- Collective contribution: [How teams support strategy]\n\n### Cross-Team Alignment Assessment\n- Areas of strong alignment: [Where teams are well-aligned]\n- Alignment gaps: [Where misalignment exists]\n- Alignment enhancement opportunities: [How to improve]\n- Discussion notes: [Key points from alignment discussion]\n\n## Joint Commitments\n### Cross-Team Initiatives\n1. [Initiative 1]:\n   - Participating teams: [Teams involved]\n   - Description: [What this entails]\n   - Expected value: [Benefits anticipated]\n   - Timeline: [When it will happen]\n   - Coordination approach: [How teams will work together]\n   - Success criteria: [How to measure success]\n   - Lead team/person: [Who drives this]\n\n2. [Initiative 2]:\n   - Participating teams: [Teams involved]\n   - Description: [What this entails]\n   - Expected value: [Benefits anticipated]\n   - Timeline: [When it will happen]\n   - Coordination approach: [How teams will work together]\n   - Success criteria: [How to measure success]\n   - Lead team/person: [Who drives this]\n\n### Individual Team Commitments\n- Team A: [Specific commitments]\n- Team B: [Specific commitments]\n- Team C: [Specific commitments]\n\n### Follow-up Mechanism\n- Progress tracking: [How progress will be monitored]\n- Next checkpoint: [When progress will be reviewed]\n- Escalation path: [How to handle issues]\n\n## Session Effectiveness\n- Participation quality: [Assessment]\n- Value generated: [Assessment]\n- Areas to improve: [For next session]\n- AI contribution effectiveness: [Assessment]\n\n## Next Session\n- Date: [Next session date]\n- Focus areas: [Special topics for next time]\n- Preparation needed: [What to prepare]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Quarterly Alignment Session Template (180 min)
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Quarterly Alignment Session Template (180 min)', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Quarterly Cross-Team Alignment Session - [Quarter]\n\n## Session Information\n- Date: [Date]\n- Facilitator: [Name]\n- Teams Represented: [List of teams]\n- Executive Sponsors: [Names]\n- Participants: [Names]\n- AI Roles: [Strategic Synthesizer, Portfolio Analyst, Facilitator]\n\n## Agenda\n1. Strategic Context Sharing (30 min)\n2. Cross-Team Performance Review (30 min)\n3. Portfolio-Level Pattern Identification (40 min)\n4. Cross-Cutting Initiative Development (40 min)\n5. Resource Alignment Planning (40 min)\n\n## Strategic Context Sharing\n### Organizational Direction\n- Strategic priorities: [Key organizational objectives]\n- Market/industry developments: [Relevant external changes]\n- Organizational changes: [Internal structural changes]\n- Executive perspective: [Leadership''s viewpoint]\n\n### Strategic Horizon\n- Short-term focus (3-6 months): [Immediate priorities]\n- Medium-term direction (6-12 months): [Upcoming priorities]\n- Long-term vision (12+ months): [Future direction]\n- Critical success factors: [What must go right]\n\n### Strategic Q&A Session\n- Key questions raised: [Important clarifications sought]\n- Executive responses: [Leadership perspective]\n- Team concerns: [Issues raised by teams]\n- Alignment discussion notes: [Key points from discussion]\n\n## Cross-Team Performance Review\n### Collective Performance Metrics\n- Delivery performance: [Cross-team delivery assessment]\n- Quality metrics: [Cross-team quality assessment]\n- Business outcomes: [Collective business impact]\n- Collaboration effectiveness: [How well teams work together]\n\n### Team-Specific Highlights\n- Team A: [Key achievements, challenges, focus]\n- Team B: [Key achievements, challenges, focus]\n- Team C: [Key achievements, challenges, focus]\n\n### Performance Pattern Analysis\n- Common strengths: [Shared success patterns]\n- Common challenges: [Shared obstacle patterns]\n- Performance variance: [Differences in results]\n- Performance trends: [Direction of movement]\n\n### AI-Generated Performance Insights\n1. [Performance insight 1]: [Evidence] - [Strategic implication]\n2. [Performance insight 2]: [Evidence] - [Strategic implication]\n3. [Performance insight 3]: [Evidence] - [Strategic implication]\n\n## Portfolio-Level Pattern Identification\n### System-Level Patterns\n#### Pattern 1: [Name]\n- Description: [Detailed explanation]\n- Evidence across teams: [How it manifests]\n- Business impact: [Effect on outcomes]\n- Root causes: [Underlying drivers]\n- Strategic significance: [Why it matters]\n- Discussion notes: [Key points from exploration]\n\n#### Pattern 2: [Name]\n- Description: [Detailed explanation]\n- Evidence across teams: [How it manifests]\n- Business impact: [Effect on outcomes]\n- Root causes: [Underlying drivers]\n- Strategic significance: [Why it matters]\n- Discussion notes: [Key points from exploration]\n\n#### Pattern 3: [Name]\n- Description: [Detailed explanation]\n- Evidence across teams: [How it manifests]\n- Business impact: [Effect on outcomes]\n- Root causes: [Underlying drivers]\n- Strategic significance: [Why it matters]\n- Discussion notes: [Key points from exploration]\n\n### Dependency Mapping\n- Critical dependencies: [Key cross-team dependencies]\n- Dependency health assessment: [How well managed]\n- Risk areas: [Problematic dependencies]\n- Improvement opportunities: [How to enhance]\n\n### Knowledge Flow Analysis\n- Knowledge transfer effectiveness: [Assessment]\n- Information silos: [Isolated knowledge areas]\n- Knowledge amplification points: [Where knowledge is leveraged]\n- Knowledge enhancement opportunities: [How to improve]\n\n## Cross-Cutting Initiative Development\n### Initiative 1: [Name]\n- Strategic alignment: [How it supports strategy]\n- Scope: [What it encompasses]\n- Participating teams: [Who''s involved]\n- Expected benefits: [Anticipated outcomes]\n- Success criteria: [How success will be measured]\n- Timeline: [When it will happen]\n- Resources required: [What''s needed]\n- Governance approach: [How it will be managed]\n- Executive sponsor: [Leadership sponsor]\n- Initiative lead: [Who drives this]\n\n### Initiative 2: [Name]\n- Strategic alignment: [How it supports strategy]\n- Scope: [What it encompasses]\n- Participating teams: [Who''s involved]\n- Expected benefits: [Anticipated outcomes]\n- Success criteria: [How success will be measured]\n- Timeline: [When it will happen]\n- Resources required: [What''s needed]\n- Governance approach: [How it will be managed]\n- Executive sponsor: [Leadership sponsor]\n- Initiative lead: [Who drives this]\n\n### Initiative 3: [Name]\n- Strategic alignment: [How it supports strategy]\n- Scope: [What it encompasses]\n- Participating teams: [Who''s involved]\n- Expected benefits: [Anticipated outcomes]\n- Success criteria: [How success will be measured]\n- Timeline: [When it will happen]\n- Resources required: [What''s needed]\n- Governance approach: [How it will be managed]\n- Executive sponsor: [Leadership sponsor]\n- Initiative lead: [Who drives this]\n\n## Resource Alignment Planning\n### Capacity Overview\n- Team A capacity: [Available capacity]\n- Team B capacity: [Available capacity]\n- Team C capacity: [Available capacity]\n- Shared resource capacity: [Cross-team resources]\n- Specialized capability availability: [Critical skills]\n\n### Allocation Decision Framework\n- Strategic imperatives: [Must-do priorities]\n- Value optimization: [Highest ROI activities]\n- Risk management: [Risk-based priorities]\n- Capability development: [Learning investments]\n- Allocation principles: [How decisions will be made]\n\n### Resource Allocation Decisions\n- Team A allocation: [How capacity will be used]\n- Team B allocation: [How capacity will be used]\n- Team C allocation: [How capacity will be used]\n- Shared resource allocation: [How shared resources will be used]\n- Specialized capability allocation: [How critical skills will be deployed]\n\n### Bottleneck & Constraint Management\n- Identified bottlenecks: [Resource constraints]\n- Mitigation strategies: [How to address constraints]\n- Executive support needs: [Where leadership help is needed]\n- Escalation process: [How to handle issues]\n\n## Alignment Commitments\n### Executive Commitments\n- Resource commitments: [What leadership will provide]\n- Barrier removal: [Obstacles leadership will address]\n- Decision support: [How decisions will be supported]\n- Visibility & recognition: [How success will be highlighted]\n\n### Team Commitments\n- Team A: [Specific commitments]\n- Team B: [Specific commitments]\n- Team C: [Specific commitments]\n- Cross-team: [Collective commitments]\n\n### Governance & Monitoring\n- Initiative oversight: [How initiatives will be tracked]\n- Cross-team coordination: [How teams will work together]\n- Progress reporting: [How progress will be communicated]\n- Issue resolution: [How problems will be addressed]\n- Success celebration: [How achievements will be recognized]\n\n## Next Steps\n- Immediate actions (next 2 weeks):\n  - [ ] [Action description] (@owner) (due: [date])\n  - [ ] [Action description] (@owner) (due: [date])\n  - [ ] [Action description] (@owner) (due: [date])\n\n- Monthly check-in schedule: [Dates for monthly reviews]\n- Next quarterly session: [Date for next quarterly meeting]\n\n## Session Effectiveness\n- Strategic clarity achieved: [Assessment]\n- Alignment quality: [Assessment]\n- Decision effectiveness: [Assessment]\n- Participant engagement: [Assessment]\n- AI contribution value: [Assessment]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: AI Role Definition Template
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 AI Role Definition', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# AI Role Definition - [Role Name]\n\n## Role Identification\n- Role Name: [Descriptive name]\n- Domain Focus: [Primary domain]\n- Version: [Version number]\n- Created by: [Team member(s)]\n- Date: [Creation date]\n- Last updated: [Update date]\n\n## Role Purpose & Scope\n### Primary Purpose\n[Clear description of the role''s main purpose and value]\n\n### Key Responsibilities\n1. [Responsibility 1]\n2. [Responsibility 2]\n3. [Responsibility 3]\n4. [Responsibility 4]\n5. [Responsibility 5]\n\n### Domain Scope\n- Primary focus: [Core domain]\n- Related domains: [Connected areas]\n- Out of scope: [Explicit exclusions]\n\n## Specialized Capabilities\n### Key Functions\n1. [Function 1]: [Description]\n2. [Function 2]: [Description]\n3. [Function 3]: [Description]\n4. [Function 4]: [Description]\n5. [Function 5]: [Description]\n\n### Knowledge Requirements\n- Core knowledge areas: [Essential domain knowledge]\n- Related knowledge: [Helpful related knowledge]\n- Operational knowledge: [Process/procedural knowledge]\n- Team-specific context: [Team-specific knowledge]\n\n### Tool/Technology Integration\n- Primary tools: [Main tools integrated with]\n- Data sources: [Key data sources]\n- APIs/Services: [Connected services]\n- Output formats: [Expected output formats]\n\n## Collaboration Framework\n### Human-AI Interaction Model\n- Interaction pattern: [Turn-taking/Simultaneous/Interactive/Other]\n- Communication style: [Formal/Conversational/Technical/Other]\n- Escalation triggers: [When to involve humans]\n- Feedback mechanisms: [How AI should solicit feedback]\n\n### Graduated Autonomy Framework\n#### Level 1: Assisted Cognition\n- Tasks: [Appropriate tasks]\n- Authority: [Decision rights]\n- Oversight: [Human verification requirements]\n- Exception handling: [How to address edge cases]\n\n#### Level 2: Collaborative Execution\n- Tasks: [Appropriate tasks]\n- Authority: [Decision rights]\n- Oversight: [Human verification requirements]\n- Exception handling: [How to address edge cases]\n\n#### Level 3: Guided Autonomy\n- Tasks: [Appropriate tasks]\n- Authority: [Decision rights]\n- Oversight: [Human verification requirements]\n- Exception handling: [How to address edge cases]\n\n#### Level 4: Supervised Independence\n- Tasks: [Appropriate tasks]\n- Authority: [Decision rights]\n- Oversight: [Human verification requirements]\n- Exception handling: [How to address edge cases]\n\n### Handoff Protocols\n- Human -> AI handoff: [Process and expectations]\n- AI -> Human handoff: [Process and triggers]\n- Documentation requirements: [What must be documented]\n- Verification procedures: [How outputs are verified]\n\n## Performance Framework\n### Success Criteria\n- Quality standards: [Expected quality level]\n- Efficiency metrics: [Speed/resource expectations]\n- Value indicators: [How value is measured]\n- Learning indicators: [How improvement is assessed]\n\n### Performance Monitoring\n- Metrics to track: [Key performance indicators]\n- Feedback collection: [How feedback is gathered]\n- Improvement mechanism: [How performance evolves]\n- Review cadence: [When performance is evaluated]\n\n## Implementation Details\n### Required Context Package\n- Knowledge base sections: [Required knowledge]\n- Historical examples: [Past examples to learn from]\n- Team terminology: [Specialized vocabulary]\n- Style guidelines: [Communication standards]\n\n### Technical Configuration\n```\n# Base Configuration\nmodel_config:\n  base_model: [Model name]\n  temperature: [Setting]\n  top_p: [Setting]\n  max_tokens: [Setting]\n  presence_penalty: [Setting]\n  frequency_penalty: [Setting]\n\n# Role-specific parameters\nrole_config:\n  domain_focus: [Domain]\n  interaction_style: [Style]\n  specialized_parameters:\n    param1: [Value]\n    param2: [Value]\n```\n\n### Base Prompt Template\n```\n# [Role Name]\n\n## Role Context\n[Role description to prime the AI]\n\n## Domain Knowledge\n[Essential domain knowledge to include]\n\n## Current Task Context\n[Where to insert task-specific context]\n\n## Collaboration Approach\n[Instructions for collaboration style]\n\n## Expected Outputs\n[Format and standards for outputs]\n```\n\n## Evolution & Maintenance\n### Version History\n- v1.0 ([Date]): [Initial creation]\n- v1.1 ([Date]): [Changes made]\n- v2.0 ([Date]): [Major revision]\n\n### Improvement Process\n- Feedback sources: [How feedback is collected]\n- Update criteria: [When role should be updated]\n- Review schedule: [Regular review timing]\n- Ownership: [Who maintains this role]\n\n### Related Roles\n- [Related role 1]: [Relationship description]\n- [Related role 2]: [Relationship description]\n- [Related role 3]: [Relationship description]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Pair Working Session Initialization Template
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Pair Working Session Initialization', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# AI Pair Working Session Initialization\n\n## Session Information\n- Date: [Date]\n- Team Member(s): [Names]\n- AI Role: [Specific role being used]\n- Autonomy Level: [Level from role definition]\n- Session Type: [Code/Design/Analysis/Strategy/Other]\n- Expected Duration: [Estimated time]\n- Session ID: [Unique identifier for tracking]\n\n## Task Definition\n### Objective\n[Clear, specific description of what this session aims to accomplish]\n\n### Scope\n- In scope: [What is included]\n- Out of scope: [What is explicitly excluded]\n- Constraints: [Limitations or requirements]\n\n### Success Criteria\n1. [Specific, measurable criterion]\n2. [Specific, measurable criterion]\n3. [Specific, measurable criterion]\n\n## Knowledge Context\n### Relevant Domain Knowledge\n- [Link to relevant context 1] - [Relevance]\n- [Link to relevant context 2] - [Relevance]\n- [Link to relevant context 3] - [Relevance]\n\n### Specific Task Context\n[Detailed information about the current situation, problem, or opportunity]\n\n### Previous Related Work\n- [Reference to related work 1] - [Relationship]\n- [Reference to related work 2] - [Relationship]\n- [Reference to related work 3] - [Relationship]\n\n## Collaboration Configuration\n### Session Structure\n- Collaboration model: [Turn-taking/Simultaneous/Interactive/Other]\n- Role definition: [Reference to full role definition]\n- Human responsibilities: [Specific to this session]\n- AI responsibilities: [Specific to this session]\n\n### Process Protocol\n1. [Step 1 of the collaboration process]\n2. [Step 2 of the collaboration process]\n3. [Step 3 of the collaboration process]\n4. [Step 4 of the collaboration process]\n\n### Communication Preferences\n- Technical depth: [Level of technical detail]\n- Explanation style: [How concepts should be explained]\n- Questioning approach: [How clarifications should be handled]\n- Feedback style: [How feedback should be given]\n\n## Specialized Tools & Resources\n- Tool 1: [Tool name and purpose]\n- Tool 2: [Tool name and purpose]\n- Resource 1: [Resource and how it will be used]\n- Resource 2: [Resource and how it will be used]\n\n## Checkpoint Plan\n- Initial direction checkpoint: [Timing] - [Focus]\n- Progress checkpoint 1: [Timing] - [Focus]\n- Progress checkpoint 2: [Timing] - [Focus]\n- Final review checkpoint: [Timing] - [Focus]\n\n## Initial Prompt\n```\n[Carefully crafted initial prompt to initiate the session with the AI based on the role definition]\n```\n\n## Post-Session Plan\n- Documentation approach: [How outputs will be documented]\n- Knowledge capture: [What learnings should be preserved]\n- Integration plan: [How outputs will be used]\n- Follow-up activities: [Next steps after session]\n\n## Session Metrics\n- Effectiveness metrics: [How session will be evaluated]\n- Learning objectives: [What should be learned]\n- Pattern documentation: [Collaboration patterns to capture]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Comprehensive Session Log Template
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Comprehensive Session Log', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# AI Pair Working Session Log\n\n## Session Overview\n- Session ID: [Unique identifier]\n- Date: [Date]\n- Duration: [Actual time]\n- Team Member(s): [Names]\n- AI Role: [Specific role used]\n- Task: [Brief description]\n- Session Objective: [What the session aimed to accomplish]\n\n## Session Timeline\n\n### Phase 1: Initialization ([Time])\n- Initial objective statement: [Human''s initial direction]\n- AI role configuration: [How AI was configured]\n- Initial approach alignment: [How direction was established]\n- Key decisions: [Initial decisions made]\n\n### Phase 2: Early Exploration ([Time])\n- Areas explored: [Topics/approaches investigated]\n- Key insights: [Important discoveries]\n- Direction refinements: [How objectives evolved]\n- Challenges encountered: [Early obstacles]\n- Solutions developed: [How challenges were addressed]\n\n### Phase 3: Deep Collaboration ([Time])\n- Main work areas: [Primary focus]\n- Human contributions: [Key human inputs]\n- AI contributions: [Key AI inputs]\n- Breakthrough moments: [Significant advances]\n- Iteration patterns: [How solutions evolved]\n\n### Phase 4: Refinement ([Time])\n- Quality assessment: [How quality was evaluated]\n- Refinement approach: [How solutions were improved]\n- Edge cases addressed: [Specific scenarios handled]\n- Optimization methods: [How solutions were optimized]\n\n### Phase 5: Finalization ([Time])\n- Final review process: [How solution was verified]\n- Success criteria assessment: [Evaluation against criteria]\n- Output preparation: [How deliverables were prepared]\n- Remaining issues: [Unresolved matters]\n\n## Critical Decision Points\n### Decision 1: [Brief description]\n- Context: [Situation leading to decision]\n- Options considered:\n  1. [Option 1] - [Pros/cons]\n  2. [Option 2] - [Pros/cons]\n  3. [Option 3] - [Pros/cons]\n- Decision made: [What was decided]\n- Rationale: [Why this choice was made]\n- Human/AI contributions: [Who contributed what]\n- Impact: [Consequences of this decision]\n\n### Decision 2: [Brief description]\n- Context: [Situation leading to decision]\n- Options considered:\n  1. [Option 1] - [Pros/cons]\n  2. [Option 2] - [Pros/cons]\n  3. [Option 3] - [Pros/cons]\n- Decision made: [What was decided]\n- Rationale: [Why this choice was made]\n- Human/AI contributions: [Who contributed what]\n- Impact: [Consequences of this decision]\n\n### Decision 3: [Brief description]\n- Context: [Situation leading to decision]\n- Options considered:\n  1. [Option 1] - [Pros/cons]\n  2. [Option 2] - [Pros/cons]\n  3. [Option 3] - [Pros/cons]\n- Decision made: [What was decided]\n- Rationale: [Why this choice was made]\n- Human/AI contributions: [Who contributed what]\n- Impact: [Consequences of this decision]\n\n## Challenges & Solutions\n### Challenge 1: [Brief description]\n- Nature of challenge: [Detailed explanation]\n- Impact: [How it affected progress]\n- Solution approach: [How it was addressed]\n- Resolution outcome: [Final result]\n- Learning: [What to remember for future]\n\n### Challenge 2: [Brief description]\n- Nature of challenge: [Detailed explanation]\n- Impact: [How it affected progress]\n- Solution approach: [How it was addressed]\n- Resolution outcome: [Final result]\n- Learning: [What to remember for future]\n\n## Effective Collaboration Patterns\n### Pattern 1: [Pattern name]\n- Description: [How the pattern works]\n- When it emerged: [When it was first used]\n- Effectiveness: [How well it worked]\n- Reuse potential: [Where else it might apply]\n- Implementation notes: [How to use this pattern]\n\n### Pattern 2: [Pattern name]\n- Description: [How the pattern works]\n- When it emerged: [When it was first used]\n- Effectiveness: [How well it worked]\n- Reuse potential: [Where else it might apply]\n- Implementation notes: [How to use this pattern]\n\n## Knowledge Generated\n### New Insights\n1. [Insight 1]: [Explanation and significance]\n2. [Insight 2]: [Explanation and significance]\n3. [Insight 3]: [Explanation and significance]\n\n### Knowledge Base Contributions\n- [Knowledge item 1]: [How it should be added to knowledge base]\n- [Knowledge item 2]: [How it should be added to knowledge base]\n- [Knowledge item 3]: [How it should be added to knowledge base]\n\n## Session Output\n[Summary or link to the session output, e.g., code, document, design, analysis]\n\n## Performance Assessment\n### Success Criteria Achievement\n| Criterion | Achievement Level | Evidence | Notes |\n|-----------|-------------------|----------|-------|\n| [Criterion 1] | [Fully/Partially/Not met] | [Evidence] | [Notes] |\n| [Criterion 2] | [Fully/Partially/Not met] | [Evidence] | [Notes] |\n| [Criterion 3] | [Fully/Partially/Not met] | [Evidence] | [Notes] |\n\n### Efficiency Assessment\n- Time efficiency: [Assessment of time usage]\n- Resource efficiency: [Assessment of resource usage]\n- Quality result: [Assessment of output quality]\n- Innovation level: [Assessment of novelty/creativity]\n\n### Human-AI Synergy\n- Complementary strengths: [How human and AI complemented each other]\n- Role effectiveness: [How well AI fulfilled its role]\n- Communication quality: [How well human and AI communicated]\n- Collaborative flow: [How smoothly the collaboration worked]\n\n## Follow-up Actions\n- [ ] [Action description] (@owner) (due: [date])\n- [ ] [Action description] (@owner) (due: [date])\n- [ ] [Action description] (@owner) (due: [date])\n\n## Continuous Improvement\n### What Worked Well\n1. [Aspect 1]\n2. [Aspect 2]\n3. [Aspect 3]\n\n### Areas for Improvement\n1. [Area 1] - [Improvement idea]\n2. [Area 2] - [Improvement idea]\n3. [Area 3] - [Improvement idea]\n\n### AI Role Refinements\n- [Suggested refinement 1]\n- [Suggested refinement 2]\n- [Suggested refinement 3]\n\n### Process Enhancements\n- [Process improvement 1]\n- [Process improvement 2]\n- [Process improvement 3]\n\n## Future Applications\n- Related tasks: [Where similar approach could apply]\n- Extension opportunities: [How this work could be extended]\n- Integration possibilities: [How this connects to other work]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Graduated Autonomy Framework Template
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'Phase 3 Graduated Autonomy Framework', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# Graduated Autonomy Framework - [Domain Area]\n\n## Framework Overview\n- Domain: [Specific domain area]\n- Version: [Version number]\n- Created by: [Team member(s)]\n- Date: [Creation date]\n- Last updated: [Update date]\n\n## Purpose & Principles\n### Framework Purpose\n[Clear explanation of why this framework exists and what it aims to accomplish]\n\n### Guiding Principles\n1. [Principle 1]\n2. [Principle 2]\n3. [Principle 3]\n4. [Principle 4]\n5. [Principle 5]\n\n### Scope & Applicability\n- Applies to: [Specific tasks, roles, or contexts]\n- Does not apply to: [Exclusions]\n- Interaction with other frameworks: [How it relates to other frameworks]\n\n## Task Classification\n### Task Dimensions\n1. **Criticality**:\n   - High: [Definition and examples]\n   - Medium: [Definition and examples]\n   - Low: [Definition and examples]\n\n2. **Complexity**:\n   - High: [Definition and examples]\n   - Medium: [Definition and examples]\n   - Low: [Definition and examples]\n\n3. **Uncertainty**:\n   - High: [Definition and examples]\n   - Medium: [Definition and examples]\n   - Low: [Definition and examples]\n\n4. **Precedent**:\n   - Established: [Definition and examples]\n   - Partial: [Definition and examples]\n   - Novel: [Definition and examples]\n\n### Task Category Matrix\n| Task Category | Criticality | Complexity | Uncertainty | Precedent | Default Autonomy Level |\n|---------------|-------------|------------|-------------|-----------|------------------------|\n| [Category 1]  | [Level]     | [Level]    | [Level]     | [Level]   | [Level 1-4]           |\n| [Category 2]  | [Level]     | [Level]    | [Level]     | [Level]   | [Level 1-4]           |\n| [Category 3]  | [Level]     | [Level]    | [Level]     | [Level]   | [Level 1-4]           |\n| [Category 4]  | [Level]     | [Level]    | [Level]     | [Level]   | [Level 1-4]           |\n| [Category 5]  | [Level]     | [Level]    | [Level]     | [Level]   | [Level 1-4]           |\n\n## Autonomy Levels\n\n### Level 1: Assisted Cognition\n**Description**: AI provides information, suggestions, and analysis but does not take direct action. All outputs require human review and implementation.\n\n**Appropriate for**:\n- [Task category/characteristics]\n- [Task category/characteristics]\n- [Task category/characteristics]\n\n**Process Requirements**:\n- AI responsibilities: [Specific responsibilities]\n- Human responsibilities: [Specific responsibilities]\n- Verification requirements: [How outputs are verified]\n- Documentation requirements: [What must be documented]\n\n**Example Tasks**:\n- [Example task 1]\n- [Example task 2]\n- [Example task 3]\n\n### Level 2: Collaborative Execution\n**Description**: AI actively participates in execution with continuous human collaboration. Both human and AI contribute directly to outputs with frequent alignment.\n\n**Appropriate for**:\n- [Task category/characteristics]\n- [Task category/characteristics]\n- [Task category/characteristics]\n\n**Process Requirements**:\n- AI responsibilities: [Specific responsibilities]\n- Human responsibilities: [Specific responsibilities]\n- Interaction pattern: [How human and AI work together]\n- Verification checkpoints: [When verification occurs]\n- Documentation requirements: [What must be documented]\n\n**Example Tasks**:\n- [Example task 1]\n- [Example task 2]\n- [Example task 3]\n\n### Level 3: Guided Autonomy\n**Description**: AI leads execution with human guidance at key checkpoints. AI has autonomy within defined parameters, with human review at critical stages.\n\n**Appropriate for**:\n- [Task category/characteristics]\n- [Task category/characteristics]\n- [Task category/characteristics]\n\n**Process Requirements**:\n- AI responsibilities: [Specific responsibilities]\n- Human responsibilities: [Specific responsibilities]\n- Required checkpoints: [When human input is required]\n- Parameter boundaries: [Limits of AI discretion]\n- Exception handling: [How exceptions are managed]\n- Documentation requirements: [What must be documented]\n\n**Example Tasks**:\n- [Example task 1]\n- [Example task 2]\n- [Example task 3]\n\n### Level 4: Supervised Independence\n**Description**: AI executes tasks independently with human supervision. AI has broad autonomy with periodic human oversight and final review.\n\n**Appropriate for**:\n- [Task category/characteristics]\n- [Task category/characteristics]\n- [Task category/characteristics]\n\n**Process Requirements**:\n- AI responsibilities: [Specific responsibilities]\n- Human responsibilities: [Specific responsibilities]\n- Supervision approach: [How human monitors]\n- Escalation triggers: [When AI should seek human input]\n- Final verification: [How final output is verified]\n- Documentation requirements: [What must be documented]\n\n**Example Tasks**:\n- [Example task 1]\n- [Example task 2]\n- [Example task 3]\n\n## Qualification & Progression\n### AI Qualification Requirements\n| Autonomy Level | Demonstration Requirements | Verification Process | Qualification Authority |\n|----------------|---------------------------|---------------------|------------------------|\n| Level 1        | [Requirements]           | [Process]           | [Who approves]         |\n| Level 2        | [Requirements]           | [Process]           | [Who approves]         |\n| Level 3        | [Requirements]           | [Process]           | [Who approves]         |\n| Level 4        | [Requirements]           | [Process]           | [Who approves]         |\n\n### Progression Path\n- From Level 1 to 2: [Requirements and process]\n- From Level 2 to 3: [Requirements and process]\n- From Level 3 to 4: [Requirements and process]\n\n### Regression Triggers\n- Regression from Level 4 to 3: [Conditions]\n- Regression from Level 3 to 2: [Conditions]\n- Regression from Level 2 to 1: [Conditions]\n- Suspension of autonomy: [Conditions]\n\n## Implementation Guidance\n### Session Initialization\n- Task classification process: [How to categorize tasks]\n- Autonomy level selection: [How to choose appropriate level]\n- Configuration requirements: [What must be configured]\n- Context requirements: [What context must be provided]\n\n### During Execution\n- Monitoring requirements: [How progress is monitored]\n- Checkpoint protocols: [How checkpoints are conducted]\n- Adaptation procedures: [How to adjust during execution]\n- Exception handling: [How to handle unexpected situations]\n\n### Post-Completion\n- Verification procedures: [How to verify outputs]\n- Documentation requirements: [What must be documented]\n- Learning capture: [How to record learnings]\n- Performance feedback: [How to provide feedback]\n\n## Governance & Oversight\n### Oversight Responsibilities\n- Team level: [Team responsibilities]\n- AI Steward: [Steward responsibilities]\n- Domain Expert: [Expert responsibilities]\n- Management: [Management responsibilities]\n\n### Audit & Compliance\n- Audit frequency: [How often audits occur]\n- Audit scope: [What is examined]\n- Compliance requirements: [Required standards]\n- Records retention: [What records must be kept and for how long]\n\n### Risk Management\n- Risk assessment: [How risks are evaluated]\n- Risk mitigation: [How risks are addressed]\n- Incident response: [How incidents are handled]\n- Continuous improvement: [How framework evolves]\n\n## Framework Evolution\n### Performance Metrics\n- Autonomy effectiveness: [How effectiveness is measured]\n- Human-AI efficiency: [How efficiency is measured]\n- Quality outcomes: [How quality is measured]\n- Learning rate: [How improvement is measured]\n\n### Review & Improvement Process\n- Feedback collection: [How feedback is gathered]\n- Review cadence: [When reviews occur]\n- Update process: [How updates are made]\n- Versioning approach: [How versions are managed]\n\n### Change Management\n- Notification process: [How changes are communicated]\n- Training requirements: [What training is needed for changes]\n- Transition approach: [How transitions between versions occur]\n- Backward compatibility: [How backward compatibility is handled]',
--     1, admin_team_id, NOW());
-- END $$;

-- --
-- -- End of Phase 3 Templates
-- --

-- --
-- -- Inserting Phase 3 Workflows
-- --

-- -- Workflow: AnalyzeContextHealth
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: AnalyzeContextHealth\n# Description: Analyzes a list of documents and their metadata to suggest context health issues.\n\ninputDocumentSelectors:\n  - "Input_ContextHealthAnalysis*" # Designed for manually compiled documents\ninputDateSelector: null\noutputName: "ContextHealthAnalysis_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Review the following list of documents, their modification dates, keywords, and any manually noted relationships from the document titled "{{InputFileName}}".\n  Based *only* on the information provided in this input document:\n\n  1.  **Potential Stale Areas:** Identify up to 3 documents that seem oldest or haven''t been mentioned as related to recent documents, suggesting they might be stale. Provide the document name and its last modified date.\n  2.  **Potential Orphaned Items:** Identify up to 3 documents that are not mentioned as related to any other documents in the "Known Relationships" section (if provided).\n  3.  **Potential Keyword Clusters:** Identify 2-3 groups of documents that share common keywords, suggesting thematic clusters. List the cluster keywords and the associated document names.\n  4.  **Gaps in Relationships:** Based on keywords or document names, suggest 1-2 potential relationships between documents that are not explicitly listed but might be relevant.\n\n  Format your output clearly under these headings.\n\n  INPUT DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```\n\n  Provide only the analysis based on the input document.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 AnalyzeContextHealth', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: IdentifyBoundaryAreas
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: IdentifyBoundaryAreas\n# Description: Identifies potential boundary areas from document lists of multiple teams.\n\ninputDocumentSelectors:\n  - "Input_BoundaryAnalysis*"\ninputDateSelector: null\noutputName: "Output_BoundaryAnalysis_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Review the lists of documents and their associated keywords from different teams, as provided in the document titled "{{InputFileName}}".\n  Based *only* on the document names and keywords provided:\n\n  1.  **Shared Document Mentions/Keywords:** Identify any document names or keywords that appear in the lists of more than one team. For each, list the shared item and the teams involved.\n  2.  **Potential Overlapping Topics:** Based on recurring keywords across different teams, suggest 2-3 potential overlapping topics or boundary areas that might require cross-team discussion or alignment. For each topic, list the supporting keywords and the involved teams.\n  3.  **Potential Dependencies:** Based on document names or keywords (e.g., "ComponentA_Design" from one team and "UsageReport_ComponentA" from another), suggest 1-2 potential dependencies between teams.\n\n  Format your output clearly under these headings.\n\n  INPUT DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 IdentifyBoundaryAreas', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: GenerateDecisionOptions
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: GenerateDecisionOptions\n# Description: Brainstorms decision options based on a problem statement and context.\n\ninputDocumentSelectors:\n  - "DecisionInitialization*"\ninputDateSelector: null\noutputName: "Output_GeneratedOptions_for_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Based on the "Problem Statement", "Decision Criteria", "Stakeholder Perspectives", and "Constraints" sections in the Decision Initialization document titled "{{InputFileName}}", generate 3-5 distinct and creative options to address the core problem.\n\n  For each option:\n  1.  Provide a brief name or title for the option.\n  2.  Provide a 1-2 sentence description of the option.\n  3.  Briefly explain the rationale or how it addresses the problem based on the input.\n\n  Focus on generating diverse approaches.\n\n  DECISION INITIALIZATION DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 GenerateDecisionOptions', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: AnalyzeDecisionFactors
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: AnalyzeDecisionFactors\n# Description: Analyzes decision options, scores, and biases from an evaluation document.\n\ninputDocumentSelectors:\n  - "StructuredEvaluation*"\ninputDateSelector: null\noutputName: "Output_DecisionFactorAnalysis_for_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Review the "Multi-Criteria Analysis" (including option scoring against weighted criteria), "Bias Identification", and "Sensitivity Analysis" (if provided) sections of the Structured Evaluation document titled "{{InputFileName}}".\n\n  Based *only* on the information provided in this input document:\n\n  1.  **Key Differentiating Criteria:** Identify 1-2 criteria that seem to most significantly differentiate the scores between the top options.\n  2.  **Impact of Stated Biases:** For each "Potential Bias Identified" in the input, briefly discuss how it might have influenced the "Justification" or "Score" for one of the options, if evident from the text.\n  3.  **Sensitivity Highlights (if data available):** If the "Sensitivity Testing Results" section is filled, summarize which options appear most/least robust based on the stated assumption variations.\n  4.  **Alignment Check:** Briefly comment on whether the "Highest scoring option" aligns with the "Most robust option" and "Stakeholder preferred option" if these are identified in the "Evaluation Summary" section of the input.\n\n  Format your output clearly.\n\n  STRUCTURED EVALUATION DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 AnalyzeDecisionFactors', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: AnalyzeSprintRetroData
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: AnalyzeSprintRetroData\n# Description: Analyzes manually compiled sprint retrospective data.\n\ninputDocumentSelectors:\n  - "SprintRetroAnalysis*"\ninputDateSelector: null\noutputName: "SprintRetroInsights_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Based *only* on the content of the Sprint Retrospective Analysis document titled "{{InputFileName}}", which includes sections like "Quantitative Performance Analysis", "Deep Pattern Analysis", "Previous Action Assessment", "Team Health Assessment", and "AI-Generated Insights" (from a previous step or human input):\n\n  1.  **Summarize Key Performance Trends:** From the "Quantitative Performance Analysis" and "Deep Pattern Analysis", identify and summarize 2-3 notable performance trends (e.g., in velocity, quality, cycle time).\n  2.  **Highlight Recurring Themes:** From the "Deep Pattern Analysis" and "Previous Action Assessment", identify 1-2 themes or issues that appear to be recurring across sprints or from previous actions.\n  3.  **Identify Potential Systemic Root Causes:** Based on the "Systemic Root Causes" section (if provided with evidence) or by inferring from recurring themes, list 1-2 potential systemic root causes for discussion.\n  4.  **Suggest Discussion Prompts:** Generate 3 thought-provoking questions based on your analysis. These questions should help the team delve deeper into the identified trends, themes, or root causes.\n\n  Format your output clearly under these headings.\n\n  INPUT DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 AnalyzeSprintRetroData', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: SuggestSprintActions
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: SuggestSprintActions\n# Description: Suggests potential action items based on retrospective session notes.\n\ninputDocumentSelectors:\n  - "SprintRetroSession*"\ninputDateSelector: null\noutputName: "Output_SuggestedSprintActions_for_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Review the "Focused Pattern Exploration", "Root Cause Investigation", and "Strategic Improvement Planning" sections of the Retrospective Session Notes from the document titled "{{InputFileName}}".\n  Based on the identified root causes and planned improvement initiatives or experiments:\n\n  Suggest 3-5 concrete, actionable, and measurable (if possible) improvement actions the team could take.\n  For each suggested action:\n  - Provide a clear description of the action.\n  - Briefly state the rationale, linking it to a specific root cause or improvement initiative discussed in the notes.\n\n  Example Format:\n  **Suggested Action 1:**\n  - Description: [Action description]\n  - Rationale: [Rationale based on notes, e.g., "Addresses root cause X discussed under Pattern Y"]\n\n  RETROSPECTIVE SESSION NOTES DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 SuggestSprintActions', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: AnalyzeQuarterlyTrends
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: AnalyzeQuarterlyTrends\n# Description: Analyzes synthesized quarterly retrospective data for broader trends.\n\ninputDocumentSelectors:\n  - "QuarterlyMetaRetro*"\ninputDateSelector: null\noutputName: "Output_QuarterlyTrendsAnalysis_for_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Based *only* on the content of the Quarterly Meta-Retrospective document titled "{{InputFileName}}", which includes sections like "Performance Trend Analysis", "System Dynamics Exploration", and "Capability Assessment":\n\n  1.  **Identify Key Quarterly Performance Trends:** Summarize 2-3 significant performance trends observed over the quarter as described in the "Performance Trend Analysis" section.\n  2.  **Highlight Systemic Dynamics:** From "System Dynamics Exploration", identify 1-2 key systemic forces or constraints that were prominent during the quarter.\n  3.  **Summarize Capability Evolution:** Based on "Capability Assessment & Development Planning", summarize 1-2 key insights about the team''s capability evolution or gaps during the quarter.\n  4.  **Suggest Strategic Discussion Points:** Generate 2-3 strategic questions for the team to consider for the next quarter, based on the overall quarterly analysis.\n\n  Format your output clearly.\n\n  INPUT DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 AnalyzeQuarterlyTrends', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: AnalyzeAnnualPerformance
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: AnalyzeAnnualPerformance\n# Description: Analyzes synthesized annual retrospective data for strategic insights.\n\ninputDocumentSelectors:\n  - "AnnualStrategicRetro*"\ninputDateSelector: null\noutputName: "Output_AnnualPerformanceAnalysis_for_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Based *only* on the content of the Annual Strategic Retrospective document titled "{{InputFileName}}", which includes sections like "Annual Performance Review", "Team Evolution Analysis", "Business Impact Assessment", and "Capability Development Strategy":\n\n  1.  **Summarize Major Annual Achievements & Challenges:** From "Annual Performance Review", list 2-3 major achievements and 2-3 notable challenges of the year.\n  2.  **Key Team Evolution Insights:** From "Team Evolution Analysis", highlight 1-2 significant aspects of the team''s evolution (composition, skills, practices).\n  3.  **Business Impact Highlights:** From "Business Impact Assessment", summarize 1-2 key business impacts delivered by the team during the year.\n  4.  **Strategic Capability Focus:** Based on "Capability Development Strategy", identify 1-2 strategic capability areas that were or should be a focus.\n  5.  **Generate Long-Term Strategic Questions:** Formulate 2-3 questions to guide the team''s long-term strategic visioning based on the annual review.\n\n  Format your output clearly.\n\n  INPUT DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 AnalyzeAnnualPerformance', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: SynthesizeCrossTeamUpdates
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: SynthesizeCrossTeamUpdates\n# Description: Synthesizes updates from multiple teams to find patterns.\n\ninputDocumentSelectors:\n  - "Input_CrossTeamUpdates*"\ninputDateSelector: null\noutputName: "CrossPollinationSummary_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Review the compiled updates or summaries from multiple teams provided in the document titled "{{InputFileName}}".\n  Based *only* on the information within this document:\n\n  1.  **Common Themes or Challenges:** Identify any themes, challenges, or key developments that are mentioned by more than one team.\n  2.  **Potential Knowledge Sharing Opportunities:** Highlight any learnings or successes from one team that could benefit others.\n  3.  **Potential Collaboration Points:** Suggest 1-2 areas where teams might benefit from collaborating based on their reported activities or challenges.\n\n  Format your output clearly.\n\n  INPUT DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 SynthesizeCrossTeamUpdates', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: IdentifySharedChallenges
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: IdentifySharedChallenges\n# Description: Identifies shared challenges and potential common root causes.\n\ninputDocumentSelectors:\n  - "Input_SharedChallengesAnalysis*"\ninputDateSelector: null\noutputName: "Output_SharedChallengesAnalysis_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Review the detailed challenge descriptions from multiple teams provided in the document titled "{{InputFileName}}".\n  Based *only* on this information:\n\n  1.  **Categorize Challenges:** Group the described challenges into 2-4 broad categories.\n  2.  **Identify Cross-Cutting Themes:** For each category, identify any themes or specific issues that are reported by multiple teams.\n  3.  **Suggest Potential Common Root Causes:** For 1-2 of the most prevalent shared challenges, suggest potential underlying root causes that might affect multiple teams.\n\n  Format your output clearly.\n\n  INPUT DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 IdentifySharedChallenges', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: SuggestCollaborativePractices
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: SuggestCollaborativePractices\n# Description: Suggests shared or best practices from a review of team practices.\n\ninputDocumentSelectors:\n  - "Input_TeamPracticesReview*"\ninputDateSelector: null\noutputName: "Output_CollaborativePractices_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Review the descriptions of current practices from multiple teams provided in the document titled "{{InputFileName}}".\n  Based *only* on this information:\n\n  1.  **Identify Highly Effective Practices:** Highlight 1-2 practices described by one team that seem particularly effective or innovative and could be beneficial to others. Explain why.\n  2.  **Identify Areas for Standardization:** Point out 1-2 areas where teams are using different practices for similar tasks, and where a standardized approach might be beneficial.\n  3.  **Suggest a "Hybrid" Best Practice:** If applicable, combine elements from different teams'' practices to suggest one "hybrid" best practice for a common activity.\n\n  Format your output clearly.\n\n  INPUT DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 SuggestCollaborativePractices', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: AnalyzePortfolioPatterns
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: AnalyzePortfolioPatterns\n# Description: Analyzes strategic information from multiple teams for portfolio-level patterns.\n\ninputDocumentSelectors:\n  - "Input_PortfolioReview*"\ninputDateSelector: null\noutputName: "Output_PortfolioPatterns_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  Review the strategic information and performance data from multiple teams/projects, as compiled in the document titled "{{InputFileName}}".\n  Based *only* on this information:\n\n  1.  **Common Strategic Themes:** Identify 2-3 strategic themes or objectives that are common across multiple teams/projects.\n  2.  **Portfolio-Level Risks/Opportunities:** Highlight 1-2 potential risks or opportunities that emerge when looking across the portfolio (e.g., resource contention, synergistic opportunities).\n  3.  **Areas of High/Low Performance Concentration:** Identify if there are particular types of projects or strategic areas where performance (as described in the input) is consistently high or low across the portfolio.\n  4.  **Suggested Discussion Points for Alignment:** Based on the analysis, suggest 2-3 key discussion points for a cross-team strategic alignment session.\n\n  Format your output clearly.\n\n  INPUT DOCUMENT CONTENT:\n  ```\n  {{DocumentContext}}\n  ```';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 AnalyzePortfolioPatterns', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: DraftSectionAdvanced
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: DraftSectionAdvanced\n# Description: Drafts a document section based on detailed instructions and source material in the input document.\n\ninputDocumentSelectors:\n  - "PairInput*"\ninputDateSelector: null\noutputName: "DraftOutput_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  The following input document "{{InputFileName}}" contains a request to draft a text section.\n  The request includes an outline, potentially some source material snippets, and specific instructions regarding tone or key terms.\n\n  Based *only* on the information provided in the input document below, please draft the requested text section.\n  Adhere strictly to the provided outline. Incorporate the source material snippets where relevant.\n  Maintain the specified tone and naturally weave in any key terms mentioned.\n  Aim for a comprehensive and well-structured draft.\n\n  Input Document Content:\n  ```\n  {{DocumentContext}}\n  ```\n\n  Begin your response directly with the drafted section.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 DraftSectionAdvanced', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: BrainstormStrategicIdeas
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: BrainstormStrategicIdeas\n# Description: Brainstorms strategic ideas based on a detailed context.\n\ninputDocumentSelectors:\n  - "PairInput*"\ninputDateSelector: null\noutputName: "BrainstormOutput_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  The input document "{{InputFileName}}" contains a request for brainstorming strategic ideas.\n  It details a problem/opportunity, background context, constraints, and a desired future state.\n\n  Based *only* on this information, generate 5-7 distinct strategic ideas.\n  For each idea:\n  - Provide a concise title.\n  - Briefly explain the core concept of the idea.\n  - Briefly mention how it aligns with the desired future state or addresses the problem within the given constraints.\n\n  Present the ideas as a numbered list.\n\n  Input Document Content:\n  ```\n  {{DocumentContext}}\n  ```\n\n  Begin your response directly with the list of brainstormed strategic ideas.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 BrainstormStrategicIdeas', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: SummarizeComplexDoc
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: SummarizeComplexDoc\n# Description: Summarizes a complex document focusing on user-defined aspects.\n\ninputDocumentSelectors:\n  - "PairInput*"\ninputDateSelector: null\noutputName: "SummaryOutput_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  The input document "{{InputFileName}}" contains a body of text to be summarized AND specific instructions or questions outlining the desired focus areas for the summary.\n\n  Carefully review the "Focus Areas for Summary" (or similar instruction section) and the "Full Text of Document to Summarize" within the input document.\n\n  Based *only* on the provided text and instructions, generate a summary that directly addresses each of the specified focus areas or questions.\n  Structure your output clearly, addressing each point from the focus areas.\n\n  Input Document Content:\n  ```\n  {{DocumentContext}}\n  ```\n\n  Begin your response directly with the focused summary.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'Phase 3 SummarizeComplexDoc', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- --
-- -- End of Phase 3 Workflows
-- --

-- --
-- -- Inserting LACM Templates
-- --

-- -- Template: Strategy
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM Strategy', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Strategy - Effective Date: {{CurrentDate_YYYY-MM-DD}}\n\n## 1. Vision\n*Where are you going long-term?*\n-\n\n## 2. Mission\n*What do you do day-to-day?*\n-\n\n## 3. Core Values\n*What principles guide your actions?*\n-\n-\n\n## 4. Strategic Pillars / Themes\n*What are the 3-5 major areas of focus to achieve your vision?*\n- Pillar 1:\n- Pillar 2:\n\n## 5. Key Goals (Long-Term / Annual)\n*What major objectives support your pillars for the next 12-24 months?*\n- Goal A:\n- Goal B:\n\n## 6. Target Audience / Market Segments\n*Who are your primary customers/users?*\n- Primary Segment:\n  - Characteristics:\n- Secondary Segment (Optional):\n  - Characteristics:\n\n## 7. Core Offerings / Value Proposition\n*What products/services do you provide and what unique value do they offer?*\n- Offering 1:\n  - Value:\n- Offering 2:\n  - Value:\n\n## 8. Competitive Landscape Overview\n*Who are your main competitors and what is your general positioning against them? (Detailed analysis in `Competitors_YYYY-MM-DD`)*\n- Competitor A:\n- Competitor B:\n\n## 9. Key Success Metrics (Strategic Level)\n*How will you measure the success of this strategy?*\n- Metric 1:\n- Metric 2:\n\n## 10. Assumptions\n*What key assumptions underpin this strategy?*\n-',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: ManualNewsInput
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM ManualNewsInput', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Manual News & External Information Input - {{CurrentDate_YYYY-MM-DD}}\n\n## Instructions for User:\n* Manually research and gather relevant news, articles, blog posts, social media trends, or other external information from the last 24-48 hours.\n* Focus on items potentially impacting your strategy, competitors, target markets, or ongoing projects.\n* For each item, provide a source (if applicable), a brief summary or the full text if concise, and optionally, your initial thoughts on its relevance.\n* This document will be processed by an AI workflow to generate the `DailyNewsAnalysis_YYYY-MM-DD`.\n\n---\n\n## Item 1\n- **Source (URL/Name):**\n- **Date Published:**\n- **Summary / Key Points / Pasted Text:**\n- **Initial Relevance Assessment (Optional):**\n\n## Item 2\n- **Source (URL/Name):**\n- **Date Published:**\n- **Summary / Key Points / Pasted Text:**\n- **Initial Relevance Assessment (Optional):**\n\n## Item 3\n- **Source (URL/Name):**\n- **Date Published:**\n- **Summary / Key Points / Pasted Text:**\n- **Initial Relevance Assessment (Optional):**\n\n*(Add more items as needed)*',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Competitors
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM Competitors', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Competitor Analysis - Last Updated: {{CurrentDate_YYYY-MM-DD}}\n\n## Competitor 1: [Name]\n- **Website:**\n- **Main Focus / Offerings:**\n- **Perceived Strengths:**\n  -\n- **Perceived Weaknesses:**\n  -\n- **Recent Activities / News (Manual Entry - Link to `ManualNewsInput` if source):**\n  -\n- **Strategic Notes:**\n\n## Competitor 2: [Name]\n- **Website:**\n- **Main Focus / Offerings:**\n- **Perceived Strengths:**\n  -\n- **Perceived Weaknesses:**\n  -\n- **Recent Activities / News (Manual Entry):**\n  -\n- **Strategic Notes:**\n\n*(Add more competitors as needed)*',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: TargetMarkets
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM TargetMarkets', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Target Market Analysis - Last Updated: {{CurrentDate_YYYY-MM-DD}}\n\n## Primary Market Segment 1: [e.g., Small Manufacturing Businesses, Germany]\n- **Description:**\n- **Key Characteristics / Demographics:**\n- **Needs / Pain Points:**\n- **Size / Potential (Estimate):**\n- **Trends Affecting This Segment (Manual Entry):**\n\n## Secondary Market Segment 2 (Optional): [e.g., Freelance Consultants in Tech]\n- **Description:**\n- **Key Characteristics / Demographics:**\n- **Needs / Pain Points:**\n- **Size / Potential (Estimate):**\n- **Trends Affecting This Segment (Manual Entry):**\n\n*(Add more segments as needed)*',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: QuarterlyGoals
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM QuarterlyGoals', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Quarterly Goals - Q{{CurrentQuarterNumber}} / {{CurrentYear}}\n\n## Objective 1: [Clear, Ambitious, Qualitative Objective Title]\n*Alignment: Links to Strategic Pillar/Goal X from `Strategy_YYYY-MM-DD`*\n- **Key Result 1.1:** [Specific, Measurable, Achievable, Relevant, Time-bound (SMART) Key Result]\n  - Target:\n  - Current:\n- **Key Result 1.2:** [SMART Key Result]\n  - Target:\n  - Current:\n- **Key Result 1.3:** [SMART Key Result]\n  - Target:\n  - Current:\n\n## Objective 2: [Clear, Ambitious, Qualitative Objective Title]\n*Alignment: Links to Strategic Pillar/Goal Y from `Strategy_YYYY-MM-DD`*\n- **Key Result 2.1:** [SMART Key Result]\n  - Target:\n  - Current:\n- **Key Result 2.2:** [SMART Key Result]\n  - Target:\n  - Current:\n\n*(Add 1-3 more Objectives for the quarter, each with 2-4 Key Results)*\n\n## Overall Confidence Score for this Quarter''s Goals (Manual Assessment):\n* [e.g., 7/10 - Provide brief rationale]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: WeeklyPlanPreview_Initial
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM WeeklyPlanPreview_Initial', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Weekly Plan Preview - Week {{CurrentWeekNumber}} / {{CurrentYear}} (Initial Setup Focus)\n\n*Initial plan for starting with and setting up the LACM process.*\n\n## Main Objectives for Week {{CurrentWeekNumber}} (Aligned with Q{{CurrentQuarterNumber}} Initial Goals)\n\n1.  **Objective:** Complete LACM Initial Document Setup\n    *Why:* Prerequisite for starting daily cycles (links to Q{{CurrentQuarterNumber}} Objective 1).\n2.  **Objective:** Begin Daily LACM Cycle Execution\n    *Why:* Start integrating the process into routine (links to Q{{CurrentQuarterNumber}} Objective 1).\n3.  **Objective (If Applicable):** [Another key early setup goal]\n    *Why:*\n\n## Key Tasks / Projects Requiring Focus in Week {{CurrentWeekNumber}}\n- **Task/Project:** Create initial versions of all required LACM setup documents (Strategy, Competitors, Target Markets, Initial Quarterly Goals, etc.).\n  *Related Objective(s):* 1\n- **Task/Project:** Populate `ManualNewsInput_YYYY-MM-DD` with relevant information for the first AI-driven Daily Analysis.\n  *Related Objective(s):* 2\n- **Task/Project:** Execute the "Daily News & Environment Analysis" AI Workflow for the first time on [Target Day].\n  *Related Objective(s):* 2\n- **Task/Project:** Conduct the "Daily Review & Context Capture" (manual input to `DailyLogInput_YYYY-MM-DD`, then AI processing) for the first time on [Target Day].\n  *Related Objective(s):* 2\n- **Task/Project:** Conduct "Daily Planning" (using AI Workflow based on logs, analysis, this weekly plan) for the first time on [Target Day].\n  *Related Objective(s):* 2\n\n## Notes for the Week\n- Focus on understanding the inputs and outputs of each daily step.\n- Don''t aim for perfection in documents; aim for completion of the initial setup.',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: TaskList
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM TaskList', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Task List - Last Updated: {{CurrentDate_YYYY-MM-DD}}\n\n## Instructions:\n* Add new tasks with a description, priority, status, and optionally an owner and due date.\n* Update status as tasks progress.\n* The AI Daily Planning workflow will consider "To Do" and "In Progress" tasks.\n\n---\n\n## Task ID: [Unique ID, e.g., TSK-001]\n- **Description:**\n- **Priority:** [High / Medium / Low]\n- **Status:** [To Do / In Progress / Blocked / Done / Archived]\n- **Owner (Optional):**\n- **Due Date (Optional):**\n- **Related Goal/Objective (Optional):** [e.g., Q2 Objective 1.1, Strategy Pillar A]\n- **Notes:**\n\n## Task ID: [TSK-002]\n- **Description:**\n- **Priority:**\n- **Status:**\n- **Owner (Optional):**\n- **Due Date (Optional):**\n- **Related Goal/Objective (Optional):**\n- **Notes:**\n\n*(Add more tasks as needed)*',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: AvailableTime
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM AvailableTime', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Estimated Available Focused Work Time - Updated: {{CurrentDate_YYYY-MM-DD}}\n\n## Next 24 Hours (for {{TomorrowDate_YYYY-MM-DD}})\n- **Total Team Focused Hours Available:** [e.g., 6] hours\n- **Breakdown (if team):**\n  - Member A: [e.g., 3] hours\n  - Member B: [e.g., 3] hours\n- **Key Commitments / Blockers of Time:**\n  - [e.g., Meeting X from 10-11 AM]\n  - [e.g., Member A unavailable PM]\n\n## Next 7 Days (Week starting {{NextMondayDate_YYYY-MM-DD}})\n- **Total Team Focused Hours Available:** [e.g., 25] hours\n- **Breakdown (if team):**\n  - Member A: [e.g., 15] hours\n  - Member B: [e.g., 10] hours\n- **Known Absences / Major Time Commitments:**\n  -',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: Processes
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM Processes', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Key Operational Processes - Last Updated: {{CurrentDate_YYYY-MM-DD}}\n\n## Process 1: [Name of Process, e.g., New Feature Development Cycle]\n- **Owner:**\n- **Objective:**\n- **Key Steps:**\n  1.\n  2.\n  3.\n- **Roles Involved & Responsibilities:**\n  -\n- **Key Performance Indicators (KPIs):**\n  -\n- **Associated TIP Workflows (if any):**\n  - [Workflow Name in TIP] - Purpose:\n- **Improvement Notes (from Retrospectives):**\n  -\n\n## Process 2: [Name of Process, e.g., Customer Support Ticket Handling]\n- **Owner:**\n- **Objective:**\n- **Key Steps:**\n  1.\n  2.\n- **Roles Involved & Responsibilities:**\n  -\n- **Key Performance Indicators (KPIs):**\n  -\n- **Associated TIP Workflows (if any):**\n  -\n- **Improvement Notes:**\n  -\n\n*(Add more processes as they are defined/refined)*',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: IdeaBacklog
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM IdeaBacklog', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Idea Backlog - Last Updated: {{CurrentDate_YYYY-MM-DD}}\n\n## Idea ID: [Unique ID, e.g., IDEA-001]\n- **Idea Title/Summary:**\n- **Problem Solved / Opportunity Addressed:**\n- **Source / Inspiration:**\n- **Date Captured:** {{CurrentDate_YYYY-MM-DD}}\n- **Proposer (Optional):**\n- **Initial Assessment:**\n  - Strategic Fit (High/Medium/Low):\n  - Potential Impact (High/Medium/Low):\n  - Feasibility (High/Medium/Low):\n- **Status:** [New / Under Review / Prioritized / Archived / Implemented]\n- **Next Steps / Notes:**\n\n## Idea ID: [IDEA-002]\n- **Idea Title/Summary:**\n- **Problem Solved / Opportunity Addressed:**\n- **Source / Inspiration:**\n- **Date Captured:**\n- **Proposer (Optional):**\n- **Initial Assessment:**\n  - Strategic Fit:\n  - Potential Impact:\n  - Feasibility:\n- **Status:**\n- **Next Steps / Notes:**\n\n*(Add more ideas as they arise)*',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: PrioritizedInnovationInitiatives
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM PrioritizedInnovationInitiatives', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Prioritized Innovation Initiatives - As of: {{CurrentDate_YYYY-MM-DD}}\n\n## Prioritized Initiative 1: [Title from Idea Backlog]\n- **Idea ID:** [Link to `IdeaBacklog` entry]\n- **Brief Description:**\n- **Strategic Rationale for Prioritization:**\n- **Key Success Metrics (if defined):**\n- **Potential Next Steps / Resources Needed:**\n- **Target Quarter for Consideration:** Q[Number] / [Year]\n\n## Prioritized Initiative 2: [Title from Idea Backlog]\n- **Idea ID:**\n- **Brief Description:**\n- **Strategic Rationale for Prioritization:**\n- **Key Success Metrics (if defined):**\n- **Potential Next Steps / Resources Needed:**\n- **Target Quarter for Consideration:**\n\n*(Add more prioritized initiatives)*',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: CustomerFeedback
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM CustomerFeedback', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Customer Feedback Log - Last Updated: {{CurrentDate_YYYY-MM-DD}}\n\n## Feedback Entry 1\n- **Date Received:** {{CurrentDate_YYYY-MM-DD}}\n- **Source:** [e.g., Email, Survey, Call, Meeting with Client X]\n- **Customer (Optional):** [Name/Company]\n- **Product/Service:** [If specific]\n- **Feedback Type:** [Positive / Negative / Suggestion / Bug Report / Question]\n- **Summary of Feedback:**\n- **Key Quotes (if applicable):**\n- **Sentiment (Manual Assessment):** [Positive/Neutral/Negative/Mixed]\n- **Actionable Insights / Themes Identified:**\n- **Follow-up Action Taken / Planned (Optional):**\n  - Action:\n  - Owner:\n  - Status:\n\n## Feedback Entry 2\n- **Date Received:**\n- **Source:**\n- **Customer (Optional):**\n- **Product/Service:**\n- **Feedback Type:**\n- **Summary of Feedback:**\n- **Key Quotes (if applicable):**\n- **Sentiment (Manual Assessment):**\n- **Actionable Insights / Themes Identified:**\n- **Follow-up Action Taken / Planned (Optional):**\n\n*(Add more feedback entries)*',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: SalesHandbook
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM SalesHandbook', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Sales Handbook - Last Updated: {{CurrentDate_YYYY-MM-DD}}\n\n## 1. Sales Philosophy & Approach\n-\n\n## 2. Target Customers & Ideal Customer Profile (ICP)\n*(Reference `TargetMarkets_YYYY-MM-DD`)*\n-\n\n## 3. Product/Service Offerings & Pricing\n*(Reference Core Offerings in `Strategy_YYYY-MM-DD`)*\n- **Offering A:**\n  - Description:\n  - Key Benefits:\n  - Pricing:\n- **Offering B:**\n  - Description:\n  - Key Benefits:\n  - Pricing:\n\n## 4. Sales Process Overview\n- Lead Generation:\n- Qualification:\n- Needs Analysis:\n- Proposal:\n- Closing:\n- Onboarding:\n\n## 5. Key Sales Metrics & Targets\n- [e.g., Monthly Recurring Revenue (MRR)]\n- [e.g., Customer Acquisition Cost (CAC)]\n- [e.g., Sales Cycle Length]\n\n## 6. Sales Tools & Resources\n- CRM:\n- Proposal Templates: [Link to TIP Document name if applicable]\n- Marketing Materials: [Link to TIP Document name if applicable]\n\n## 7. Handling Objections\n- Objection 1:\n  - Response:\n- Objection 2:\n  - Response:\n\n## 8. Competitive Positioning (Sales Focused)\n*(Reference `Competitors_YYYY-MM-DD`)*\n- How we differentiate from Competitor X:\n- Key selling points against Competitor Y:\n\n## 9. Sales Team Structure & Roles (If applicable)\n-',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: DailyLogInput
-- -- Note: This template name might conflict with a general "Daily Log Input" if not distinguished.
-- -- Assuming "DailyLogInput" is specific enough.
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM DailyLogInput', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Daily Log - Input Data for {{CurrentDate_YYYY-MM-DD}}\n\n## Team Member (Optional, if individual inputs): [Your Name]\n\n## 1. Key Accomplishments (Since last log)\n*What did you complete or make significant progress on?*\n-\n-\n\n## 2. Challenges & Blockers Encountered\n*What issues did you face? What''s preventing progress?*\n-\n-\n\n## 3. Key Interactions (Internal/External Meetings, Calls, Emails)\n*Summarize important communications and their outcomes.*\n- Interaction with [Person/Team/Client] regarding [Topic]:\n  - Outcome/Decision:\n  - Action Items (if any):\n-\n\n## 4. Learnings & Insights\n*What did you learn? Any new ideas or observations?*\n-\n-\n\n## 5. Open Points / Questions / Items for Next 24h Focus\n*What needs immediate attention or is top of mind for tomorrow?*\n-\n-\n\n## 6. Relevant External Context Items (from `DailyNewsAnalysis_YYYY-MM-DD` or manual input)\n*Any specific news or external factors that influenced your day or plans?*\n-',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: DailyPlanReview
-- -- This template is described as a structure for AI output / human review.
-- -- It will be inserted as a regular template.
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM DailyPlanReview', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Daily Plan - {{CurrentDate_YYYY-MM-DD}} (Structure for AI Output & Human Review)\n\n## Plan Next 24h (Aligned with KW{{CurrentWeekNumber}} Objectives)\n\n| Priority | Task Description                      | Who    | Effort | Notes / Dependency |\n| :------- | :------------------------------------ | :----- | :----- | :----------------- |\n| High     | [Specific, actionable task 1]         | [Name] | [S/M/L]| [e.g., Blocked by X]|\n| High     | [Specific, actionable task 2]         | [Name] | [S/M/L]|                    |\n| Medium   | [Specific, actionable task 3]         | [Name] | [S/M/L]|                    |\n| Low      | [Specific, actionable task 4]         | [Name] | [S/M/L]|                    |\n*Feasibility Check: Proposed effort roughly aligns with `AvailableTime_YYYY-MM-DD`.*\n\n## Outlook Next 7 Days (Focus on KW{{CurrentWeekNumber}} Objectives from `KW[Num]_WeeklyPlanPreview`)\n- [Key Task/Theme 1 from Weekly Plan Preview]\n- [Key Task/Theme 2 from Weekly Plan Preview]\n\n## Outlook Next 31 Days (Strategic Focus from `Goals_Q[Num]_[Year]` or `Strategy`)\n- [Key Strategic Theme/Milestone 1]\n\n## Review Notes (Human):\n* [Any adjustments made to the AI-proposed plan and why]\n* [Confirm alignment with available time and weekly objectives]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: WeeklyRetroSummary
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM WeeklyRetroSummary', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Weekly Retrospective Summary - Week {{CurrentWeekNumber}} ({{DateRangeOfWeek}})\n\n## Date of Retrospective: {{CurrentDate_YYYY-MM-DD}}\n## Participants:\n-\n\n## 1. What Went Well This Week?\n-\n-\n\n## 2. What Were the Main Challenges / Could Be Improved?\n-\n-\n\n## 3. Key Learnings & Insights from This Week\n-\n-\n\n## 4. Action Items for Improvement (To be added to `TaskList`)\n- **Action 1:**\n  - Owner:\n  - Due Date:\n  - Success Metric (Optional):\n- **Action 2:**\n  - Owner:\n  - Due Date:\n  - Success Metric (Optional):\n\n## 5. Process Improvement Notes (Potential updates for `Processes_Internal`)\n-\n\n## Overall Mood / Sentiment for the Week:\n- [Briefly describe, e.g., Positive, Challenging but Productive, Stressed]',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: MeetingSummary
-- -- This name might conflict with a general "Meeting Summary" template if one exists from other files.
-- -- Adding "" prefix to ensure it's specific to this library's context.
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM MeetingSummary', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Meeting Summary - {{CurrentDate_YYYY-MM-DD}}\n\n**Meeting Topic:**\n**Date & Time:**\n**Attendees:**\n-\n**Apologies:**\n-\n\n## 1. Agenda / Purpose of Meeting\n-\n\n## 2. Key Discussion Points\n-\n-\n-\n\n## 3. Decisions Made\n- Decision 1:\n  - Rationale:\n  - Agreed by:\n- Decision 2:\n\n## 4. Action Items\n| Action Description | Owner | Due Date | Status   | Notes |\n| :----------------- | :---- | :------- | :------- | :---- |\n|                    |       |          | To Do    |       |\n|                    |       |          |          |       |\n\n## 5. Other Notes / Open Questions\n-\n\n## 6. Next Meeting (If applicable)\n- Date/Time:\n- Tentative Agenda:',
--     1, admin_team_id, NOW());
-- END $$;

-- -- Template: DecisionLog
-- DO $$
-- DECLARE
--     template_item_id uuid := public.uuid_generate_v4();
--     template_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (template_item_id, admin_team_id, 'TEMPLATE', 'LACM DecisionLog', true, template_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (template_version_id, template_item_id,
-- E'# LACM Team Decision Log - Last Updated: {{CurrentDate_YYYY-MM-DD}}\n\n## Decision ID: [Unique ID, e.g., DEC-2025-001]\n- **Date of Decision:**\n- **Decision Made:** [Clear statement of the decision]\n- **Problem / Context:** [Briefly describe the issue or situation leading to the decision]\n- **Options Considered (Optional):**\n  - Option A:\n  - Option B:\n- **Rationale for Decision:**\n- **Key Stakeholders / People Involved in Decision:**\n- **Expected Outcome / Impact:**\n- **Follow-up Actions (if any, link to Task List):**\n  - [Task ID from `TaskList`]\n- **Review Date (Optional):**\n\n## Decision ID: [DEC-2025-002]\n- **Date of Decision:**\n- **Decision Made:**\n- **Problem / Context:**\n- **Options Considered (Optional):**\n- **Rationale for Decision:**\n- **Key Stakeholders / People Involved in Decision:**\n- **Expected Outcome / Impact:**\n- **Follow-up Actions (if any, link to Task List):**\n- **Review Date (Optional):**\n\n*(Add more decisions as they are made)*',
--     1, admin_team_id, NOW());
-- END $$;

-- --
-- -- End of LACM Templates
-- --

-- --
-- -- Inserting LACM Workflows - Phase 1: Daily Routine Workflows
-- --

-- -- Workflow: Workflow_DailyNewsAnalysis
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_DailyNewsAnalysis\n# Description: Analyzes manually inputted news against strategy, competitors, and markets.\n\ninputDocumentSelectors: # User will select relevant documents based on these patterns\n  - "ManualNewsInput*" # Expecting one for the current day\n  - "Strategy*"\n  - "Competitors*"\n  - "TargetMarkets*" \ninputDateSelector: null # User selects the relevant dated ''ManualNewsInput''\noutputName: "DailyNewsAnalysis_{{Year}}-{{Month}}-{{Day}}" # Tries to use date from input filename\nprompt: |\n  **Role:** You are an AI News Analyst supporting the LACM process. Your task is to filter and assess external information provided MANUALLY in the input documents for operational relevance.\n  **Goal:** Identify and concisely summarize the MOST relevant news impacting our strategy and markets from the provided input, directly supporting informed daily decision-making.\n  **Context:**\n  - Primary Input: News items are provided in a document matching the pattern "ManualNewsInput*". This document contains manually gathered summaries or pasted text of news from the last 24-48 hours.\n  - Assessment Criteria: Evaluate news relevance based on potential direct impact on objectives outlined in the "Strategy*" document, activities mentioned in the "Competitors*" document, and trends within the "TargetMarkets*" document. All these context documents are part of the input.\n  - Today''s Date: {{CurrentDate_YYYY-MM-DD}}.\n\n  **Task:**\n  1. Carefully review all provided input documents: the news input document and the context documents (Strategy, Competitors, Target Markets).\n  2. From the "ManualNewsInput*" document, select ONLY THE TOP 3-5 items with the HIGHEST potential relevance based on the Assessment Criteria found in the other provided context documents. Prioritize actionable information over general updates.\n  3. For each selected news item, write a concise summary covering:\n      - Source: (As provided in the input document)\n      - Key Point: (1-2 sentence summary of the core information)\n      - Relevance/Impact: (Briefly explain WHY it''s relevant based on the provided Strategy, Competitors, or Target Markets documents. Focus on potential consequence or required action.)\n  4. If an item requires URGENT attention (e.g., significant competitor move, major policy change impacting core business based on provided context), prefix its summary with the flag "**FLAG: IMPORTANT** - ". Use this flag sparingly.\n  5. Generate the output strictly in Markdown format.\n\n  **Format:**\n  ```markdown\n  # Daily News & Environment Analysis - {{CurrentDate_YYYY-MM-DD}}\n  *Based on manual input from {{InputFileName}} and contextual documents.*\n\n  ## Top Relevant News Items\n\n  - **Source:** [Source Name from input]\n    **Key Point:** [1-2 sentence summary]\n    **Relevance/Impact:** [Brief explanation of why it matters based on provided Strategy/Competitors/Target Markets documents]\n\n  - **FLAG: IMPORTANT** - **Source:** [Source Name from input]\n    **Key Point:** [1-2 sentence summary of urgent item]\n    **Relevance/Impact:** [Explanation of urgency and potential consequence based on provided Strategy/Competitors/Target Markets documents]\n\n  *(Repeat for other selected items, max 3-5 total)*\n  ```\n  **Constraints:** Be factual and objective. Base your analysis ONLY on the content within the provided input documents. Avoid speculation. Exclude items with low or indirect relevance. Focus on clarity and brevity.\n  {{DocumentContext}} # This will contain all selected input documents concatenated.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM DailyNewsAnalysis', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: Workflow_DailyLogGenerator
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_DailyLogGenerator\n# Description: Structures team inputs into a formal daily log.\n\ninputDocumentSelectors:\n  - "DailyLogInput*" # Primary input with team''s raw notes\n  - "*DailyPlan" # Previous day''s plan (user selects the correct one)\n  - "DailyNewsAnalysis*" # Today''s news analysis (user selects the correct one)\ninputDateSelector: null\noutputName: "DailyLog_{{InputFileName | replace: ''LACM DailyLogInput_'', '''' | replace: ''.md'', ''''}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  **Role:** You are an AI Documenter supporting the LACM process. Your task is to accurately capture and structure the team''s daily operational context based on the provided input documents.\n  **Goal:** Consolidate and structure the essential events, outcomes, and insights from the team''s input (found in "DailyLogInput*") covering the last 24 hours, creating a clear record for knowledge preservation and planning. Use the previous day''s plan ("*DailyPlan") and today''s news analysis ("DailyNewsAnalysis*") for context.\n  **Context:**\n  - Primary Input Document (Team Notes): Content matching "DailyLogInput*".\n  - Supporting Context Documents:\n    - Previous Day''s Plan: Content matching "*DailyPlan".\n    - Today''s News Analysis: Content matching "DailyNewsAnalysis*".\n  - Today''s Date: {{CurrentDate_YYYY-MM-DD}}.\n\n  **Task:**\n  1. Carefully analyze all provided input documents.\n  2. From the "DailyLogInput*" document, extract and categorize information clearly under the predefined headings below. Focus on concrete facts and outcomes.\n  3. Compare achievements against the "*DailyPlan" (previous day''s plan) if possible, and note alignment or deviations if explicitly mentioned in the input notes.\n  4. Note any relevant links to the day''s external context if mentioned in the input notes or found in "DailyNewsAnalysis*".\n  5. Generate the structured Markdown file.\n\n  **Format:** Use the following Markdown structure precisely:\n  ```markdown\n  # Daily Log - {{CurrentDate_YYYY-MM-DD}}\n\n  ## 1. Accomplishments\n  *(Summarize from "Key Accomplishments" in the input document)*\n  - [Specific task completed or milestone reached. Briefly mention outcome/value.]\n  - [Another accomplishment.]\n\n  ## 2. Challenges & Blockers\n  *(Summarize from "Challenges & Blockers Encountered" in the input document)*\n  - [Specific problem encountered. Mention root cause if known from input.]\n  - [Any blockers preventing progress? Who/what is needed, if mentioned?]\n\n  ## 3. Key Interactions (Internal/External)\n  *(Summarize from "Key Interactions" in the input document)*\n  - **Interaction:** [Meeting/Call with X from input]\n    **Outcome:** [Decision made, key info received, next step agreed from input]\n  - **Interaction:** [Customer email/call from input]\n    **Outcome:** [Feedback received, issue resolved, follow-up needed from input]\n\n  ## 4. Learnings & Insights\n  *(Summarize from "Learnings & Insights" in the input document)*\n  - [Key takeaway, discovery, or something learned that could improve future work from input.]\n  - [Insight gained from data, analysis, or observation from input.]\n\n  ## 5. Open Points / Action Items (for today or carry-over)\n  *(Summarize from "Open Points / Questions / Items for Next 24h Focus" in the input document)*\n  - [Specific small task identified that needs doing from input.]\n  - [Carry-over item from yesterday needing attention from input.]\n\n  ## 6. Relevant External Context (If mentioned in inputs or News Analysis)\n  - [Reference any item from the provided "DailyNewsAnalysis*" or "Relevant External Context Items" in input that directly impacted the day''s status or plans.]\n  ```\n  **Constraints:** Use neutral, factual language. Avoid interpretation unless explicitly stated as a ''Learning/Insight'' in the input. Ensure all key input points are captured concisely under the correct heading. This structure is critical for process consistency and future analysis. Base your output ONLY on the content of the provided documents.\n  {{DocumentContext}}';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM DailyLogGenerator', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: Workflow_DailyPlanGenerator
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_DailyPlanGenerator\n# Description: Drafts a daily plan considering strategic goals, weekly focus, daily context, tasks, and available time.\n\ninputDocumentSelectors: # User selects all relevant documents\n  - "Strategy*" \n  - "Goals_Quarter*" \n  - "*WeeklyPlanPreview*" \n  - "DailyLog*" # Today''s log\n  - "DailyPlan*" # Today''s plan (Note: This was in the source, seems like it might be an error to use today''s plan as input for generating today''s plan. Keeping as per source.)\n  - "DailyNewsAnalysis*" # Today''s news analysis\n  - "TaskList*" \n  - "AvailableTime*" \ninputDateSelector: null\noutputName: "DailyPlan_{{InputFileName | regex_replace: ''.*(DailyLog_|AvailableTime_)([^_]+_[^_]+_[^_]+).*'', ''$2''}}_{{Year}}-{{Month}}-{{Day}}" # Complex attempt to get date part\nprompt: |\n  **Role:** You are an AI Planning Assistant supporting the LACM process. Your task is to draft a focused and realistic daily plan.\n  **Goal:** Propose a prioritized, actionable plan for the next 24 hours that directly contributes to the current Weekly Objectives (from "*WeeklyPlanPreview*") and Quarterly Goals (from "Goals_Quarter*"), considering today''s context ("DailyLog*", "DailyNewsAnalysis*"), overall tasks ("TaskList*"), and available capacity ("AvailableTime*"). Also provide a brief forward look.\n  **Context:**\n  - Strategic Direction: Content from "Strategy*", "Goals_Quarter*".\n  - Weekly Focus: Crucially, align with "*WeeklyPlanPreview*". Identify the current week number if possible from file names or content.\n  - Today''s Status: Content from "DailyLog*" (Accomplishments, Blockers, Open Points).\n  - External Factors: Content from "DailyNewsAnalysis*".\n  - Resources: Content from "TaskList*" (Backlog), "AvailableTime*" (Capacity for next 24h).\n  - Today: {{CurrentDate_YYYY-MM-DD}}. Let''s assume Current Week is {{CurrentWeekNumber}}.\n\n  **Task:**\n  1. **Analyze Inputs:** Synthesize information from all provided documents, paying special attention to the objectives in "*WeeklyPlanPreview*".\n  2. **Identify Priorities:** Determine the most critical tasks based on:\n      - Direct contribution to Weekly/Quarterly goals.\n      - Urgency arising from "DailyLog*" (e.g., resolving blockers).\n      - Tasks from "TaskList*" that align with weekly objectives.\n  3. **Propose 24h Plan:** Draft a list of specific, achievable tasks for the next 24 hours.\n      - Prioritize mercilessly based on alignment and urgency.\n      - Consider dependencies between tasks mentioned in the inputs.\n      - **Crucially, compare proposed effort against "AvailableTime*" for feasibility.**\n      - Suggest task assignments (''Who'') if obvious from context or roles. Estimate rough effort (''Effort'') if possible (e.g., S/M/L or hours).\n  4. **Propose 7d Outlook:** Briefly list the 1-3 most important tasks/themes from the "*WeeklyPlanPreview*" that should be kept in focus over the next 7 days.\n  5. **Propose 31d Outlook:** Briefly list 1-2 key strategic themes or milestones from "Goals_Quarter*" or "Strategy*" relevant in the next month.\n  6. Generate the Markdown file.\n\n  **Format:** Use the following Markdown structure precisely:\n  ```markdown\n  # Daily Plan - {{CurrentDate_YYYY-MM-DD}}\n\n  ## Plan Next 24h (Aligned with KW{{CurrentWeekNumber}} Objectives)\n\n  | Priority | Task Description                      | Who    | Effort | Notes / Dependency |\n  | :------- | :------------------------------------ | :----- | :----- | :----------------- |\n  | High     | [Specific, actionable task 1]         | [Name] | [S/M/L]| [e.g., Blocked by X]|\n  | High     | [Specific, actionable task 2]         | [Name] | [S/M/L]|                    |\n  | Medium   | [Specific, actionable task 3]         | [Name] | [S/M/L]|                    |\n  | Low      | [Specific, actionable task 4]         | [Name] | [S/M/L]|                    |\n  *Feasibility Check: Proposed effort roughly aligns with available time stated in "AvailableTime*".*\n\n  ## Outlook Next 7 Days (Focus on KW{{CurrentWeekNumber}} Objectives)\n  - [Key Task/Theme 1 from Weekly Plan Preview document]\n  - [Key Task/Theme 2 from Weekly Plan Preview document]\n\n  ## Outlook Next 31 Days (Strategic Focus)\n  - [Key Strategic Theme/Milestone 1 from Goals/Strategy documents]\n  ```\n  **Constraints:** Be concrete and action-oriented in the 24h plan. Ensure proposed tasks directly support stated goals found in the input documents. The feasibility check against available time is critical. Keep outlooks high-level. Base your output ONLY on the content of the provided documents.\n  {{DocumentContext}}';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM DailyPlanGenerator', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- --
-- -- End of LACM Workflows - Phase 1: Daily Routine Workflows
-- --

-- --
-- -- Inserting LACM Workflows - Phase 2: Weekly Routine Workflows
-- --

-- -- Workflow: Workflow_WeeklyAnalysis
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_WeeklyAnalysis\n# Description: Summarizes daily news analyses for the week and identifies trends against strategy.\n\ninputDocumentSelectors:\n  - "DailyNewsAnalysis*" # User selects 5-7 relevant daily analyses for the week\n  - "Strategy*" \ninputDateSelector: null # User manually selects the relevant week''s documents\noutputName: "KW{{CurrentWeekNumber}}_WeeklyAnalysis_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  **Role:** You are an AI Analyst supporting the LACM process by synthesizing weekly external trends.\n  **Goal:** Summarize the provided daily external analyses (from "DailyNewsAnalysis*" documents), identify significant recurring themes or emerging trends/patterns, and assess their potential cumulative impact on our strategy (from "Strategy*") to inform tactical planning for Week {{CurrentWeekNumber}}.\n  **Context:**\n  - Primary Input: Content from several "DailyNewsAnalysis*" documents for the past week.\n  - Strategic Lens: Assess findings against objectives and focus areas in the provided "Strategy*" document.\n  - Current Week: {{CurrentWeekNumber}}. Today''s Date: {{CurrentDate_YYYY-MM-DD}}.\n\n  **Task:**\n  1. Analyze all provided "DailyNewsAnalysis*" documents.\n  2. **Identify Recurring Themes:** Group similar news items or recurring topics mentioned throughout these documents.\n  3. **Highlight Emerging Trends/Patterns:** Look for developments that show a direction or acceleration over the week based on the inputs.\n  4. **Synthesize Top 3-5 Insights:** Determine the most strategically significant themes or trends based on their potential impact (positive or negative) on the objectives outlined in "Strategy*".\n  5. **Assess Cumulative Impact:** For each key insight, briefly explain its potential implication for our strategy or operations, based on the provided strategy document.\n  6. **Identify Discussion Points:** Flag 1-2 key insights that most warrant discussion regarding potential tactical adjustments for the upcoming week.\n  7. Generate the Markdown file.\n\n  **Format:** Use the following Markdown structure precisely:\n  ```markdown\n  # Weekly Analysis Summary - Week {{CurrentWeekNumber}} (Generated: {{CurrentDate_YYYY-MM-DD}})\n\n  ## Key External Themes & Trends Observed This Week\n  *(Based on provided Daily News Analysis documents)*\n\n  1.  **Theme/Trend:** [Concise description of the first major theme/trend]\n      **Observations:** [Briefly mention specific examples from daily analyses supporting this]\n      **Potential Strategic Impact (based on `Strategy*`):** [Assess how this could affect goals in the provided strategy document]\n\n  2.  **Theme/Trend:** [Concise description of the second major theme/trend]\n      **Observations:** [...]\n      **Potential Strategic Impact (based on `Strategy*`):** [...]\n\n  *(Repeat for Top 3-5 insights)*\n\n  ## Key Discussion Points for Tactical Planning\n  - **Point 1:** [Highlight the insight most needing discussion regarding next week''s actions]\n  - **Point 2:** [Optional: Second point for discussion]\n  ```\n  **Constraints:** Focus on synthesis and strategic relevance, not just listing daily news. Prioritize insights with potential actionable consequences. Maintain a neutral, analytical tone. Base your output ONLY on the content of the provided documents.\n  {{DocumentContext}}';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM WeeklyAnalysis', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: Workflow_WeeklyRetroPrep
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_WeeklyRetroPrep\n# Description: Analyzes weekly daily logs and plan to prepare for a retrospective.\n\ninputDocumentSelectors:\n  - "DailyLog*" # User selects 5-7 daily logs for the week\n  - "*WeeklyPlanPreview*" # User selects the plan for the week being reviewed\n  - "Processes*" # Optional, user selects if relevant\ninputDateSelector: null\noutputName: "KW{{CurrentWeekNumber}}_RetroPreparation_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  **Role:** You are an AI Analyst supporting the LACM weekly retrospective by identifying patterns in operational data.\n  **Goal:** Analyze the provided "DailyLog*" documents for Week {{CurrentWeekNumber}}, compare against the objectives in "*WeeklyPlanPreview*", and identify recurring patterns (positive and negative) related to workflow, collaboration, and goal achievement. This will provide objective data points for the team retrospective. Reference "Processes*" if provided and relevant.\n  **Context:**\n  - Primary Input: Content from "DailyLog*" documents for the past 7 days.\n  - Planned Work: Content from "*WeeklyPlanPreview*" (objectives set for this week).\n  - Documented Processes (Optional): Content from "Processes*".\n  - Current Week: {{CurrentWeekNumber}}. Today''s Date: {{CurrentDate_YYYY-MM-DD}}.\n\n  **Task:**\n  1. Analyze all provided "DailyLog*" documents, focusing on sections: ''Accomplishments'', ''Challenges & Blockers'', ''Learnings & Insights''.\n  2. **Identify Positive Patterns:** Note recurring types of successes, frequently mentioned effective actions, or positive feedback loops from the logs. Compare accomplishments against the weekly plan document.\n  3. **Identify Negative Patterns:** Note recurring challenges, frequently mentioned blockers, reported inefficiencies, or deviations from planned work in the weekly plan document, based on the daily logs.\n  4. **Correlate with Processes (If `Processes*` is provided):** Where possible, tentatively link identified patterns (especially negative ones) to specific steps or areas in "Processes*". Note if issues seem related to undocumented workflows.\n  5. **Synthesize Key Data Points:** Prepare a neutral summary listing the most prominent positive and negative patterns observed. Avoid judgmental language.\n  6. **Formulate Open Questions:** Based on the patterns, formulate 2-3 open-ended questions designed to spark discussion during the retrospective (e.g., "What contributed to the recurring success in X?", "What might be underlying the repeated challenges with Y?", "How could process Z (from `Processes*` if provided) be adjusted based on observation W?").\n  7. Generate the Markdown file.\n\n  **Format:** Use the following Markdown structure precisely:\n  ```markdown\n  # Weekly Retro Preparation - Week {{CurrentWeekNumber}} (Generated: {{CurrentDate_YYYY-MM-DD}})\n\n  ## Data Analysis from Daily Logs & Weekly Plan\n\n  **Observed Positive Patterns:**\n  - [Recurring success type 1, e.g., "Consistent positive feedback on X demos mentioned in logs"] (Mention frequency if possible from logs)\n  - [Effective action/workflow, e.g., "Use of specific approach Y repeatedly noted as helpful in logs"]\n  - [Alignment: Weekly objectives A & B (from plan document) largely achieved per logs]\n\n  **Observed Challenges/Negative Patterns:**\n  - [Recurring blocker/issue 1, e.g., "Delays in receiving input for task Z mentioned 3 times in logs"] (Note potential link to a process in "Processes*" if provided and clear from logs)\n  - [Inefficiency noted, e.g., "Multiple logs mention difficulty finding information for task X"]\n  - [Deviation: Weekly objective C (from plan document) appears significantly behind based on logs]\n\n  **Potential Discussion Questions:**\n  1. [Open question related to a key positive pattern]\n  2. [Open question related to a key negative pattern/challenge]\n  3. [Optional: Open question about process (from `Processes*` if provided) or collaboration based on data]\n  ```\n  **Constraints:** Present data objectively. Clearly separate observations from potential discussion questions. Focus on patterns, not isolated incidents. Ensure questions are open-ended and promote reflection, not blame. Base your output ONLY on the content of the provided documents.\n  {{DocumentContext}}';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM WeeklyRetroPrep', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: Workflow_WeeklyPlanPreviewGenerator
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_WeeklyPlanPreviewGenerator\n# Description: Drafts a plan preview for the upcoming week.\n\ninputDocumentSelectors:\n  - "*WeeklyAnalysis*" \n  - "*WeeklyRetroSummary*" \n  - "Strategy*" \n  - "Goals_Quarter*" \n  - "TaskList*" \n  - "PrioritizedInnovationInitiatives*" # Optional, user may not select if N/A\ninputDateSelector: null\noutputName: "KW{{CurrentWeekNumber + 1}}_WeeklyPlanPreview_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  **Role:** You are an AI Planning Assistant supporting the LACM weekly planning cycle.\n  **Goal:** Draft a focused and achievable preview of the main objectives and key tasks for the upcoming week (KW{{CurrentWeekNumber + 1}}), ensuring alignment with quarterly goals (from "Goals_Quarter*"), strategic priorities (from "Strategy*"), and incorporating insights from the previous week''s analysis ("*WeeklyAnalysis*") and retrospective summary ("*WeeklyRetroSummary*"). Consider tasks from "TaskList*" and initiatives from "PrioritizedInnovationInitiatives*" if provided.\n  **Context:**\n  - Strategic Guidance: Content from "Strategy*", "Goals_Quarter*".\n  - Key Inputs from Current Week (Week {{CurrentWeekNumber}}): "*WeeklyAnalysis*", "*WeeklyRetroSummary*".\n  - Task & Initiative Context: "TaskList*", "PrioritizedInnovationInitiatives*" (if provided).\n  - Upcoming Week: {{CurrentWeekNumber + 1}}. Today''s Date: {{CurrentDate_YYYY-MM-DD}}.\n\n  **Task:**\n  1. **Synthesize Inputs:** Analyze all context documents to identify key drivers for the upcoming week.\n  2. **Identify Strategic Themes:** Extract relevant objectives from "Goals_Quarter*" and "Strategy*" that require progress in KW{{CurrentWeekNumber + 1}}. Include prioritized innovation initiatives if provided and relevant.\n  3. **Incorporate Recent Insights:** Explicitly consider the ''Discussion Points'' from "*WeeklyAnalysis*" and any actionable improvement items from "*WeeklyRetroSummary*".\n  4. **Propose 3-5 Main Weekly Objectives:** Draft clear, outcome-oriented objectives for KW{{CurrentWeekNumber + 1}}. These should be stepping stones towards the quarterly goals. Frame them as "Achieve X", "Complete Y", "Decide on Z".\n  5. **List Key Supporting Tasks/Projects:** Identify the most significant tasks or project milestones from "TaskList*" or implied by the objectives that need to be tackled in KW{{CurrentWeekNumber + 1}}. Differentiate between ongoing work and new initiatives.\n  6. **Generate the Markdown file.**\n\n  **Format:** Use the following Markdown structure precisely:\n  ```markdown\n  # Weekly Plan Preview - Week {{CurrentWeekNumber + 1}} (Generated: {{CurrentDate_YYYY-MM-DD}})\n\n  *This plan provides focus for daily planning cycles in the upcoming week.*\n\n  ## Main Objectives for Week {{CurrentWeekNumber + 1}} (Aligned with QX Goals)\n\n  1.  **Objective:** [Clear, outcome-oriented objective 1, e.g., "Finalize specification for Feature X"] (Link to QX Goal if clear from input documents)\n      *Why:* [Briefly state strategic reason or context based on inputs]\n  2.  **Objective:** [Clear, outcome-oriented objective 2, e.g., "Resolve key issues identified in KW{{CurrentWeekNumber}} Retro"]\n      *Why:* [Connects to continuous improvement based on retro summary]\n  3.  **Objective:** [Clear, outcome-oriented objective 3]\n      *Why:* [...]\n  *(Max 3-5 objectives)*\n\n  ## Key Tasks / Projects Requiring Focus in Week {{CurrentWeekNumber + 1}}\n  *(Derived from Task List, Innovation Initiatives, or supporting the objectives above)*\n  - **Task/Project:** [Significant task 1]\n    *Related Objective(s):* [Link to objective number(s) above]\n  - **Task/Project:** [Significant task 2]\n    *Related Objective(s):* [...]\n  - **Task/Project:** [Action item from Retro needing completion]\n    *Related Objective(s):* [Objective 2, or relevant objective]\n  - ...\n\n  *Note: Detailed task breakdown occurs during Daily Planning.*\n  ```\n  **Constraints:** Objectives must be specific and outcome-focused. Ensure a clear link between weekly objectives and quarterly goals/strategy based on the provided documents. Keep the list of key tasks high-level. The ''Why'' justification for objectives is important. Base your output ONLY on the content of the provided documents.\n  {{DocumentContext}}';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM WeeklyPlanPreviewGenerator', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- --
-- -- End of LACM Workflows - Phase 2: Weekly Routine Workflows
-- --

-- --
-- -- Inserting LACM Workflows - Phase 3: Monthly Routine Workflows
-- --

-- -- Workflow: Workflow_MonthlyAnalysisStrategyCheck
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_MonthlyAnalysisStrategyCheck\n# Description: Performs a monthly analysis of weekly trends against strategy and goals.\n\ninputDocumentSelectors:\n  - "*WeeklyAnalysis*" # User selects 4-5 weekly analyses for the month\n  - "Strategy*"\n  - "Goals_Quarter*" # Current quarter''s goals\n  - "*MonthlyAnalysisStrategyCheck" # Optional: previous month''s report\ninputDateSelector: null\noutputName: "{{Year}}-{{Month}}_MonthlyAnalysisStrategyCheck"\nprompt: |\n  **Role:** You are an AI Strategy Analyst supporting the LACM monthly review cycle.\n  **Goal:** Synthesize the past month''s weekly analyses (from "*WeeklyAnalysis*"), identify significant trends/deviations, and rigorously assess alignment with current strategy ("Strategy*") and quarterly goals ("Goals_Quarter*"). Highlight key points for strategic discussion. If the previous month''s analysis ("*MonthlyAnalysisStrategyCheck") is provided, use it for trend comparison.\n  **Context:**\n  - Primary Input: Content from "*WeeklyAnalysis*" documents for the specified month.\n  - Strategic Framework: Content from "Strategy*", "Goals_Quarter*".\n  - Historical Context (Optional): Content from a previous "*MonthlyAnalysisStrategyCheck".\n  - Current Month/Year: {{CurrentMonthName}} {{CurrentYear}}. Assume the Quarter from the "Goals_Quarter*" filename (e.g., Q{{CurrentQuarterNumber}}).\n\n  **Task:**\n  1. **Analyze Weekly Inputs:** Review all provided "*WeeklyAnalysis*" documents.\n  2. **Synthesize Monthly Trends:** Identify the 3-5 most significant overarching trends (external or internal patterns implied by multiple weekly reports). If previous month''s analysis is available, compare and note continuing or new trends.\n  3. **Assess Goal Progress:** Evaluate progress towards the objectives listed in "G_Quarter*" based on the cumulative information from the weekly analyses. Note areas clearly on track, lagging, or facing significant challenges.\n  4. **Perform Strategy Alignment Check:** Explicitly compare the identified monthly trends and goal progress against the key pillars/objectives defined in "Strategy*". Are we still aligned? Are strategic assumptions holding?\n  5. **Identify Key Deviations/Challenges/Opportunities:** Highlight significant variances from plan, persistent challenges, or new strategic opportunities revealed during the month.\n  6. **Formulate Strategic Discussion Points:** Based on the analysis, formulate 2-4 specific, high-level questions or points that require management attention or strategic decision-making.\n  7. Generate the Markdown file.\n\n  **Format:** Use the following Markdown structure precisely:\n  ```markdown\n  # Monthly Analysis & Strategy Check - {{CurrentMonthName}} {{CurrentYear}}\n\n  ## 1. Key Trends Observed This Month\n  *(Based on provided Weekly Analysis documents)*\n  - **Trend 1:** [Description of significant trend, note if continuing from last month if that document was provided]\n    *Supporting Evidence:* [Brief reference to weekly analysis themes]\n  - **Trend 2:** [...]\n  - **Trend 3:** [...]\n  *(Max 3-5 key trends)*\n\n  ## 2. Progress Towards Quarterly Goals (Q{{CurrentQuarterNumber}} {{CurrentYear}} from "Goals_Quarter*")\n  - **Objective:** [Objective from "Goals_Quarter*"]\n    *Status:* [On Track / At Risk / Off Track / Completed - based on analysis of weekly reports]\n    *Observations:* [Brief explanation based on monthly analysis of weekly reports]\n  - **Objective:** [...]\n    *Status:* [...]\n    *Observations:* [...]\n  *(Cover all current Quarter Goals based on provided "Goals_Quarter*")*\n\n  ## 3. Strategic Alignment Assessment\n  *(Based on comparison with provided "Strategy*")*\n  - [Assessment point 1 regarding alignment of trends/progress with strategy. Is a specific strategic assumption challenged?]\n  - [Assessment point 2...]\n\n  ## 4. Significant Deviations / Challenges / Opportunities\n  - **Deviation/Challenge:** [Description of major variance or persistent issue]\n  - **Opportunity:** [Description of new strategic opportunity identified]\n\n  ## 5. Key Points for Strategic Discussion\n  1. [Specific question or topic needing management attention, e.g., "How should we respond to Trend X impacting Goal Y?"]\n  2. [Another strategic question, e.g., "Does persistent Challenge Z require a change in approach outlined in Strategy section A?"]\n  *(Max 2-4 points)*\n  ```\n  **Constraints:** Focus on strategic implications. Ensure clear linkage between observations, goal progress, and strategic alignment. Discussion points should be forward-looking. Maintain a concise, executive summary style. Base your output ONLY on the content of the provided documents.\n  {{DocumentContext}}';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM MonthlyAnalysisStrategyCheck', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: Workflow_ContextCondensation
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_ContextCondensation\n# Description: Condenses multiple older documents into a summary of key strategic insights.\n\ninputDocumentSelectors: # User selects a batch of older documents to condense\n  - "DailyLog*"\n  - "*WeeklyAnalysis*"\n  - "DailyNewsAnalysis*" \ninputDateSelector: null # User should select documents from a specific past period.\noutputName: "CondensedContext_{{InputFileName | replace: '''', '''' | truncate: 30, ''''}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  **Role:** You are an AI Archivar supporting the LACM process by condensing historical operational context.\n  **Goal:** From the provided set of older documents ({{InputFileNames}}), extract and synthesize ONLY the most critical long-term strategic events, decisions, trends, and insights. Discard transient operational details, routine updates, and information not relevant for future strategic reviews (e.g., 6-12+ months from now). The aim is to create a highly concise digest.\n  **Context:**\n  - Input Files: The content of multiple documents selected by the user. These could be daily logs, weekly analyses, etc., from a past period.\n  - Retention Focus: Identify information with potential relevance for future annual reviews or understanding long-term strategic evolution. Discard details relevant only to the specific day/week they were created unless they represent a major strategic point.\n\n  **Task:**\n  1. Analyze all provided input documents.\n  2. **Identify Core Strategic Content:** Extract only points discussing:\n      - Major market shifts or significant competitor actions with lasting impact.\n      - Key strategic decisions made, and their rationale if stated.\n      - Significant trends (internal or external) with long-term implications identified during that period.\n      - Outcomes that directly impacted long-term goals or required a shift in strategy.\n      - Significant, unique learnings that changed fundamental approaches.\n  3. **Synthesize and Condense:** Rewrite the extracted core content into a very brief, integrated summary for the entire period covered by the input documents. Use bullet points for clarity. Eliminate redundancy.\n  4. **Ensure No Critical Loss:** Double-check that no truly critical strategic information (as defined above) has been omitted, even if condensing heavily.\n  5. Generate the Markdown file.\n\n  **Format:** Use the following Markdown structure precisely:\n  ```markdown\n  # Condensed Context Summary\n  *Source Documents (approximate period): {{InputFileNames}} (Processed on {{CurrentDate_YYYY-MM-DD}})*\n\n  *This summary preserves key strategic insights from the input documents while omitting operational details.*\n\n  ## Key Strategic Events & Decisions\n  - [Summary of major event/decision 1 from the period]\n  - [...]\n\n  ## Significant Long-Term Trends Identified\n  - [Summary of major trend 1 observed during the period]\n  - [...]\n\n  ## Major Challenges/Outcomes Impacting Strategy\n  - [Summary of significant challenge or outcome related to long-term goals during the period]\n  - [...]\n\n  ## Key Learnings with Enduring Value\n  - [A significant learning that influenced long-term direction or process]\n  - [...]\n  ```\n  **Constraints:** **Be extremely concise.** The primary goal is significant size reduction. Only retain information likely needed for strategic look-backs months or years later. If multiple documents cover the same event, synthesize it once. Base your output ONLY on the content of the provided documents.\n  {{DocumentContext}}';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM ContextCondensation', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: Workflow_MonthlyProcessRetroPrep
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_MonthlyProcessRetroPrep\n# Description: Analyzes monthly weekly retro summaries for process improvement insights.\n\ninputDocumentSelectors:\n  - "*WeeklyRetroSummary*" # User selects 4-5 weekly retro summaries for the month\n  - "Processes*" # The current documented processes\ninputDateSelector: null\noutputName: "{{Year}}-{{Month}}_ProcessRetroPreparation"\nprompt: |\n  **Role:** You are an AI Process Analyst supporting the LACM monthly process review.\n  **Goal:** Analyze the provided "*WeeklyRetroSummary*" documents for the month of {{CurrentMonthName}} {{CurrentYear}}. Identify recurring feedback, suggestions, or issues specifically related to the documented workflows in the provided "Processes*" document. This will provide structured input for the team''s process improvement discussion.\n  **Context:**\n  - Primary Input: Content from "*WeeklyRetroSummary*" documents. Focus on sections about challenges and improvement ideas.\n  - Process Documentation: Content from "Processes*".\n  - Current Month/Year: {{CurrentMonthName}}, {{CurrentYear}}.\n\n  **Task:**\n  1. Analyze the relevant sections (challenges, improvement ideas, action items) of all provided "*WeeklyRetroSummary*" documents.\n  2. **Filter for Process Relevance:** Extract only those points that directly mention, criticize, or suggest changes to a specific process or step documented in "Processes*", or highlight a clear gap where a documented process might be needed.\n  3. **Group by Process Area:** Group the extracted points according to the relevant process name or area from "Processes*".\n  4. **Identify Recurring Themes:** Within each process area, note if the same issue or suggestion appears multiple times across different weekly retros.\n  5. **Synthesize Findings:** Prepare a concise list summarizing the process-related feedback, grouped by process area and highlighting recurring themes.\n  6. Generate the Markdown file.\n\n  **Format:** Use the following Markdown structure precisely:\n  ```markdown\n  # Process Retro Preparation - {{CurrentMonthName}} {{CurrentYear}}\n  *Summary of process-related feedback from weekly retrospectives, cross-referenced with "Processes*".*\n\n  ## Process Area: [Name of Process 1 from "Processes*"]\n  - **Recurring Issue/Suggestion:** [Theme identified across multiple retros, e.g., "Lack of clarity on input requirements for Step X"] (Mention frequency if clear from inputs, e.g., "Noted in 3 retros")\n  - **Specific Feedback:** [Isolated but relevant point from one retro]\n  - ...\n\n  ## Process Area: [Name of Process 2 from "Processes*"]\n  - **Recurring Issue/Suggestion:** [...] (Frequency: X)\n  - **Specific Feedback:** [...]\n  - ...\n\n  ## Potential Process Gaps / Undocumented Areas Mentioned\n  - [Note feedback suggesting a need for process clarification or documentation in a specific area, e.g., "Confusion about handover between Role A and Role B"]\n\n  ```\n  **Constraints:** Focus strictly on feedback related to defined processes or clear process gaps, as found in the input documents. Avoid general complaints not tied to a workflow. Clearly indicate recurring themes. Maintain neutral language. Base your output ONLY on the content of the provided documents.\n  {{DocumentContext}}';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM MonthlyProcessRetroPrep', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- --
-- -- End of LACM Workflows - Phase 3: Monthly Routine Workflows
-- --

-- --
-- -- Inserting LACM Workflows - Phase 4: Quarterly & Annual Routine Workflows
-- --

-- -- Workflow: Workflow_QuarterlyReviewPrep
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_QuarterlyReviewPrep\n# Description: Prepares analysis and draft OKRs for quarterly review and planning.\n\ninputDocumentSelectors: # User selects all relevant documents for the quarter\n  - "*MonthlyAnalysisStrategyCheck"\n  - "Strategy*"\n  - "SalesHandbook*" # Optional\n  - "Goals_Quarter*" # Expiring and potentially next quarter''s draft if iterative\n  - "PrioritizedInnovationInitiatives*" # Optional\n  - "QuarterlyPerformanceData*" # User-created doc with metrics\ninputDateSelector: null\noutputName: "Q{{CurrentQuarterNumber}}_{{Year}}_ReviewPreparation_DraftOKRs_Q{{CurrentQuarterNumber + 1}}"\nprompt: |\n  **Role:** You are an AI Strategy Analyst supporting the LACM quarterly review and planning cycle.\n  **Goal:** Synthesize the concluding quarter''s (Q{{CurrentQuarterNumber}} {{CurrentYear}}) performance and strategic context based on provided monthly reports and performance data. Evaluate progress against Q{{CurrentQuarterNumber}} goals (OKRs from "Goals_Quarter_Q{{CurrentQuarterNumber}}_{{Year}}"). Assess strategic alignment based on "Strategy*" and "SalesHandbook*" (if provided). Propose data-informed, draft Objectives and Key Results (OKRs) for the upcoming quarter (Q{{CurrentQuarterNumber + 1}}) considering "PrioritizedInnovationInitiatives*" (if provided).\n  **Context:**\n  - Monthly Summaries: Content from "*MonthlyAnalysisStrategyCheck" for Q{{CurrentQuarterNumber}}.\n  - Strategic Framework: Content from "Strategy*", "SalesHandbook*".\n  - Concluding Goals: Content from "Goals_Quarter_Q{{CurrentQuarterNumber}}_{{Year}}".\n  - Future Focus (Optional): Content from "PrioritizedInnovationInitiatives*".\n  - Other Inputs (Optional): Relevant financial/performance data summaries provided in other input documents.\n  - Concluded Quarter: Q{{CurrentQuarterNumber}}, {{CurrentYear}}. Upcoming Quarter: Q{{CurrentQuarterNumber + 1}}.\n\n  **Task:**\n  1. **Synthesize Quarterly Performance:** Analyze the monthly reports and performance data. Summarize the 3-5 most significant strategic findings, trends, and outcomes for Q{{CurrentQuarterNumber}}.\n  2. **Evaluate Q{{CurrentQuarterNumber}} OKR Achievement:** For each Objective and Key Result in "Goals_Quarter_Q{{CurrentQuarterNumber}}_{{Year}}", assess the final status (e.g., Achieved, Partially Achieved, Not Achieved) and briefly note key contributing factors or reasons based on the monthly analyses.\n  3. **Assess Strategic Alignment & Validity:** Review the findings from Task 1 & 2 against "Strategy*". Highlight areas where strategic assumptions were validated or challenged. Suggest specific sections of "Strategy*" or "SalesHandbook*" that may warrant discussion or updates.\n  4. **Incorporate Innovation Focus:** Consider "PrioritizedInnovationInitiatives*" if provided; identify which initiatives are ready for potential inclusion in the next quarter''s goals.\n  5. **Draft Q{{CurrentQuarterNumber + 1}} OKRs:** Based on the analysis (especially strategic gaps/opportunities and unfinished business from Q{{CurrentQuarterNumber}}), propose 3-5 ambitious but achievable Objectives for Q{{CurrentQuarterNumber + 1}}. For each Objective, propose 2-4 specific, measurable, achievable, relevant, time-bound (SMART) Key Results. Ensure these draft OKRs clearly contribute to the overarching "Strategy*".\n  6. **Structure for Review:** Generate the Markdown file.\n\n  **Format:** Use the following Markdown structure precisely:\n  ```markdown\n  # Quarterly Review Prep & Q{{CurrentQuarterNumber + 1}} Draft OKRs - Q{{CurrentQuarterNumber}} {{CurrentYear}} (Generated: {{CurrentDate_YYYY-MM-DD}})\n\n  ## 1. Q{{CurrentQuarterNumber}} Performance Summary & Key Strategic Insights\n  *(Based on provided Monthly Analysis, Performance Data, etc.)*\n  - **Insight 1:** [Significant finding/trend from the quarter]\n  - **Insight 2:** [...]\n  - **Insight 3:** [...]\n  *(Max 3-5 key insights)*\n\n  ## 2. Final Status of Q{{CurrentQuarterNumber}} OKRs\n  *(Based on provided "Goals_Quarter_Q{{CurrentQuarterNumber}}_{{Year}}" and performance data)*\n  - **Objective 1:** [Objective text from input]\n    *Final Status:* [Achieved / Partially Achieved / Not Achieved]\n    *Key Results & Notes:*\n      - KR 1.1: [KR text from input] - Status: [Final score/status]. Notes: [Brief reason/context from inputs]\n      - KR 1.2: [...] - Status: [...]. Notes: [...]\n  - **Objective 2:** [...]\n  *(Cover all Q{{CurrentQuarterNumber}} Objectives)*\n\n  ## 3. Strategic Alignment & Validity Check\n  *(Based on comparison with "Strategy*" and "SalesHandbook*")*\n  - [Assessment of how Q{{CurrentQuarterNumber}} outcomes impact a strategic assumption from "Strategy*"]\n  - [Suggestion: Review section X of "Strategy*" based on finding Y]\n\n  ## 4. Draft OKRs for Q{{CurrentQuarterNumber + 1}} {{CurrentYear}} (Proposal for Discussion)\n  *(Considering strategic alignment, Q{{CurrentQuarterNumber}} outcomes, and Innovation Initiatives if provided)*\n  - **Objective 1:** [Proposed Objective - Clear, ambitious, qualitative]\n    *Alignment:* [Links to Strategy Goal X from "Strategy*"]\n    *Key Results:*\n      - KR 1.1: [Specific, measurable result 1]\n      - KR 1.2: [Specific, measurable result 2]\n  - **Objective 2:** [Proposed Objective 2...]\n  *(Propose 3-5 Objectives, each with 2-4 KRs)*\n  ```\n  **Constraints:** Ensure analysis is strategic. OKR evaluation should be factual. Draft OKRs must follow SMART principles. Base your output ONLY on the content of the provided documents.\n  {{DocumentContext}}';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM QuarterlyReviewPrep', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: Workflow_InnovationIdeaGeneration
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_InnovationIdeaGeneration\n# Description: Generates new ideas based on provided analytical and strategic documents.\n\ninputDocumentSelectors: # User selects relevant context documents\n  - "*Analysis*" # Various analysis reports\n  - "Competitors*"\n  - "CustomerFeedback*"\n  - "IdeaBacklog*" \n  - "Strategy*" \ninputDateSelector: null\noutputName: "NewIdeas_Q{{CurrentQuarterNumber}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  **Role:** You are an AI Ideation Catalyst supporting the LACM innovation process.\n  **Goal:** Generate 5-10 concrete, relevant, and potentially innovative ideas for new products, services, process improvements, or strategic approaches. Base these ideas ONLY on the analysis of the provided input documents: recent performance/trend reports (various *Analysis*.md files), "Competitors*", "CustomerFeedback*", "Strategy*". Check "IdeaBacklog*" to avoid duplicating existing ideas.\n  **Context:**\n  - Performance & Trends: Content from various *Analysis*.md documents provided.\n  - Market & Customer: Content from "Competitors*", "CustomerFeedback*".\n  - Internal State: Content from "IdeaBacklog*" (for checking existing ideas), "Strategy*" (for identifying gaps or areas needing innovation).\n\n  **Task:**\n  1. **Analyze Context Deeply:** Review all provided input documents to identify:\n      - Unmet customer needs or recurring complaints (from "CustomerFeedback*").\n      - Competitor weaknesses or market gaps (from "Competitors*", analysis documents).\n      - Emerging technological or market trends (from analysis documents).\n      - Internal process bottlenecks or inefficiencies (from analysis documents, if mentioned).\n      - Areas where "Strategy*" indicates a need for new approaches or has gaps.\n  2. **Generate Diverse Ideas:** Based on this analysis, generate 5-10 distinct ideas. Aim for a mix covering: New Product/Service concepts, Enhancements, Process Improvements, Novel Strategic Approaches. Do not suggest ideas already listed in the "IdeaBacklog*" document.\n  3. **Formulate Ideas Clearly:** For each idea, provide:\n      - A short, descriptive title.\n      - A brief explanation (1-3 sentences) of the core concept and the problem it solves or opportunity it addresses based on the input documents.\n      - The primary source of inspiration from the input documents (e.g., "Inspired by customer feedback on X in `CustomerFeedback`", "Addresses competitor Y''s weakness noted in `Competitors`").\n  4. Generate the Markdown file.\n\n  **Format:** Use the following Markdown structure precisely:\n  ```markdown\n  # New Ideas Generated - Q{{CurrentQuarterNumber}} {{CurrentYear}} (Based on Provided Documents)\n\n  ## Idea 1: [Descriptive Title]\n  - **Concept:** [Brief explanation of the idea and problem/opportunity addressed.]\n  - **Inspiration (from input documents):** [Source document and specific point, e.g., "CustomerFeedback.md - recurring request for feature Z"]\n\n  ## Idea 2: [Descriptive Title]\n  - **Concept:** [...]\n  - **Inspiration (from input documents):** [...]\n\n  *(Repeat for 5-10 ideas)*\n  ```\n  **Constraints:** Ideas should be concrete. Ensure ideas are relevant to the business context defined in "Strategy*". Aim for novelty where possible. Clearly state the inspiration/rationale based ONLY on the provided documents.\n  {{DocumentContext}}';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM InnovationIdeaGeneration', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: Workflow_AnnualStrategyAnalysisPrep
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_AnnualStrategyAnalysisPrep\n# Description: Prepares a comprehensive analysis for the annual strategy review.\n\ninputDocumentSelectors: # User selects all relevant documents for the year\n  - "*ReviewPreparation*" # All quarterly review preps\n  - "*AnnualFinancialReport" # Optional, if user created this\n  - "MarketResearchSummary*" # Optional, user-created\n  - "Strategy*" # The strategy document for the year being reviewed\ninputDateSelector: null\noutputName: "{{Year}}_AnnualStrategyAnalysisInput"\nprompt: |\n  **Role:** You are an AI Senior Strategy Analyst supporting the LACM annual strategic review for the year {{CurrentYear}}.\n  **Goal:** Synthesize the entire year''s performance, learnings, and market context based on the provided quarterly review preparation documents, financial reports (if any), market research summaries (if any), and the expiring strategy document ("Strategy*" for {{CurrentYear}}). Critically evaluate the effectiveness and ongoing validity of the current strategy. Identify major strategic challenges and opportunities to support leadership''s decision-making for the upcoming year.\n  **Context:**\n  - Quarterly Performance: Content from "*ReviewPreparation*" documents for {{CurrentYear}}.\n  - Financials (If provided): Content from "*AnnualFinancialReport".\n  - Market (If provided): Content from "MarketResearchSummary*".\n  - Current Strategy: The expiring "Strategy*" for {{CurrentYear}}.\n  - Completed Year: {{CurrentYear}}.\n\n  **Task:**\n  1. **Synthesize Annual Performance:** Analyze all inputs to identify the most significant strategic outcomes, trends, successes, and failures over the entire year. Compare overall performance against the goals stated in the expiring "Strategy*".\n  2. **Critically Evaluate Current Strategy:** Assess each major section/pillar of the expiring "Strategy*". Based on the year''s evidence from the inputs, which assumptions held true? Which were challenged? Which strategic initiatives were most/least effective? Is the overall strategic logic still sound given the current market context (as described in inputs)?\n  3. **Identify Major Strategic Challenges & Opportunities:** Based on the year''s performance and updated market understanding (from inputs), what are the 3-5 most critical strategic challenges the organization faces going into next year? What are the 2-3 most significant strategic opportunities?\n  4. **Structure Findings for Leadership Review:** Generate a comprehensive Markdown report summarizing findings from tasks 1-3 in a clear, evidence-based manner suitable for executive review.\n\n  **Format:** Use the following Markdown structure precisely:\n  ```markdown\n  # Annual Strategy Analysis Input - Year {{CurrentYear}} (Generated: {{CurrentDate_YYYY-MM-DD}})\n  *Based on analysis of provided quarterly reviews, financial data (if any), market research (if any), and the {{CurrentYear}} strategy document.*\n\n  ## 1. {{CurrentYear}} Performance Summary & Key Strategic Outcomes\n  - [Overall Finding 1 regarding annual performance against strategic goals...]\n  - [Overall Finding 2 regarding significant trends observed throughout the year...]\n  - ...\n\n  ## 2. Critical Evaluation of {{CurrentYear}} Strategy (from "Strategy*")\n  - **Strategic Pillar/Section A:** [Assessment of its validity/effectiveness based on evidence from inputs. Were assumptions met? What were key outcomes related to this pillar?]\n  - **Strategic Pillar/Section B:** [...]\n  - ...\n\n  ## 3. Top Strategic Challenges Identified for {{CurrentYear + 1}}\n  *(Based on analysis of all provided documents)*\n  - [Challenge 1 description and evidence from inputs...]\n  - [Challenge 2 description and evidence from inputs...]\n  - ...\n\n  ## 4. Top Strategic Opportunities Identified for {{CurrentYear + 1}}\n  *(Based on analysis of all provided documents)*\n  - [Opportunity 1 description and evidence from inputs...]\n  - [Opportunity 2 description and evidence from inputs...]\n  - ...\n  ```\n  **Constraints:** Maintain a high-level strategic perspective. Analysis must be evidence-based, drawing directly from the provided input documents. Evaluation of the strategy should be objective and critical. Challenges/Opportunities identified must be truly strategic. Output should be structured logically. Base your output ONLY on the content of the provided documents.\n  {{DocumentContext}}';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM AnnualStrategyAnalysisPrep', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- --
-- -- End of LACM Workflows - Phase 4: Quarterly & Annual Routine Workflows
-- --

-- --
-- -- Inserting LACM Workflows - General Purpose / Pair Working Workflows (LACM Context)
-- --

-- -- Workflow: Workflow_DraftSection
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_DraftSection\n# Description: Drafts a text section based on topic, keywords, or outline from an input document.\n\ninputDocumentSelectors:\n  - "PairInput*" \ninputDateSelector: null\noutputName: "DraftOutput_from_{{InputFileName | replace: ''PairInput_'', '''' | truncate: 30, ''''}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  The input document titled "{{InputFileName}}" contains a request to draft a text section.\n  The request might include a topic, keywords, a brief outline, or some source material from other parts of the document.\n\n  Based **only** on the information provided in the input document below, please draft the requested text section.\n  Aim for clarity, conciseness, and adhere to any specified tone or style if mentioned in the input.\n  If the input is an outline, expand on each point.\n  If keywords are provided, weave them naturally into the text.\n\n  Input Document Content:\n  ```\n  {{DocumentContext}}\n  ```\n\n  Begin your response directly with the drafted section. Do not add any prefatory remarks.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM DraftSection', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: Workflow_BrainstormIdeas
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_BrainstormIdeas\n# Description: Brainstorms ideas based on a problem statement or topic from an input document.\n\ninputDocumentSelectors:\n  - "PairInput*" \ninputDateSelector: null\noutputName: "BrainstormOutput_from_{{InputFileName | replace: ''PairInput_'', '''' | truncate: 30, ''''}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  The input document "{{InputFileName}}" contains a request for brainstorming ideas.\n  This request could be a problem statement, a question, or a topic.\n\n  Based **only** on the information and request provided in the input document below, generate a list of 5-10 distinct ideas related to the core request.\n  Present the ideas as a bulleted list. Each idea should be concise.\n\n  Input Document Content:\n  ```\n  {{DocumentContext}}\n  ```\n\n  Begin your response directly with the list of brainstormed ideas. Do not add any prefatory remarks.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM BrainstormIdeas', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- -- Workflow: Workflow_AnalyzeTextSegment
-- DO $$
-- DECLARE
--     workflow_item_id uuid := public.uuid_generate_v4();
--     workflow_version_id uuid := public.uuid_generate_v4();
--     admin_team_id uuid := '04a9a4ec-18d8-4cfd-bead-d0ef99199e17';
--     workflow_content text := E'# Workflow Name: Workflow_AnalyzeTextSegment\n# Description: Analyzes a provided text segment based on instructions in the input document.\n\ninputDocumentSelectors:\n  - "PairInput*" \ninputDateSelector: null\noutputName: "AnalysisOutput_from_{{InputFileName | replace: ''PairInput_'', '''' | truncate: 30, ''''}}_{{Year}}-{{Month}}-{{Day}}"\nprompt: |\n  The input document "{{InputFileName}}" contains a segment of text and a specific request for how to analyze that text.\n  Carefully read the "Analysis Request" (or similar instruction) and the "Text to Analyze" (or similar content section) within the input document.\n\n  Perform **only** the requested analysis on the provided text segment.\n  Structure your output clearly based on the nature of the analysis requested. For example, if asked for pros and cons, use those headings. If asked for themes, list them. If asked for a summary, provide a concise summary.\n\n  Input Document Content:\n  ```\n  {{DocumentContext}}\n  ```\n\n  Begin your response directly with the results of your analysis. Do not add any prefatory remarks.';
-- BEGIN
--     INSERT INTO public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at)
--     VALUES (workflow_item_id, admin_team_id, 'WORKFLOW', 'LACM AnalyzeTextSegment', true, workflow_version_id, NOW(), NOW());

--     INSERT INTO public.content_versions (version_id, item_id, markdown_content, version_number, saved_by_team_id, created_at)
--     VALUES (workflow_version_id, workflow_item_id, workflow_content, 1, admin_team_id, NOW());
-- END $$;

-- --
-- -- End of LACM Workflows - General Purpose / Pair Working Workflows (LACM Context)
-- --

--
-- Data for Name: content_items; Type: TABLE DATA; Schema: public; Owner: ulacm_user
--
-- No initial team-specific documents are being added in this script.
-- Only admin-owned templates and workflows.
-- The COPY statement for content_items is intentionally left empty for user-created content.
COPY public.content_items (item_id, team_id, item_type, name, is_globally_visible, current_version_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: content_versions; Type: TABLE DATA; Schema: public; Owner: ulacm_user
--
-- The COPY statement for content_versions is populated by the DO $$ blocks above for each template/workflow.
COPY public.content_versions (
    version_id,
    item_id,
    markdown_content,
    version_number,
    saved_by_team_id,
    created_at,
    content_tsv,
    content_vector
) FROM stdin;
\.


--
-- Name: content_items content_items_pkey; Type: CONSTRAINT; Schema: public; Owner: ulacm_user
--

ALTER TABLE ONLY public.content_items
    ADD CONSTRAINT content_items_pkey PRIMARY KEY (item_id);


--
-- Name: content_versions content_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: ulacm_user
--

ALTER TABLE ONLY public.content_versions
    ADD CONSTRAINT content_versions_pkey PRIMARY KEY (version_id);


--
-- Name: teams teams_pkey; Type: CONSTRAINT; Schema: public; Owner: ulacm_user
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (team_id);


--
-- Name: teams teams_team_name_key; Type: CONSTRAINT; Schema: public; Owner: ulacm_user
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_team_name_key UNIQUE (team_name);


--
-- Name: teams teams_username_key; Type: CONSTRAINT; Schema: public; Owner: ulacm_user
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_username_key UNIQUE (username);


--
-- Name: content_versions uq_item_version_number; Type: CONSTRAINT; Schema: public; Owner: ulacm_user
--

ALTER TABLE ONLY public.content_versions
    ADD CONSTRAINT uq_item_version_number UNIQUE (item_id, version_number);


--
-- Name: content_items uq_team_item_name_type; Type: CONSTRAINT; Schema: public; Owner: ulacm_user
--

ALTER TABLE ONLY public.content_items
    ADD CONSTRAINT uq_team_item_name_type UNIQUE (team_id, name, item_type);


--
-- Name: idx_content_items_created_at; Type: INDEX; Schema: public; Owner: ulacm_user
--

CREATE INDEX idx_content_items_created_at ON public.content_items USING btree (created_at);


--
-- Name: idx_content_items_current_version_id; Type: INDEX; Schema: public; Owner: ulacm_user
--

CREATE INDEX idx_content_items_current_version_id ON public.content_items USING btree (current_version_id);


--
-- Name: idx_content_items_item_type; Type: INDEX; Schema: public; Owner: ulacm_user
--

CREATE INDEX idx_content_items_item_type ON public.content_items USING btree (item_type);


--
-- Name: idx_content_items_name_lower_team; Type: INDEX; Schema: public; Owner: ulacm_user
--

CREATE INDEX idx_content_items_name_lower_team ON public.content_items USING btree (team_id, lower((name)::text), item_type);


--
-- Name: idx_content_items_team_id; Type: INDEX; Schema: public; Owner: ulacm_user
--

CREATE INDEX idx_content_items_team_id ON public.content_items USING btree (team_id);


--
-- Name: idx_content_versions_item_id; Type: INDEX; Schema: public; Owner: ulacm_user
--

CREATE INDEX idx_content_versions_item_id ON public.content_versions USING btree (item_id);


--
-- Name: idx_content_versions_item_id_created_at; Type: INDEX; Schema: public; Owner: ulacm_user
--

CREATE INDEX idx_content_versions_item_id_created_at ON public.content_versions USING btree (item_id, created_at);


--
-- Name: idx_content_versions_saved_by_team_id; Type: INDEX; Schema: public; Owner: ulacm_user
--

CREATE INDEX idx_content_versions_saved_by_team_id ON public.content_versions USING btree (saved_by_team_id);


--
-- Name: idx_gin_content_items_name_tsv; Type: INDEX; Schema: public; Owner: ulacm_user
--

CREATE INDEX idx_gin_content_items_name_tsv ON public.content_items USING gin (to_tsvector('english'::regconfig, (name)::text));


--
-- Name: idx_gin_content_versions_content_tsv; Type: INDEX; Schema: public; Owner: ulacm_user
--

CREATE INDEX idx_gin_content_versions_content_tsv ON public.content_versions USING gin (content_tsv);


--
-- Name: idx_teams_team_name_lower; Type: INDEX; Schema: public; Owner: ulacm_user
--

CREATE INDEX idx_teams_team_name_lower ON public.teams USING btree (lower((team_name)::text));


--
-- Name: idx_teams_username_lower; Type: INDEX; Schema: public; Owner: ulacm_user
--

CREATE INDEX idx_teams_username_lower ON public.teams USING btree (lower((username)::text));


--
-- Name: content_versions tsvectorupdate; Type: TRIGGER; Schema: public; Owner: ulacm_user
--

CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE ON public.content_versions FOR EACH ROW EXECUTE FUNCTION tsvector_update_trigger('content_tsv', 'pg_catalog.english', 'markdown_content');


--
-- Name: content_items update_content_items_updated_at; Type: TRIGGER; Schema: public; Owner: ulacm_user
--

CREATE TRIGGER update_content_items_updated_at BEFORE UPDATE ON public.content_items FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: teams update_teams_updated_at; Type: TRIGGER; Schema: public; Owner: ulacm_user
--

CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON public.teams FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: content_items content_items_current_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ulacm_user
--

ALTER TABLE ONLY public.content_items
    ADD CONSTRAINT content_items_current_version_id_fkey FOREIGN KEY (current_version_id) REFERENCES public.content_versions(version_id) ON DELETE SET NULL;


--
-- Name: content_items content_items_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ulacm_user
--

ALTER TABLE ONLY public.content_items
    ADD CONSTRAINT content_items_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(team_id) ON DELETE CASCADE;


--
-- Name: content_versions content_versions_saved_by_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ulacm_user
--

ALTER TABLE ONLY public.content_versions
    ADD CONSTRAINT content_versions_saved_by_team_id_fkey FOREIGN KEY (saved_by_team_id) REFERENCES public.teams(team_id) ON DELETE SET NULL;


--
-- Name: content_versions fk_content_versions_item_id; Type: FK CONSTRAINT; Schema: public; Owner: ulacm_user
--

ALTER TABLE ONLY public.content_versions
    ADD CONSTRAINT fk_content_versions_item_id FOREIGN KEY (item_id) REFERENCES public.content_items(item_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

--
-- Final step: Populate/Refresh content_tsv for all existing content_versions rows
-- This ensures that data inserted by this script (e.g., initial templates/workflows)
-- has its tsvector generated, as the trigger is defined after these inserts.
--
UPDATE public.content_versions
SET content_tsv = to_tsvector('pg_catalog.english', markdown_content);
