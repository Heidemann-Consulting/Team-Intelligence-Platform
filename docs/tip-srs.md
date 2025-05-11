# Software Requirements Specification: Team Intelligence Platform (TIP)

**Version:** 1.0
**Date:** May 11, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0
**Based on PRD:** Team Intelligence Platform PRD v1.0, dated 2025-05-11

## Table of Contents

- [Software Requirements Specification: Team Intelligence Platform (TIP)](#software-requirements-specification-team-intelligence-platform-tip)
  - [Table of Contents](#table-of-contents)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Document Conventions](#12-document-conventions)
    - [1.3 Intended Audience](#13-intended-audience)
    - [1.4 Product Scope](#14-product-scope)
    - [1.5 Definitions, Acronyms, and Abbreviations](#15-definitions-acronyms-and-abbreviations)
    - [1.6 References](#16-references)
    - [1.7 Overview](#17-overview)
  - [2. Overall Description](#2-overall-description)
    - [2.1 Product Perspective](#21-product-perspective)
    - [2.2 Product Functions](#22-product-functions)
    - [2.3 User Characteristics](#23-user-characteristics)
    - [2.4 Constraints](#24-constraints)
    - [2.5 Assumptions and Dependencies](#25-assumptions-and-dependencies)
  - [3. System Features (Functional Requirements)](#3-system-features-functional-requirements)
    - [3.1 General System Requirements](#31-general-system-requirements)
    - [3.2 Admin Account \& Interface](#32-admin-account--interface)
    - [3.3 Team User Authentication](#33-team-user-authentication)
    - [3.4 Content Management](#34-content-management)
      - [3.4.1 General Content Operations](#341-general-content-operations)
      - [3.4.2 Markdown Editor](#342-markdown-editor)
    - [3.5 Versioning](#35-versioning)
    - [3.6 Search](#36-search)
    - [3.7 Process Workflow Definition and Execution](#37-process-workflow-definition-and-execution)
      - [3.7.1 Workflow Definition (Admin-created)](#371-workflow-definition-admin-created)
      - [3.7.2 Workflow Execution (Team-initiated)](#372-workflow-execution-team-initiated)
    - [3.8 Sharing and Visibility](#38-sharing-and-visibility)
    - [3.9 Duplication](#39-duplication)
    - [3.10 AI Co-Management Support](#310-ai-co-management-support)
    - [3.11 Basic Security Best Practices](#311-basic-security-best-practices)
  - [4. External Interface Requirements](#4-external-interface-requirements)
    - [4.1 User Interfaces](#41-user-interfaces)
    - [4.2 Software Interfaces](#42-software-interfaces)
      - [4.2.1 PostgreSQL Database Interface](#421-postgresql-database-interface)
      - [4.2.2 Ollama Server Interface](#422-ollama-server-interface)
    - [4.3 Hardware Interfaces](#43-hardware-interfaces)
    - [4.4 Communications Interfaces](#44-communications-interfaces)
  - [5. Non-Functional Requirements](#5-non-functional-requirements)
    - [5.1 Performance Requirements](#51-performance-requirements)
    - [5.2 Security Requirements](#52-security-requirements)
    - [5.3 Usability Requirements](#53-usability-requirements)
    - [5.4 Reliability Requirements](#54-reliability-requirements)
    - [5.5 Maintainability Requirements](#55-maintainability-requirements)
    - [5.6 Deployability Requirements](#56-deployability-requirements)
    - [5.7 Scalability Requirements](#57-scalability-requirements)
  - [6. System Architecture](#6-system-architecture)
    - [6.1 Architectural Style](#61-architectural-style)
    - [6.2 High-Level Component Diagram](#62-high-level-component-diagram)
    - [6.3 Component Descriptions](#63-component-descriptions)
      - [6.3.1 Frontend SPA (React)](#631-frontend-spa-react)
      - [6.3.2 Backend API Service (Python/FastAPI)](#632-backend-api-service-pythonfastapi)
      - [6.3.3 PostgreSQL Database](#633-postgresql-database)
      - [6.3.4 Ollama Server (External/Co-deployed)](#634-ollama-server-externalco-deployed)
    - [6.4 Deployment View](#64-deployment-view)
  - [7. Data Design](#7-data-design)
    - [7.1 Data Storage](#71-data-storage)
    - [7.2 Conceptual Data Model (ERD)](#72-conceptual-data-model-erd)
    - [7.3 Detailed Data Dictionary](#73-detailed-data-dictionary)
      - [7.3.1 `teams` Table](#731-teams-table)
      - [7.3.2 `content_items` Table](#732-content_items-table)
      - [7.3.3 `content_versions` Table](#733-content_versions-table)
  - [8. API Design (RESTful)](#8-api-design-restful)
    - [8.1 API Design Principles \& Conventions](#81-api-design-principles--conventions)
    - [8.2 Authentication API](#82-authentication-api)
      - [8.2.1 Admin Login](#821-admin-login)
      - [8.2.2 Team User Login](#822-team-user-login)
      - [8.2.3 Logout](#823-logout)
      - [8.2.4 Get Current Authenticated User](#824-get-current-authenticated-user)
    - [8.3 Admin API (Team Management)](#83-admin-api-team-management)
      - [8.3.1 Create Team](#831-create-team)
      - [8.3.2 List Teams](#832-list-teams)
      - [8.3.3 Get Team Details](#833-get-team-details)
      - [8.3.4 Update Team](#834-update-team)
      - [8.3.5 Deactivate Team](#835-deactivate-team)
      - [8.3.6 Reactivate Team](#836-reactivate-team)
      - [8.3.7 Delete Team](#837-delete-team)
    - [8.4 Content Item APIs](#84-content-item-apis)
      - [8.4.1 List Content Items](#841-list-content-items)
      - [8.4.2 Create Content Item](#842-create-content-item)
      - [8.4.3 Get Content Item Details](#843-get-content-item-details)
      - [8.4.4 Update Content Item Metadata](#844-update-content-item-metadata)
      - [8.4.5 Delete Content Item](#845-delete-content-item)
      - [8.4.6 Duplicate Content Item](#846-duplicate-content-item)
    - [8.5 Content Version APIs](#85-content-version-apis)
      - [8.5.1 Save New Version](#851-save-new-version)
      - [8.5.2 List Item Versions (History)](#852-list-item-versions-history)
      - [8.5.3 Get Specific Version Content](#853-get-specific-version-content)
    - [8.6 Search API](#86-search-api)
      - [8.6.1 Search Content Items](#861-search-content-items)
    - [8.7 Workflow Execution API](#87-workflow-execution-api)
      - [8.7.1 Run Workflow](#871-run-workflow)
  - [9. Frontend Design](#9-frontend-design)
    - [9.1 Frontend Technology Choices](#91-frontend-technology-choices)
    - [9.2 Key UI Components and Views](#92-key-ui-components-and-views)
      - [9.2.1 Core Layout Components](#921-core-layout-components)
      - [9.2.2 Authentication Views](#922-authentication-views)
      - [9.2.3 Admin Interface Views](#923-admin-interface-views)
      - [9.2.4 Team User Interface Views](#924-team-user-interface-views)
      - [9.2.5 Reusable UI Components](#925-reusable-ui-components)
    - [9.3 State Management](#93-state-management)
    - [9.4 Routing](#94-routing)
  - [10. File Tree Structure](#10-file-tree-structure)
    - [10.1 Backend File Structure (FastAPI/Python)](#101-backend-file-structure-fastapipython)
    - [10.2 Frontend File Structure (React/Vite/TypeScript)](#102-frontend-file-structure-reactvitetypescript)
    - [10.3 Docker Configuration Files](#103-docker-configuration-files)
  - [11. Detailed Module Designs](#11-detailed-module-designs)
    - [11.1 Backend Modules (FastAPI/Python)](#111-backend-modules-fastapipython)
      - [11.1.1 Authentication \& Authorization Module](#1111-authentication--authorization-module)
      - [11.1.2 Team Management Module](#1112-team-management-module)
      - [11.1.3 Content Item Management Module](#1113-content-item-management-module)
      - [11.1.4 Versioning Module](#1114-versioning-module)
      - [11.1.5 Workflow Engine Module](#1115-workflow-engine-module)
      - [11.1.6 Search Module](#1116-search-module)
    - [11.2 Frontend Modules (React/TypeScript)](#112-frontend-modules-reacttypescript)
      - [11.2.1 Authentication Service \& Context](#1121-authentication-service--context)
      - [11.2.2 Content Service](#1122-content-service)
      - [11.2.3 Workflow Service](#1123-workflow-service)
      - [11.2.4 Markdown Editor Component](#1124-markdown-editor-component)
      - [11.2.5 Editor View Page/Component](#1125-editor-view-pagecomponent)

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) document defines the detailed requirements for the Team Intelligence Platform (TIP). TIP is a self-contained web application designed to transform how product development teams integrate AI into their collaborative workflows. It enables "AI Co-Management," a paradigm where AI becomes an integrated team member contributing to collective intelligence.
This SRS aims to provide a comprehensive and unambiguous specification for the system, serving as the foundation for design, development, testing, and validation activities. It elaborates on the features and constraints outlined in the Team Intelligence Platform Product Requirements Document (PRD) v1.0.

### 1.2 Document Conventions
* **FR-XXX-YYY**: Functional Requirement identifier, traceable to the PRD.
* **NFR-XXX-YYY**: Non-Functional Requirement identifier, traceable to the PRD.
* **SHALL**: Indicates a mandatory requirement.
* **SHOULD**: Indicates a recommended feature or function that is desirable but not mandatory.
* **MAY**: Indicates an optional feature or function.
* All terms specific to the TIP domain are as defined in the PRD v1.0 (Section 1.4 Glossary) or in Section 1.5 of this SRS.

### 1.3 Intended Audience
This SRS is intended for:
* **Development Team**: To understand the system's requirements for design and implementation.
* **QA/Testing Team**: To develop test plans and test cases.
* **Project Managers**: To manage the scope and progress of the project.
* **Stakeholders**: To understand the capabilities and constraints of the proposed system.

### 1.4 Product Scope
The scope of the Team Intelligence Platform (TIP) is as defined in the TIP PRD v1.0, Section 1.2 "Scope." In summary, the product is a self-contained, Dockerized web application enabling teams to manage Markdown-based documents, admin-created templates, and admin-created AI-driven workflows using a local Ollama server and PostgreSQL database. Key functionalities include team-based access, content versioning, Markdown editing (EasyMDE), workflow execution, and search.
Items explicitly out of scope are detailed in the PRD v1.0, Section 1.2 "Out of Scope."

### 1.5 Definitions, Acronyms, and Abbreviations

| Term/Acronym                       | Definition                                                                                                                                                               |
| :--------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AI Co-Management** | A paradigm where AI becomes an integrated team member contributing to collective intelligence, rather than just an individual productivity tool.                             |
| **Administrator** | A user with privileges to manage team user accounts and system-level Templates and Process Workflows via a dedicated admin interface.                                              |
| **Admin System** | A special system-level identifier (`ADMIN_SYSTEM_TEAM_ID`) used as the owner for all Templates and Workflows created by Administrators.                                        |
| **API** | Application Programming Interface                                                                                                                                        |
| **Backend API** | The server-side application (FastAPI) providing APIs for the frontend, managing business logic, and interacting with the database and Ollama.                             |
| **CRUD** | Create, Read, Update, Delete                                                                                                                                             |
| **CSRF** | Cross-Site Request Forgery                                                                                                                                               |
| **DB** | Database                                                                                                                                                                 |
| **Document** | A Markdown-based content artifact created by a team, often based on a template or generated by a Process Workflow. Documents have versions and are owned by teams.        |
| **Document Template** | A Markdown-based blueprint used as a starting point for creating new Documents. Templates are created and managed by Administrators and can be made globally visible.      |
| **EasyMDE** | The specific in-app web-based Markdown editor used in TIP.                                                                                                               |
| **FR** | Functional Requirement                                                                                                                                                   |
| **Frontend** | The web-based Single-Page Application (React) providing the user interface.                                                                                             |
| **FTS** | Full-Text Search.                                                                                                                                                        |
| **Global Visibility** | A flag that allows admin-created Templates/Workflows or team-created Documents to be visible (read-only or for use) by other teams.                                       |
| **GUI** | Graphical User Interface                                                                                                                                                 |
| **HTTP(S)** | HyperText Transfer Protocol (Secure)                                                                                                                                     |
| **JSON** | JavaScript Object Notation                                                                                                                                               |
| **LLM** | Large Language Model                                                                                                                                                     |
| **Markdown Editor** | The in-app web-based editor (EasyMDE) used for creating and modifying the content of Documents, Templates, and Process Workflows.                                          |
| **NFR** | Non-Functional Requirement                                                                                                                                               |
| **Ollama Server** | A locally hosted server running Large Language Models, used by TIP for AI-assisted tasks. Configuration includes a default model and temperature.                           |
| **OS** | Operating System                                                                                                                                                         |
| **PostgreSQL Database** | The relational database used for storing all TIP data, including documents, templates, workflows, versions, team information, and full-text search capabilities.        |
| **PRD** | Product Requirements Document                                                                                                                                            |
| **Process Workflow** | A definition (in a specific YAML-like Markdown format) for automated processes, including LLM prompts and input/output specifications. Managed by Admins.                   |
| **Rituals and Practices** | Core team activities and patterns supported by TIP to foster AI Co-Management (e.g., Collective Context Management, AI-Assisted Documentation).                             |
| **SPA** | Single-Page Application                                                                                                                                                  |
| **SQL** | Structured Query Language                                                                                                                                                |
| **SRS** | Software Requirements Specification                                                                                                                                      |
| **Team User** | A shared account used by multiple members of a team to access TIP.                                                                                                       |
| **TIP (Team Intelligence Platform)** | The complete application, comprising the frontend, backend API, and database, designed to facilitate AI Co-Management.                                                    |
| **UI** | User Interface                                                                                                                                                           |
| **UX** | User Experience                                                                                                                                                          |
| **Versioning** | The system's capability to store and manage multiple iterations of Documents, Templates, and Process Workflows. A new version is created upon saving.                      |
| **XSS** | Cross-Site Scripting                                                                                                                                                     |
| **YAML** | YAML Ain't Markup Language (a human-readable data serialization standard)                                                                                                  |

### 1.6 References
1.  Team Intelligence Platform Product Requirements Document (TIP PRD) v1.0 - Dated 2025-05-11.
2.  IEEE Std 830-1998: IEEE Recommended Practice for Software Requirements Specifications (used as a guiding structure for this SRS).

### 1.7 Overview
This SRS is organized into several sections.
* **Section 1 (Introduction)**: Provides an overview of the SRS, its purpose, scope, definitions, and references.
* **Section 2 (Overall Description)**: Describes the general factors affecting the product and its requirements, including product perspective, functions, user characteristics, constraints, assumptions, and dependencies.
* **Section 3 (System Features)**: Details the functional requirements of the system.
* **Section 4 (External Interface Requirements)**: Defines the interfaces with users, hardware, other software, and communications.
* **Section 5 (Non-Functional Requirements)**: Specifies quality attributes such as performance, security, usability, and maintainability.
* **Section 6 (System Architecture)**: Describes the high-level architecture of TIP.
* **Section 7 (Data Design)**: Details the database schema and data management aspects.
* **Section 8 (API Design)**: Outlines the RESTful API provided by the backend.
* **Section 9 (Frontend Design)**: Describes conceptual aspects of the frontend application.
* **Section 10 (File Tree Structure)**: Provides a conceptual overview of the project's file organization.
* **Section 11 (Detailed Module Designs)**: Offers a closer look at key backend and frontend modules.

## 2. Overall Description

### 2.1 Product Perspective
The Team Intelligence Platform (TIP) v1.0 is a new, self-contained product. It is designed to operate independently, with its primary external dependencies being a local Ollama server for LLM processing and a PostgreSQL database for data persistence. The system will be deployed using Docker and docker-compose, simplifying its setup and management. It does not replace any existing systems but aims to provide a novel solution for teams wishing to implement AI Co-Management practices.

The system comprises three main components:
1.  **Frontend SPA (React)**: The primary interface for team users and administrators.
2.  **Backend API Service (Python/FastAPI)**: The core logic and orchestration layer.
3.  **PostgreSQL Database**: The persistent storage for all application data.

TIP will interact with a local Ollama instance, sending prompts and receiving generated text, but it will not manage the Ollama server itself (beyond optionally including it in the docker-compose setup for convenience).

### 2.2 Product Functions
TIP provides the following key functions, derived from the PRD v1.0:
1.  **Team Account Management**: Administrators can create and manage shared team accounts.
2.  **User Authentication**: Team users log in with shared credentials; Administrators use a dedicated password.
3.  **Content Creation and Management**:
    * Teams create and manage Documents.
    * Administrators create and manage Document Templates and Process Workflows.
4.  **Markdown Editing**: An in-app EasyMDE editor supports Markdown content creation for all item types.
5.  **Versioning**: All Documents, Templates, and Process Workflows have a linear version history. Saving creates a new version.
6.  **Process Workflow Definition**: Administrators define workflows in a YAML-like format within the Markdown editor, specifying inputs, LLM prompts, and output parameters.
7.  **Process Workflow Execution**: Team users can manually run globally visible, Admin-created workflows, which interact with a local Ollama server to process input documents and generate new output documents.
8.  **Search Functionality**: Users can search for accessible content items by name, creation date, and full-text content.
9.  **Content Sharing & Visibility**:
    * Team-owned Documents can be marked globally visible (read-only) by the owning team.
    * Admin-created Templates and Workflows can be marked globally visible by an Administrator for team use.
10. **Content Duplication**: Users can duplicate accessible content items.
11. **AI Co-Management Support**: The system facilitates practices like Collective Context Management, AI-Assisted Documentation, and Context-Aware Planning.
12. **Deployment**: The entire system is Dockerized and deployable via docker-compose.

### 2.3 User Characteristics
Two primary types of users are anticipated:

1.  **Team User**:
    * **Description**: A member of a product development team who uses TIP to integrate AI into their collaborative workflows.
    * **Technical Proficiency**: Assumed to be comfortable with standard web applications and basic Markdown syntax. May not have deep technical expertise in LLMs or databases.
    * **Domain Knowledge**: Familiar with their team's operational processes and the types of documents they work with. Will be trained on or familiar with AI Co-Management practices.
    * **Goals**: To efficiently manage their documents, automate repetitive tasks using AI, collaborate with their team, and leverage AI as a team member.
    * **Interaction**: Primarily through the web-based SPA frontend.

2.  **Administrator**:
    * **Description**: A privileged user responsible for managing team accounts and system-level content (Templates and Workflows).
    * **Technical Proficiency**: Assumed to have basic system administration skills, sufficient to manage docker-compose environments and configure system parameters.
    * **Domain Knowledge**: Understands the purpose of TIP and the need for team account and system content management.
    * **Goals**: To manage team access to TIP, provide standardized Templates and Workflows, and ensure system integrity.
    * **Interaction**: Primarily through a dedicated web-based admin interface.

### 2.4 Constraints
The system development and operation are subject to the following constraints, as outlined in the TIP PRD v1.0:
* **C-SYS-001 (Self-Contained)**: TIP SHALL be a self-contained application (SPA frontend, backend API). (PRD 1.2)
* **C-SYS-002 (Dockerization)**: All components (frontend, backend, PostgreSQL) SHALL be dockerized and deployable via `docker-compose.yml`. (PRD 1.2)
* **C-SYS-003 (English Only)**: UI and system messages SHALL be in English only. (PRD 1.2)
* **C-DATA-001 (PostgreSQL Storage)**: All application data SHALL be stored in a local PostgreSQL database. No external file system storage (Git, Obsidian) is permitted. (PRD 1.2)
* **C-LLM-001 (Local Ollama Only)**: Interaction SHALL be solely with a locally configured Ollama server. No other LLM tools, agents, or services. (PRD 1.2)
* **C-EDIT-001 (Markdown Editor)**: All content editing (Documents, Templates, Workflows) SHALL use the in-app EasyMDE Markdown editor. (PRD 1.2)
* **C-VER-001 (Linear Versioning)**: Versioning for Documents, Templates, and Workflows SHALL be linear; saving creates a new version. (PRD 1.2)
* **C-SEC-001 (Basic Security)**: Basic security best practices SHALL be implemented. (PRD 1.2)
* **C-DEP-001 (No CI/CD)**: Continuous Integration / Continuous Deployment (CI/CD) pipelines are out of scope for v1.0. (PRD 1.2)
* **C-USER-001 (Team Accounts)**: Only team-based accounts and a single system administrator are supported; no individual user accounts. (PRD 1.2)

### 2.5 Assumptions and Dependencies
* **A-OLLAMA-001 (Ollama Availability)**: A functional Ollama server instance is assumed to be available and accessible from the TIP backend service. Its configuration (URL, default model, default temperature) will be provided to the TIP backend.
* **A-DB-001 (PostgreSQL Availability)**: A PostgreSQL server instance is assumed to be available. The docker-compose setup will typically provide this.
* **A-NET-001 (Network Connectivity)**: Reliable network connectivity is assumed between the user's browser and the TIP frontend, between the frontend and backend API, and between the backend API and the PostgreSQL database and Ollama server.
* **A-BROWSER-001 (Modern Browsers)**: Users are assumed to use modern web browsers (e.g., latest versions of Chrome, Firefox, Edge, Safari) that support the chosen frontend technology stack (React).
* **A-HW-001 (Hardware Resources)**: The server hosting the Dockerized TIP service is assumed to have sufficient resources (CPU, RAM, disk) for TIP, PostgreSQL, and potentially Ollama.
* **D-OLLAMA-001 (Ollama API Stability)**: TIP depends on the stability and consistency of the API provided by the local Ollama server.
* **D-FE-001 (Frontend Framework)**: The choice of frontend framework (React) and its associated libraries (e.g., EasyMDE) influences development.
* **D-BE-001 (Backend Framework)**: The choice of backend framework (FastAPI) influences development.

## 3. System Features (Functional Requirements)

This section details the functional requirements of the Team Intelligence Platform (TIP). Each requirement is uniquely identified and traces back to the TIP PRD v1.0 where applicable.

### 3.1 General System Requirements
* **FR-SYS-001**: The system SHALL be a self-contained web application consisting of a Single-Page Application (SPA) frontend (React) and a backend API service (Python/FastAPI).
    * *Verification*: Architectural review, deployment test.
    * *Source*: PRD 1.2, 3.1, 4.1.
* **FR-SYS-002**: All parts of the system (frontend, backend, PostgreSQL database) SHALL be dockerized and deployable via a single `docker-compose up` command. The Ollama server MAY optionally be part of this Docker Compose setup.
    * *Verification*: Deployment test using `docker-compose`.
    * *Source*: PRD 1.2, 3.1, 5.7.
* **FR-SYS-003**: The system UI and all system-generated messages SHALL be in English only.
    * *Verification*: UI review, code inspection.
    * *Source*: PRD 1.2, 4.1.
* **FR-SYS-004**: The system SHALL use a local PostgreSQL database for all data storage. No data shall be stored in Git, Obsidian, or other external file systems beyond PostgreSQL.
    * *Verification*: Data storage inspection, architectural review.
    * *Source*: PRD 1.2, 3.1, 4.1, 6.1.
* **FR-SYS-005**: The system SHALL only interact with a locally configured Ollama server for LLM requests, using a globally configured model and temperature setting in the backend.
    * *Verification*: Code inspection, network traffic analysis during workflow execution.
    * *Source*: PRD 1.2, 3.1, 4.1, 4.7.1.

### 3.2 Admin Account & Interface
* **FR-ADM-001**: The system SHALL provide a dedicated admin web interface, separate from the team user interface.
    * *Description*: A distinct set of web pages accessible via a specific URL (e.g., `/admin`) for managing team accounts, Document Templates, and Process Workflows.
    * *Verification*: UI inspection, access control test.
    * *Source*: PRD 1.2, 2.2, 4.2.
* **FR-ADM-002**: Access to the admin interface SHALL be protected by a single, configurable administrator password. This password SHALL be configurable via environment variables.
    * *Description*: The admin interface will have its own login mechanism. The admin password will not be stored in the database as a user record but checked against a configured value. Rate limiting SHALL be applied to the admin login endpoint.
    * *Verification*: Security test, configuration inspection.
    * *Source*: PRD 1.2, 4.2, 4.11.
* **FR-ADM-003**: The Administrator SHALL be able to create new team user accounts. This includes specifying:
    * Team Name (string, e.g., "Marketing Team Alpha", max 100 characters, required)
    * Team Username (string, e.g., "marketing_alpha_user", max 50 characters, unique across all teams, alphanumeric and underscores, required)
    * Team Password (string, min 8 characters, required)
    * *Description*: The admin interface will provide a form for these inputs. The backend will validate the inputs and create a new team record in the database.
    * *Verification*: Functional test of team creation, input validation test.
    * *Source*: PRD 2.2, 4.2.
* **FR-ADM-004**: The Administrator SHALL be able to view a list of all existing team user accounts (excluding the `ADMIN_SYSTEM_TEAM_ID`), displaying their Team Name, Team Username, and active status.
    * *Description*: The admin interface will display a table or list of all teams.
    * *Verification*: Functional test of team listing.
    * *Source*: PRD 2.2, 4.2.
* **FR-ADM-005**: The Administrator SHALL be able to modify existing team user accounts, including changing the Team Name, resetting the Team Password, and changing the active status. The Team Username SHALL NOT be updatable.
    * *Description*: The admin interface will allow selection of a team and provide forms to update its details.
    * *Verification*: Functional test of team modification.
    * *Source*: PRD 2.2, 4.2.
* **FR-ADM-006**: The Administrator SHALL be able to deactivate a team user account, preventing login for that team.
    * *Description*: A deactivated team cannot log in. Their data remains in the system.
    * *Verification*: Functional test of deactivation and login attempt with a deactivated account.
    * *Source*: PRD 2.2, 4.2.
* **FR-ADM-007**: The Administrator SHALL be able to reactivate a previously deactivated team user account.
    * *Description*: Allows a previously deactivated team to log in again.
    * *Verification*: Functional test of reactivation and successful login.
    * *Source*: PRD 2.2, 4.2.
* **FR-ADM-008**: The Administrator SHALL be able to delete a team user account. Deleting a team account SHALL result in the hard deletion of the team and all its exclusively owned content items (Documents) and their versions. A confirmation prompt MUST be displayed before deletion.
    * *Description*: This is a permanent action. ContentVersions saved by the deleted team will have `saved_by_team_id` set to NULL if the DB schema supports it.
    * *Verification*: Functional test of team deletion, data verification in DB, confirmation prompt check.
    * *Source*: PRD 2.2, 4.2, 6.2.
* **FR-ADM-009**: The Administrator SHALL be able to create, view, edit (name and content), delete, and manage global visibility for Document Templates. These Templates are owned by the `ADMIN_SYSTEM_TEAM_ID`.
    * *Verification*: Functional test of template management by admin.
    * *Source*: PRD 2.2, 3.2, 4.2.
* **FR-ADM-010**: The Administrator SHALL be able to create, view, edit (name and content), delete, and manage global visibility for Process Workflows. These Workflows are owned by the `ADMIN_SYSTEM_TEAM_ID`.
    * *Verification*: Functional test of workflow management by admin.
    * *Source*: PRD 2.2, 3.2, 4.2.
* **FR-ADM-011**: The Administrator SHALL be able to view all Documents created by any team.
    * *Verification*: Functional test of admin viewing documents from various teams.
    * *Source*: PRD 2.2.
* **FR-ADM-012**: The Administrator SHALL be able to edit metadata (name, global visibility) of any Document.
    * *Verification*: Functional test of admin editing document metadata.
    * *Source*: PRD 2.2.
* **FR-ADM-013**: The Administrator SHALL be able to delete any Document created by any team. A confirmation prompt MUST be displayed before deletion.
    * *Verification*: Functional test of admin deleting documents from various teams.
    * *Source*: PRD 2.2.

### 3.3 Team User Authentication
* **FR-AUTH-001**: Team users SHALL log in to the system using their shared team username and password via a login page on the main SPA.
    * *Verification*: Functional test of login.
    * *Source*: PRD 2.1, 4.3.
* **FR-AUTH-002**: The system SHALL securely store team user passwords using strong hashing algorithms (e.g., bcrypt).
    * *Verification*: Code review of password handling, database inspection of stored password format.
    * *Source*: PRD 1.2, 4.3, 4.11.
* **FR-AUTH-003**: Upon successful login, the system SHALL establish a session for the team user. This session SHALL be managed using secure mechanisms (e.g., HTTP-only, secure cookies containing a session token).
    * *Verification*: Security test of session management, inspection of cookie attributes.
    * *Source*: PRD 1.2, 4.3, 4.11.
* **FR-AUTH-004**: Multiple members of the same team SHALL be able to log in and use the system concurrently with the same team username and password.
    * *Verification*: Concurrent login and usage test by multiple clients using the same team credentials.
    * *Source*: PRD 2.1, 4.3.
* **FR-AUTH-005**: The system SHALL provide a logout mechanism for team users, which invalidates their current session.
    * *Verification*: Functional test of logout and subsequent access attempt.
    * *Source*: PRD 4.3.

### 3.4 Content Management

#### 3.4.1 General Content Operations
* **FR-CM-001 (Teams - Documents)**: Team users SHALL be able to create new Documents by selecting an available (admin-created, globally visible) Document Template.
    * *Verification*: Functional test of document creation from a template.
    * *Source*: PRD 2.1, 4.4.1.
* **FR-CM-002 (Admins - Templates/Workflows)**: Administrators SHALL be able to create new Document Templates and Process Workflows. These items are owned by `ADMIN_SYSTEM_TEAM_ID`.
    * *Verification*: Functional test of admin creating templates and workflows.
    * *Source*: PRD 2.2, 4.4.1.
* **FR-CM-003 (Document from Template Content)**: New Documents SHALL start with content copied from the selected Document Template's current version.
    * *Verification*: Content verification of new document against template.
    * *Source*: PRD 4.4.1.
* **FR-CM-004 (Template/Workflow Initial Content)**: New Document Templates and Process Workflows created by an Administrator SHALL be initialized with default instructional content provided by the frontend.
    * *Description*: The frontend will populate the editor with placeholder/guidance text when an admin creates a new template or workflow.
    * *Verification*: Functional test of admin creating new template/workflow, check initial content.
    * *Source*: PRD 4.4.1.
* **FR-CM-005 (Listing Items)**: Users (Teams/Admins) SHALL be able to view a list of items relevant to their role and the item type:
    * Team Users: View Documents owned by their team, and globally visible Documents, Templates, and Workflows.
    * Administrators: View all Documents, all Templates, and all Process Workflows.
    * *Description*: Lists should display item name, type, and last modification date.
    * *Verification*: Functional test of listing for both roles, visibility checks.
    * *Source*: PRD 2.1, 2.2, 4.4.1.
* **FR-CM-006 (Viewing Content)**: Users SHALL be able to open and view the content of accessible items. The content will be displayed in the Markdown editor (potentially in a read-only mode if not editable by the user).
    * *Verification*: Functional test of viewing content for each item type and role.
    * *Source*: PRD 2.1, 2.2, 4.4.1.
* **FR-CM-007 (Editing Content)**:
    * Team Users SHALL be able to edit Documents they own.
    * Administrators SHALL be able to edit Document Templates and Process Workflows they manage (owned by `ADMIN_SYSTEM_TEAM_ID`).
    * Administrators SHALL NOT directly edit the content of Documents owned by teams (content edits are versioned and tied to a saver; admins can edit metadata).
    * *Verification*: Functional test of editing permissions for different roles and item types.
    * *Source*: PRD 2.1, 2.2, 4.4.1.
* **FR-CM-008 (Deleting Items)**:
    * Team Users SHALL be able to delete Documents they own.
    * Administrators SHALL be able to delete Document Templates, Process Workflows, and any Document.
    * A confirmation prompt MUST be displayed before deletion. Deletion removes the item and its version history.
    * *Verification*: Functional test of deletion, confirmation prompt check, data verification in DB.
    * *Source*: PRD 2.1, 2.2, 4.4.1.
* **FR-CM-009 (Name Uniqueness)**: Item names (for Documents, Templates, Workflows) MUST be unique per `team_id` (owner) and `item_type`. Case-insensitive checks SHOULD be performed.
    * *Example*: A team cannot have two Documents named "Q1 Report". An Admin cannot have two Templates named "Standard PRD".
    * *Verification*: Functional test of creation/renaming with unique and duplicate names.
    * *Source*: PRD 4.4.1.

#### 3.4.2 Markdown Editor
* **FR-EDIT-001**: The system SHALL provide an in-app web-based Markdown editor (EasyMDE) for creating and modifying the Markdown content of Documents, Templates, and Process Workflows.
    * *Verification*: UI inspection.
    * *Source*: PRD 1.2, 4.4.2.
* **FR-EDIT-002**: The Markdown editor (EasyMDE) SHALL provide standard Markdown formatting options such as headings, bold, italics, lists, links, images, tables, etc., via its toolbar and/or keyboard shortcuts.
    * *Verification*: Functional test of editor features.
    * *Source*: PRD 4.4.2.
* **FR-EDIT-003**: The Markdown editor (EasyMDE) SHALL offer a user-friendly interface with preview capabilities (e.g., side-by-side or tabbed preview).
    * *Verification*: Usability testing, feature review.
    * *Source*: PRD 4.4.2.

### 3.5 Versioning
* **FR-VER-001**: All Documents, Document Templates, and Process Workflows (collectively "items") SHALL have a version history.
    * *Verification*: Database schema review, functional testing of save operations.
    * *Source*: PRD 1.2, 4.5.
* **FR-VER-002**: When a user saves changes to an item using a "Save" button in the UI, a new version of that item's content SHALL be created and stored immutably in the PostgreSQL database. Previous versions SHALL remain accessible.
    * *Verification*: Functional test of saving an edited item, database inspection.
    * *Source*: PRD 1.2, 4.5.
* **FR-VER-003**: Each version SHALL be associated with:
    * A unique version identifier (`version_id`).
    * The identifier of the item it belongs to (`item_id`).
    * The full Markdown content (`markdown_content`).
    * A timestamp indicating when the version was saved (`created_at`).
    * The identifier of the team that performed the save (`saved_by_team_id` - this can be a user team or `ADMIN_SYSTEM_TEAM_ID`).
    * A sequential version number for that specific item (`version_number`).
    * *Verification*: Database schema review, inspection of version metadata.
    * *Source*: PRD 4.5, 6.1.
* **FR-VER-004**: Users SHALL be able to view an item's version history, displaying at least the version number, save timestamp, and the saving team/user.
    * *Verification*: UI inspection, functional test of accessing version history.
    * *Source*: PRD 2.1, 4.5.
* **FR-VER-005**: Users SHALL be able to load the content of any previous version of an item into the editor. Loading a previous version replaces the current editor content; subsequent saves will create a new version.
    * *Verification*: Functional test of loading an older version.
    * *Source*: PRD 2.1, 4.5.
* **FR-VER-006**: The Markdown editor (EasyMDE) SHALL provide standard undo/redo functionality for unsaved changes within the current editing session. This is distinct from the system's item versioning.
    * *Verification*: Functional test of editor's undo/redo.
    * *Source*: PRD 2.1, 4.5.

### 3.6 Search
* **FR-SRCH-001**: Team users SHALL be able to search accessible Documents, Templates, and Workflows. Administrators SHALL be able to search all Documents, Templates, and Workflows.
    * *Verification*: UI inspection, search functionality test for both roles.
    * *Source*: PRD 2.1, 4.6.
* **FR-SRCH-002**: Search functionality SHALL allow users to specify search criteria, including:
    * Item Name: Partial or full match, case-insensitive.
    * Full-text search: Of the Markdown content of the current version of items.
    * Item Type: Filter by Document, Template, or Workflow.
    * Creation Date: Filter by date range (after/before a specific date).
    * *Verification*: Functional test of search with each criterion and combinations.
    * *Source*: PRD 4.6.
* **FR-SRCH-003**: Search results SHALL be filtered by team ownership or global visibility, appropriate to the searching user's role and permissions.
    * *Verification*: Security test: perform searches as different users/roles and verify result visibility.
    * *Source*: PRD 4.6.
* **FR-SRCH-004**: Search results SHALL be displayed in a clear, paginated list. Each result item SHALL display at least the Item Name, Item Type, and a content snippet (if from FTS and applicable).
    * *Verification*: UI inspection of search results format, pagination test.
    * *Source*: PRD 4.6.

### 3.7 Process Workflow Definition and Execution

#### 3.7.1 Workflow Definition (Admin-created)
* **FR-WFDEF-001**: Process Workflows SHALL be defined by Administrators by entering text conforming to a specific YAML-like structure into the system's Markdown editor. These are owned by `ADMIN_SYSTEM_TEAM_ID`.
    * *Verification*: Functional test of admin creating/editing workflow definition text.
    * *Source*: PRD 2.2, 3.2, 4.7.1.
* **FR-WFDEF-002**: The system SHALL validate the structure and basic syntax of the Process Workflow definition text against the specified YAML-like format when an Administrator attempts to save it. Invalid definitions SHALL be rejected with clear error messages.
    * *Verification*: Test saving valid and invalid workflow definitions, check error messages.
    * *Source*: PRD 4.7.1.
* **FR-WFDEF-003**: A valid Process Workflow definition (YAML-like structure) MUST include:
    * `inputDocumentSelectors`: (List of strings, required) Glob patterns for input Document names (e.g., `["KW*_Weekly_Analysis", "Daily_Log_????-??-??"]`).
    * `inputDateSelector`: (String, optional) Date filter (e.g., `olderThanDays 7`, `between_YYYY-MM-DD_YYYY-MM-DD`).
    * `outputName`: (String, required) Template for output Document name (placeholders: `{{Year}}`, `{{Month}}`, `{{Day}}`, `{{InputFileName}}`, `{{WorkflowName}}`).
    * `prompt`: (Multiline string, required) LLM prompt with placeholders.
    * *Note*: LLM model and temperature are global backend settings, not defined per workflow.
    * *Verification*: Review of saved workflow definitions, validation logic inspection.
    * *Source*: PRD 3.2, 4.7.1.
* **FR-WFDEF-004**: The `prompt` field SHALL support placeholders: `{{DocumentContext}}`, `{{CurrentDate}}`, `{{CurrentTime}}`, `{{Year}}`, `{{Month}}`, `{{Day}}`, `{{InputFileNames}}`, `{{InputFileCount}}`, `{{InputFileName}}`, `{{WorkflowName}}`.
    * *Verification*: Test workflow execution with prompts using these placeholders.
    * *Source*: PRD 4.7.1.
* **FR-WFDEF-005**: Default instructional content SHALL be provided by the frontend for new Process Workflows created by an Administrator.
    * *Verification*: Check initial content of a new workflow.
    * *Source*: PRD 4.7.1.

#### 3.7.2 Workflow Execution (Team-initiated)
* **FR-WFEX-001**: Team users SHALL be able to manually trigger execution of globally visible, Admin-created Process Workflows.
    * *Verification*: Functional test of triggering a workflow by a team user.
    * *Source*: PRD 2.1, 4.7.2.
* **FR-WFEX-002**: On workflow trigger, the system SHALL:
    1.  Select input Documents (latest version) visible to the team, matching `inputDocumentSelectors` and `inputDateSelector`.
    2.  Construct the final prompt using content from selected documents and placeholders.
    3.  Send the prompt to the Ollama server (using global model/temperature settings).
    * *Verification*: Step-through debugging or logging of workflow execution.
    * *Source*: PRD 4.7.2.
* **FR-WFEX-003**: The system UI SHALL display the LLM's complete, raw response to the user in a modal or dedicated view after execution.
    * *Verification*: UI inspection during/after workflow execution.
    * *Source*: PRD 4.7.2.
* **FR-WFEX-004**: A new Document SHALL be created upon successful LLM response:
    * Owned by the executing team, private by default.
    * Name generated from `outputName` template (ensuring uniqueness).
    * Content is the raw LLM output.
    * *Verification*: Functional test of workflow execution, verification of created document.
    * *Source*: PRD 4.7.2.
* **FR-WFEX-005**: The UI SHALL provide feedback on execution status (in progress, completed, failed).
    * *Verification*: UI inspection during and after workflow execution.
    * *Source*: PRD 4.7.2.
* **FR-WFEX-006**: Ollama server errors or unavailability SHALL be reported clearly to the user, and no output document should be created.
    * *Verification*: Test workflow execution with Ollama server issues.
    * *Source*: PRD 4.7.2.

### 3.8 Sharing and Visibility
* **FR-SHARE-001 (Documents - Team)**: Team-created Documents SHALL be private to the owning team by default. The owning team SHALL be able to mark their Documents as "globally visible".
    * *Verification*: Test document creation and visibility toggle.
    * *Source*: PRD 2.1, 3.2, 4.8.
* **FR-SHARE-002 (Templates/Workflows - Admin)**: Admin-created Document Templates and Process Workflows (owned by `ADMIN_SYSTEM_TEAM_ID`) SHALL be private to Admins by default. Administrators SHALL be able to mark them "globally visible".
    * *Verification*: Test template/workflow creation by admin and visibility toggle.
    * *Source*: PRD 2.2, 3.2, 4.8.
* **FR-SHARE-003 (Global Read Access)**: Globally visible items SHALL be viewable (read-only for content) by all other authenticated team users.
    * *Verification*: As a different team, verify visibility of shared items.
    * *Source*: PRD 4.8.
* **FR-SHARE-004 (Template Usage)**: Teams SHALL be able to use globally visible Document Templates to create new Documents.
    * *Verification*: As a team, create a document using a globally shared template.
    * *Source*: PRD 2.1, 4.8.
* **FR-SHARE-005 (Workflow Input Usage)**: Teams SHALL be able to use globally visible Documents (owned by other teams) as inputs for their Process Workflows if they match selectors.
    * *Verification*: Execute a workflow using a globally shared document as input.
    * *Source*: PRD 2.1, 4.8.
* **FR-SHARE-006 (Workflow Execution Usage)**: Teams SHALL be able to view and execute globally visible Process Workflows.
    * *Verification*: As a team, view and execute a globally shared workflow.
    * *Source*: PRD 2.1, 4.8.
* **FR-SHARE-007 (No Edit/Delete by Others)**: Globally visible items SHALL NOT be editable (content or metadata, except by Admin for any doc metadata) or deletable by non-owning teams/non-admins.
    * *Verification*: Attempt edit/delete of a shared item as a non-owner.
    * *Source*: PRD 4.8.
* **FR-SHARE-008 (Revert to Private)**: Owners (Teams for their Documents, Admins for Templates/Workflows) SHALL be able to revert their globally visible items back to private.
    * *Verification*: Functional test of changing visibility from global to private.
    * *Source*: PRD 4.8.

### 3.9 Duplication
* **FR-DUP-001 (Who Can Duplicate)**:
    * Team Users SHALL be able to duplicate Documents they own, or globally visible Documents and Document Templates.
    * Administrators SHALL be able to duplicate any Document, Document Template, or Process Workflow.
    * *Verification*: Test duplication functionality for different roles and item types.
    * *Source*: PRD 2.1, 2.2, 4.9.
* **FR-DUP-002 (Duplicate Properties)**: Duplication SHALL create an independent copy with content from the source's specified (or current) version. The new item SHALL:
    * Be owned by the duplicating team/admin (for T/W, owned by `ADMIN_SYSTEM_TEAM_ID` if admin duplicates).
    * Be private by default (unless an Admin duplicates an already global T/W, which may remain global).
    * Start its own version history (Version 1 with copied content).
    * *Verification*: Verify properties of the duplicated item.
    * *Source*: PRD 4.9.
* **FR-DUP-003 (Naming Duplicate)**: The user SHALL be prompted for a new, unique name for the duplicated item (unique per owner and type).
    * *Verification*: UI inspection of naming prompt, test unique/non-unique names.
    * *Source*: PRD 4.9.

### 3.10 AI Co-Management Support
* **FR-AICM-001**: The system's features (Documents, Templates, Workflows, Versioning, Search, LLM Integration) SHALL collectively support AI Co-Management rituals and practices such as Collective Context Management, AI-Assisted Documentation, Collaborative Prompt Development (by Admins for Workflows), and AI-Supported Decision Making.
    * *Verification*: Scenario testing based on AI Co-Management principles.
    * *Source*: PRD 1.3, 3.2, 4.10.
* **FR-AICM-002**: Process Workflow structures SHALL be flexible enough for Administrators to define various AI roles (e.g., Documentarian, Analyst, Facilitator) as described in AI Co-Management practices, by crafting appropriate prompts and selecting relevant inputs.
    * *Verification*: Review of workflow definition capabilities against AI role examples.
    * *Source*: PRD 4.10.

### 3.11 Basic Security Best Practices
* **FR-SEC-001 (HTTPS)**: Communication between the frontend SPA and the backend API SHALL be over HTTPS (typically handled by a reverse proxy in deployment).
    * *Verification*: Network traffic inspection, reverse proxy configuration review.
    * *Source*: PRD 4.11.
* **FR-SEC-002 (Common Vulnerabilities)**: The system MUST implement input validation on all user-supplied data (frontend and backend) and output encoding in the frontend to protect against common web vulnerabilities such as Cross-Site Scripting (XSS). Parameterized queries or an ORM SHALL be used for database interactions to prevent SQL Injection.
    * *Verification*: Security testing, code review.
    * *Source*: PRD 4.11.
* **FR-SEC-003 (Password Hashing)**: Passwords (admin and team user) SHALL be hashed using bcrypt.
    * *Verification*: Code review, database inspection.
    * *Source*: PRD 1.2, 4.3, 4.11.
* **FR-SEC-004 (Session Management)**: Secure session management SHALL be implemented using HTTP-only cookies. Rate limiting SHALL be applied to the admin login endpoint.
    * *Verification*: Security testing, inspection of cookie attributes.
    * *Source*: PRD 1.2, 4.3, 4.11.
* **FR-SEC-005 (Admin Auth Distinction)**: Distinct authentication mechanisms SHALL be used for administrators versus team users.
    * *Verification*: Security testing.
    * *Source*: PRD 4.11.
* **FR-SEC-006 (Configurable DB Credentials)**: Database credentials SHALL be configurable via environment variables and not hardcoded.
    * *Verification*: Inspection of Docker configuration and application code.
    * *Source*: PRD 4.11.
* **FR-SEC-007 (Configurable Ollama Details)**: Ollama server details (URL, default model, default temperature) SHALL be configurable via environment variables and not hardcoded.
    * *Verification*: Inspection of Docker configuration and application code.
    * *Source*: PRD 1.2, 3.1, 4.1, 4.11.

## 4. External Interface Requirements

This section defines the interfaces for the Team Intelligence Platform (TIP) with users, other software systems, and hardware.

### 4.1 User Interfaces
* **UI-001 (Web Browser Interface)**: The primary user interface for both Team Users and Administrators SHALL be a web-based Single-Page Application (SPA) accessible via modern web browsers (e.g., latest versions of Chrome, Firefox, Edge, Safari) on desktop operating systems (Windows, macOS, Linux).
    * *Source*: PRD 3.1.
* **UI-002 (Responsiveness)**: The UI SHOULD be responsive and usable on common desktop screen resolutions (e.g., 1366x768 and above). While full mobile optimization is not a primary goal for v1.0, the application should degrade gracefully and remain minimally usable on tablet-sized screens. Major UI elements should not break or overlap on smaller desktop views.
    * *Source*: PRD 5.5.
* **UI-003 (Navigation)**: Navigation within the application SHALL be intuitive, with clear menus and links. The admin interface SHALL be clearly distinct from the team user interface.
    * *Source*: PRD 5.5.
* **UI-004 (Feedback)**: The UI SHALL provide immediate and clear visual feedback for user actions, such as loading indicators for asynchronous operations (API calls, workflow execution), success messages (e.g., toasts) upon completion of tasks (e.g., "Document saved successfully!"), and user-friendly error messages if an operation fails.
    * *Source*: PRD 5.5.
* **UI-005 (Accessibility)**: The UI SHOULD strive to meet basic web accessibility guidelines (e.g., sufficient color contrast, keyboard navigability for primary functions, ARIA attributes where appropriate).
    * *Source*: PRD 1.3 (Ease of Use & Accessibility).
* **UI-006 (Markdown Editor UI)**: The EasyMDE Markdown editor interface (FR-EDIT-*) is a key component of the UI, providing text formatting and preview capabilities.
    * *Source*: PRD 1.2, 4.4.2.
* **UI-007 (Admin Interface Simplicity)**: The admin interface (FR-ADM-*) SHALL be simple and functional, focusing on the tasks of team account management, and system-level Template and Workflow management.
    * *Source*: PRD 2.2.
* **UI-008 (Language)**: The UI SHALL be presented in English only.
    * *Source*: PRD 1.2.

### 4.2 Software Interfaces

#### 4.2.1 PostgreSQL Database Interface
* **SI-DB-001 (Connection Protocol)**: The backend API SHALL connect to the PostgreSQL database using an appropriate Python library that supports asynchronous operations (e.g., `asyncpg` with SQLAlchemy).
    * *Source*: PRD 3.3 (SQLAlchemy async with asyncpg).
* **SI-DB-002 (Authentication)**: Database connection credentials (host, port, database name, username, password) SHALL be configurable via environment variables, as per FR-SEC-006.
    * *Source*: PRD 4.11.
* **SI-DB-003 (Data Language)**: The backend API SHALL use SQL, primarily through an ORM (SQLAlchemy), to interact with the PostgreSQL database for all CRUD operations and querying. Parameterized queries generated by the ORM MUST be used to prevent SQL injection vulnerabilities.
    * *Source*: PRD 3.3, 4.11.
* **SI-DB-004 (Transactions)**: Database operations that involve multiple related writes (e.g., creating an item and its first version, updating an item and its `current_version_id`) SHALL be performed within atomic database transactions to ensure data consistency.
    * *Source*: General best practice.
* **SI-DB-005 (Full-Text Search)**: The system SHALL leverage PostgreSQL's built-in full-text search capabilities for searching content within Documents, Templates, and Workflows. This includes using `tsvector` and `tsquery` types and GIN indexes.
    * *Source*: PRD 1.2, 3.1, 4.6.

#### 4.2.2 Ollama Server Interface
* **SI-OLLAMA-001 (Connection Protocol)**: The backend API SHALL communicate with the local Ollama server via HTTP requests to its API endpoint (typically `/api/generate`).
    * *Source*: PRD 1.2, 3.1, 4.7.2.
* **SI-OLLAMA-002 (Configuration)**: The URL of the Ollama server (e.g., `http://localhost:11434`), the default model (e.g., `ollama/llama3:latest`), and default temperature (e.g., `0.7`) SHALL be configurable via environment variables, as per FR-SEC-007.
    * *Source*: PRD 1.2, 3.1, 4.1, 4.7.1, 4.11.
* **SI-OLLAMA-003 (Request Format)**: The backend API SHALL send requests to the Ollama API in JSON format, including at least:
    * `model`: (string) The globally configured model name.
    * `prompt`: (string) The full prompt text.
    * `stream`: (boolean, value: `false`) For TIP's current needs, streaming is not required.
    * `options`: (object, optional) Including `temperature` from the global configuration.
    * *Source*: PRD 4.7.1, Backend Code (`ollama_service.py`).
* **SI-OLLAMA-004 (Response Format)**: The backend API SHALL expect to receive responses from the Ollama `/api/generate` endpoint in JSON format. The key field containing the generated text (typically `response`) will be extracted. The service SHALL strip `<think>...</think>` tags and leading/trailing newlines from the response.
    * *Source*: PRD 4.7.2, Backend Code (`ollama_service.py`).
* **SI-OLLAMA-005 (Error Handling)**: The backend API MUST gracefully handle HTTP error codes (e.g., 404 if model not found, 500 for server errors) and network errors (e.g., connection refused, timeout) when communicating with the Ollama server. These errors should be reported to the user as per FR-WFEX-006.
    * *Source*: PRD 4.7.2.

### 4.3 Hardware Interfaces
No direct hardware interfaces are specified for TIP beyond standard network interface cards for communication and disk drives for data storage, which are managed by the underlying operating system and Docker environment.

### 4.4 Communications Interfaces
* **CI-001 (HTTPS - Frontend to Backend)**: All communication between the frontend SPA and the backend API SHALL be over HTTPS. This is typically achieved by deploying the backend behind a reverse proxy (e.g., Nginx provided in the `docker-compose.yml`) that handles SSL termination.
    * *Source*: PRD 4.11 (FR-SEC-001).
* **CI-002 (HTTP - Backend to Ollama)**: The backend API SHALL communicate with the local Ollama server over HTTP by default, as Ollama typically runs locally without SSL. If the local Ollama instance is configured for HTTPS, the backend SHOULD be configurable to support this, though it's not a primary requirement for v1.0.
    * *Source*: PRD 3.1.
* **CI-003 (TCP/IP - Backend to PostgreSQL)**: The backend API SHALL communicate with the PostgreSQL database using the standard PostgreSQL wire protocol, which operates over TCP/IP.
    * *Source*: Standard database communication.

## 5. Non-Functional Requirements

This section details the non-functional requirements (quality attributes) of the Team Intelligence Platform (TIP).

### 5.1 Performance Requirements
* **NFR-PERF-001 (API Response Times)**: Average API response times for common interactive operations (e.g., loading a document list, opening an item, saving an item without complex workflow triggers) SHALL be less than 2 seconds under typical load conditions.
    * *Verification*: Performance testing with simulated load.
    * *Source*: PRD 5.1.
* **NFR-PERF-002 (Search Latency)**: Search results (as per FR-SRCH-*) SHALL be returned within 3 seconds for typical queries on a moderately sized dataset.
    * *Verification*: Performance testing of search functionality.
    * *Source*: PRD 5.1.
* **NFR-PERF-003 (Workflow System Overhead)**: The TIP system's overhead for Process Workflow execution (excluding the time taken by the Ollama LLM itself for generation) SHALL be less than 500 milliseconds per workflow.
    * *Verification*: Performance profiling of workflow execution.
    * *Source*: PRD 5.1.
* **NFR-PERF-004 (Markdown Editor Responsiveness)**: The in-app Markdown editor (EasyMDE) MUST load and respond to user input without noticeable lag for documents up to approximately 50,000 characters.
    * *Verification*: Usability testing with large documents.
    * *Source*: PRD 5.1.
* **NFR-PERF-005 (Version Loading)**: Loading a previous version of an item SHOULD be comparable in performance to loading the latest version.
    * *Verification*: Performance testing of version loading.
    * *Source*: PRD 5.1.

### 5.2 Security Requirements
* **NFR-SEC-001 (Least Privilege - DB)**: The application's database user account SHALL have the minimum necessary privileges for its operations.
    * *Verification*: Review of database user privileges.
    * *Source*: PRD 5.4.
* **NFR-SEC-002 (Dependency Management)**: Third-party libraries and dependencies SHOULD be sourced from trusted repositories and periodically scanned for vulnerabilities.
    * *Verification*: Review of dependency sources; demonstration of vulnerability scanning process (if implemented).
    * *Source*: PRD 5.4.
* **NFR-SEC-003 (Secure Configuration)**: Sensitive configuration data (admin password, DB credentials, Ollama URL, session secrets) MUST be supplied via environment variables and NOT hardcoded, as per FR-SEC-003, FR-SEC-006, FR-SEC-007.
    * *Verification*: Code review, inspection of Docker configuration.
    * *Source*: PRD 5.4.
* **NFR-SEC-004 (Admin Login Rate Limiting)**: The Administrator login interface SHALL implement rate limiting on login attempts (e.g., max 5 failed attempts per IP per minute).
    * *Verification*: Security testing of admin login.
    * *Source*: PRD 1.2, 4.2, 5.4.
* **NFR-SEC-005 (Error Message Security)**: Error messages displayed to users SHOULD NOT reveal sensitive system information or internal stack traces. Detailed errors SHALL be logged internally.
    * *Verification*: Review of UI error messages, inspection of logs.
    * *Source*: General security best practice.
* **NFR-SEC-006 (Session Integrity)**: Session tokens SHOULD be regenerated upon login to prevent session fixation.
    * *Verification*: Security testing of session management.
    * *Source*: General security best practice.

### 5.3 Usability Requirements
* **NFR-UX-001 (Learnability)**: The UI for team users MUST be intuitive. A user familiar with web applications SHOULD perform common tasks with minimal training.
    * *Verification*: Usability testing.
    * *Source*: PRD 1.3, 5.5.
* **NFR-UX-002 (Consistency)**: UI design, navigation, terminology, and interaction patterns SHALL be consistent.
    * *Verification*: UI review.
    * *Source*: PRD 5.5.
* **NFR-UX-003 (Feedback Clarity)**: The system MUST provide clear, concise, and timely visual feedback (loading states, success/error messages via toasts) for all user actions, as per UI-004.
    * *Verification*: UI review, usability testing.
    * *Source*: PRD 5.5.
* **NFR-UX-004 (Editor Experience)**: The EasyMDE Markdown editor MUST provide a usable and modern experience for content creation.
    * *Verification*: Usability testing.
    * *Source*: PRD 1.2, 5.5.
* **NFR-UX-005 (Desktop Responsiveness)**: The application MUST display correctly on common desktop resolutions (1366x768 and above) without horizontal scrolling for primary content.
    * *Verification*: Testing on different screen resolutions.
    * *Source*: PRD 5.5.
* **NFR-UX-006 (Streamlined Workflows)**: User interaction flows for common tasks SHOULD be streamlined, minimizing unnecessary steps.
    * *Verification*: Usability testing, task completion analysis.
    * *Source*: PRD 5.5.
* **NFR-UX-007 (Readability)**: Font choices, text sizes, and color contrast SHOULD ensure good readability.
    * *Verification*: Visual inspection, accessibility check.
    * *Source*: PRD 5.5.

### 5.4 Reliability Requirements
* **NFR-AVAIL-001 (Error Handling - Internal)**: System components SHALL implement robust internal error handling to prevent crashes. Errors SHALL be caught, logged, and reported gracefully.
    * *Verification*: Code review, fault injection testing.
    * *Source*: PRD 5.3.
* **NFR-AVAIL-002 (External Service Resilience)**: The system MUST handle transient errors or unavailability of Ollama or PostgreSQL gracefully, informing the user and allowing retries where appropriate, as per FR-WFEX-006.
    * *Verification*: Test scenarios with Ollama/DB temporarily unavailable.
    * *Source*: PRD 5.3.
* **NFR-AVAIL-003 (Data Integrity - DB Backups)**: The `docker-compose.yml` setup SHALL use a persistent Docker volume for PostgreSQL data. Regular backup procedures are the user's responsibility but facilitated by this persistence.
    * *Verification*: Review of `docker-compose.yml`.
    * *Source*: PRD 5.3, 6.2.
* **NFR-AVAIL-004 (Logging)**: The backend API SHALL generate sufficient logs for key events, errors, and operations to aid troubleshooting. Logs SHALL be accessible via `docker logs`. The frontend MAY log critical errors to the console.
    * *Verification*: Inspection of logs.
    * *Source*: PRD 5.3 (logging_config.py).
* **NFR-AVAIL-005 (Session Persistence)**: User sessions SHOULD be reasonably persistent across browser refreshes, assuming the session cookie has not expired.
    * *Verification*: Functional testing.
    * *Source*: General usability expectation.

### 5.5 Maintainability Requirements
* **NFR-MAIN-001 (Code Quality)**: Source code (Python backend, React frontend) MUST be well-organized, adhering to consistent standards, and appropriately commented.
    * *Verification*: Code reviews, static analysis tool reports (e.g., Ruff, ESLint).
    * *Source*: PRD 5.6.
* **NFR-MAIN-002 (Modularity - Backend)**: The backend API design SHALL be modular (e.g., CRUD layer, services, API endpoints as seen in `ulacm_backend/app` structure).
    * *Verification*: Architectural review of backend code.
    * *Source*: PRD 5.6.
* **NFR-MAIN-003 (Database Schema Documentation)**: The PostgreSQL database schema SHALL be documented via the `init_db.sql` script and ORM models.
    * *Verification*: Review of `init_db.sql` and SQLAlchemy models.
    * *Source*: PRD 5.6.
* **NFR-MAIN-004 (Configuration Management)**: All application configuration parameters MUST be externalized via environment variables (`.env` files), as per NFR-SEC-003.
    * *Verification*: Code review, inspection of deployment scripts.
    * *Source*: PRD 5.6.
* **NFR-MAIN-005 (Testability)**: System components SHOULD be designed for testability, with unit tests for backend logic.
    * *Verification*: Review of testing strategy and existing tests.
    * *Source*: PRD 5.6.

### 5.6 Deployability Requirements
* **NFR-DEP-001 (Docker Compose Deployment)**: The entire TIP service MUST be deployable using `docker-compose up`, as per FR-SYS-002.
    * *Verification*: Successful deployment using `docker-compose up`.
    * *Source*: PRD 5.7.
* **NFR-DEP-002 (Persistent DB Storage via Docker Volume)**: The `docker-compose.yml` MUST configure PostgreSQL data to be stored in a persistent Docker volume.
    * *Verification*: Test data persistence across container restarts.
    * *Source*: PRD 5.3, 5.7.
* **NFR-DEP-003 (Ollama Integration in Compose)**: The `docker-compose.yml` MAY include an optional service definition for Ollama. Clear instructions MUST be provided for connecting to an external Ollama instance.
    * *Verification*: Review of `docker-compose.yml` and deployment instructions.
    * *Source*: PRD 5.7.
* **NFR-DEP-004 (Deployment Documentation)**: Clear, step-by-step instructions MUST be provided for building images (if needed), configuring environment variables, and running the system.
    * *Verification*: Review of deployment documentation (e.g., README).
    * *Source*: PRD 5.7.
* **NFR-DEP-005 (Minimal Post-Deployment Configuration)**: The system SHOULD require minimal manual configuration after `docker-compose up`. Setting environment variables before startup should suffice.
    * *Verification*: Review of post-deployment setup.
    * *Source*: PRD 5.7.

### 5.7 Scalability Requirements
* **NFR-SCALE-001 (Concurrent User Support)**: The system architecture MUST support typical concurrent usage from multiple teams without significant performance degradation, aiming for responsiveness with multiple active users. (Refer to PRD 4.1 for target user load if specified, otherwise general responsiveness is key).
    * *Verification*: Load testing.
    * *Source*: PRD 5.2.
* **NFR-SCALE-002 (Stateless Backend Design)**: The backend API service (FastAPI) SHALL be stateless to facilitate potential future horizontal scaling (though v1.0 is single-instance via docker-compose). Session state is managed via client-side cookies.
    * *Verification*: Architectural review of backend state management.
    * *Source*: PRD 5.2.
* **NFR-SCALE-003 (Database Performance with Growth)**: The PostgreSQL schema and queries MUST be designed for efficient data growth, using appropriate indexing (PKs, FKs, FTS indexes, indexes on frequently filtered columns).
    * *Verification*: Database schema review, query plan analysis.
    * *Source*: PRD 5.2.
* **NFR-SCALE-004 (Large Document Handling)**: The system MUST gracefully handle large Markdown documents (up to 50,000 characters per NFR-PERF-004) without excessive memory use or processing time during save, load, or versioning.
    * *Verification*: Testing with large document content.
    * *Source*: PRD 5.2.

## 6. System Architecture

This section describes the architecture of the Team Intelligence Platform (TIP).

### 6.1 Architectural Style
TIP will adopt a **three-tier layered architecture**, deployed as a set of containerized services. This style promotes separation of concerns, modularity, and maintainability. The tiers are:

1.  **Presentation Tier (Frontend)**: A Single-Page Application (SPA) running in the user's web browser.
    * *Technology*: React with TypeScript, Vite for building, and Tailwind CSS for styling.
    * *Responsibilities*: User interface rendering, user input handling, client-side validation, interaction with the Backend API via RESTful calls.
2.  **Application Tier (Backend API Service)**: A stateless server-side application.
    * *Technology*: Python with FastAPI.
    * *Responsibilities*: Business logic, authentication/authorization, request validation, orchestration of operations (including calls to Ollama), data access, and manipulation via the Data Tier. Exposes a RESTful API.
3.  **Data Tier**: Consists of the persistent data store and the AI model server.
    * **PostgreSQL Database**: Stores all application data (team information, ContentItems, ContentVersions).
        * *Technology*: PostgreSQL 15+.
    * **Local Ollama Server**: Provides LLM processing capabilities. The TIP backend acts as a client to this server.
        * *Technology*: Ollama (external or containerized).

All components (Frontend, Backend API, PostgreSQL) are containerized using Docker and orchestrated via `docker-compose.yml`. The Ollama server can optionally be part of this Docker Compose setup. (PRD 3.1, 3.3)

### 6.2 High-Level Component Diagram

```mermaid
graph LR
    User[Team User / Admin] -- HTTPS --> Browser[Web Browser (Frontend SPA - React)]

    subgraph Dockerized Environment [TIP Docker Compose Environment]
        Browser -- HTTP/HTTPS (REST API) --> Backend[Backend API Service (FastAPI/Python)]
        Backend -- TCP/IP (SQLAlchemy/asyncpg) --> DB[(PostgreSQL Database)]
        Backend -- HTTP --> Ollama[Ollama Server (Local)]
    end

    style User fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px
    style Browser fill:#fff,stroke:#333,stroke-width:2px
    style Backend fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    style DB fill:#f8cecc,stroke:#b85450,stroke-width:2px
    style Ollama fill:#e1d5e7,stroke:#9673a6,stroke-width:2px
```

**Diagram Legend:**
* Arrows indicate the primary direction of data flow or requests.
* Components within the "TIP Docker Compose Environment" are managed by `docker-compose.yml`.

### 6.3 Component Descriptions

#### 6.3.1 Frontend SPA (React)
* **Purpose**: Provides the interactive user interface for Team Users and Administrators.
* **Key Modules/Responsibilities**:
    * **UI Components**: Reusable UI elements (buttons, forms, lists, Markdown editor wrapper using `react-simplemde-editor` for EasyMDE). Located in `ulacm_frontend/src/components/`.
    * **Routing**: Manages navigation between different views/pages of the SPA using `react-router-dom`. Defined in `ulacm_frontend/src/App.tsx`.
    * **State Management**: Manages client-side application state.
        * Global authentication state: `AuthContext` (`ulacm_frontend/src/contexts/AuthContext.tsx`).
        * Local component state: React hooks (`useState`, `useEffect`).
    * **API Client**: Handles communication with the Backend API service using `axios`. Configured in `ulacm_frontend/src/services/apiClient.ts`.
    * **Authentication Handling**: Manages login/logout flows.
    * **Views/Pages**: Located in `ulacm_frontend/src/pages/`. Includes:
        * `LoginPage`, `AdminLoginPage`
        * `TeamDashboardPage`, `AdminDashboardPage`
        * `ContentListPage` (for Documents, Templates, Workflows)
        * `EditorViewPage` (for Documents, Templates, Workflows)
        * `ExecuteWorkflowPage`
        * `SearchPage`
        * `TeamManagementPage` (Admin)
* **Key Technologies**: React, TypeScript, Vite, Tailwind CSS, `react-simplemde-editor` (EasyMDE), `axios`, `react-router-dom`, `lucide-react` (icons), `react-hot-toast`. (PRD 3.3)

#### 6.3.2 Backend API Service (Python/FastAPI)
* **Purpose**: Implements the core business logic, data processing, and external service interactions.
* **Key Modules/Responsibilities** (located in `ulacm_backend/app/`):
    * **API Endpoints (RESTful)**: Defines HTTP endpoints for all application functionalities using FastAPI routers. Located in `api/v1/endpoints/`.
    * **Authentication & Authorization Module**: Handles team user and admin authentication (JWTs via HTTP-only cookies), session validation, and access control. Implemented in `core/security.py` and `api/v1/deps.py`.
    * **Team Management Module**: Logic for CRUD operations on team accounts (Admin only). Implemented in `crud/crud_team.py` and `api/v1/endpoints/admin_teams.py`.
    * **Content Item Management Module**: Logic for CRUD operations on Documents, Templates, and Workflows. Implemented in `crud/crud_content_item.py` and `api/v1/endpoints/content_items.py`.
    * **Versioning Module**: Manages creation and retrieval of content versions. Implemented in `crud/crud_content_version.py` and `api/v1/endpoints/versions.py`.
    * **Workflow Engine Module**: Parses workflow definitions, selects input documents, constructs prompts, interacts with the Ollama Service, and creates output documents. Implemented in `services/workflow_service.py`, `services/workflow_parser.py`, and `api/v1/endpoints/workflows_exec.py`.
    * **Search Module**: Interfaces with the database to perform full-text searches. Implemented in `crud/crud_search.py` and `api/v1/endpoints/search.py`.
    * **Database Interaction Layer**: Uses SQLAlchemy (async with `asyncpg`) for ORM and database operations. Models in `db/models/`, CRUD base in `crud/base.py`.
    * **Ollama Client Module**: Handles communication with the Ollama server API. Implemented in `services/ollama_service.py`.
* **Key Technologies**: Python 3.10+, FastAPI, Pydantic, SQLAlchemy (async), `asyncpg`, `httpx`, `passlib[bcrypt]`, `python-jose`. (PRD 3.3)

#### 6.3.3 PostgreSQL Database
* **Purpose**: Provides persistent storage for all application data.
* **Key Responsibilities**:
    * Storing Team account information (including hashed passwords).
    * Storing ContentItems (Documents, Templates, Workflows) metadata.
    * Storing all ContentVersions of items.
    * Enforcing data integrity through constraints (PKs, FKs, unique constraints).
    * Supporting efficient querying and full-text search (via GIN indexes and `tsvector` columns).
* **Key Technologies**: PostgreSQL 15+. Schema defined in `ulacm_backend/init_db.sql` and reflected in SQLAlchemy models (`ulacm_backend/app/db/models/`). (PRD 3.1, 3.3, 6.1)

#### 6.3.4 Ollama Server (External/Co-deployed)
* **Purpose**: Provides access to local Large Language Models for text generation.
* **Key Responsibilities (from TIP's perspective)**:
    * Exposing an HTTP API (e.g., `/api/generate`) to accept prompts and model parameters.
    * Processing prompts using the specified LLM.
    * Returning generated text responses.
* **Interaction**: The TIP Backend API is a client to the Ollama server. TIP does not manage the Ollama server's lifecycle or model management beyond sending requests to it. Configuration (URL, default model, temperature) is managed via environment variables for the backend. (PRD 3.1, 4.2.2)

### 6.4 Deployment View
The system SHALL be deployed using Docker and `docker-compose` as specified in FR-SYS-002 and NFR-DEP-001.
The `docker-compose.yml` file defines the services, networks, volumes, and environment variables for the application components.

* **Services**:
    * `frontend`: Builds from `ulacm_frontend/Dockerfile`, serves static React build using Nginx (as per `ulacm_frontend/nginx.conf`).
    * `backend`: Builds from `ulacm_backend/Dockerfile`, runs the FastAPI application using Uvicorn.
    * `db`: Uses the official `postgres:15-alpine` image.
    * `ollama` (optional): Can use `ollama/ollama:latest` image.
* **Networks**: A bridge network (e.g., `ulacm_network`) allows services to communicate.
* **Volumes**:
    * `postgres_data`: Persistent storage for the PostgreSQL database.
    * `ollama_data` (if Ollama is co-deployed): Persistent storage for Ollama models.
* **Environment Variables**: Configured via an `.env` file in `ulacm_backend/` for the backend and database services (e.g., `POSTGRES_USER`, `POSTGRES_PASSWORD`, `ADMIN_PASSWORD`, `SESSION_SECRET_KEY`, `OLLAMA_API_URL`, `OLLAMA_MODEL`, `OLLAMA_TEMPERATURE`). Frontend environment variables are typically build-time arguments or served via Nginx configuration if needed at runtime.
* **Database Initialization**: The `init_db.sql` script is used to initialize the database schema and the `ADMIN_SYSTEM_TEAM_ID` record when the `db` service starts for the first time.
* **Reverse Proxy**: The Nginx service within the `frontend` container also acts as a reverse proxy, forwarding requests prefixed with `/api/` to the `backend` service. This handles HTTPS termination if SSL certificates are configured for Nginx (though for local dev, it's often HTTP).

(Refer to `docker-compose.yml` in the codebase for the exact structure and configuration.)

## 7. Data Design

This section details the data storage strategy, conceptual data model, and detailed data dictionary for the Team Intelligence Platform (TIP).

### 7.1 Data Storage
All application data, including team accounts, Documents, Templates, Process Workflows, and their versions, SHALL be stored in a PostgreSQL relational database, as per FR-SYS-004. The database schema is designed to support the functional requirements, including versioning, ownership, sharing, and full-text search.

### 7.2 Conceptual Data Model (ERD)

```mermaid
erDiagram
    TEAMS {
        UUID team_id PK "Team ID (Primary Key)"
        VARCHAR team_name "Team Name (Unique)"
        VARCHAR username "Team Login Username (Unique)"
        VARCHAR hashed_password "Hashed Password"
        BOOLEAN is_active "Is account active?"
        TIMESTAMP created_at "Creation Timestamp"
        TIMESTAMP updated_at "Last Update Timestamp"
    }

    CONTENT_ITEMS {
        UUID item_id PK "Content Item ID (Primary Key)"
        UUID team_id FK "Owning Team ID (FK to TEAMS)"
        content_item_type_enum item_type "Type (DOCUMENT, TEMPLATE, WORKFLOW)"
        VARCHAR name "Item Name"
        BOOLEAN is_globally_visible "Is visible to all teams?"
        UUID current_version_id FK "Points to active version in CONTENT_VERSIONS (ON DELETE SET NULL)"
        TIMESTAMP created_at "Creation Timestamp"
        TIMESTAMP updated_at "Last Update Timestamp"
        CONSTRAINT UQ_team_item_name_type UNIQUE (team_id, name, item_type)
    }

    CONTENT_VERSIONS {
        UUID version_id PK "Version ID (Primary Key)"
        UUID item_id FK "Content Item ID (FK to CONTENT_ITEMS, ON DELETE CASCADE)"
        TEXT markdown_content "Full Markdown content of this version"
        INTEGER version_number "Sequential version number for the item"
        TSVECTOR content_tsv "For Full-Text Search"
        UUID saved_by_team_id FK "Team ID that saved this version (FK to TEAMS, ON DELETE SET NULL)"
        TIMESTAMP created_at "Version Creation Timestamp (Save Time)"
        CONSTRAINT UQ_item_version_number UNIQUE (item_id, version_number)
    }

    TEAMS ||--o{ CONTENT_ITEMS : "owns (or ADMIN_SYSTEM_TEAM_ID owns)"
    CONTENT_ITEMS ||--o{ CONTENT_VERSIONS : "has versions"
    CONTENT_ITEMS }|--|| CONTENT_VERSIONS : "active version is"
    TEAMS ||--o{ CONTENT_VERSIONS : "saved by"

```

**Relationships:**
* One `TEAM` can own many `CONTENT_ITEMS` (or `ADMIN_SYSTEM_TEAM_ID` can own Templates/Workflows).
* One `CONTENT_ITEM` belongs to one `TEAM` (its owner, which can be `ADMIN_SYSTEM_TEAM_ID`).
* One `CONTENT_ITEM` has many `CONTENT_VERSIONS`.
* One `CONTENT_VERSION` belongs to one `CONTENT_ITEM`.
* One `CONTENT_VERSION` is saved by one `TEAM` (the team logged in at the time of save, or `ADMIN_SYSTEM_TEAM_ID`).
* One `CONTENT_ITEM` has one `current_version_id` pointing to its active `CONTENT_VERSION`.

### 7.3 Detailed Data Dictionary

This section provides a detailed description of each table and column in the PostgreSQL database.

#### 7.3.1 `teams` Table
Stores information about team accounts, including the special `ADMIN_SYSTEM_TEAM_ID`.
*Source*: PRD 6.1, Backend Model `ulacm_backend/app/db/models/team.py`

| Column Name     | Data Type                  | Constraints                                  | Description                                                                      |
| :-------------- | :------------------------- | :------------------------------------------- | :------------------------------------------------------------------------------- |
| `team_id`       | `UUID`                     | `PRIMARY KEY`, `DEFAULT uuid_generate_v4()`  | Unique identifier for the team.                                                  |
| `team_name`     | `VARCHAR(100)`             | `NOT NULL`, `UNIQUE`                         | Display name of the team (e.g., "Marketing Team Alpha"). FR-ADM-003.             |
| `username`      | `VARCHAR(50)`              | `NOT NULL`, `UNIQUE`                         | Login username for the team (e.g., "marketing_alpha_user"). FR-ADM-003.         |
| `hashed_password`| `VARCHAR(255)`            | `NOT NULL`                                   | Securely hashed password for the team account. FR-AUTH-002.         |
| `is_active`     | `BOOLEAN`                  | `NOT NULL`, `DEFAULT TRUE`                   | Flag indicating if the team account is active (TRUE) or deactivated (FALSE). FR-ADM-006. |
| `created_at`    | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`    | Timestamp of when the team record was created.                                   |
| `updated_at`    | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`    | Timestamp of when the team record was last updated (Auto-update via trigger).   |

**Indexes:**
* Primary Key on `team_id`.
* Unique index on `LOWER(team_name)`.
* Unique index on `LOWER(username)`.

---

#### 7.3.2 `content_items` Table
Stores metadata for Documents, Templates, and Process Workflows.
*Source*: PRD 6.1, Backend Model `ulacm_backend/app/db/models/content_item.py`

| Column Name           | Data Type                  | Constraints                                  | Description                                                                                   |
| :-------------------- | :------------------------- | :------------------------------------------- | :-------------------------------------------------------------------------------------------- |
| `item_id`             | `UUID`                     | `PRIMARY KEY`, `DEFAULT uuid_generate_v4()`  | Unique identifier for the content item.                                                       |
| `team_id`             | `UUID`                     | `NOT NULL`, `REFERENCES teams(team_id) ON DELETE CASCADE` | Foreign key referencing the `teams` table, indicating the owning team (or `ADMIN_SYSTEM_TEAM_ID`). FR-ADM-008 (cascade). |
| `item_type`           | `content_item_type_enum`   | `NOT NULL`                                   | Type of the content item (`DOCUMENT`, `TEMPLATE`, `WORKFLOW`).                                |
| `name`                | `VARCHAR(255)`             | `NOT NULL`                                   | Name of the content item. FR-CM-009.        |
| `is_globally_visible` | `BOOLEAN`                  | `NOT NULL`, `DEFAULT FALSE`                  | Flag indicating if the item is visible to all teams (TRUE) or private to owner (FALSE). FR-SHARE-001, FR-SHARE-002. |
| `current_version_id`  | `UUID`                     | `NULL`, `REFERENCES content_versions(version_id) ON DELETE SET NULL` | Foreign key referencing the active version in `content_versions`. |
| `created_at`          | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`    | Timestamp of when the content item record was created.                                        |
| `updated_at`          | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`    | Timestamp of when the content item record was last updated (Auto-update via trigger). |
|                       |                            | `CONSTRAINT uq_team_item_name_type UNIQUE (team_id, name, item_type)` | Ensures name is unique per type within an owner. FR-CM-009. |

**Indexes:**
* Primary Key on `item_id`.
* Index on `team_id`.
* Index on `current_version_id`.
* Index on `item_type`.
* Index on `LOWER(name)` (for case-insensitive searching by name).
* Index on `created_at`.
* GIN index on `to_tsvector('english', name)` for FTS on names.

---

#### 7.3.3 `content_versions` Table
Stores the actual Markdown content for each version of each content item.
*Source*: PRD 6.1, Backend Model `ulacm_backend/app/db/models/content_version.py`

| Column Name         | Data Type                  | Constraints                                  | Description                                                                      |
| :------------------ | :------------------------- | :------------------------------------------- | :------------------------------------------------------------------------------- |
| `version_id`        | `UUID`                     | `PRIMARY KEY`, `DEFAULT uuid_generate_v4()`  | Unique identifier for this specific version.                                     |
| `item_id`           | `UUID`                     | `NOT NULL`, `REFERENCES content_items(item_id) ON DELETE CASCADE` | Foreign key referencing the `content_items` table this version belongs to. FR-CM-008 (cascade). |
| `markdown_content`  | `TEXT`                     | `NOT NULL`                                   | The full Markdown content of this version.                                       |
| `version_number`    | `INTEGER`                  | `NOT NULL`                                   | Sequential version number for this item (e.g., 1, 2, 3...). FR-VER-003. |
| `content_tsv`       | `TSVECTOR`                 | `NULL`                                       | Stores the `tsvector` of `markdown_content` for FTS, populated by a DB trigger. |
| `saved_by_team_id`  | `UUID`                     | `NOT NULL`, `REFERENCES teams(team_id) ON DELETE SET NULL` | Foreign key referencing the `teams` table, indicating the team that saved this version (can be `ADMIN_SYSTEM_TEAM_ID`). FR-VER-003. `ON DELETE SET NULL` allows team deletion without orphaning versions if that team only acted as a saver. |
| `created_at`        | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`    | Timestamp of when this version was created (i.e., when it was saved). FR-VER-003. |
|                     |                            | `CONSTRAINT uq_item_version_number UNIQUE (item_id, version_number)` | Ensures version number is unique per item. |

**Indexes:**
* Primary Key on `version_id`.
* Index on `item_id`.
* Index on `saved_by_team_id`.
* Index on (`item_id`, `created_at DESC`) for ordered history retrieval.
* GIN index on `content_tsv` for full-text search on content.

**Database Triggers:**
* A trigger on `teams` and `content_items` tables automatically updates the `updated_at` column on any row update.
* A trigger on `content_versions` automatically updates the `content_tsv` column from `markdown_content` on `INSERT` or `UPDATE`.

**Initial Data:**
* The `teams` table will be initialized with a record for `ADMIN_SYSTEM_TEAM_ID` ('04a9a4ec-18d8-4cfd-bead-d0ef99199e17') as per `init_db.sql`.

## 8. API Design (RESTful)

This section outlines the RESTful API exposed by the Backend API Service. The API is designed based on the functionalities identified in the `ulacm_backend/app/api/v1/api.py` and its constituent endpoint modules.

### 8.1 API Design Principles & Conventions
* **Base URL**: All API v1 endpoints are prefixed with `/api/v1`.
* **Authentication**:
    * Admin APIs (e.g., `/api/v1/admin/teams/*`) require a valid Admin session token (`admin_session_id` cookie).
    * Team User APIs (e.g., `/api/v1/items/*`, `/api/v1/auth/me`) require a valid Team User session token (`team_session_id` cookie).
    * Session tokens are JWTs managed via HTTP-only cookies.
* **Request/Response Format**: JSON is used for request and response bodies.
* **HTTP Methods**: Standard HTTP methods are used (GET, POST, PUT, DELETE).
* **Status Codes**: Standard HTTP status codes are used (200, 201, 204, 400, 401, 403, 404, 409, 422, 500).
* **Error Responses**: Error responses include a JSON body with a `detail` field (string or array of error objects for 422).
* **UUIDs**: Primary keys (`team_id`, `item_id`, `version_id`) are UUIDs (string representation).
* **Timestamps**: All timestamps (`created_at`, `updated_at`) are in ISO 8601 format with UTC timezone.
* **Pagination**: List endpoints support `offset` and `limit` query parameters. Responses include `total_count`, `offset`, `limit`, and the list of `items` or `teams`.
* **Rate Limiting**: Applied to sensitive endpoints like admin login (FR-SEC-004).

### 8.2 Authentication API
*Source*: `ulacm_backend/app/api/v1/endpoints/auth.py`

#### 8.2.1 Admin Login
* **Endpoint**: `POST /api/v1/admin/auth/login`
* **Description**: Authenticates the Administrator (FR-ADM-002).
* **Request Body**: `{ "password": "admin_password_string" }`
* **Success Response (200 OK)**: Sets `admin_session_id` cookie. Body: `{ "message": "Admin login successful." }`
* **Error Responses**: 400, 401, 429 (Rate Limit Exceeded).

#### 8.2.2 Team User Login
* **Endpoint**: `POST /api/v1/auth/login`
* **Description**: Authenticates a Team User (FR-AUTH-001).
* **Request Body**: `{ "username": "team_username_string", "password": "team_password_string" }`
* **Success Response (200 OK)**: Sets `team_session_id` cookie. Body: `TeamSchema` (see `ulacm_backend/app/schemas/team.py`).
* **Error Responses**: 400 (inactive account), 401.

#### 8.2.3 Logout
* **Endpoint (Team User)**: `POST /api/v1/auth/logout`
* **Endpoint (Admin)**: `POST /api/v1/admin/auth/logout`
* **Description**: Invalidates the current user's session (FR-AUTH-005). Clears the respective session cookie.
* **Success Response (200 OK)**: `{ "message": "Logout successful." }`

#### 8.2.4 Get Current Authenticated User
* **Endpoint (Team User)**: `GET /api/v1/auth/me`
* **Description**: Fetches details for the currently authenticated team user.
* **Success Response (200 OK)**: `TeamSchema`.
* **Error Responses**: 401.
* **Endpoint (Admin)**: `GET /api/v1/admin/auth/me`
* **Description**: Checks if the current session belongs to a valid administrator.
* **Success Response (200 OK)**: `{ "message": "Admin session is valid" }`.
* **Error Responses**: 401.

### 8.3 Admin API (Team Management)
*Source*: `ulacm_backend/app/api/v1/endpoints/admin_teams.py`
*All endpoints require Admin authentication.*

#### 8.3.1 Create Team
* **Endpoint**: `POST /api/v1/admin/teams`
* **Description**: Creates a new team account (FR-ADM-003).
* **Request Body**: `TeamCreate` schema (team_name, username, password).
* **Success Response (201 Created)**: `TeamSchema`.
* **Error Responses**: 400, 401, 409 (username/team_name conflict), 422.

#### 8.3.2 List Teams
* **Endpoint**: `GET /api/v1/admin/teams`
* **Description**: Retrieves a list of all team accounts (FR-ADM-004).
* **Query Parameters**: `offset`, `limit`.
* **Success Response (200 OK)**: `TeamListResponse` schema.
* **Error Responses**: 401.

#### 8.3.3 Get Team Details
* **Endpoint**: `GET /api/v1/admin/teams/{team_id}`
* **Description**: Retrieves details for a specific team account.
* **Success Response (200 OK)**: `TeamSchema`.
* **Error Responses**: 401, 404.

#### 8.3.4 Update Team
* **Endpoint**: `PUT /api/v1/admin/teams/{team_id}`
* **Description**: Updates an existing team account's details (FR-ADM-005). Username is not updatable.
* **Request Body**: `TeamUpdate` schema (optional team_name, password, is_active).
* **Success Response (200 OK)**: `TeamSchema`.
* **Error Responses**: 400, 401, 404, 409 (team_name conflict), 422.

#### 8.3.5 Deactivate Team
* **Endpoint**: `POST /api/v1/admin/teams/{team_id}/deactivate`
* **Description**: Deactivates a team account (FR-ADM-006).
* **Success Response (200 OK)**: `TeamSchema` (with `is_active: false`).
* **Error Responses**: 401, 404, 409 (already deactivated).

#### 8.3.6 Reactivate Team
* **Endpoint**: `POST /api/v1/admin/teams/{team_id}/reactivate`
* **Description**: Reactivates a previously deactivated team account (FR-ADM-007).
* **Success Response (200 OK)**: `TeamSchema` (with `is_active: true`).
* **Error Responses**: 401, 404, 409 (already active).

#### 8.3.7 Delete Team
* **Endpoint**: `DELETE /api/v1/admin/teams/{team_id}`
* **Description**: Permanently deletes a team account and its owned content (FR-ADM-008).
* **Success Response (200 OK)**: `{ "message": "Team '...' deleted successfully." }`. (Note: SRS v2.0 said 204, codebase returns 200 with Msg)
* **Error Responses**: 401, 404.

### 8.4 Content Item APIs
*Source*: `ulacm_backend/app/api/v1/endpoints/content_items.py`
*Most endpoints require Team User or Admin authentication based on context.*

#### 8.4.1 List Content Items
* **Endpoint**: `GET /api/v1/items`
* **Description**: Retrieves a list of content items (Documents, Templates, Workflows) accessible to the authenticated user/admin.
* **Query Parameters**: `item_type` (optional), `offset`, `limit`, `sort_by`, `sort_order`, `for_usage` (boolean, for teams listing T/W).
* **Success Response (200 OK)**: `ContentItemListResponse` schema (containing `ContentItemWithCurrentVersion` items).
* **Error Responses**: 401.

#### 8.4.2 Create Content Item
* **Endpoint**: `POST /api/v1/items`
* **Description**: Creates a new Document (by Team User from Template), or a new Template/Workflow (by Admin). (FR-CM-001, FR-CM-002).
* **Request Body**: `ContentItemCreate` schema (item_type, name, optional template_id for Documents, optional owner_team_id for Admin creating T/W - though backend uses `ADMIN_SYSTEM_TEAM_ID` for admin-created T/W).
* **Success Response (201 Created)**: `ContentItemSchema` (basic metadata of the created item).
* **Error Responses**: 400, 401, 403, 404 (template not found), 409 (name conflict), 422.

#### 8.4.3 Get Content Item Details
* **Endpoint**: `GET /api/v1/items/{item_id}`
* **Description**: Retrieves details for a specific content item, including the Markdown content of its current version (FR-CM-006).
* **Success Response (200 OK)**: `ContentItemWithCurrentVersion` schema.
* **Error Responses**: 401, 403, 404.

#### 8.4.4 Update Content Item Metadata
* **Endpoint**: `PUT /api/v1/items/{item_id}/meta`
* **Description**: Updates metadata (name, global visibility) of an existing content item.
* **Request Body**: `ContentItemUpdateMeta` schema (optional name, is_globally_visible).
* **Success Response (200 OK)**: `ContentItemSchema`.
* **Error Responses**: 400, 401, 403, 404, 409 (name conflict), 422.

#### 8.4.5 Delete Content Item
* **Endpoint**: `DELETE /api/v1/items/{item_id}`
* **Description**: Permanently deletes a content item and all its versions (FR-CM-008).
* **Success Response (200 OK)**: `{ "message": "Content item '...' deleted successfully." }`. (Note: SRS v2.0 said 204, codebase returns 200 with Msg)
* **Error Responses**: 401, 403, 404.

#### 8.4.6 Duplicate Content Item
* **Endpoint**: `POST /api/v1/items/{item_id}/duplicate`
* **Description**: Creates a new, independent copy of the specified content item (FR-DUP-001).
* **Request Body**: `ContentItemDuplicatePayload` schema (new_name, optional source_version_id, optional target_owner_team_id for admin).
* **Success Response (201 Created)**: `ContentItemWithCurrentVersion` schema for the new duplicated item.
* **Error Responses**: 400, 401, 403, 404, 409 (name conflict), 422.

### 8.5 Content Version APIs
*Source*: `ulacm_backend/app/api/v1/endpoints/versions.py`
*Endpoints require appropriate Team User or Admin authentication.*

#### 8.5.1 Save New Version
* **Endpoint**: `POST /api/v1/items/{item_id}/versions`
* **Description**: Saves new Markdown content as a new version of an existing content item (FR-VER-002).
* **Request Body**: `ContentVersionCreate` schema (`markdown_content`).
* **Success Response (201 Created)**: `SaveVersionResponse` schema (includes new version details and item's updated_at).
* **Error Responses**: 400 (invalid workflow definition if item_type is WORKFLOW), 401, 403, 404, 422.

#### 8.5.2 List Item Versions (History)
* **Endpoint**: `GET /api/v1/items/{item_id}/versions`
* **Description**: Retrieves the version history for a specific content item (FR-VER-004).
* **Query Parameters**: `offset`, `limit`, `sort_order` ('asc'/'desc' for version_number).
* **Success Response (200 OK)**: `ContentVersionListResponse` schema.
* **Error Responses**: 401, 403, 404.

#### 8.5.3 Get Specific Version Content
* **Endpoint**: `GET /api/v1/items/{item_id}/versions/{version_id}`
* **Description**: Retrieves the Markdown content and metadata of a specific version (FR-VER-005).
* **Success Response (200 OK)**: `ContentVersionDetails` schema.
* **Error Responses**: 401, 403, 404.

### 8.6 Search API
*Source*: `ulacm_backend/app/api/v1/endpoints/search.py`
*Requires Team User authentication.*

#### 8.6.1 Search Content Items
* **Endpoint**: `GET /api/v1/search`
* **Description**: Performs a search across accessible Documents, Templates, and Workflows (FR-SRCH-001).
* **Query Parameters**: `query` (text), `item_types` (comma-separated string), `created_after` (date), `created_before` (date), `offset`, `limit`.
* **Success Response (200 OK)**: `SearchResultsResponse` schema (containing `ContentItemSearchResult` items with snippets).
* **Error Responses**: 400, 401, 422.

### 8.7 Workflow Execution API
*Source*: `ulacm_backend/app/api/v1/endpoints/workflows_exec.py`
*Requires Team User authentication.*

#### 8.7.1 Run Workflow
* **Endpoint**: `POST /api/v1/workflows/{workflow_item_id}/run`
* **Description**: Manually triggers the execution of a specified, globally visible, Admin-created Process Workflow (FR-WFEX-001).
* **Success Response (200 OK)**: `RunWorkflowResponse` schema (includes message, output_document details, and llm_raw_response).
* **Error Responses**: 400 (workflow definition error, value error), 401, 403, 404, 500, 503 (Ollama service error).

## 9. Frontend Design

This section outlines the conceptual design for the Frontend Single-Page Application (SPA) of the Team Intelligence Platform (TIP).

### 9.1 Frontend Technology Choices
* **Primary Framework**: React with TypeScript.
    * *Reasoning*: Large ecosystem, strong community support, component-based architecture, good performance, and excellent for SPAs. TypeScript enhances code quality and maintainability. (PRD 3.3)
* **Styling**: Tailwind CSS.
    * *Reasoning*: Utility-first CSS framework for rapid UI development, consistency, and maintainability. (PRD 3.3)
* **State Management**:
    * Global State: React Context API (`AuthContext`) for authentication status and current user/team information.
    * Local/Feature State: React hooks (`useState`, `useEffect`, `useCallback`, `useMemo`).
    * *Reasoning*: Standard React patterns for managing state effectively.
* **Routing**: React Router (`react-router-dom`).
    * *Reasoning*: Standard routing library for React applications. (Codebase: `App.tsx`)
* **API Communication**: Axios.
    * *Reasoning*: Promise-based HTTP client with ease of use, automatic JSON parsing, and error handling capabilities. Configured in `services/apiClient.ts`. (Codebase: `services/apiClient.ts`)
* **Markdown Editor**: `react-simplemde-editor` (a wrapper for EasyMDE).
    * *Reasoning*: Provides a user-friendly Markdown editing experience with preview capabilities. (PRD 1.2, 4.4.2, Codebase: `components/content/ReactSimpleMDEEditor.tsx`)
* **Build Tool**: Vite.
    * *Reasoning*: Fast development server startup and build times. (Codebase: `vite.config.ts`)
* **UI Components**:
    * Icons: `lucide-react`.
    * Notifications (Toasts): `react-hot-toast`.
    * Custom components are built using React and styled with Tailwind CSS.
* **Form Handling**: Standard React controlled components with local state management.
* **Testing**:
    * Unit/Integration Tests: Jest with React Testing Library. (Codebase: `jest.config.js`)
    * E2E Tests: Cypress. (Codebase: `cypress.config.ts`)

### 9.2 Key UI Components and Views
The frontend is structured with layouts, pages (views), and reusable components, as seen in the `ulacm_frontend/src/` directory structure.

#### 9.2.1 Core Layout Components
* **`App.tsx`**: Root component, sets up `BrowserRouter`, `AuthProvider`, and defines routes.
* **`MainLayout.tsx`**: Standard layout for authenticated team users, includes a sidebar for navigation (Dashboard, Documents, Execute Workflows) and a header area.
* **`AdminLayout.tsx`**: Standard layout for authenticated administrators, includes a sidebar for navigation (Admin Dashboard, Team Management, Template Management, Workflow Management) and a header area.
* **`ProtectedRoute.tsx`**: Higher-order component to protect routes requiring team user authentication.
* **`AdminProtectedRoute.tsx`**: Higher-order component to protect routes requiring administrator authentication.

#### 9.2.2 Authentication Views
* **`LoginPage.tsx`**: Form for team username and password input (FR-AUTH-001).
* **`AdminLoginPage.tsx`**: Form for admin password input (FR-ADM-002).

#### 9.2.3 Admin Interface Views
* **`AdminDashboardPage.tsx`**: Main view for admin, links to management sections.
* **`TeamManagementPage.tsx`**: Displays list of teams, allows creation, editing, activation/deactivation, and deletion of teams (FR-ADM-003 to FR-ADM-008). Uses `TeamFormModal.tsx`.
* **`ContentListPage.tsx` (Admin Context)**: Reused to list Document Templates and Process Workflows. Allows navigation to create/edit these items. (FR-ADM-009, FR-ADM-010)
* **`EditorViewPage.tsx` (Admin Context)**: Reused for creating and editing Document Templates and Process Workflows by Admins. (FR-ADM-009, FR-ADM-010)

#### 9.2.4 Team User Interface Views
* **`TeamDashboardPage.tsx`**: Main landing page after team login. Provides overview and quick links.
* **`ContentListPage.tsx` (Team Context)**: Primarily lists Documents owned by the team or globally visible. Allows navigation to create/edit Documents. (FR-CM-001, FR-CM-005)
* **`EditorViewPage.tsx` (Team Context)**: Main view for creating/editing Documents.
    * Contains the `ReactSimpleMDEEditor` component (FR-EDIT-001).
    * Displays item name, version history, save button, and other actions like visibility toggle, duplication, deletion. (FR-VER-*, FR-SHARE-*, FR-DUP-*)
* **`ExecuteWorkflowPage.tsx`**: Lists globally visible, Admin-created Process Workflows for teams to execute. Displays workflow details (input selectors, output name template) and allows triggering execution. (FR-WFEX-001)
* **`SearchPage.tsx`**: Interface for search queries and displaying results across accessible Documents, Templates, and Workflows. (FR-SRCH-*)
* **`CreateDocumentModal.tsx`**: Modal dialog for team users to select a Document Template when creating a new Document. (FR-CM-001)
* **`RunWorkflowModal.tsx`**: Modal to display workflow execution status and results (LLM output, link to generated document). (FR-WFEX-003, FR-WFEX-005)
* **`NotFoundPage.tsx`**: Displays a 404 error message for invalid routes.

#### 9.2.5 Reusable UI Components
Located in `ulacm_frontend/src/components/common/` and `ulacm_frontend/src/components/content/`:
* `LoadingSpinner.tsx`
* `ConfirmationModal.tsx`
* `ReactSimpleMDEEditor.tsx`
* Buttons, input fields, and other UI elements are typically styled directly with Tailwind CSS within their respective components/pages.

### 9.3 State Management
* **Global Authentication State**: Managed by `AuthContext` (`ulacm_frontend/src/contexts/AuthContext.tsx`). Provides `currentTeam`, `isAuthenticated`, `isAdminAuthenticated`, `isLoading`, `error`, and auth-related functions (`teamLogin`, `adminLogin`, `logout`, `checkSession`).
* **Local Component State**: Handled using React hooks (`useState`, `useEffect`, etc.) within individual components for form data, UI states (modal visibility, loading flags), and editor content.
* **Server Cache / Data Fetching State**: API calls are managed via services (`contentService.ts`, `adminService.ts`) which use `axios`. Loading and error states for these calls are typically managed within the components that trigger them. There is no explicit client-side caching layer like React Query or SWR in the current codebase, meaning data is refetched as needed.

### 9.4 Routing
Routing is managed by `react-router-dom` in `App.tsx`. Key routes include:
* `/login`: `LoginPage`
* `/admin/login`: `AdminLoginPage`
* Protected Admin Routes (`/admin/*`):
    * `/admin/dashboard`: `AdminDashboardPage`
    * `/admin/teams`: `TeamManagementPage`
    * `/admin/templates`: `ContentListPage` (context for Templates)
    * `/admin/templates/new`: `EditorViewPage` (context for new Template)
    * `/admin/templates/:itemId`: `EditorViewPage` (context for existing Template)
    * `/admin/workflows`: `ContentListPage` (context for Workflows)
    * `/admin/workflows/new`: `EditorViewPage` (context for new Workflow)
    * `/admin/workflows/:itemId`: `EditorViewPage` (context for existing Workflow)
* Protected Team User Routes (`/app/*`):
    * `/app/dashboard`: `TeamDashboardPage`
    * `/app/documents`: `ContentListPage` (context for Documents)
    * `/app/documents/:itemId`: `EditorViewPage` (context for Documents)
    * `/app/execute-workflow`: `ExecuteWorkflowPage`
    * `/app/search`: `SearchPage`
* Redirects and a catch-all `NotFoundPage` are also implemented.

## 10. File Tree Structure

This section provides a conceptual overview of the project's file structure, based on the provided `ULACM_Codebase.txt`.

### 10.1 Backend File Structure (FastAPI/Python)

Located under `Team Intelligence Platform/ulacm_backend/`:

```
ulacm_backend/
├── app/                                # Main application package
│   ├── __init__.py
│   ├── api/                            # API endpoint definitions (routers)
│   │   ├── __init__.py
│   │   └── v1/                         # API version 1
│   │       ├── __init__.py
│   │       ├── api.py                  # Main v1 API router, includes sub-routers
│   │       ├── deps.py                 # API dependencies (e.g., get_current_user)
│   │       └── endpoints/              # Routers for different resources
│   │           ├── __init__.py
│   │           ├── admin_teams.py      # Admin team management endpoints
│   │           ├── auth.py             # Authentication endpoints
│   │           ├── content_items.py    # Documents, Templates, Workflows CRUD
│   │           ├── search.py           # Search endpoint
│   │           ├── versions.py         # Content versioning endpoints
│   │           └── workflows_exec.py   # Workflow execution endpoint
│   ├── core/                           # Core application settings and utilities
│   │   ├── __init__.py
│   │   ├── config.py                   # Application configuration (Pydantic BaseSettings)
│   │   ├── limiter.py                  # Rate limiter configuration (slowapi)
│   │   ├── logging_config.py           # Logging setup
│   │   └── security.py                 # Password hashing, JWT management
│   ├── crud/                           # Create, Read, Update, Delete operations
│   │   ├── __init__.py
│   │   ├── base.py                     # Base CRUD class
│   │   ├── crud_content_item.py
│   │   ├── crud_content_version.py
│   │   ├── crud_search.py
│   │   └── crud_team.py
│   ├── db/                             # Database setup and ORM models
│   │   ├── __init__.py
│   │   ├── base_class.py               # SQLAlchemy Base declarative class
│   │   ├── database.py                 # Database engine and session factory
│   │   └── models/                     # SQLAlchemy ORM models
│   │       ├── __init__.py
│   │       ├── content_item.py
│   │       ├── content_version.py
│   │       └── team.py
│   ├── schemas/                        # Pydantic schemas for API request/response validation
│   │   ├── __init__.py
│   │   ├── content_item.py
│   │   ├── content_version.py
│   │   ├── msg.py                      # Simple message schema
│   │   ├── team.py
│   │   ├── token.py
│   │   └── workflow_definition.py      # Schema for Process Workflow structure
│   ├── services/                       # Business logic services
│   │   ├── __init__.py
│   │   ├── ollama_service.py           # Client for interacting with Ollama
│   │   ├── workflow_parser.py          # For parsing workflow definition YAML
│   │   └── workflow_service.py         # Logic for executing workflows
│   └── main.py                         # FastAPI application instance and main setup
├── Dockerfile                          # For building the backend Docker image
├── init_db.sql                         # SQL script for database schema initialization
├── postgres_conf/
│   └── pg_hba.conf                     # PostgreSQL host-based authentication config
├── pyproject.toml                      # Project metadata and dependencies (Poetry)
└── tests/                              # Automated tests
    ├── __init__.py
    ├── api/
    │   ├── __init__.py
    │   └── test_main.py                # Basic API tests
    ├── conftest.py                     # Pytest fixtures
    ├── core/
    │   └── test_security.py
    ├── crud/
    │   ├── test_crud_content_item.py
    │   ├── test_crud_content_version.py
    │   ├── test_crud_search.py
    │   └── test_crud_team.py
    ├── db/
    │   └── test_models.py
    └── services/
        ├── __init__.py
        ├── test_ollama_service.py
        ├── test_workflow_parser.py
        └── test_workflow_service.py
```

### 10.2 Frontend File Structure (React/Vite/TypeScript)

Located under `Team Intelligence Platform/ulacm_frontend/`:

```
ulacm_frontend/
├── Dockerfile                          # For building the frontend Docker image (Nginx)
├── __mocks__/
│   └── fileMock.js                     # Jest mock for static files
├── cypress/                            # Cypress E2E tests
│   └── e2e/
│       ├── admin_team_management.cy.ts
│       └── login.cy.ts
├── cypress.config.ts                   # Cypress configuration
├── index.html                          # Main HTML entry point for Vite
├── jest.config.js                      # Jest configuration
├── jest.setup.js                       # Jest setup file
├── nginx.conf                          # Nginx configuration for serving the SPA
├── package.json                        # Project metadata and dependencies (npm/yarn/pnpm)
├── postcss.config.js                   # PostCSS configuration (for Tailwind CSS)
├── public/                             # Static assets directly copied to build output
│   └── tip-logo-*.png                  # Application logos/favicons
├── src/                                # Source code
│   ├── App.tsx                         # Main application component (routing setup)
│   ├── components/                     # Reusable UI components
│   │   ├── admin/
│   │   │   └── TeamFormModal.tsx
│   │   ├── common/                     # General purpose components
│   │   │   ├── AdminProtectedRoute.tsx
│   │   │   ├── ConfirmationModal.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   └── content/                    # Components related to content items
│   │       ├── CreateDocumentModal.tsx
│   │       ├── ReactSimpleMDEEditor.tsx # EasyMDE wrapper
│   │       └── RunWorkflowModal.tsx
│   ├── contexts/                       # React Context providers
│   │   └── AuthContext.tsx
│   ├── index.css                       # Global styles and Tailwind directives
│   ├── layouts/                        # Layout components
│   │   ├── AdminLayout.tsx
│   │   └── MainLayout.tsx
│   ├── main.tsx                        # Application entry point (renders App.tsx)
│   ├── pages/                          # Top-level view components for routes
│   │   ├── AdminLoginPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── NotFoundPage.tsx
│   │   ├── admin/
│   │   │   ├── AdminDashboardPage.tsx
│   │   │   └── TeamManagementPage.tsx
│   │   └── team/
│   │       ├── ContentListPage.tsx
│   │       ├── EditorViewPage.tsx
│   │       ├── ExecuteWorkflowPage.tsx
│   │       ├── SearchPage.tsx
│   │       └── TeamDashboardPage.tsx
│   ├── services/                       # API service clients
│   │   ├── adminService.ts
│   │   ├── apiClient.ts                # Axios instance setup
│   │   └── contentService.ts
│   ├── types/                          # TypeScript type definitions
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── content.ts
│   └── utils/                          # Utility functions and constants
│       └── constants.ts
├── tailwind.config.js                  # Tailwind CSS configuration
├── tsconfig.json                       # TypeScript compiler options
└── vite.config.ts                      # Vite build tool configuration
```

### 10.3 Docker Configuration Files
* **`Team Intelligence Platform/docker-compose.yml`**: Defines and orchestrates the multi-container application (frontend, backend, db, optionally ollama). Manages services, networks, volumes, and environment variables.
* **`Team Intelligence Platform/ulacm_backend/Dockerfile`**: Defines steps to build the Docker image for the backend FastAPI application.
* **`Team Intelligence Platform/ulacm_frontend/Dockerfile`**: Defines steps to build the Docker image for the frontend React application (builds static assets and serves them with Nginx).
* **`Team Intelligence Platform/ulacm_frontend/nginx.conf`**: Nginx configuration used by the frontend Docker image to serve static files and proxy API requests.
* **`Team Intelligence Platform/ulacm_backend/postgres_conf/pg_hba.conf`**: PostgreSQL client authentication configuration file, typically mounted into the PostgreSQL container if custom rules are needed (though default image behavior might suffice for Docker networking).
* **`Team Intelligence Platform/ulacm_backend/init_db.sql`**: SQL script used by the PostgreSQL service in `docker-compose.yml` to initialize the database schema on first run.

## 11. Detailed Module Designs

This section provides a more detailed look into the design of key backend and frontend modules. It outlines their purpose, responsibilities, key functions/methods, and interactions, based on the existing codebase.

### 11.1 Backend Modules (FastAPI/Python)

#### 11.1.1 Authentication & Authorization Module
* **Location**: `ulacm_backend/app/core/security.py`, `ulacm_backend/app/api/v1/deps.py`, `ulacm_backend/app/api/v1/endpoints/auth.py`
* **Purpose**: Handles user and admin authentication, password management, JWT generation/validation, and dependency injection for authenticated user objects.
* **Key Responsibilities & Functions**:
    * **`core/security.py`**:
        * `get_password_hash(password: str) -> str`: Hashes passwords using bcrypt.
        * `verify_password(plain_password: str, hashed_password: str) -> bool`: Verifies plain password against a hash.
        * `create_access_token(...) -> str`: Creates JWTs for sessions.
        * `decode_token(token: str) -> Optional[TokenPayload]`: Decodes and validates JWTs.
        * `verify_admin_password(password: str) -> bool`: Verifies the admin password against the configured one.
    * **`api/v1/deps.py`**:
        * `get_current_team_user(...) -> TeamModel`: FastAPI dependency to get the authenticated team user from the `team_session_id` cookie. Raises HTTP 401/403/404 if invalid.
        * `get_current_admin_user(...) -> TokenPayload`: FastAPI dependency to verify an admin user from the `admin_session_id` cookie. Raises HTTP 401/403 if invalid.
        * `get_current_user_or_admin_marker(...)`: Dependency to identify if the request is from an admin or a team user.
        * `ensure_admin_user(...)`: Dependency that strictly requires an admin user.
    * **`api/v1/endpoints/auth.py`**:
        * Defines `/auth/login` (team), `/auth/logout` (team), `/admin/auth/login` (admin), `/admin/auth/logout` (admin), `/auth/me` (team), `/admin/auth/me` (admin) endpoints.
* **Interactions**:
    * Uses `app.core.config` for `SESSION_SECRET_KEY`, token expiry, `ADMIN_PASSWORD`, `ADMIN_USERNAME`.
    * Interacts with `crud_team` to fetch team details during token validation.
    * Uses Pydantic schemas from `app.schemas.token` and `app.schemas.team`.

#### 11.1.2 Team Management Module
* **Location**: `ulacm_backend/app/crud/crud_team.py`, `ulacm_backend/app/api/v1/endpoints/admin_teams.py`
* **Purpose**: Handles business logic and data access for Team User account management by Administrators.
* **Key Functions (`crud_team.py`)**:
    * `create(db: AsyncSession, *, obj_in: TeamCreate) -> TeamModel`: Creates a new team.
    * `get_by_id(db: AsyncSession, *, team_id: UUID4) -> Optional[TeamModel]`: Retrieves a team by ID.
    * `get_by_username(db: AsyncSession, *, username: str) -> Optional[TeamModel]`: Retrieves a team by username.
    * `get_by_team_name(db: AsyncSession, *, team_name: str) -> Optional[TeamModel]`: Retrieves a team by team name.
    * `get_all_teams(db: AsyncSession, *, skip: int, limit: int) -> Tuple[List[TeamModel], int]`: Retrieves a paginated list of teams (excluding `ADMIN_SYSTEM_TEAM_ID`).
    * `update(db: AsyncSession, *, db_obj: TeamModel, obj_in: TeamUpdate) -> TeamModel`: Updates team details.
    * `activate_deactivate_team(db: AsyncSession, *, team: TeamModel, is_active: bool) -> TeamModel`: Sets the `is_active` status.
    * `remove_team(db: AsyncSession, *, team_id: UUID4) -> Optional[TeamModel]`: Deletes a team (cannot delete `ADMIN_SYSTEM_TEAM_ID`).
* **API Layer (`admin_teams.py`)**: Exposes CRUD functions via REST endpoints, handles request/response serialization (Pydantic schemas), and ensures admin authentication using `get_current_admin_user`.
* **Interactions**:
    * Uses `app.db.database` for `AsyncSession`.
    * Uses `app.db.models.team.Team` for ORM operations.
    * Uses `app.schemas.team` for data validation/serialization.
    * Uses `app.core.security.get_password_hash` for password updates.
    * Uses `app.core.config.settings.ADMIN_SYSTEM_TEAM_ID`.

#### 11.1.3 Content Item Management Module
* **Location**: `ulacm_backend/app/crud/crud_content_item.py`, `ulacm_backend/app/api/v1/endpoints/content_items.py`
* **Purpose**: Handles business logic and data access for Documents, Templates, and Workflows (metadata, ownership, visibility, duplication).
* **Key Functions (`crud_content_item.py`)**:
    * `create_item_for_team_or_admin(...) -> ContentItemModel`: Creates a new `ContentItem`.
        * For Documents: Takes `template_id`, copies content from the template to create the first version. Owner is the acting team.
        * For Templates/Workflows: Owner is `ADMIN_SYSTEM_TEAM_ID`. Initial content is set by frontend via first version save.
    * `get_by_id(db: AsyncSession, *, item_id: UUID4) -> Optional[ContentItemModel]`: Retrieves an item by ID, eagerly loading current version and owner/saving teams.
    * `get_items_for_team_or_admin(...) -> Tuple[List[ContentItemModel], int]`: Lists items based on user role, ownership, global visibility, and filters.
    * `check_name_uniqueness(...) -> bool`: Checks if an item name is unique for a given owner and type.
    * `update_item_meta_for_owner_or_admin(...) -> Optional[ContentItemModel]`: Updates item's name or `is_globally_visible` flag.
    * `remove_item_for_owner_or_admin(...) -> Optional[ContentItemModel]`: Deletes an item and its versions (cascades).
    * `duplicate_item_logic(...) -> ContentItemModel`: Duplicates an item, creating a new item and copying content from the source's current or specified version to the new item's first version.
* **API Layer (`content_items.py`)**: Exposes CRUD via REST, handles Pydantic schemas, and uses `get_current_user_or_admin_marker` for authentication and authorization.
* **Interactions**:
    * `crud_content_version` for version creation during item creation/duplication.
    * `app.db.models.content_item.ContentItem`.
    * `app.schemas.content_item`.
    * `app.core.config.settings.ADMIN_SYSTEM_TEAM_ID`.

#### 11.1.4 Versioning Module
* **Location**: `ulacm_backend/app/crud/crud_content_version.py`, `ulacm_backend/app/api/v1/endpoints/versions.py`
* **Purpose**: Manages the creation and retrieval of `ContentVersion` records.
* **Key Functions (`crud_content_version.py`)**:
    * `create_new_version(db: AsyncSession, *, item_id: UUID4, version_in: ContentVersionCreate, saved_by_team_id: UUID4, is_initial_version: bool = False) -> ContentVersionModel`:
        * Determines the next `version_number`.
        * Creates a new `ContentVersion` record.
        * Updates `current_version_id` and `updated_at` on the parent `ContentItem` in the same transaction.
    * `get_by_id(db: AsyncSession, *, version_id: UUID4) -> Optional[ContentVersionModel]`: Retrieves a specific version.
    * `get_versions_for_item(...) -> Tuple[List[ContentVersionModel], int]`: Lists versions for an item, paginated and sorted.
    * `get_specific_version_by_number(...) -> Optional[ContentVersionModel]`: Retrieves a version by its number for a given item.
* **API Layer (`versions.py`)**: Exposes endpoints for saving new versions, listing versions, and getting specific version content.
* **Interactions**:
    * `app.db.models.content_version.ContentVersion`, `app.db.models.content_item.ContentItem`.
    * `app.schemas.content_version`.
    * `app.core.config.settings.ADMIN_SYSTEM_TEAM_ID` (for `saved_by_team_id`).
    * `app.services.workflow_parser` (to validate workflow definition on save if item is a workflow).

#### 11.1.5 Workflow Engine Module
* **Location**: `ulacm_backend/app/services/workflow_service.py`, `ulacm_backend/app/services/workflow_parser.py`, `ulacm_backend/app/services/ollama_service.py`, `ulacm_backend/app/api/v1/endpoints/workflows_exec.py`
* **Purpose**: Orchestrates the definition, parsing, and execution of Process Workflows.
* **Key Components & Functions**:
    * **`services/ollama_service.py` (`OllamaService`)**:
        * `generate(prompt: str) -> str`: Makes HTTP POST request to the configured Ollama server's `/api/generate` endpoint using the globally configured `OLLAMA_MODEL` and `OLLAMA_TEMPERATURE`. Strips `<think>` tags and leading/trailing newlines from the response. Handles errors and timeouts.
    * **`services/workflow_parser.py` (`WorkflowDefinitionParser`, `ValidatedWorkflowDefinition`)**:
        * `parse_and_validate(workflow_content_str: str) -> ValidatedWorkflowDefinition`: Parses the YAML-like string from a Workflow's content into a `ValidatedWorkflowDefinition` Pydantic model. Validates required fields (`inputDocumentSelectors`, `outputName`, `prompt`), `inputDateSelector` format, and trigger type.
    * **`services/workflow_service.py`**:
        * `execute_workflow(db: AsyncSession, workflow_item: ContentItemModel, executing_team_id: UUID4) -> Tuple[ContentItemModel, str]`:
            1.  Parses the workflow definition from `workflow_item.current_version.markdown_content`.
            2.  `_select_input_documents(...)`: Finds accessible documents matching `inputDocumentSelectors` and `inputDateSelector`.
            3.  `_construct_prompt(...)`: Populates placeholders in the prompt template.
            4.  Calls `ollama_service_instance.generate()`.
            5.  `_generate_output_name(...)` and `_ensure_unique_output_name(...)`: Generates and ensures a unique name for the output document.
            6.  Creates a new Document `ContentItem` and its first `ContentVersion` with the LLM response, owned by `executing_team_id`.
* **API Layer (`workflows_exec.py`)**: Provides the `/workflows/{workflow_item_id}/run` endpoint for team users to trigger workflow execution.
* **Interactions**:
    * `crud_content_item` and `crud_content_version` for data access.
    * `OllamaService` for LLM interaction.
    * Pydantic schemas for workflow definition.

#### 11.1.6 Search Module
* **Location**: `ulacm_backend/app/crud/crud_search.py`, `ulacm_backend/app/api/v1/endpoints/search.py`
* **Purpose**: Provides full-text search functionality across content items.
* **Key Functions (`crud_search.py`)**:
    * `search_content_items_complex(...) -> Tuple[List[Tuple[ContentItemModel, Optional[str]]], int]`:
        * Constructs dynamic SQL queries using SQLAlchemy.
        * Filters by `team_id` (owner) OR `is_globally_visible = TRUE`, and by `item_type` and date filters if provided.
        * Uses PostgreSQL FTS functions (`to_tsvector`, `plainto_tsquery`, `ts_rank_cd`, `ts_headline`) on `ContentVersion.content_tsv` (for content) and `ContentItem.name`.
        * Returns a list of `ContentItemModel` objects and their corresponding search snippets, along with the total count.
* **API Layer (`search.py`)**: Exposes the `/search` endpoint.
* **Interactions**:
    * `app.db.models.content_item.ContentItem`, `app.db.models.content_version.ContentVersion`.
    * `app.schemas.content_item.ContentItemSearchResult`, `app.schemas.content_item.SearchResultsResponse`.

### 11.2 Frontend Modules (React/TypeScript)

#### 11.2.1 Authentication Service & Context
* **Location**: `ulacm_frontend/src/services/apiClient.ts`, `ulacm_frontend/src/contexts/AuthContext.tsx`
* **Purpose**: Manage client-side authentication state and API interactions for login/logout.
* **`services/apiClient.ts`**:
    * Configures an `axios` instance with `baseURL`, `withCredentials: true`, and a response interceptor for global error handling (including 401 redirects and toast notifications).
* **`contexts/AuthContext.tsx`**:
    * **State**: `isAuthenticated`, `isAdminAuthenticated`, `currentTeam`, `isLoading`, `error`.
    * **Functions**: `teamLogin`, `adminLogin`, `logout`, `checkSession`. `checkSession` calls `/auth/me` and `/admin/auth/me` to determine initial auth state.
    * **Purpose**: Provides global authentication state and methods to the application.
* **Interactions**:
    * Uses `apiClient` for API calls.
    * Consumed by `App.tsx`, `ProtectedRoute.tsx`, `AdminProtectedRoute.tsx`, login pages, and layout components.

#### 11.2.2 Content Service
* **Location**: `ulacm_frontend/src/services/contentService.ts`
* **Purpose**: Handles all API interactions related to ContentItems (Documents, Templates, Workflows) and their versions, and search.
* **Key Functions (all return Promises with typed responses)**:
    * `getItems(params)`: GET `/items` (lists items).
    * `createItem(itemData)`: POST `/items` (creates item metadata).
    * `getItemDetails(itemId)`: GET `/items/{itemId}`.
    * `updateItemMeta(itemId, metaData)`: PUT `/items/{itemId}/meta`.
    * `deleteItem(itemId)`: DELETE `/items/{itemId}`.
    * `duplicateItem(itemId, payload)`: POST `/items/{itemId}/duplicate`.
    * `saveNewVersion(itemId, payload)`: POST `/items/{itemId}/versions`.
    * `listVersions(itemId, params)`: GET `/items/{itemId}/versions`.
    * `getVersionContent(itemId, versionId)`: GET `/items/{itemId}/versions/{versionId}`.
    * `searchItems(params)`: GET `/search`.
    * `runWorkflow(workflowItemId)`: POST `/workflows/{workflowItemId}/run`.
* **Interactions**: Uses `apiClient`. Called by pages like `ContentListPage.tsx`, `EditorViewPage.tsx`, `ExecuteWorkflowPage.tsx`, `SearchPage.tsx`.

#### 11.2.3 Workflow Service
*Note: In the current codebase, workflow execution (`runWorkflow`) is part of `contentService.ts`. If it were a separate module, it would be located at `ulacm_frontend/src/services/workflowService.ts`.*
* **Purpose**: Specifically for Process Workflow execution API calls.
* **Key Functions**:
    * `runWorkflow(workflowItemId: string): Promise<RunWorkflowResponse>`: POSTs to `/api/v1/workflows/{workflowItemId}/run`.
* **Interactions**: Uses `apiClient`. Called from `ExecuteWorkflowPage.tsx` and potentially `EditorViewPage.tsx` (for Admin test runs).

#### 11.2.4 Markdown Editor Component
* **Location**: `ulacm_frontend/src/components/content/ReactSimpleMDEEditor.tsx`
* **Purpose**: Provides the EasyMDE Markdown editing experience.
* **Props**: `value` (string), `onChange` (function), `editable` (boolean), `placeholder` (string).
* **Internal Logic**:
    * Wraps `react-simplemde-editor`.
    * Configures EasyMDE options (toolbar, status bar, placeholder).
    * Manages the editor instance and updates its `readOnly` state based on the `editable` prop.
    * Implements a debounced `onChange` handler.
* **Interactions**: Used within `EditorViewPage.tsx`.

#### 11.2.5 Editor View Page/Component
* **Location**: `ulacm_frontend/src/pages/team/EditorViewPage.tsx`
* **Purpose**: Central page for viewing, creating, and editing Documents, Templates, or Workflows.
* **Key State**: `itemDetails`, `editorItemType`, `newItemName` (for new items), `editorContent`, `isDirty`, `isLoading`, `isSaving`, `error`, `versionHistory`, `loadedVersionNumber`.
* **Key Functions/Event Handlers**:
    * `useEffect` hooks to load item details/version history or set up for new item creation based on route parameters (`:itemId` or `/new`) and user role.
    * `handleEditorChange(markdownContent)`: Updates `editorContent` and `isDirty` state.
    * `handleSave()`:
        * If creating a new item: Calls `contentService.createItem` then `contentService.saveNewVersion`. Navigates to the new item's edit page.
        * If updating an existing item: Calls `contentService.saveNewVersion`. Updates local state and version history.
    * `loadVersion(versionId)`: Loads content of a specific historical version into the editor.
    * `handleToggleVisibility()`: Calls `contentService.updateItemMeta`.
    * `handleDuplicate()`: Prompts for new name, calls `contentService.duplicateItem`.
    * `handleDelete()`: Shows confirmation modal, then calls `contentService.deleteItem`.
    * `handleRunWorkflow()` (Admin only, for Workflows): Shows `RunWorkflowModal`, calls `contentService.runWorkflow`.
* **Interactions**:
    * Uses `contentService` extensively.
    * Renders `ReactSimpleMDEEditor`.
    * Displays item metadata, version history, and action buttons.
    * Uses `useAuth` for user/admin context and permissions.
    * Interacts with `ConfirmationModal` and `RunWorkflowModal`.
