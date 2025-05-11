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

* Export templates and workflows in ulacm_backend/init_db.sql

## Prio 2

* Rework the api endpoint /api/v1/items to enable filtering directly via the query, so that there is no problem when the amount of documents exceeds 100. Also rework all occasions where this endpoint is used in order to take advantage of the new filtering functionality (and move filtering / search from frontend to backend).
combin with:
* Performance: Using ContentItemWithCurrentVersion for lists means that for every item, its current version's details (including potentially large markdown_content) are loaded and serialized. Because lists could become very long or performance becomes an issue, create a more lightweight schema specifically for list items that includes item_id, name, item_type, current_version_number, and other essential list view fields, but omits the full markdown_content.

* The API endpoint (/run) would immediately acknowledge the request (e.g., HTTP 202 Accepted), possibly returning a task/job ID.
The actual workflow processing would happen in the background (e.g., using FastAPI's BackgroundTasks for simple cases, or a dedicated task queue like Celery for more robust needs).
The frontend could then poll a status endpoint or use WebSockets to get updates on the workflow's progress and retrieve the results when ready. This is a more significant architectural change but leads to a much more responsive and robust application. The PRD and SRS (FR-WFEX-001, SRS 8.7.1) currently imply a synchronous request-response for the manual trigger. If such long processing times are common, you might consider revisiting this requirement for a better user experience.

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

## Prio 3

* Complete backend unit tests
* Implement Frontend tests
* Add CI workflows
* Ensure Frontend Usability and Polish
* Verify XSS Protection in Frontend
* Change lines that are tagged with: !!! TODO: Change in PRODUCTION !!!
