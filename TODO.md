# TODOs

## Prio 1

* ✅ When Workflow Output Document (Name) exists, then the existing document shall be updated with a new version (no new name).
* ✅ In RunWorkflowModal the Name of the output result shall be displayed.
* ✅ When duplicating a document that it duplicates based on the currently selected version and not automatically uses the newest version.
* ✅ the ollama model shall be configured via env file not via workflow definition - remove it everywhere it is not needed any longer.
* ✅ The model output shall be stripped from everything starting with "<think>" and ending with "</think>", including these two tags. Also all linebreaks/newlines at the start and at the end of the document shall be removed after the "<think>" part has been removed.

* ✅ Templates and Workflows shall only visible & editable by Admins, not by teams anymore.
* ✅ All Templates and Workflows shall automatically be usable by all teams.
* ✅ Teams get a separate "Execute Workflow" view that does not show the workflow code/content itself, but allows execution of the workflow in the same manner as it was possible for users befor this change.

* ✅ Rework README.md, PITCH.md and CONTRIBUTING.md

* ✅ Rename to Team Intelligence Platform (TIP)
* ✅ Add TIP Logo to Web-Pages (Dashboards & Logins) and to Website-Favicon

* ✅ Remove separate search view
* ✅ In Document, Template and Workflow List-Views behind each version tag display the creation date of that version
* ✅ Integrate search in each element list views to select visible documents based on full text search
* ✅ Integrate sort in each element list views so that users can sort ascending and descending for name and for latest version creation date
* ✅ Hide Admin-Team in Teamlistview (so that it cannot be removed or changed)

* ✅ When in apiClient.ts a user is redirected to login because the session is expired make sure that the existing cookie is deleted.
* ✅ The modal "Create New Document" window shall show a preview of the selected template

* ✅ Under each workflow in the team user view show which documents it uses (i.e. list all inputDocumentSelectors) as input and which document it creates as output (i.e. show outputName with correctly replaced placeholders in it).
* ✅ Make sure that each workflow can indeed take multiple different kinds of documents as defined by multiple inputDocumentSelectors as input.

* ✅ Create / Update PRD and SRS
* ✅ Update the rituals and practices documents and create matching workflow libraries

* ✅ Make template selection list in the create new document modal be alphabetically sorted.
* ✅ Added functionality that when starting a workflow users can choose via an alphabetically sorted list of applicable documents with checkboxes which documents will be used as input documents. It shall also contain an explicit warning when no applicable documents were found and offer to either cancel or run the workflow anyways.

* ✅ Create templates and workflows for Lean AI-Co-Management (LACM) process

* ✅ Export templates and workflows in ulacm_backend/init_db.sql

## Prio 2

* ✅ Rework the api endpoint /api/v1/items to enable filtering directly via the query, so that there is no problem when the amount of documents exceeds 100. Also rework all occasions where this endpoint is used in order to take advantage of the new filtering functionality (and move filtering / search from frontend to backend).
combin with:
* ✅ Performance: Using ContentItemWithCurrentVersion for lists means that for every item, its current version's details (including potentially large markdown_content) are loaded and serialized. Because lists could become very long or performance becomes an issue, create a more lightweight schema specifically for list items that includes item_id, name, item_type, current_version_number, and other essential list view fields, but omits the full markdown_content.

* ✅ Document default name (the prefilled entry for the document name) should always correspond to "Templatename_YYYY_MM_DD" with YYYY_MM_DD being the current date and "LACM ", "Phase 1 ", "Phase 2 " and "Phase 3 " prefixes shall be stripped from the Templatename.
* ✅ Fix search api endpoint gives unauthorized for admin users.
* ✅ Filtering via search should adjust amount of pages according to results (but not for workflows, which is ok)

* ✅ Make sure the markdown editor does not apply any styles in editor mode and applies all markdown styles in preview mode.

* ✅ Rename „View Documents“ to „Manage Knowledge“

* ✅ Ensure that after creation of each new vdersion the search index is updated too.

* ✅ Ensure that all Workflow Syntax used is supported by the code

* ✅ Update the the nginx proxy timeout to 300s

* ✅ Instead of replacing spaces with underscore in the proposed document name from templates, remove it completely.

* ✅ Make workflow filtering do a full text search on the workflows and their contents.
* ✅ Remove "LACM_" from LACM Workflow Input Document Selectors

