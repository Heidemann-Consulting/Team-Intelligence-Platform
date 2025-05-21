# **Team Intelligence Platform (TIP) - Phase 2 Workflow Library**

**Version:** 1.0
**Date:** May 11, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

## **Table of Contents**

- [**Team Intelligence Platform (TIP) - Phase 2 Workflow Library**](#team-intelligence-platform-tip---phase-2-workflow-library)
  - [**Table of Contents**](#table-of-contents)
  - [**Introduction**](#introduction)
  - [**Core Phase 2 Workflows**](#core-phase-2-workflows)
    - [1. Extract Context Elements Workflow](#1-extract-context-elements-workflow)
    - [2. Analyze Context Metrics Workflow](#2-analyze-context-metrics-workflow)
    - [3. Analyze Retrospective Data Workflow](#3-analyze-retrospective-data-workflow)
    - [4. Suggest Retrospective Actions Workflow](#4-suggest-retrospective-actions-workflow)
    - [5. Analyze Planning Data Workflow](#5-analyze-planning-data-workflow)
    - [6. Draft Section Workflow (Pair Working)](#6-draft-section-workflow-pair-working)
    - [7. Brainstorm Ideas Workflow (Pair Working)](#7-brainstorm-ideas-workflow-pair-working)
    - [8. Analyze Text Segment Workflow (Pair Working)](#8-analyze-text-segment-workflow-pair-working)
  - [**Notes on Usage by Team Users**](#notes-on-usage-by-team-users)
  - [**Notes for Administrators**](#notes-for-administrators)

## **Introduction**

This document serves as a library of predefined Process Workflows for Phase 2 of the Team Intelligence Platform (TIP) adoption, "The Collaborative Acceleration." These workflows are designed to be created by System Administrators within TIP's Process Workflow management area. Team Users can then execute these globally visible workflows, using TIP Documents as inputs, to assist with their tasks and rituals.

Each workflow definition below is presented in the YAML-like format expected by TIP when an Administrator creates or edits a Process Workflow's content in the Markdown editor. The prompts are designed to work with LLMs that do not have internet or external tool access.

All input documents for these workflows are expected to be **TIP Documents**, often created using templates from the `tip-phase2-templates-library.md`.

## **Core Phase 2 Workflows**

### 1. Extract Context Elements Workflow

* **Workflow Name (in TIP):** `ExtractContextElements`
* **Description:** This workflow processes a TIP Document (typically a daily capture like `DailyContextCuration_YYYY-MM-DD` created using `Template_DailyQuickCapture_Phase2`) to identify and suggest classifications for key context elements.
* **Ritual Relevance:** Enhanced Context Management (Daily Quick Capture).
* **Input Document Template (Expected):** `Template_DailyQuickCapture_Phase2` from `tip-phase2-templates-library.md`.

**TIP Process Workflow Definition:**
```yaml
# Workflow Name: ExtractContextElements
# Description: Extracts key elements, suggests classifications, and potential relations from daily context updates.

inputDocumentSelectors:
  - "DailyContextCuration_*" # Designed for documents like DailyContextCuration_YYYY-MM-DD
inputDateSelector: null
outputName: "ExtractedElements_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  Review the following daily context updates from the document titled "{{InputFileName}}".
  For each team member's update, identify 3-5 key informational elements (e.g., decisions, findings, new terms, project updates, risks identified).

  For each extracted element:
  1.  Suggest a brief, relevant CATEGORY (e.g., Decision, Finding, Risk, New Term, Project Update, Technical Debt).
  2.  If the element seems related to common project themes or other items mentioned in the input, briefly note a "Potential Relation" (e.g., "Related to: Feature X Rollout", "Related to: Sprint Goal Y").

  Format your output clearly for each team member. Example:

  Team Member: [Name]
  - Extracted Element: [Element text]
    - Suggested Category: [Category]
    - Potential Relation: [Relation text or N/A]
  - Extracted Element: [...]
    - Suggested Category: [...]
    - Potential Relation: [...]

  DOCUMENT CONTENT:
  ```
  {{DocumentContext}}
  ```

  Provide only the extracted elements, categories, and potential relations as requested.
```

### 2. Analyze Context Metrics Workflow

* **Workflow Name (in TIP):** `AnalyzeContextMetrics`
* **Description:** This workflow processes a TIP Document containing a curated list of document names and their metadata (e.g., last modified date, author, or keywords if available and manually added to the input document). It aims to generate a basic context health dashboard or a set of metrics that can be used to populate such a dashboard.
* **Ritual Relevance:** Enhanced Context Management (Weekly Structured Curation).
* **Input Document Template (Expected):** A manually compiled TIP Document, for example, named `Input_ContextMetrics_YYYY-MM-DD_KW[WeekNumber]`. This document should list other TIP document names and any relevant metadata the team wishes to analyze for context health.
    * Example input document content structure:
        ```markdown
        # Input for Context Metrics Analysis - YYYY-MM-DD - KWXX

        ## Document List for Analysis:
        - DocumentName: "ProjectAlpha_Goals_V1", LastModified: "YYYY-MM-DD", Keywords: "goals, project alpha, strategy"
        - DocumentName: "DailyContextCuration_YYYY-MM-DD", LastModified: "YYYY-MM-DD", Keywords: "daily update, team sync"
        - DocumentName: "MeetingNotes_SprintReview_YYYY-MM-DD", LastModified: "YYYY-MM-DD", Keywords: "sprint review, feedback"
        - DocumentName: "OldDocument_Specification_V0.1", LastModified: "YYYY-MM-01", Keywords: "spec, old version"
        # Add more document entries as needed

        ## Analysis Focus (Optional - User can specify what to look for):
        - Identify documents not modified in the last 30 days.
        - Count documents per primary keyword.
        ```

**TIP Process Workflow Definition:**
```yaml
# Workflow Name: AnalyzeContextMetrics
# Description: Analyzes a list of TIP documents and their metadata to generate context health metrics.

inputDocumentSelectors:
  - "Input_ContextMetrics_*" # Designed for manually compiled documents listing other documents
inputDateSelector: null
outputName: "Output_ContextHealthDashboard_Data_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}.md"
prompt: |
  **Role:** You are an AI Knowledge Management Assistant. Your task is to analyze the provided list of documents and their metadata to identify basic context health metrics.
  **Goal:** Generate a structured report based ONLY on the information within the input document titled "{{InputFileName}}". This report will serve as data for a Context Health Dashboard.

  **Context:**
  - The input document contains a list of other TIP document names and may include metadata such as "LastModified" dates and "Keywords".
  - It may also contain an "Analysis Focus" section specifying what the user wants to identify.
  - Today's Date for reference: {{CurrentDate_YYYY-MM-DD}}.

  **Task:**
  Based *only* on the content of the input document "{{InputFileName}}":

  1.  **Document Count:**
      - Report the total number of documents listed in the input.

  2.  **Activity Summary (if "LastModified" dates are provided):**
      - Identify and list any documents not modified in the last 30 days (calculate based on {{CurrentDate_YYYY-MM-DD}} and the provided "LastModified" dates).
      - Identify and list documents modified in the last 7 days.

  3.  **Keyword Analysis (if "Keywords" are provided):**
      - If keywords are present for each document, count the occurrences of the top 3-5 most frequent primary keywords across all listed documents.
      - List documents associated with each of these top keywords.

  4.  **User-Defined Analysis Focus (if "Analysis Focus" section is provided in the input):**
      - Address any specific requests made in the "Analysis Focus" section of the input document, using the provided data.

  5.  **Potential Issues (General Observations):**
      - Briefly note any obvious potential issues based *only* on the provided list, e.g., a high number of very old documents, or very few recent documents if that context is inferable from document names/dates.

  **Format Output Clearly:**
  Structure your output with clear headings for each section (e.g., "Document Count", "Activity Summary", "Keyword Analysis", "User-Defined Analysis", "Potential Issues").

  **Constraint:** Base your entire analysis strictly on the information explicitly provided within the "{{InputFileName}}" document. Do not make assumptions or infer information beyond what is written.

  INPUT DOCUMENT CONTENT:
  ```
  {{DocumentContext}}
  ```
```

### 3. Analyze Retrospective Data Workflow

* **Workflow Name (in TIP):** `AnalyzeRetroData`
* **Description:** This workflow takes a TIP Document containing manually compiled retrospective data (e.g., `PreRetroData_SprintX_YYYY-MM-DD` created from `Template_PreRetrospectiveAnalysis_Phase2`) and generates insights, identifies patterns, and suggests discussion prompts for the AI-Enhanced Retrospective.
* **Ritual Relevance:** AI-Enhanced Retrospective (Pre-Retro Analysis).
* **Input Document Template (Expected):** `Template_PreRetrospectiveAnalysis_Phase2` from `tip-phase2-templates-library.md`.

**TIP Process Workflow Definition:**
```yaml
# Workflow Name: AnalyzeRetroData
# Description: Analyzes pre-compiled retrospective data to identify patterns and suggest discussion prompts.

inputDocumentSelectors:
  - "PreRetroData_*" # Designed for documents like PreRetroData_SprintX_YYYY-MM-DD
inputDateSelector: null
outputName: "AI_RetroInsights_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  Based on the content of the Pre-Retrospective Analysis document titled "{{InputFileName}}", perform the following analysis. The input document contains sections like "Metrics Analysis", "Communication Pattern Analysis", and "Historical Pattern Identification".

  1.  **Insight Summary:**
      - Identify 2-3 key strengths to leverage from the data.
      - Identify 2-3 significant opportunities for improvement.
      - Identify 1-2 potential systemic patterns or recurring themes.
  2.  **Suggested Discussion Prompts:**
      - Generate 3-4 thought-provoking questions based on your analysis of the "Systemic Patterns", "Opportunities for Improvement", or "Historical Pattern Identification" sections of the input document. These questions should help the team explore root causes or potential solutions.

  Format your output clearly.

  Pre-Retrospective Analysis Document Content:
  ```
  {{DocumentContext}}
  ```
```

### 4. Suggest Retrospective Actions Workflow

* **Workflow Name (in TIP):** `SuggestRetroActions`
* **Description:** Takes a TIP Document containing notes from a retrospective session (e.g., `RetroSessionNotes_SprintX_YYYY-MM-DD` based on `Template_RetrospectiveSession_Phase2`) and suggests potential action items.
* **Ritual Relevance:** AI-Enhanced Retrospective (Action Planning).
* **Input Document Template (Expected):** `Template_RetrospectiveSession_Phase2` from `tip-phase2-templates-library.md`.

**TIP Process Workflow Definition:**
```yaml
# Workflow Name: SuggestRetroActions
# Description: Suggests potential action items based on retrospective session notes.

inputDocumentSelectors:
  - "RetroSessionNotes_*" # Designed for documents from the Retrospective Session Template
inputDateSelector: null
outputName: "SuggestedActions_for_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  Review the Retrospective Session Notes from the document titled "{{InputFileName}}".
  Based on the "Key Pattern Discussion", "Root Cause Exploration", and "Improvement Options" sections, suggest 3-5 concrete, actionable, and measurable (if possible) improvement actions the team could take.

  For each suggested action, provide:
  - A clear description of the action.
  - A brief rationale linking it to the discussion in the notes.

  Example Format:
  **Suggested Action 1:**
  - Description: [Action description]
  - Rationale: [Rationale based on notes]

  **Suggested Action 2:**
  - Description: [Action description]
  - Rationale: [Rationale based on notes]

  Retrospective Session Notes Document Content:
  ```
  {{DocumentContext}}
  ```
```

### 5. Analyze Planning Data Workflow

* **Workflow Name (in TIP):** `AnalyzePlanningData`
* **Description:** This workflow takes a TIP Document containing manually compiled pre-planning data (e.g., `PrePlanningData_SprintY_YYYY-MM-DD` created from `Template_PrePlanningAnalysis_Phase2`) and generates insights related to historical performance, risks, and potential sprint scope.
* **Ritual Relevance:** Context-Aware Planning (Pre-Planning Analysis).
* **Input Document Template (Expected):** `Template_PrePlanningAnalysis_Phase2` from `tip-phase2-templates-library.md`.

**TIP Process Workflow Definition:**
```yaml
# Workflow Name: AnalyzePlanningData
# Description: Analyzes pre-compiled planning data to provide insights for sprint planning.

inputDocumentSelectors:
  - "PrePlanningData_*" # Designed for documents like PrePlanningData_SprintY_YYYY-MM-DD
inputDateSelector: null
outputName: "AI_PlanningInsights_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  Based on the content of the Pre-Planning Analysis document titled "{{InputFileName}}", provide the following:

  1.  **Historical Performance Summary (from input data):**
      - Briefly summarize any trends in velocity or cycle time mentioned in the "Historical Performance Analysis" section.
      - Highlight any significant estimation patterns (over/under estimation) noted.
  2.  **Key Work Item Considerations (from input data):**
      - For up to 3 "Key Work Items" listed, summarize their complexity and risk factors as presented in the input.
  3.  **Risk Profile Summary (from input data):**
      - List the top 2-3 "Technical Risk Factors" and "External Risk Factors" with their probability/impact if provided in the input.
  4.  **Suggested Planning Focus Areas:**
      - Based on the overall input data, suggest 1-2 areas the team might want to focus on during their planning session (e.g., addressing a specific risk, considering capacity against a complex item).

  Format your output clearly under these headings.

  Pre-Planning Analysis Document Content:
  ```
  {{DocumentContext}}
  ```
```

### 6. Draft Section Workflow (Pair Working)

* **Workflow Name (in TIP):** `DraftSection-PairWorking`
* **Description:** Helps a team member draft a section of a document based on a provided topic, keywords, or an outline.
* **Ritual Relevance:** Basic AI Pair Working.
* **Input Document Template (Expected):** Can be a simple TIP Document created by the user, containing their topic, keywords, outline, or source text. Example input document name: `PairInput_DraftProductDescription_YYYY-MM-DD`.

**TIP Process Workflow Definition:**
```yaml
# Workflow Name: DraftSection-PairWorking
# Description: Drafts a text section based on a topic, keywords, or outline provided in the input document.

inputDocumentSelectors:
  - "PairInput_*" # User prepares a document with their specific input, e.g., PairInput_DraftFeatureX_YYYY-MM-DD
inputDateSelector: null
outputName: "DraftOutput_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  The following input document "{{InputFileName}}" contains a request to draft a text section.
  The request might include a topic, keywords, a brief outline, or some source material.

  Based **only** on the information provided in the input document below, please draft the requested text section.
  Aim for clarity, conciseness, and adhere to any specified tone or style if mentioned in the input.
  If the input is an outline, expand on each point.
  If keywords are provided, weave them naturally into the text.

  Input Document Content:
  ```
  {{DocumentContext}}
  ```

  Begin your response directly with the drafted section. Do not add any prefatory remarks.
```

### 7. Brainstorm Ideas Workflow (Pair Working)

* **Workflow Name (in TIP):** `BrainstormIdeas-PairWorking`
* **Description:** Generates a list of ideas based on a problem statement, question, or topic provided in an input TIP Document.
* **Ritual Relevance:** Basic AI Pair Working.
* **Input Document Template (Expected):** Can be a simple TIP Document created by the user, containing their problem statement or topic. Example input document name: `PairInput_BrainstormSolutionsForX_YYYY-MM-DD`.

**TIP Process Workflow Definition:**
```yaml
# Workflow Name: BrainstormIdeas-PairWorking
# Description: Brainstorms ideas based on a problem statement or topic from an input document.

inputDocumentSelectors:
  - "PairInput_*" # User prepares a document with their specific input
inputDateSelector: null
outputName: "BrainstormOutput_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  The input document "{{InputFileName}}" contains a request for brainstorming ideas.
  This request could be a problem statement, a question, or a topic.

  Based **only** on the information and request provided in the input document below, generate a list of 5-10 distinct ideas related to the core request.
  Present the ideas as a bulleted list.

  Input Document Content:
  ```
  {{DocumentContext}}
  ```

  Begin your response directly with the list of brainstormed ideas.
```

### 8. Analyze Text Segment Workflow (Pair Working)

* **Workflow Name (in TIP):** `AnalyzeTextSegment-PairWorking`
* **Description:** Performs a specific analysis (e.g., identify pros and cons, extract key arguments, summarize a short segment) on a piece of text provided in an input TIP Document. The user specifies the type of analysis in their input document.
* **Ritual Relevance:** Basic AI Pair Working.
* **Input Document Template (Expected):** A TIP Document where the user pastes the text segment and clearly states the type of analysis needed. Example: `PairInput_AnalyzeCustomerFeedback_YYYY-MM-DD`. The document might contain:
    ```
    Analysis Request: Identify sentiment (positive, negative, neutral) and key themes in the following customer feedback.

    Text to Analyze:
    [...customer feedback text...]
    ```

**TIP Process Workflow Definition:**
```yaml
# Workflow Name: AnalyzeTextSegment-PairWorking
# Description: Analyzes a provided text segment based on instructions in the input document.

inputDocumentSelectors:
  - "PairInput_*" # User prepares a document with text and analysis instructions
inputDateSelector: null
outputName: "AnalysisOutput_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  The input document "{{InputFileName}}" contains a segment of text and a specific request for how to analyze that text.
  Carefully read the "Analysis Request" and the "Text to Analyze" sections within the input document.

  Perform **only** the requested analysis on the provided text.
  Structure your output clearly based on the nature of the analysis requested. For example, if asked for pros and cons, use those headings. If asked for themes, list them.

  Input Document Content:
  ```
  {{DocumentContext}}
  ```

  Begin your response directly with the results of your analysis.
```

## **Notes on Usage by Team Users**

* To use these workflows, navigate to the "Run Workflows" section in TIP.
* Select the desired workflow (e.g., `ExtractContextElements`).
* TIP will then prompt you to select the input TIP Document(s) based on the `inputDocumentSelectors` defined in the workflow.
    * Ensure your input TIP Document is named according to the convention specified in the workflow's `inputDocumentSelectors` for easier selection (e.g., a document named `DailyContextCuration_2025-05-11` for `ExtractContextElements`).
    * For "Pair Working" workflows, you will typically create a new TIP Document (e.g., `PairInput_MyTaskDescription_YYYY-MM-DD`) containing the specific text or instructions for the LLM, then select this document as input to the workflow.
* The workflow will process the input document(s) using the LLM and its defined prompt.
* A new TIP Document will be created with the output, named according to the `outputName` template defined in the workflow. You can then review, edit, and use this AI-generated document.
* Since the LLM has no internet or tool access, all necessary information for the workflow must be contained within the input TIP Document(s).

## **Notes for Administrators**

* These workflow definitions should be created or updated in the "Workflow Management" area of TIP (accessible via the Admin interface).
* The "Workflow Name (in TIP)" mentioned above is the human-readable name you assign to the Process Workflow when creating it in TIP. This is the name users will see in the list of executable workflows.
* The YAML content provided for each workflow should be pasted into the Markdown editor when creating/editing the Process Workflow's content in TIP.
* Ensure that the prompts are well-suited for the capabilities of the locally configured LLM in your TIP instance. Refine prompts based on observed output quality.
* The global LLM model and temperature settings configured in the TIP backend will apply to these workflows.
* Regularly review the "Prompt Development Workshop" outputs (documented in TIP Documents using `Template_PromptDocumentation_Phase2`) and update these Process Workflow definitions with improved prompts as needed.
