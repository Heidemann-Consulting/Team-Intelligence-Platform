# **Team Intelligence Platform (TIP) - Phase 1 Workflow Library**

**Version:** 1.0
**Date:** May 11, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

## **Table of Contents**

- [**Team Intelligence Platform (TIP) - Phase 1 Workflow Library**](#team-intelligence-platform-tip---phase-1-workflow-library)
  - [**Table of Contents**](#table-of-contents)
  - [**Introduction**](#introduction)
  - [**Core Phase 1 Workflows**](#core-phase-1-workflows)
    - [1. Summarize Text Workflow](#1-summarize-text-workflow)
    - [2. Generate Meeting Summary Workflow](#2-generate-meeting-summary-workflow)
  - [**Notes on Usage by Team Users**](#notes-on-usage-by-team-users)
  - [**Notes for Administrators**](#notes-for-administrators)

## **Introduction**

This document serves as a library of predefined Process Workflows for Phase 1 of the Team Intelligence Platform (TIP) adoption. These workflows are designed to be created by System Administrators within TIP's Process Workflow management area. Team Users can then execute these globally visible workflows to assist with their tasks.

Each workflow definition below is presented in the YAML-like format expected by TIP when an Administrator creates or edits a Process Workflow's content in the Markdown editor.

## **Core Phase 1 Workflows**

### 1. Summarize Text Workflow

* **Workflow Name (in TIP):** `SummarizeTextWorkflow`
* **Description:** This workflow takes a single TIP Document as input and generates a concise summary of its content. It's useful for quick digests of articles, reports, or lengthy context items.
* **Ritual Relevance:**
    * Context Curation Ritual (Optional daily summarization)
    * General ad-hoc summarization tasks.

**TIP Process Workflow Definition:**
```yaml
# Workflow Name: SummarizeTextWorkflow
# Description: Summarizes the content of a single input TIP document.

inputDocumentSelectors:
  - "*" # Allows user to select any one document visible to them at runtime.
inputDateSelector: null # No specific date filter by default for this generic workflow.
outputName: "Summary_of_{{InputFileName}}_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  Please provide a concise summary of the following document:

  DOCUMENT CONTENT:
  ```
  {{DocumentContext}}
  ```

  Focus on the key points, main arguments, and any conclusions presented in the document.
  The summary should be easy to understand and capture the essence of the original text.
```

---

### 2. Generate Meeting Summary Workflow

* **Workflow Name (in TIP):** `GenerateMeetingSummaryWorkflow`
* **Description:** This workflow processes a TIP Document containing raw meeting notes (ideally created using the "Meeting_Notes_Template" from the `tip-phase1-ritual-templates-library.md`) and generates a structured meeting summary. It looks for plain text markers like `#decision` and `#action` to help structure the output.
* **Ritual Relevance:**
    * AI-Assisted Documentation Ritual.

**TIP Process Workflow Definition:**
```yaml
# Workflow Name: GenerateMeetingSummaryWorkflow
# Description: Generates a structured meeting summary from a meeting notes document.

inputDocumentSelectors:
  - "MeetingNotes_*" # Designed for documents like MeetingNotes_ProjectAlpha_YYYY-MM-DD.md
  - "Meeting_Notes_*"
  - "*_MeetingNotes_*"
inputDateSelector: null # User will typically select a recent meeting notes document.
outputName: "MeetingSummary_from_{{InputFileName}}_AI-Generated_{{Year}}-{{Month}}-{{Day}}"
prompt: |
  You are an AI assistant tasked with creating a structured summary from the provided meeting notes.

  MEETING NOTES DOCUMENT:
  ```
  {{DocumentContext}}
  ```

  Please carefully read the meeting notes and generate a summary that includes the following sections:
  1.  **Overview:** A brief 1-2 sentence overview of the meeting's purpose and main outcome.
  2.  **Key Decisions:** List all significant decisions made. Look for lines or sections marked with '#decision'.
  3.  **Action Items:** List all action items identified. Look for lines or sections marked with '#action'. Try to identify the owner and due date if mentioned.
  4.  **Discussion Summary:** For each main topic discussed, provide a concise summary of the key points.

  Format the output clearly. For example:

  # Summary: [Extract Meeting Name from InputFileName if possible] - {{CurrentDate}}

  ## Overview
  [Generated overview here]

  ## Key Decisions
  - [Decision 1 text]
  - [Decision 2 text]

  ## Action Items
  - [ ] [Action 1 text] (Owner: @name) (Due: YYYY-MM-DD)
  - [ ] [Action 2 text] (Owner: @name)

  ## Discussion Summary
  ### [Topic 1 Name]
  [Summary of discussion for topic 1]
  ### [Topic 2 Name]
  [Summary of discussion for topic 2]

  Current Date for reference: {{CurrentDate}}
  Source Document Name: {{InputFileName}}
```

---

## **Notes on Usage by Team Users**

* To use these workflows, navigate to the "Execute Workflow" section in TIP.
* Select the desired workflow (e.g., `SummarizeTextWorkflow` or `GenerateMeetingSummaryWorkflow`).
* TIP will then prompt you to select the input document(s) based on the `inputDocumentSelectors` defined in the workflow.
    * For `SummarizeTextWorkflow`, you can generally select any document you want to summarize.
    * For `GenerateMeetingSummaryWorkflow`, you should select the TIP Document containing the raw meeting notes. Ensure your meeting notes documents follow a consistent naming convention (e.g., starting with "MeetingNotes_") for easier selection.
* The workflow will then process the input document(s) using the LLM and its defined prompt.
* A new TIP Document will be created with the output, named according to the `outputName` template defined in the workflow. You can then review and edit this AI-generated document.

## **Notes for Administrators**

* These workflow definitions should be created or updated in the "Process Workflows" management area of TIP.
* The `workflowName` mentioned above is the human-readable name you assign to the workflow in TIP.
* The YAML content provided should be pasted into the Markdown editor for the respective Process Workflow.
* Ensure that the prompts are well-suited for the capabilities of the locally configured LLM in your TIP instance, as it does not have internet or external tool access.
* Prompts can be refined over time through the "Prompt Development Workshop" ritual. The outcomes of these workshops (documented in TIP Documents using the "Prompt_Documentation_Template") should guide updates to these Process Workflow definitions.
* The global LLM model and temperature settings configured in the TIP backend will apply to these workflows.