* ✅ Make sure that the template preview in the Create New Document modal windows applies all markdown styles, e.g. bullet point lists and tables correctly.
* ✅ Make sure default sorting of content items list view is set to: Newest modified first.

* ✅ Add full text search to Run Workflow document selection. Make sure that selected documents always stay selected and visible even if the current full text search does not match them.
* ✅ Add a full text field to the start Workflow modal window named "Additional input for the AI:" which will be added to the workflow prompt as if it were an added document.
* ✅ Change Workflow Input Selectors to better match more possibilities

* ✅ Add a "Ask AI" text field on top of the document editor and the Actions box, but below the Document Title/Version/Lastsaved box, which can be executed like a workflow and sends the current document in its current state and the content of the text field to the LLM and presents the answer in a new modal popup window with the option to save the answer as a new document (which asks for Document name) or alternatively to close the modal answer window without saving the answer.

* ✅ Add info to readme regarding differences between LACM and the 3 phases: LACM is an easy to use lower barrier of entry process, the 3 phases aim at organizational transformation on a multi-team (and possibly multi-project) level.

* ✅ Add the corresponding prompt as a preview (in a scrollable textbox) of what the workflows do to each workflow box to the ExecuteWorkflowPage - between the info about "INPUT DOCUMENT SELECTORS" and the info about "OUTPUT NAME TEMPLATE".

* ✅ Add „An empty template“ to the list of templates.
* ✅ Also add „A generic workflow“ that has * as Input-Selector and a generic prompt like „You are a helpful AI assistant, have a look at the following:“

* ✅ Adapt headings-sizes in markdown editor and make sure that editor mode sizes and preview mode sizes match.

* ✅ Create slides for short intro to LACM to introduce an overview to the processes in these.

* ✅ Update the LICENSE and create a NOTICE file.

## Prio 3

* ✅ The API endpoint (/run) should stream the response from Ollama. The frontend should show the streamed answer in a textbox rather than showing a spinning wheel animation.

* ✅ Fix jitter when loading workflows in the list of workflows.

* ✅ Move from http to https protocol

* Add Export-Function for the currently opened document in the document editor.
* Add Export-Function for all currently selected Documents in the Document Overview List.

* When auth cookie expires:
Abrupt Redirects: A sudden redirect can be jarring if the user is in the middle of something.
Lost State: If the user was filling out a form or had unsaved changes, a direct window.location.href change will lose that state.
Message to User: The user might not understand why they were redirected. A small, temporary message (e.g., using a toast notification before redirecting) like "Your session has expired. Redirecting to login..." can improve UX. Your current code has console.warn("API returned 401 Unauthorized."); but doesn't show a toast for 401.
Redirect Loops:
The condition !window.location.pathname.includes('/login') is a good basic check to prevent an immediate redirect loop if the /login page itself (or API calls made from it) somehow triggers a 401.
Ensure your /login page does not make API calls that could return a 401 before the user has a chance to log in (e.g., trying to fetch user data with an expired token).
Centralized Authentication State Management:
As hinted in your commented code (// Potentially trigger a global logout event here if using Zustand/Redux), a more robust approach often involves a global state management solution (like Zustand, Redux, React Context).
When a 401 occurs, you would dispatch an action or update a global state that signifies the user is unauthenticated.
Your routing logic (e.g., using ProtectedRoute components or similar) would then react to this state change and automatically render the login page or redirect.
This allows for cleaner separation of concerns: apiClient detects the 401 and updates auth state; UI components/router react to auth state.
This also makes it easier to clear any user-specific data (like tokens, user profile info) from the client-side state upon logout/unauthorization.
Token Refresh Mechanisms:
For an even more robust system (though potentially more complex to implement), if you're using JWTs with refresh tokens, a 401 could trigger an attempt to silently refresh the access token using the refresh token. If the refresh is successful, the original failed request can be retried automatically without the user even noticing. If the refresh token is also invalid or expired, then you would proceed to log the user out and redirect. This is usually beyond basic 401 handling.

* Complete backend unit tests
* Implement Frontend tests
* Add CI workflows
* Ensure Frontend Usability and Polish
* Verify XSS Protection in Frontend
* Change lines that are tagged with: !!! TODO: Change in PRODUCTION !!!
