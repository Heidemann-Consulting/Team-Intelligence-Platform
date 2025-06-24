# Product Requirements Document: Team Intelligence Platform (TIP)

**Version:** 1.0
**Date:** May 11, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

## Table of Contents

- [Product Requirements Document: Team Intelligence Platform (TIP)](#product-requirements-document-team-intelligence-platform-tip)
  - [Table of Contents](#table-of-contents)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Scope](#12-scope)
    - [1.3 Goals](#13-goals)
    - [1.4 Glossary](#14-glossary)
  - [2. Target Audience \& User Roles](#2-target-audience--user-roles)
    - [2.1 Team User](#21-team-user)
    - [2.2 Administrator](#22-administrator)
  - [3. System Overview](#3-system-overview)
    - [3.1 High-Level Architecture](#31-high-level-architecture)
    - [3.2 Core Concepts](#32-core-concepts)
    - [3.3 Technology Stack](#33-technology-stack)
  - [4. Functional Requirements](#4-functional-requirements)
    - [4.1 General System Requirements](#41-general-system-requirements)
    - [4.2 Admin Account \& Interface](#42-admin-account--interface)
    - [4.3 Team User Authentication](#43-team-user-authentication)
    - [4.4 Content Management](#44-content-management)
      - [4.4.1 General Content Operations](#441-general-content-operations)
      - [4.4.2 Markdown Editor](#442-markdown-editor)
    - [4.5 Versioning](#45-versioning)
    - [4.6 Search](#46-search)
    - [4.7 Process Workflow Definition and Execution](#47-process-workflow-definition-and-execution)
      - [4.7.1 Workflow Definition (Admin-created)](#471-workflow-definition-admin-created)
      - [4.7.2 Workflow Execution (Team-initiated)](#472-workflow-execution-team-initiated)
    - [4.8 Sharing and Visibility](#48-sharing-and-visibility)
    - [4.9 Duplication](#49-duplication)
    - [4.10 AI Co-Management Support](#410-ai-co-management-support)
    - [4.11 Basic Security Best Practices](#411-basic-security-best-practices)
  - [5. Non-Functional Requirements](#5-non-functional-requirements)
    - [5.1 Performance](#51-performance)
    - [5.2 Scalability](#52-scalability)
    - [5.3 Availability and Reliability](#53-availability-and-reliability)
    - [5.4 Security](#54-security)
    - [5.5 Usability and User Experience (UX)](#55-usability-and-user-experience-ux)
    - [5.6 Maintainability](#56-maintainability)
    - [5.7 Deployability](#57-deployability)
  - [6. Data Management](#6-data-management)
    - [6.1 Data Model](#61-data-model)
    - [6.2 Data Retention and Deletion](#62-data-retention-and-deletion)
  - [7. Future Considerations (Post-Initial Release Optional)](#7-future-considerations-post-initial-release-optional)
  - [8. Conclusion](#8-conclusion)

## 1. Introduction

### 1.1 Purpose

This document outlines the requirements for the Team Intelligence Platform (TIP). TIP is a self-contained web application designed to transform how product development teams integrate AI into their collaborative workflows. It enables "AI Co-Management," a paradigm where AI becomes an integrated team member contributing to collective intelligence. TIP provides a streamlined platform for shared knowledge management, AI-driven workflow automation, and AI-assisted content generation, focusing on simplicity, team collaboration, and efficient process execution using Large Language Models (LLMs) via a local Ollama server.

### 1.2 Scope

**In Scope:**

* **Self-Contained Application:** A Single-Page Application (SPA) frontend (React) and a backend API service (Python/FastAPI).
* **Core Entities:** Management of Documents (team-created), Document Templates (admin-created), and Process Workflows (admin-created).
* **Content Editing:** In-app Markdown editor (EasyMDE) for all content creation and modification.
* **Versioning:** Built-in version control for Documents, Templates, and Process Workflows. Saving an item creates a new version. Users can load and view previous versions.
* **LLM Integration:** Interaction with a locally hosted and configured Ollama server for LLM requests as defined in Process Workflows. Default model and temperature are configured globally in the backend.
* **Data Storage:** All application data, including documents, templates, workflows, versions, and team information, stored in a local PostgreSQL database. Includes Full-Text Search (FTS) capabilities for content.
* **Team-Based System:** Multi-team support with shared team accounts.
    * Documents are owned by teams.
    * Templates and Workflows are managed by Administrators (owned by a system-level admin entity) and can be made globally visible for teams to use.
    * Documents owned by teams can also be marked globally visible for read-only access by other teams.
* **AI Co-Management Support:** Features enabling practices like Collective Context Management, AI-Assisted Documentation, and Context-Aware Planning.
* **Search:** Functionality for team users to search Documents, and globally visible Templates/Workflows by name, creation date, and full-text content.
* **Security:** Secure password hashing (bcrypt), session management via HTTP-only cookies, and protection against common web vulnerabilities. Rate limiting on sensitive admin login endpoints.
* **Deployment:** Dockerized components (frontend, backend, PostgreSQL) orchestrated via docker-compose. Optional Ollama containerization within the same setup.
* **Admin Interface:** A web-based admin interface for managing team user accounts and system-level Templates and Workflows, protected by an administrator password.
* **Language:** English language support only for the UI and system messages.

**Out of Scope:**

* Continuous Integration / Continuous Deployment (CI/CD) pipelines.
* Storage of data in Git, Obsidian, or any external file systems beyond PostgreSQL.
* Interaction with external LLM tools, agents, Model Context Protocol (MCP) servers, or any LLM services other than the configured local Ollama server.
* Individual user accounts (only team-based accounts and a single system administrator).
* Complex permission models beyond team ownership for documents, admin ownership for templates/workflows, and global read-only sharing.
* Advanced Git-like versioning features (e.g., branching, merging). Versioning is linear.
* Real-time collaborative editing. Versioning is based on explicit "Save" actions.
* External identity providers or SSO.

### 1.3 Goals

* **Enable AI Co-Management:** Foster a collective intelligence where the team's combined human-AI capability surpasses the sum of its individual parts by integrating AI as a team member.
* **Transform Team Workflows:** Provide tools for teams to collaboratively create, manage, and automate document-centric processes using AI.
* **Enhance Collective Performance:** Offer team-focused AI rituals and collaboration patterns optimized for human-AI teamwork.
* **Preserve and Enhance Team Context:** Focus on building and maintaining a shared, persistent team knowledge base accessible to both humans and AI.
* **Leverage Local LLMs:** Integrate seamlessly with a local Ollama server for AI assistance while maintaining data privacy and control.
* **Ensure Ease of Use & Accessibility:** Deliver an intuitive user experience through a modern web interface and a fully open-source component stack.
* **Facilitate Deployment:** Ensure the entire system can be easily deployed and managed using Docker and docker-compose.

### 1.4 Glossary

| Term                               | Description                                                                                                                                                              |
| :--------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **TIP (Team Intelligence Platform)** | The complete application, comprising the frontend, backend API, and database, designed to facilitate AI Co-Management.                                                    |
| **Frontend** | The web-based Single-Page Application (React) providing the user interface.                                                                                             |
| **Backend API** | The server-side application (FastAPI) providing APIs for the frontend, managing business logic, and interacting with the database and Ollama.                             |
| **Ollama Server** | A locally hosted server running Large Language Models, used by TIP for AI-assisted tasks. Configuration includes a default model and temperature.                           |
| **PostgreSQL Database** | The relational database used for storing all TIP data, including documents, templates, workflows, versions, team information, and full-text search capabilities.        |
| **Team User** | A shared account used by multiple members of a team to access TIP.                                                                                                       |
| **Administrator** | A user with privileges to manage team user accounts and system-level Templates and Workflows via a dedicated admin interface.                                              |
| **Document** | A Markdown-based content artifact created by a team, often based on a template or generated by a Process Workflow. Documents have versions and are owned by teams.        |
| **Document Template** | A Markdown-based blueprint used as a starting point for creating new Documents. Templates are created and managed by Administrators and can be made globally visible.      |
| **Process Workflow** | A definition (in a specific YAML-like Markdown format) for automated processes, including LLM prompts and input/output specifications. Managed by Admins.                   |
| **Markdown Editor** | The in-app web-based editor (EasyMDE) used for creating and modifying the content of Documents, Templates, and Process Workflows.                                          |
| **Versioning** | The system's capability to store and manage multiple iterations of Documents, Templates, and Process Workflows. A new version is created upon saving.                      |
| **AI Co-Management** | A paradigm where AI becomes an integrated team member contributing to collective intelligence, rather than just an individual productivity tool.                             |
| **Rituals and Practices** | Core team activities and patterns supported by TIP to foster AI Co-Management (e.g., Collective Context Management, AI-Assisted Documentation).                             |
| **Global Visibility** | A flag that allows admin-created Templates/Workflows or team-created Documents to be visible (read-only or for use) by other teams.                                       |
| **Admin System** | A special system-level identifier used as the owner for all Templates and Workflows created by Administrators.                                                           |

## 2. Target Audience & User Roles

### 2.1 Team User

**Description:** A member of a product development team who uses TIP to integrate AI into their collaborative workflows and participate in AI Co-Management rituals.

**Access:** Logs in using a shared team account (username and password). Multiple members can be logged in concurrently.

**Capabilities:**

* View the team dashboard.
* **Documents:**
    * Create new Documents by selecting an available (admin-created, globally visible) Document Template.
    * View, edit (content and name), and save new versions of Documents owned by their team.
    * View Documents owned by other teams if marked as globally visible.
    * Delete Documents owned by their team.
    * Mark Documents owned by their team as "globally visible" (or private).
    * Duplicate Documents they have access to (creating a new document owned by their team).
* **Templates & Workflows (Usage):**
    * View and use globally visible Document Templates (created by Admins) to create new Documents.
    * View and execute globally visible Process Workflows (created by Admins). Input documents for workflows are those visible to the team. Output documents are owned by the team.
* **Content Editing:** Utilize the in-app Markdown editor for all content modifications.
* **Versioning:** Save new versions of Documents. View version history for Documents and load previous versions into the editor. The editor provides standard undo/redo for current unsaved edits.
* **Search:** Search for their own Documents, and globally visible Documents, Templates, and Workflows.
* **AI Co-Management Participation:** Engage in rituals like Context Curation (by managing shared documents), AI-Assisted Documentation (through workflow outputs), and Context-Aware Planning (by leveraging search and accessible information).

### 2.2 Administrator

**Description:** A privileged user responsible for managing team accounts and system-level content (Templates and Workflows).

**Access:** Logs in using a dedicated admin username and a configurable admin password to access a specific admin web interface.

**Capabilities:**

* **Team Account Management:**
    * Create new team user accounts (defining team name, team username, and team password).
    * View a list of all existing team user accounts.
    * Modify existing team accounts (team name, password, active status). Username is not updatable.
    * Deactivate or reactivate team user accounts.
    * Delete team user accounts (which also deletes content exclusively owned by that team).
* **Template Management:**
    * Create new Document Templates. These are owned by the ADMIN_SYSTEM_TEAM_ID.
    * View, edit (content and name), save new versions, and delete Document Templates.
    * Mark Document Templates as "globally visible" (or private).
    * Duplicate Document Templates.
* **Workflow Management:**
    * Create new Process Workflows. These are owned by the ADMIN_SYSTEM_TEAM_ID.
    * View, edit (content and name), save new versions, and delete Process Workflows.
    * Mark Process Workflows as "globally visible" (or private).
    * Duplicate Process Workflows.
    * Test run Process Workflows they own.
* **Document Management (View/Meta Edit):**
    * View all Documents created by any team.
    * Edit metadata (name, global visibility) of any Document.
    * Delete any Document.
* View the admin dashboard.

## 3. System Overview

### 3.1 High-Level Architecture

TIP is a three-tier application:

1.  **Frontend (Single-Page Application - React):**
    * Provides the user interface for all team user and administrator interactions.
    * Includes modules for dashboard views, content listing, Markdown editing (using EasyMDE), version history display, search, workflow execution triggering, and admin-specific team/template/workflow management.
    * Communicates with the Backend API via RESTful APIs.
2.  **Backend API Service (Python/FastAPI):**
    * Handles all business logic, including:
        * Authentication and authorization for team users and the administrator.
        * CRUD operations for Teams, Documents, Templates, and Process Workflows.
        * Versioning logic for all content items.
        * Interaction with the PostgreSQL database.
        * Orchestration of Process Workflow execution, including formatting prompts and communicating with the local Ollama server using globally configured model and temperature settings.
        * Full-text search indexing and query processing against the database.
3.  **Data Layer & AI Layer:**
    * **PostgreSQL Database:** Primary data store for:
        * Team account information (hashed passwords).
        * ContentItems (Documents, Templates, Workflows) metadata including team_id (owner), item_type, name, is_globally_visible, current_version_id.
        * ContentVersions storing the Markdown content, version_number, saved_by_team_id, and a content_tsv column for full-text search.
    * **Local Ollama Server:** An independent, locally running server hosting LLMs. The Backend API sends requests (prompts) to this server and receives generated text. TIP connects to a pre-configured Ollama instance; it does not manage Ollama itself.

All components (Frontend, Backend API, PostgreSQL) are containerized using Docker and deployed via `docker-compose.yml`. The Ollama server can optionally be part of this Docker Compose setup.

### 3.2 Core Concepts

* **Documents:** Markdown-based artifacts created by teams, potentially from Templates or as workflow outputs. Owned by teams, can be shared globally.
* **Document Templates:** Markdown-based blueprints for Documents. Managed by Admins, owned by ADMIN_SYSTEM_TEAM_ID, and can be made globally visible for teams to use. Default content provided upon creation.
* **Process Workflows:** Definitions for automated processes, written in a YAML-like format within the Markdown editor. Managed by Admins, owned by ADMIN_SYSTEM_TEAM_ID, and can be made globally visible for teams to execute. Include `inputDocumentSelectors` (list of glob patterns), `inputDateSelector`, `outputName` template, and a prompt structure. LLM model and temperature are global backend settings, not defined per workflow. Default content provided upon creation.
* **Versioning:** All Documents, Templates, and Workflows have a linear version history. Saving an item creates a new, immutable version. Users can view history and load prior versions into the editor. The editor itself provides undo/redo for current, unsaved edits.
* **Team/Admin Ownership and Sharing:**
    * Teams own the Documents they create.
    * Administrators create Templates and Workflows, which are owned by a special ADMIN_SYSTEM_TEAM_ID.
    * Team-owned Documents and Admin-owned Templates/Workflows can be marked `is_globally_visible`. Globally visible items can be read or used (e.g., a template to create a document, a document as workflow input) by other teams but not edited by them.
* **AI Co-Management:** The overarching philosophy where TIP facilitates AI becoming an integral part of team collaboration through shared context (managed documents), explicit AI roles (defined by workflows), and integration into team ceremonies (via AI-assisted documentation and planning).

### 3.3 Technology Stack

* **Frontend:** React, Vite, Tailwind CSS, react-simplemde-editor (EasyMDE).
* **Backend API:** Python 3.10+, FastAPI, Uvicorn, SQLAlchemy (async with asyncpg), Pydantic.
* **Database:** PostgreSQL 15+.
* **LLM Server:** Ollama (external or containerized).
* **Containerization & Orchestration:** Docker, Docker Compose.
* **Security:** Passlib (bcrypt) for password hashing, python-jose for JWTs.
* **Workflow Definition Language:** YAML-like structure parsed from Markdown content.

## 4. Functional Requirements

### 4.1 General System Requirements

* **FR-SYS-001:** Self-contained web application (SPA frontend, backend API).
* **FR-SYS-002:** Dockerized components deployable via `docker-compose up`.
* **FR-SYS-003:** Support for typical team usage, aiming for responsiveness with multiple concurrent users.
* **FR-SYS-004:** UI and system messages in English only.
* **FR-SYS-005:** PostgreSQL for all data storage. No external file system storage.
* **FR-SYS-006:** Interaction solely with a locally configured Ollama server using backend-defined model and temperature.

### 4.2 Admin Account & Interface

* **FR-ADM-001:** Dedicated admin web interface.
* **FR-ADM-002:** Admin access protected by a configurable administrator password (via `.env`).
* **FR-ADM-003:** Admin can create team accounts (team name, unique username, password).
* **FR-ADM-004:** Admin can list all team accounts (excluding ADMIN_SYSTEM_TEAM_ID).
* **FR-ADM-005:** Admin can update team details (team name, password, active status). Username is not updatable.
* **FR-ADM-006:** Admin can deactivate/reactivate team accounts.
* **FR-ADM-007:** Admin can delete team accounts. Deletion cascades to team-owned ContentItems. ContentVersions saved by the team will have `saved_by_team_id` set to NULL if the DB schema supports it, or the deletion might be blocked if foreign key constraints are stricter (current schema: `ON DELETE SET NULL` for `content_versions.saved_by_team_id` if `teams.team_id` is deleted).
* **FR-ADM-008:** Admin can create, view, edit, delete, and manage global visibility for Document Templates.
* **FR-ADM-009:** Admin can create, view, edit, delete, and manage global visibility for Process Workflows.
* **FR-ADM-010:** Admin can view all documents from all teams and manage their metadata (name, global visibility) and delete them.

### 4.3 Team User Authentication

* **FR-AUTH-001:** Team users log in with shared team username and password.
* **FR-AUTH-002:** Passwords stored securely (hashed with bcrypt).
* **FR-AUTH-003:** Session established via HTTP-only cookies.
* **FR-AUTH-004:** Multiple team members can use the same account concurrently.
* **FR-AUTH-005:** Logout mechanism provided.

### 4.4 Content Management

#### 4.4.1 General Content Operations

* **FR-CM-001 (Teams):** Team users can create new Documents from available (globally visible, admin-created) Templates.
* **FR-CM-001 (Admins):** Admins can create new Document Templates and Process Workflows.
* **FR-CM-002:** New Documents start with content copied from the selected Template's current version.
* **FR-CM-003:** New Document Templates and Process Workflows are initialized with default instructional content by the frontend.
* **FR-CM-004:** Users (Teams/Admins) can view a list of items relevant to their role and the item type:
    * Teams: Own Documents; Globally see Documents, Templates, Workflows.
    * Admins: All Templates, Workflows, Documents.
* **FR-CM-005:** Users can open and view content of accessible items.
* **FR-CM-006 (Editing):**
    * Teams can edit Documents they own.
    * Admins can edit Templates and Workflows they manage (owned by ADMIN_SYSTEM_TEAM_ID). Admins can edit metadata of any document but not its content directly (content edits are versioned and tied to a saver).
* **FR-CM-007 (Deletion):**
    * Teams can delete Documents they own.
    * Admins can delete Templates, Workflows, and any Document. Confirmation required.
* **FR-CM-008 (Uniqueness):** Item names must be unique per `team_id` (owner) and `item_type`.

#### 4.4.2 Markdown Editor

* **FR-EDIT-001:** In-app web-based Markdown editor (EasyMDE).
* **FR-EDIT-002:** Standard Markdown formatting options (headings, bold, lists, links, etc.).
* **FR-EDIT-003:** User-friendly interface with preview capabilities.

### 4.5 Versioning

* **FR-VER-001:** Documents, Templates, and Workflows have a version history.
* **FR-VER-002:** Saving an item creates a new version. Previous versions are accessible.
* **FR-VER-003:** Each version includes content, version number, `saved_by_team_id` (can be user team or ADMIN_SYSTEM_TEAM_ID), and creation timestamp.
* **FR-VER-004:** Users can view an item's version history (list of versions, timestamps, saver).
* **FR-VER-005:** Users can load content of any previous version into the editor.
* **FR-VER-006:** The editor provides standard undo/redo for unsaved changes in the current editing session. Loading a previous version replaces the editor content; subsequent saves create a new version.

### 4.6 Search

* **FR-SRCH-001:** Team users can search accessible Documents, Templates, and Workflows.
* **FR-SRCH-002:** Search by item name (partial/full) and full-text content. Filters for item type and creation date (after/before).
* **FR-SRCH-003:** Results are filtered by team ownership or global visibility.
* **FR-SRCH-004:** Results display item name, type, and a content snippet (if from FTS).
* **FR-SRCH-005:** The search feature SHALL also provide semantic results using
  an embedding-based retrieval mechanism. Queries are embedded and compared
  against stored document vectors to surface relevant snippets.

### 4.7 Process Workflow Definition and Execution

#### 4.7.1 Workflow Definition (Admin-created)

* **FR-WFDEF-001:** Defined in YAML-like format within the Markdown editor by Admins.
* **FR-WFDEF-002:** Validation of structure on save. Errors reported to Admin.
* **FR-WFDEF-003:** Definition includes:
    * `inputDocumentSelectors`: (List of strings) Glob patterns for input Document names.
    * `inputDateSelector`: (String, optional) Date filter (e.g., `olderThanDays 7`, `between_YYYY-MM-DD_YYYY-MM-DD`).
    * `outputName`: (String) Template for output Document name (placeholders: `{{Year}}`, `{{Month}}`, `{{Day}}`, `{{InputFileName}}`, `{{WorkflowName}}`).
    * `prompt`: (Multiline string) LLM prompt with placeholders (e.g., `{{DocumentContext}}`, `{{CurrentDate}}`).
    * Note: LLM model and temperature are global backend settings, not per workflow.
* **FR-WFDEF-004:** Default instructional content is provided for new workflows.

#### 4.7.2 Workflow Execution (Team-initiated)

* **FR-WFEX-001:** Team users can manually trigger execution of globally visible, Admin-created Workflows.
* **FR-WFEX-002:** On trigger, the system:
    1.  Selects input Documents (latest version) visible to the team, matching selectors.
    2.  Constructs the final prompt using content from selected documents and placeholders.
    3.  Sends the prompt to the Ollama server (using global model/temp settings).
* **FR-WFEX-003:** System displays LLM response in a modal.
* **FR-WFEX-004:** A new Document is created (owned by the executing team, private by default):
    1.  Name generated from `outputName` template.
    2.  Content is the raw LLM output.
* **FR-WFEX-005:** Feedback on execution status (in progress, completed, failed) provided.
* **FR-WFEX-006:** Ollama server errors reported clearly.

### 4.8 Sharing and Visibility

* **FR-SHARE-001 (Documents):** Team-created Documents are private by default. Teams can mark their Documents "globally visible."
* **FR-SHARE-001 (Templates/Workflows):** Admin-created Templates/Workflows are private to Admins (owned by ADMIN_SYSTEM_TEAM_ID) by default. Admins can mark them "globally visible."
* **FR-SHARE-002:** Globally visible items are viewable by all other teams.
* **FR-SHARE-003:** Teams can use globally visible Templates.
* **FR-SHARE-004:** Teams can use globally visible Documents as workflow inputs.
* **FR-SHARE-005:** Teams can view and execute globally visible Workflows.
* **FR-SHARE-006:** Globally visible items cannot be edited/deleted by non-owning teams/non-admins.
* **FR-SHARE-007:** Owners (Teams for Docs, Admins for T/W) can revert items to private.

### 4.9 Duplication

* **FR-DUP-001:**
    * Teams can duplicate Documents they own or globally visible Documents/Templates. Duplicates become new Documents owned by the team.
    * Admins can duplicate Templates, Workflows, and Documents.
* **FR-DUP-002:** Duplication creates an independent copy with content from the source's specified (or current) version. New item is private by default and starts its own version history.
* **FR-DUP-003:** User prompted for a new unique name for the duplicate.

### 4.10 AI Co-Management Support

* **FR-AICM-001:** Document, Template, and Workflow features must support AI Co-Management rituals such as Collective Context Management (shared documents), AI-Assisted Documentation (workflow outputs), Collaborative Prompt Development (Admin workflow creation), and AI-Supported Decision Making (using AI-generated analysis).
* **FR-AICM-002:** Workflow structures must be flexible enough to implement various AI roles (Documentarian, Analyst, Facilitator) as described in AI Co-Management practices.

### 4.11 Basic Security Best Practices

* **FR-SEC-001:** HTTPS for frontend-backend communication (via reverse proxy).
* **FR-SEC-002:** Protection against common web vulnerabilities (FastAPI aids this).
* **FR-SEC-003:** Secure password hashing (bcrypt).
* **FR-SEC-004:** Secure session management (HTTP-only cookies). Rate limiting on admin login.
* **FR-SEC-005:** Distinct admin authentication.
* **FR-SEC-006:** Configurable DB credentials (via `.env`).
* **FR-SEC-007:** Configurable Ollama server details (via `.env`).

## 5. Non-Functional Requirements

### 5.1 Performance

* **NFR-PERF-001:** API response times for common operations < 2 seconds.
* **NFR-PERF-002:** Search results < 3 seconds for typical queries.
* **NFR-PERF-003:** Workflow system overhead < 500ms (excluding LLM processing).
* **NFR-PERF-004:** Markdown editor responsive for documents up to ~50,000 characters.
* **NFR-PERF-005:** Efficient version loading.

### 5.2 Scalability

* **NFR-SCALE-001:** Support typical concurrent usage from multiple teams.
* **NFR-SCALE-002:** Backend API (FastAPI) is async, suitable for handling concurrent requests.
* **NFR-SCALE-003:** Database schema optimized for growth (e.g., indexing on foreign keys, FTS support).
* **NFR-SCALE-004:** Graceful handling of large Markdown documents by backend.

### 5.3 Availability and Reliability

* **NFR-AVAIL-001:** Robust error handling and container restart capability.
* **NFR-AVAIL-002:** Graceful handling of transient errors (Ollama/DB unavailability) with user feedback.
* **NFR-AVAIL-003:** PostgreSQL data persistence configured in `docker-compose.yml`. Backup procedures are user responsibility.
* **NFR-AVAIL-004:** Comprehensive logging (via `logging_config.py`) for troubleshooting.

### 5.4 Security

* **NFR-SEC-001:** Principle of least privilege for DB access.
* **NFR-SEC-002:** Dependencies from trusted sources, aim for up-to-date versions.
* **NFR-SEC-003:** No hardcoded sensitive configurations; use environment variables (`.env` files).
* **NFR-SEC-004:** Admin interface protected (rate limiting on login).

### 5.5 Usability and User Experience (UX)

* **NFR-UX-001:** Intuitive and easy-to-learn UI.
* **NFR-UX-002:** Clear and consistent navigation.
* **NFR-UX-003:** Clear visual feedback (loading states, success/error messages via toasts).
* **NFR-UX-004:** Modern and usable Markdown editor experience.
* **NFR-UX-005:** Responsive on common desktop resolutions.
* **NFR-UX-006:** Streamlined workflows for content creation, versioning, and AI execution.

### 5.6 Maintainability

* **NFR-MAIN-001:** Well-organized, commented code following consistent standards (Python/FastAPI backend, React/TypeScript frontend).
* **NFR-MAIN-002:** Modular backend API (CRUD layer, services, API endpoints).
* **NFR-MAIN-003:** Database schema documented in `init_db.sql` and models.
* **NFR-MAIN-004:** Externalized configuration.

### 5.7 Deployability

* **NFR-DEP-001:** Deployable via `docker-compose up`.
* **NFR-DEP-002:** `docker-compose.yml` includes PostgreSQL with persistent storage.
* **NFR-DEP-003:** `docker-compose.yml` can include Ollama service or allow connection to external Ollama.
* **NFR-DEP-004:** Clear instructions for building, configuring, and running (as in README).
* **NFR-DEP-005:** Minimal manual configuration post-deployment.

## 6. Data Management

### 6.1 Data Model

**Teams (`teams` table):**

* `team_id` (UUID, PK)
* `team_name` (String, Unique)
* `username` (String, Unique)
* `hashed_password` (String)
* `is_active` (Boolean)
* `created_at`, `updated_at` (Timestamps)
* Includes a special ADMIN_SYSTEM_TEAM_ID ('04a9a4ec-18d8-4cfd-bead-d0ef99199e17') record for owning Templates/Workflows.

**ContentItems (`content_items` table):**

* `item_id` (UUID, PK)
* `team_id` (UUID, FK to Teams, ON DELETE CASCADE): Owning team or ADMIN_SYSTEM_TEAM_ID.
* `item_type` (Enum: 'DOCUMENT', 'TEMPLATE', 'WORKFLOW')
* `name` (String)
* `is_globally_visible` (Boolean)
* `current_version_id` (UUID, FK to ContentVersions, ON DELETE SET NULL): Points to the current `version_id`.
* `created_at`, `updated_at` (Timestamps)
* Unique constraint on (`team_id`, `name`, `item_type`).

**ContentVersions (`content_versions` table):**

* `version_id` (UUID, PK)
* `item_id` (UUID, FK to ContentItems, ON DELETE CASCADE)
* `markdown_content` (Text)
* `version_number` (Integer)
* `saved_by_team_id` (UUID, FK to Teams, ON DELETE SET NULL): Team that saved this version (user team or ADMIN_SYSTEM_TEAM_ID).
* `created_at` (Timestamp)
* `content_tsv` (TSVECTOR): For full-text search, populated by DB trigger.
* `content_vector` (VECTOR): Embedding of the full content for semantic search.
* `vector` (VECTOR): Reserved for future embedding experimentation.
* Unique constraint on (`item_id`, `version_number`).

**DocumentChunks (`document_chunks` table):**

* `chunk_id` (UUID, PK)
* `version_id` (UUID, FK to ContentVersions, ON DELETE CASCADE)
* `chunk_index` (Integer)
* `chunk_text` (Text)
* `embedding` (VECTOR): Embedding vector for the chunk text used in retrieval.

The PostgreSQL service MUST enable the `pgvector` extension so these vector
columns can store and compare embeddings.

### 6.2 Data Retention and Deletion

Deleting a team results in the hard deletion of the Team record and, due to `ON DELETE CASCADE` on `content_items.team_id`, all ContentItem records (Documents, Templates, Workflows) directly owned by that team. This further cascades to delete their associated ContentVersion records (as `content_versions.item_id` also has `ON DELETE CASCADE`).

If a team is deleted, ContentVersion records where `saved_by_team_id` pointed to the deleted team will have this foreign key set to NULL, due to `ON DELETE SET NULL`.

Deleting an individual ContentItem (Document, Template, or Workflow) results in a hard delete of the item and all its associated ContentVersion records due to the `ON DELETE CASCADE` on `content_versions.item_id`.

### 6.3 Setup Considerations

* When deploying with Docker Compose, the PostgreSQL container executes
  `init_db.sql` on first run. This script enables the `vector` (pgvector)
  extension required for embedding-based retrieval. If you run against an
  external database, ensure this extension is installed.

## 7. Future Considerations (Post-Initial Release Optional)

* Advanced Search Capabilities (e.g., semantic search if local Ollama embedding generation becomes efficient).
* Enhanced Admin Dashboard (system analytics, detailed logging).
* Workflow Scheduling.
* Inter-Document Linking.
* UI Themes (Light/Dark mode).

## 8. Conclusion

The Team Intelligence Platform (TIP) aims to provide a robust, team-centric platform for AI-assisted document and workflow management. By focusing on AI Co-Management principles, simplicity, and leveraging local LLM capabilities via Ollama, TIP will empower teams to enhance their productivity and collective knowledge management practices. The Docker-based deployment ensures ease of setup and operation.
