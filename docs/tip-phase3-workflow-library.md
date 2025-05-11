# **Team Intelligence Platform (TIP) - Phase 3 Workflow Library**

**Version:** 1.0
**Date:** May 11, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

## **Table of Contents**

- [**Team Intelligence Platform (TIP) - Phase 3 Workflow Library**](#team-intelligence-platform-tip---phase-3-workflow-library)
  - [**Table of Contents**](#table-of-contents)
  - [**Introduction**](#introduction)
  - [**Core Phase 3 Workflows**](#core-phase-3-workflows)
    - [1. Networked Context Management Workflows](#1-networked-context-management-workflows)
      - [1.1. Analyze Context Health Workflow](#11-analyze-context-health-workflow)
      - [1.2. Identify Boundary Areas Workflow](#12-identify-boundary-areas-workflow)
    - [2. AI-Driven Decision Framework Workflows](#2-ai-driven-decision-framework-workflows)
      - [2.1. Generate Decision Options Workflow](#21-generate-decision-options-workflow)
      - [2.2. Analyze Decision Factors Workflow](#22-analyze-decision-factors-workflow)
    - [3. Advanced Retrospective System Workflows](#3-advanced-retrospective-system-workflows)
      - [3.1. Analyze Sprint Retrospective Data Workflow](#31-analyze-sprint-retrospective-data-workflow)
      - [3.2. Suggest Sprint Retrospective Actions Workflow](#32-suggest-sprint-retrospective-actions-workflow)
      - [3.3. Analyze Quarterly Trends Workflow](#33-analyze-quarterly-trends-workflow)
      - [3.4. Analyze Annual Performance Workflow](#34-analyze-annual-performance-workflow)
    - [4. Cross-Team Intelligence Workflows](#4-cross-team-intelligence-workflows)
      - [4.1. Synthesize Cross-Team Updates Workflow](#41-synthesize-cross-team-updates-workflow)
      - [4.2. Identify Shared Challenges Workflow](#42-identify-shared-challenges-workflow)
      - [4.3. Suggest Collaborative Practices Workflow](#43-suggest-collaborative-practices-workflow)
      - [4.4. Analyze Portfolio Patterns Workflow](#44-analyze-portfolio-patterns-workflow)
    - [5. Advanced AI Pair Working Workflows (Examples)](#5-advanced-ai-pair-working-workflows-examples)
      - [5.1. Draft Document Section Workflow (Advanced)](#51-draft-document-section-workflow-advanced)
      - [5.2. Brainstorm Strategic Ideas Workflow (Advanced)](#52-brainstorm-strategic-ideas-workflow-advanced)
      - [5.3. Summarize Complex Document Workflow (Advanced)](#53-summarize-complex-document-workflow-advanced)
  - [**Notes on Usage by Team Users**](#notes-on-usage-by-team-users)
  - [**Notes for Administrators**](#notes-for-administrators)

## **Introduction**

This document serves as a library of predefined Process Workflows for Phase 3 of the Team Intelligence Platform (TIP) adoption, "The Transformative Intelligence." These workflows are designed to be created by System Administrators within TIP's Process Workflow management area. Team Users can then execute these globally visible workflows, using TIP Documents as inputs, to assist with advanced collaborative tasks and rituals.

Each workflow definition below is presented in the YAML-like format expected by TIP when an Administrator creates or edits a Process Workflow's content in the Markdown editor. The prompts are designed to work with LLMs that do not have internet or external tool access. All necessary information for the workflow must be contained within the input TIP Document(s).

All input documents for these workflows are expected to be **TIP Documents**, often created using templates from the `tip-phase3-templates-library.md` or by manually compiling information into a new TIP Document. Consistent naming of input TIP Documents is crucial for their selection and for the overall organization of knowledge within TIP.

## **Core Phase 3 Workflows**

### 1. Networked Context Management Workflows

#### 1.1. Analyze Context Health Workflow

* **Workflow Name (in TIP):** `AnalyzeContextHealth`
* **Description:** This workflow processes a TIP Document containing a list of recently changed or key document names (and optionally summaries or keywords for each) to identify potential context health issues like orphaned documents or stale areas based on the provided information.
* **Ritual Relevance:** Networked Context Management (Weekly Team Curation).
* **Input Document Template (Expected):** A manually compiled TIP Document (e.g., `Input_ContextHealthAnalysis_YYYY-MM-DD`) containing a list of document names, their creation/modification dates, and optionally, brief summaries or keywords for each.
    * Example input document content:
        ```markdown
        # Context Health Analysis Input - YYYY-MM-DD

        ## Documents for Analysis
        - Document Name: ProjectAlpha_Specification_V3, Last Modified: YYYY-MM-DD, Keywords: core specs, new features, UI
        - Document Name: MeetingNotes_AlphaSprintReview_YYYY-MM-DD, Last Modified: YYYY-MM-DD, Keywords: sprint review, feedback, decision
        - Document Name: Research_CompetitorX_YYYY-MM, Last Modified: YYYY-MM-DD, Keywords: competitor, analysis, market
        ... (list more documents) ...

        ## Known Relationships (Manual Entry)
        - ProjectAlpha_Specification_V3 references MeetingNotes_AlphaSprintReview_YYYY-MM-DD
        ```
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: AnalyzeContextHealth
    # Description: Analyzes a list of documents and their metadata to suggest context health issues.

    inputDocumentSelectors:
      - "Input_ContextHealthAnalysis_*" # Designed for manually compiled documents
    inputDateSelector: null
    outputName: "ContextHealthAnalysis_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      Review the following list of documents, their modification dates, keywords, and any manually noted relationships from the document titled "{{InputFileName}}".
      Based *only* on the information provided in this input document:

      1.  **Potential Stale Areas:** Identify up to 3 documents that seem oldest or haven't been mentioned as related to recent documents, suggesting they might be stale. Provide the document name and its last modified date.
      2.  **Potential Orphaned Items:** Identify up to 3 documents that are not mentioned as related to any other documents in the "Known Relationships" section (if provided).
      3.  **Potential Keyword Clusters:** Identify 2-3 groups of documents that share common keywords, suggesting thematic clusters. List the cluster keywords and the associated document names.
      4.  **Gaps in Relationships:** Based on keywords or document names, suggest 1-2 potential relationships between documents that are not explicitly listed but might be relevant.

      Format your output clearly under these headings.

      INPUT DOCUMENT CONTENT:
      ```
      {{DocumentContext}}
      ```

      Provide only the analysis based on the input document.
    ```

#### 1.2. Identify Boundary Areas Workflow

* **Workflow Name (in TIP):** `IdentifyBoundaryAreas`
* **Description:** This workflow processes a TIP Document containing lists of key document names (and optionally keywords or summaries) from multiple teams to suggest potential boundary areas or overlapping topics for cross-team alignment.
* **Ritual Relevance:** Networked Context Management (Monthly Cross-Team Alignment).
* **Input Document Template (Expected):** A manually compiled TIP Document (e.g., `Input_BoundaryAnalysis_YYYY-MM`) containing document lists from participating teams.
    * Example input document content:
        ```markdown
        # Boundary Analysis Input - YYYY-MM - Topic: SharedPlatformComponents

        ## Team Alpha Documents
        - Document Name: Alpha_ComponentA_Design_V2, Keywords: component A, API, integration
        - Document Name: Alpha_PlatformStrategy_Q3, Keywords: platform, roadmap, shared services

        ## Team Beta Documents
        - Document Name: Beta_ServiceIntegration_Guide_V1, Keywords: integration, API, shared services
        - Document Name: Beta_ComponentA_UsageReport_YYYY-MM, Keywords: component A, performance, issues

        ## Team Gamma Documents
        - Document Name: Gamma_NewFeature_Using_ComponentA, Keywords: feature spec, component A, dependency
        - Document Name: Gamma_API_Wishlist, Keywords: API, improvements, platform
        ```
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: IdentifyBoundaryAreas
    # Description: Identifies potential boundary areas from document lists of multiple teams.

    inputDocumentSelectors:
      - "Input_BoundaryAnalysis_*"
    inputDateSelector: null
    outputName: "Output_BoundaryAnalysis_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      Review the lists of documents and their associated keywords from different teams, as provided in the document titled "{{InputFileName}}".
      Based *only* on the document names and keywords provided:

      1.  **Shared Document Mentions/Keywords:** Identify any document names or keywords that appear in the lists of more than one team. For each, list the shared item and the teams involved.
      2.  **Potential Overlapping Topics:** Based on recurring keywords across different teams, suggest 2-3 potential overlapping topics or boundary areas that might require cross-team discussion or alignment. For each topic, list the supporting keywords and the involved teams.
      3.  **Potential Dependencies:** Based on document names or keywords (e.g., "ComponentA_Design" from one team and "UsageReport_ComponentA" from another), suggest 1-2 potential dependencies between teams.

      Format your output clearly under these headings.

      INPUT DOCUMENT CONTENT:
      ```
      {{DocumentContext}}
      ```
    ```

### 2. AI-Driven Decision Framework Workflows

#### 2.1. Generate Decision Options Workflow

* **Workflow Name (in TIP):** `GenerateDecisionOptions`
* **Description:** This workflow takes a TIP Document detailing a problem, criteria, and context (from `Template_DecisionInitialization_Phase3`) and brainstorms potential decision options.
* **Ritual Relevance:** AI-Driven Decision Framework (Option Development).
* **Input Document Template (Expected):** `DecisionInitialization_DecisionID_YYYY-MM-DD` (created using `Template_DecisionInitialization_Phase3` from `tip-phase3-templates-library.md`).
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: GenerateDecisionOptions
    # Description: Brainstorms decision options based on a problem statement and context.

    inputDocumentSelectors:
      - "DecisionInitialization_*"
    inputDateSelector: null
    outputName: "Output_GeneratedOptions_for_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      Based on the "Problem Statement", "Decision Criteria", "Stakeholder Perspectives", and "Constraints" sections in the Decision Initialization document titled "{{InputFileName}}", generate 3-5 distinct and creative options to address the core problem.

      For each option:
      1.  Provide a brief name or title for the option.
      2.  Provide a 1-2 sentence description of the option.
      3.  Briefly explain the rationale or how it addresses the problem based on the input.

      Focus on generating diverse approaches.

      DECISION INITIALIZATION DOCUMENT CONTENT:
      ```
      {{DocumentContext}}
      ```
    ```

#### 2.2. Analyze Decision Factors Workflow

* **Workflow Name (in TIP):** `AnalyzeDecisionFactors`
* **Description:** This workflow analyzes a TIP Document containing decision options, criteria, scores, and stated biases (from `Template_StructuredEvaluation_Phase3`) to highlight key factors, potential impacts of biases, or sensitivities.
* **Ritual Relevance:** AI-Driven Decision Framework (Structured Evaluation).
* **Input Document Template (Expected):** `StructuredEvaluation_DecisionID_YYYY-MM-DD` (created using `Template_StructuredEvaluation_Phase3` from `tip-phase3-templates-library.md`).
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: AnalyzeDecisionFactors
    # Description: Analyzes decision options, scores, and biases from an evaluation document.

    inputDocumentSelectors:
      - "StructuredEvaluation_*"
    inputDateSelector: null
    outputName: "Output_DecisionFactorAnalysis_for_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      Review the "Multi-Criteria Analysis" (including option scoring against weighted criteria), "Bias Identification", and "Sensitivity Analysis" (if provided) sections of the Structured Evaluation document titled "{{InputFileName}}".

      Based *only* on the information provided in this input document:

      1.  **Key Differentiating Criteria:** Identify 1-2 criteria that seem to most significantly differentiate the scores between the top options.
      2.  **Impact of Stated Biases:** For each "Potential Bias Identified" in the input, briefly discuss how it might have influenced the "Justification" or "Score" for one of the options, if evident from the text.
      3.  **Sensitivity Highlights (if data available):** If the "Sensitivity Testing Results" section is filled, summarize which options appear most/least robust based on the stated assumption variations.
      4.  **Alignment Check:** Briefly comment on whether the "Highest scoring option" aligns with the "Most robust option" and "Stakeholder preferred option" if these are identified in the "Evaluation Summary" section of the input.

      Format your output clearly.

      STRUCTURED EVALUATION DOCUMENT CONTENT:
      ```
      {{DocumentContext}}
      ```
    ```

### 3. Advanced Retrospective System Workflows

#### 3.1. Analyze Sprint Retrospective Data Workflow

* **Workflow Name (in TIP):** `AnalyzeSprintRetroData`
* **Description:** Takes a `SprintRetroAnalysis_SprintX_YYYY-MM-DD` TIP Document (manually compiled quantitative and qualitative data) and generates insights, identifies patterns, and suggests discussion prompts.
* **Ritual Relevance:** Advanced Retrospective System (Sprint Retrospective Pre-work Analysis).
* **Input Document Template (Expected):** `SprintRetroAnalysis_SprintX_YYYY-MM-DD` (created using `Template_SprintRetrospectiveAnalysis_Phase3` from `tip-phase3-templates-library.md`).
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: AnalyzeSprintRetroData
    # Description: Analyzes manually compiled sprint retrospective data.

    inputDocumentSelectors:
      - "SprintRetroAnalysis_*"
    inputDateSelector: null
    outputName: "SprintRetroInsights_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      Based *only* on the content of the Sprint Retrospective Analysis document titled "{{InputFileName}}", which includes sections like "Quantitative Performance Analysis", "Deep Pattern Analysis", "Previous Action Assessment", "Team Health Assessment", and "AI-Generated Insights" (from a previous step or human input):

      1.  **Summarize Key Performance Trends:** From the "Quantitative Performance Analysis" and "Deep Pattern Analysis", identify and summarize 2-3 notable performance trends (e.g., in velocity, quality, cycle time).
      2.  **Highlight Recurring Themes:** From the "Deep Pattern Analysis" and "Previous Action Assessment", identify 1-2 themes or issues that appear to be recurring across sprints or from previous actions.
      3.  **Identify Potential Systemic Root Causes:** Based on the "Systemic Root Causes" section (if provided with evidence) or by inferring from recurring themes, list 1-2 potential systemic root causes for discussion.
      4.  **Suggest Discussion Prompts:** Generate 3 thought-provoking questions based on your analysis. These questions should help the team delve deeper into the identified trends, themes, or root causes.

      Format your output clearly under these headings.

      INPUT DOCUMENT CONTENT:
      ```
      {{DocumentContext}}
      ```
    ```

#### 3.2. Suggest Sprint Retrospective Actions Workflow

* **Workflow Name (in TIP):** `SuggestSprintActions`
* **Description:** Takes a `SprintRetroSession_SprintX_YYYY-MM-DD` TIP Document containing notes from a retrospective session and suggests potential action items.
* **Ritual Relevance:** Advanced Retrospective System (Sprint Retrospective Action Planning).
* **Input Document Template (Expected):** `SprintRetroSession_SprintX_YYYY-MM-DD` (created using `Template_SprintRetrospectiveSession_Phase3` from `tip-phase3-templates-library.md`).
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: SuggestSprintActions
    # Description: Suggests potential action items based on retrospective session notes.

    inputDocumentSelectors:
      - "SprintRetroSession_*"
    inputDateSelector: null
    outputName: "Output_SuggestedSprintActions_for_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      Review the "Focused Pattern Exploration", "Root Cause Investigation", and "Strategic Improvement Planning" sections of the Retrospective Session Notes from the document titled "{{InputFileName}}".
      Based on the identified root causes and planned improvement initiatives or experiments:

      Suggest 3-5 concrete, actionable, and measurable (if possible) improvement actions the team could take.
      For each suggested action:
      - Provide a clear description of the action.
      - Briefly state the rationale, linking it to a specific root cause or improvement initiative discussed in the notes.

      Example Format:
      **Suggested Action 1:**
      - Description: [Action description]
      - Rationale: [Rationale based on notes, e.g., "Addresses root cause X discussed under Pattern Y"]

      RETROSPECTIVE SESSION NOTES DOCUMENT CONTENT:
      ```
      {{DocumentContext}}
      ```
    ```

#### 3.3. Analyze Quarterly Trends Workflow

* **Workflow Name (in TIP):** `AnalyzeQuarterlyTrends`
* **Description:** Analyzes a `QuarterlyMetaRetro_YYYY-QQ_TeamName` TIP Document (manually synthesized from sprint retrospectives) to identify broader trends and systemic patterns over the quarter.
* **Ritual Relevance:** Advanced Retrospective System (Quarterly Meta-Retrospective).
* **Input Document Template (Expected):** `QuarterlyMetaRetro_YYYY-QQ_TeamName` (created using `Template_QuarterlyMetaRetrospective_Phase3` from `tip-phase3-templates-library.md`).
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: AnalyzeQuarterlyTrends
    # Description: Analyzes synthesized quarterly retrospective data for broader trends.

    inputDocumentSelectors:
      - "QuarterlyMetaRetro_*"
    inputDateSelector: null
    outputName: "Output_QuarterlyTrendsAnalysis_for_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      Based *only* on the content of the Quarterly Meta-Retrospective document titled "{{InputFileName}}", which includes sections like "Performance Trend Analysis", "System Dynamics Exploration", and "Capability Assessment":

      1.  **Identify Key Quarterly Performance Trends:** Summarize 2-3 significant performance trends observed over the quarter as described in the "Performance Trend Analysis" section.
      2.  **Highlight Systemic Dynamics:** From "System Dynamics Exploration", identify 1-2 key systemic forces or constraints that were prominent during the quarter.
      3.  **Summarize Capability Evolution:** Based on "Capability Assessment & Development Planning", summarize 1-2 key insights about the team's capability evolution or gaps during the quarter.
      4.  **Suggest Strategic Discussion Points:** Generate 2-3 strategic questions for the team to consider for the next quarter, based on the overall quarterly analysis.

      Format your output clearly.

      INPUT DOCUMENT CONTENT:
      ```
      {{DocumentContext}}
      ```
    ```

#### 3.4. Analyze Annual Performance Workflow

* **Workflow Name (in TIP):** `AnalyzeAnnualPerformance`
* **Description:** Analyzes an `AnnualStrategicRetro_YYYY_TeamName` TIP Document (manually synthesized from quarterly retrospectives) for long-term strategic insights.
* **Ritual Relevance:** Advanced Retrospective System (Annual Strategic Retrospective).
* **Input Document Template (Expected):** `AnnualStrategicRetro_YYYY_TeamName` (created using `Template_AnnualStrategicRetrospective_Phase3` from `tip-phase3-templates-library.md`).
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: AnalyzeAnnualPerformance
    # Description: Analyzes synthesized annual retrospective data for strategic insights.

    inputDocumentSelectors:
      - "AnnualStrategicRetro_*"
    inputDateSelector: null
    outputName: "Output_AnnualPerformanceAnalysis_for_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      Based *only* on the content of the Annual Strategic Retrospective document titled "{{InputFileName}}", which includes sections like "Annual Performance Review", "Team Evolution Analysis", "Business Impact Assessment", and "Capability Development Strategy":

      1.  **Summarize Major Annual Achievements & Challenges:** From "Annual Performance Review", list 2-3 major achievements and 2-3 notable challenges of the year.
      2.  **Key Team Evolution Insights:** From "Team Evolution Analysis", highlight 1-2 significant aspects of the team's evolution (composition, skills, practices).
      3.  **Business Impact Highlights:** From "Business Impact Assessment", summarize 1-2 key business impacts delivered by the team during the year.
      4.  **Strategic Capability Focus:** Based on "Capability Development Strategy", identify 1-2 strategic capability areas that were or should be a focus.
      5.  **Generate Long-Term Strategic Questions:** Formulate 2-3 questions to guide the team's long-term strategic visioning based on the annual review.

      Format your output clearly.

      INPUT DOCUMENT CONTENT:
      ```
      {{DocumentContext}}
      ```
    ```

### 4. Cross-Team Intelligence Workflows

#### 4.1. Synthesize Cross-Team Updates Workflow

* **Workflow Name (in TIP):** `SynthesizeCrossTeamUpdates`
* **Description:** Processes a TIP Document containing compiled updates from multiple teams (or a list of relevant team update document names and their summaries) to synthesize insights and identify patterns.
* **Ritual Relevance:** Cross-Team Intelligence (Weekly Cross-Pollination).
* **Input Document Template (Expected):** A manually compiled TIP Document (e.g., `Input_CrossTeamUpdates_YYYY-MM-DD`) containing summaries/key points from different team updates or references to their update documents.
    * Example input document content:
        ```markdown
        # Cross-Team Updates Input - YYYY-MM-DD

        ## Team A Update Summary (Source: TeamUpdate_TeamA_YYYY-MM-DD)
        - Key Development: Launched feature X.
        - Learning: Found new approach for Y.
        - Challenge: Facing issue Z.

        ## Team B Update Summary (Source: TeamUpdate_TeamB_YYYY-MM-DD)
        - Key Development: Started project P.
        - Learning: Tool Q is very effective.
        - Challenge: Also facing issue Z.
        ```
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: SynthesizeCrossTeamUpdates
    # Description: Synthesizes updates from multiple teams to find patterns.

    inputDocumentSelectors:
      - "Input_CrossTeamUpdates_*"
    inputDateSelector: null
    outputName: "CrossPollinationSummary_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      Review the compiled updates or summaries from multiple teams provided in the document titled "{{InputFileName}}".
      Based *only* on the information within this document:

      1.  **Common Themes or Challenges:** Identify any themes, challenges, or key developments that are mentioned by more than one team.
      2.  **Potential Knowledge Sharing Opportunities:** Highlight any learnings or successes from one team that could benefit others.
      3.  **Potential Collaboration Points:** Suggest 1-2 areas where teams might benefit from collaborating based on their reported activities or challenges.

      Format your output clearly.

      INPUT DOCUMENT CONTENT:
      ```
      {{DocumentContext}}
      ```
    ```

#### 4.2. Identify Shared Challenges Workflow

* **Workflow Name (in TIP):** `IdentifySharedChallenges`
* **Description:** Analyzes a TIP Document compiling detailed challenge descriptions from multiple teams to identify common root causes or patterns.
* **Ritual Relevance:** Cross-Team Intelligence (Monthly Cross-Team Ritual).
* **Input Document Template (Expected):** A manually compiled TIP Document (e.g., `Input_SharedChallengesAnalysis_YYYY-MM`) detailing challenges from various teams.
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: IdentifySharedChallenges
    # Description: Identifies shared challenges and potential common root causes.

    inputDocumentSelectors:
      - "Input_SharedChallengesAnalysis_*"
    inputDateSelector: null
    outputName: "Output_SharedChallengesAnalysis_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      Review the detailed challenge descriptions from multiple teams provided in the document titled "{{InputFileName}}".
      Based *only* on this information:

      1.  **Categorize Challenges:** Group the described challenges into 2-4 broad categories.
      2.  **Identify Cross-Cutting Themes:** For each category, identify any themes or specific issues that are reported by multiple teams.
      3.  **Suggest Potential Common Root Causes:** For 1-2 of the most prevalent shared challenges, suggest potential underlying root causes that might affect multiple teams.

      Format your output clearly.

      INPUT DOCUMENT CONTENT:
      ```
      {{DocumentContext}}
      ```
    ```

#### 4.3. Suggest Collaborative Practices Workflow

* **Workflow Name (in TIP):** `SuggestCollaborativePractices`
* **Description:** Reviews a TIP Document describing current practices from multiple teams and suggests potential shared or best practices.
* **Ritual Relevance:** Cross-Team Intelligence (Monthly Cross-Team Ritual).
* **Input Document Template (Expected):** A manually compiled TIP Document (e.g., `Input_TeamPracticesReview_YYYY-MM`) describing various practices used by different teams.
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: SuggestCollaborativePractices
    # Description: Suggests shared or best practices from a review of team practices.

    inputDocumentSelectors:
      - "Input_TeamPracticesReview_*"
    inputDateSelector: null
    outputName: "Output_CollaborativePractices_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      Review the descriptions of current practices from multiple teams provided in the document titled "{{InputFileName}}".
      Based *only* on this information:

      1.  **Identify Highly Effective Practices:** Highlight 1-2 practices described by one team that seem particularly effective or innovative and could be beneficial to others. Explain why.
      2.  **Identify Areas for Standardization:** Point out 1-2 areas where teams are using different practices for similar tasks, and where a standardized approach might be beneficial.
      3.  **Suggest a "Hybrid" Best Practice:** If applicable, combine elements from different teams' practices to suggest one "hybrid" best practice for a common activity.

      Format your output clearly.

      INPUT DOCUMENT CONTENT:
      ```
      {{DocumentContext}}
      ```
    ```

#### 4.4. Analyze Portfolio Patterns Workflow

* **Workflow Name (in TIP):** `AnalyzePortfolioPatterns`
* **Description:** Analyzes a TIP Document compiling strategic information and performance data from multiple teams or projects to identify portfolio-level patterns.
* **Ritual Relevance:** Cross-Team Intelligence (Quarterly Alignment Session).
* **Input Document Template (Expected):** A manually compiled TIP Document (e.g., `Input_PortfolioReview_YYYY-QQ`) containing strategic summaries, key objectives, and high-level performance indicators from multiple teams/projects.
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: AnalyzePortfolioPatterns
    # Description: Analyzes strategic information from multiple teams for portfolio-level patterns.

    inputDocumentSelectors:
      - "Input_PortfolioReview_*"
    inputDateSelector: null
    outputName: "Output_PortfolioPatterns_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      Review the strategic information and performance data from multiple teams/projects, as compiled in the document titled "{{InputFileName}}".
      Based *only* on this information:

      1.  **Common Strategic Themes:** Identify 2-3 strategic themes or objectives that are common across multiple teams/projects.
      2.  **Portfolio-Level Risks/Opportunities:** Highlight 1-2 potential risks or opportunities that emerge when looking across the portfolio (e.g., resource contention, synergistic opportunities).
      3.  **Areas of High/Low Performance Concentration:** Identify if there are particular types of projects or strategic areas where performance (as described in the input) is consistently high or low across the portfolio.
      4.  **Suggested Discussion Points for Alignment:** Based on the analysis, suggest 2-3 key discussion points for a cross-team strategic alignment session.

      Format your output clearly.

      INPUT DOCUMENT CONTENT:
      ```
      {{DocumentContext}}
      ```
    ```

### 5. Advanced AI Pair Working Workflows (Examples)

These workflows are more generic and rely on the user providing specific instructions and context within their input TIP Document, often created from `Template_PairWorkingSessionInitialization_Phase3`.

#### 5.1. Draft Document Section Workflow (Advanced)

* **Workflow Name (in TIP):** `DraftSectionAdvanced`
* **Description:** Helps a team member draft a complex section of a document based on a detailed outline, source materials, and specific stylistic requirements provided in the input TIP Document.
* **Ritual Relevance:** Advanced AI Pair Working.
* **Input Document Template (Expected):** User-created TIP Document (e.g., `PairInput_DraftStrategyDocSection3_YYYY-MM-DD`) containing a detailed request.
    * Example content:
        ```markdown
        # Task: Draft Section 3.2 - Competitive Analysis

        ## Outline:
        - Intro to key competitors (A, B, C)
        - Competitor A: Strengths, Weaknesses, Recent Moves
        - Competitor B: Strengths, Weaknesses, Recent Moves
        - Competitor C: Strengths, Weaknesses, Recent Moves
        - Comparative summary table (Pros/Cons vs. our offering)
        - Strategic implications

        ## Source Material Snippets:
        - Source 1 (Competitor A Q1 Report): "..."
        - Source 2 (Market News Article on B): "..."
        - Source 3 (Internal notes on C): "..."

        ## Tone: Formal, analytical.
        ## Key Terms to Include: market share, disruptive innovation, value proposition.
        ```
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: DraftSectionAdvanced
    # Description: Drafts a document section based on detailed instructions and source material in the input document.

    inputDocumentSelectors:
      - "PairInput_*"
    inputDateSelector: null
    outputName: "DraftOutput_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      The following input document "{{InputFileName}}" contains a request to draft a text section.
      The request includes an outline, potentially some source material snippets, and specific instructions regarding tone or key terms.

      Based *only* on the information provided in the input document below, please draft the requested text section.
      Adhere strictly to the provided outline. Incorporate the source material snippets where relevant.
      Maintain the specified tone and naturally weave in any key terms mentioned.
      Aim for a comprehensive and well-structured draft.

      Input Document Content:
      ```
      {{DocumentContext}}
      ```

      Begin your response directly with the drafted section.
    ```

#### 5.2. Brainstorm Strategic Ideas Workflow (Advanced)

* **Workflow Name (in TIP):** `BrainstormStrategicIdeas`
* **Description:** Generates strategic ideas based on a detailed problem statement, background context, constraints, and desired future state provided in an input TIP Document.
* **Ritual Relevance:** Advanced AI Pair Working.
* **Input Document Template (Expected):** User-created TIP Document (e.g., `PairInput_BrainstormGrowthStrategy_YYYY-MM-DD`) containing a detailed request.
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: BrainstormStrategicIdeas
    # Description: Brainstorms strategic ideas based on a detailed context.

    inputDocumentSelectors:
      - "PairInput_*"
    inputDateSelector: null
    outputName: "BrainstormOutput_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      The input document "{{InputFileName}}" contains a request for brainstorming strategic ideas.
      It details a problem/opportunity, background context, constraints, and a desired future state.

      Based *only* on this information, generate 5-7 distinct strategic ideas.
      For each idea:
      - Provide a concise title.
      - Briefly explain the core concept of the idea.
      - Briefly mention how it aligns with the desired future state or addresses the problem within the given constraints.

      Present the ideas as a numbered list.

      Input Document Content:
      ```
      {{DocumentContext}}
      ```

      Begin your response directly with the list of brainstormed strategic ideas.
    ```

#### 5.3. Summarize Complex Document Workflow (Advanced)

* **Workflow Name (in TIP):** `SummarizeComplexDoc`
* **Description:** Summarizes a lengthy or complex document provided in the input TIP Document, focusing on specific aspects or questions outlined by the user in their request.
* **Ritual Relevance:** Advanced AI Pair Working.
* **Input Document Template (Expected):** User-created TIP Document (e.g., `PairInput_SummarizeResearchPaperX_YYYY-MM-DD`) containing the text to summarize and specific instructions.
    * Example content:
        ```markdown
        # Task: Summarize Research Paper on Topic Y

        ## Focus Areas for Summary:
        1.  What is the main hypothesis of the paper?
        2.  What methodology was used?
        3.  What are the key findings (3-5 bullet points)?
        4.  What are the stated limitations?
        5.  What are the main conclusions or implications for our project Z?

        ## Full Text of Document to Summarize:
        [User pastes the full text of the research paper here]
        ```
* **TIP Process Workflow Definition:**
    ```yaml
    # Workflow Name: SummarizeComplexDoc
    # Description: Summarizes a complex document focusing on user-defined aspects.

    inputDocumentSelectors:
      - "PairInput_*"
    inputDateSelector: null
    outputName: "SummaryOutput_from_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
    prompt: |
      The input document "{{InputFileName}}" contains a body of text to be summarized AND specific instructions or questions outlining the desired focus areas for the summary.

      Carefully review the "Focus Areas for Summary" (or similar instruction section) and the "Full Text of Document to Summarize" within the input document.

      Based *only* on the provided text and instructions, generate a summary that directly addresses each of the specified focus areas or questions.
      Structure your output clearly, addressing each point from the focus areas.

      Input Document Content:
      ```
      {{DocumentContext}}
      ```

      Begin your response directly with the focused summary.
    ```

## **Notes on Usage by Team Users**

* To use these workflows, navigate to the "Run Workflows" section in TIP.
* Select the desired workflow (e.g., `AnalyzeContextHealth`).
* TIP will then prompt you to select the input TIP Document(s).
    * Ensure your input TIP Document is named according to the convention specified in the workflow's `inputDocumentSelectors` (e.g., a document named `Input_ContextHealthAnalysis_2025-05-11` for `AnalyzeContextHealth`).
    * For many Phase 3 workflows, you will need to first manually compile information from various sources or other TIP Documents into a *new* input TIP Document, structured according to the workflow's needs or based on a template from `tip-phase3-templates-library.md`.
    * For "Advanced AI Pair Working" workflows, you will create a new TIP Document containing your specific text, data, and detailed instructions for the LLM, then select this document as input.
* The workflow will process the input document(s) using the LLM and its defined prompt.
* A new TIP Document will be created with the output, named according to the `outputName` template. Review, edit, and use this AI-generated document as part of the ritual.
* Since the LLM has no internet or tool access, all necessary information for the workflow must be meticulously prepared and contained within the input TIP Document(s). The quality of the output heavily depends on the quality and completeness of the input.

## **Notes for Administrators**

* These workflow definitions should be created or updated in the "Workflow Management" area of TIP.
* The "Workflow Name (in TIP)" is the human-readable name users will see.
* The YAML content provided for each workflow should be pasted into the Markdown editor when creating/editing the Process Workflow's content in TIP.
* Ensure prompts are well-suited for your TIP instance's LLM capabilities. Refine based on output quality. Prompts in Phase 3 are often more complex and may require careful tuning.
* The global LLM model and temperature settings in TIP apply.
* Regularly review team feedback and outputs from rituals (documented in TIP Documents) to identify needs for new workflows or improvements to existing prompts. The "Advanced AI Pair Working" outputs, if documented using `Template_ComprehensiveSessionLog_Phase3`, can be a rich source for identifying new, more specialized workflow needs.
