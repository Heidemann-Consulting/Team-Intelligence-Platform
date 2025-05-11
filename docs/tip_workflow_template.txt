# Glob pattern for input documents, e.g., "KW*_Weekly_Analysis", "*.txt"
inputDocumentSelectors: ["Input_Doc_*"]
# Optional date filter for input documents:
# olderThanDays 60
# newerThanDays 7
# between_YYYY-MM-DD_YYYY-MM-DD
inputDateSelector: newerThanDays 7
# Output document name template. Placeholders:
# {{Year}}, {{Month}}, {{Day}}, {{InputFileName}}, {{WorkflowName}}
outputName: "{{WorkflowName}}_Output_{{Year}}-{{Month}}-{{Day}}"
# Prompt for the LLM. Placeholders:
# {{DocumentContext}}, {{CurrentDate}}, {{CurrentTime}}, {{Year}}, {{Month}}, {{Day}}
# {{InputFileNames}}, {{InputFileCount}}, {{InputFileName}} (name of first input)
prompt: |
  SYSTEM: You are an AI assistant. Your task is to process the provided context based on the user's request.

  CONTEXT:
  {{DocumentContext}}

  INPUT_DETAILS:
  - Workflow Name: {{WorkflowName}}
  - File Count: {{InputFileCount}}
  - File Names: {{InputFileNames}}
  - First File Name (if any): {{InputFileName}}

  CURRENT_DATE_TIME:
  - Date: {{CurrentDate}}
  - Time: {{CurrentTime}}
  - Year: {{Year}}
  - Month: {{Month}}
  - Day: {{Day}}

  TASK:
  1. Analyze the provided document context thoroughly.
  2. Generate a concise summary of the key points.
  3. Identify any action items mentioned.

  OUTPUT_FORMAT:
  ## Summary of {{InputFileName | default('Input Document(s)')}} for {{WorkflowName}}

  **Key Points:**
  - [Point 1]
  - [Point 2]

  **Action Items:**
  - [Action Item 1]

  CONSTRAINTS:
  - Be concise.
  - Focus on key insights.

  SELF-CHECK:
  - Is the summary accurate and concise?
  - Are all relevant action items captured?
  - Does the output adhere to the specified format?
