# Software Requirements Specification (SRS)
# Team Intelligence Platform (TIP) - Phase 1: The Cognitive Foundation

**Version:** 1.0  
**Date:** April 12, 2025  
**Status:** Draft  
**Author:** Engineering Team, Heidemann Consulting  
**License:** Apache 2.0

---

## Table of Contents
1. [Introduction](#1-introduction)
   1. [Purpose](#11-purpose)
   2. [Scope](#12-scope)
   3. [Definitions, Acronyms, and Abbreviations](#13-definitions-acronyms-and-abbreviations)
   4. [References](#14-references)
   5. [Overview](#15-overview)
2. [System Description](#2-system-description)
   1. [System Context](#21-system-context)
   2. [Product Features](#22-product-features)
   3. [User Characteristics](#23-user-characteristics)
   4. [Constraints](#24-constraints)
   5. [Assumptions and Dependencies](#25-assumptions-and-dependencies)
3. [System Architecture](#3-system-architecture)
   1. [Architectural Overview](#31-architectural-overview)
   2. [Component Diagram](#32-component-diagram)
   3. [Deployment Options](#33-deployment-options)
   4. [Data Flow](#34-data-flow)
   5. [Integration Points](#35-integration-points)
4. [System Requirements](#4-system-requirements)
   1. [Functional Requirements](#41-functional-requirements)
   2. [Non-Functional Requirements](#42-non-functional-requirements)
5. [Component Specifications](#5-component-specifications)
   1. [LLM Runtime & Interface](#51-llm-runtime--interface)
   2. [Knowledge Management](#52-knowledge-management)
   3. [Collaboration Tools](#53-collaboration-tools)
   4. [Workflow Automation](#54-workflow-automation-optional)
   5. [Integration Layer](#55-integration-layer)
6. [Data Specifications](#6-data-specifications)
   1. [Knowledge Structure](#61-knowledge-structure)
   2. [Template Formats](#62-template-formats)
   3. [Prompt Library](#63-prompt-library)
   4. [Data Flow Specifications](#64-data-flow-specifications)
7. [Installation and Setup](#7-installation-and-setup)
   1. [Prerequisites](#71-prerequisites)
   2. [Installation Script](#72-installation-script)
   3. [Docker Deployment](#73-docker-deployment)
   4. [Configuration](#74-configuration)
8. [First-Time Setup Guide](#8-first-time-setup-guide)
   1. [Knowledge Repository Setup](#81-knowledge-repository-setup)
   2. [Team Ritual Implementation](#82-team-ritual-implementation)
   3. [Initial Prompt Library](#83-initial-prompt-library)
   4. [Workflow Integration](#84-workflow-integration)
9. [Testing Requirements](#9-testing-requirements)
   1. [Component Testing](#91-component-testing)
   2. [Integration Testing](#92-integration-testing)
   3. [User Acceptance Testing](#93-user-acceptance-testing)
10. [Security Considerations](#10-security-considerations)
    1. [Authentication and Authorization](#101-authentication-and-authorization)
    2. [Data Privacy](#102-data-privacy)
    3. [Network Security](#103-network-security)
11. [Appendices](#11-appendices)
    1. [Ritual Templates](#111-ritual-templates)
    2. [Knowledge Organization Templates](#112-knowledge-organization-templates)
    3. [Common Prompts Library](#113-common-prompts-library)
    4. [Docker Compose Configuration](#114-docker-compose-configuration)
    5. [Troubleshooting Guide](#115-troubleshooting-guide)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document defines the functional, non-functional, and technical requirements for Phase 1 of the Team Intelligence Platform (TIP) - "The Cognitive Foundation." This document is intended for software engineers, DevOps engineers, and technical team members implementing TIP, as well as AI-based software engineering agents that may assist in development.

The SRS outlines a complete and detailed specification for building a deployable solution that enables teams to implement AI Co-Management practices in Phase 1, establishing foundational practices for capturing, preserving, and leveraging team knowledge with basic AI assistance.

### 1.2 Scope

This SRS covers:

- Phase 1 core functionality implementation
- Component architecture and interactions
- Data structures and knowledge organization
- Installation and configuration procedures
- First-time setup guidance

Phase 1 focuses on establishing the Cognitive Foundation through three core rituals:
1. Context Curation (daily and weekly knowledge management)
2. Prompt Development Workshop (bi-weekly prompt engineering)
3. AI-Assisted Documentation (enhanced meeting documentation)

Future phases (Phase 2: Collaborative Acceleration and Phase 3: Transformative Intelligence) are out of scope for this document.

### 1.3 Definitions, Acronyms, and Abbreviations

| Term/Acronym | Definition |
|--------------|------------|
| TIP | Team Intelligence Platform |
| AI | Artificial Intelligence |
| LLM | Large Language Model |
| Ollama | Open-source LLM runtime for local deployment |
| Open-webui | User interface for interacting with Ollama |
| Obsidian | Markdown-based knowledge management system |
| HedgeDoc | Collaborative markdown editor |
| LangFlow | Visual workflow builder for LLM processes |
| AI Co-Management | A paradigm where AI becomes an integrated team member contributing to collective intelligence |
| Context Curation | A ritual for systematically capturing team knowledge |
| Prompt Development | A ritual for creating and refining LLM prompts |

### 1.4 References

1. TIP Product Requirements Document (PRD) - Phase 1
2. TIP Rituals and Practices Guide - Phase 1
3. Obsidian Documentation: [https://help.obsidian.md/](https://help.obsidian.md/)
4. Ollama Documentation: [https://ollama.ai/docs](https://ollama.ai/docs)
5. HedgeDoc Documentation: [https://docs.hedgedoc.org/](https://docs.hedgedoc.org/)
6. LangFlow Documentation: [https://github.com/logspace-ai/langflow](https://github.com/logspace-ai/langflow)
7. Open-webui Documentation: [https://github.com/open-webui/open-webui](https://github.com/open-webui/open-webui)

### 1.5 Overview

The remainder of this SRS is organized as follows:

- Section 2 provides a high-level system description, including context, features, and constraints
- Section 3 details the system architecture, component interactions, and deployment options
- Section 4 defines the functional and non-functional requirements
- Section 5 specifies individual component requirements
- Section 6 details data specifications and knowledge structures
- Section 7 provides installation and setup procedures
- Section 8 offers guidance for first-time setup
- Section 9 outlines testing requirements
- Section 10 addresses security considerations
- Section 11 contains appendices with templates, scripts, and additional resources

## 2. System Description

### 2.1 System Context

The Team Intelligence Platform (TIP) operates within the context of product development teams seeking to integrate AI into their collaborative workflows. Unlike traditional approaches where AI is used as an individual productivity tool, TIP enables "AI Co-Management" – a paradigm where AI becomes an integrated team member contributing to collective intelligence.

TIP is designed to work alongside existing team tools and processes, enhancing them with AI capabilities rather than replacing them. It is built entirely on open-source components to maximize accessibility and customization.

### 2.2 Product Features

Phase 1 of TIP implements the following key features:

1. **Knowledge Management System**
   - Structured team knowledge repository using Obsidian and Git
   - Version-controlled knowledge assets
   - Linked document network
   - Searchable knowledge base

2. **AI Interaction Framework**
   - Local LLM deployment with Ollama
   - User interface for AI interaction with Open-webui
   - Prompt development and management
   - AI output processing workflows

3. **Collaboration Enhancement**
   - Collaborative documentation with HedgeDoc
   - AI-assisted meeting notes and summaries
   - Shared context across team members
   - Knowledge continuity during personnel changes

4. **Team Ritual Support**
   - Templates for Context Curation
   - Frameworks for Prompt Development
   - Processes for AI-Assisted Documentation
   - Guidance for effective ritual execution

### 2.3 User Characteristics

TIP Phase 1 is designed for the following user personas:

1. **Product Owner/Project Manager**
   - Goals: Deliver maximum value, maintain alignment, reduce ambiguity
   - Technical proficiency: Moderate
   - System usage: Documentation review, context reference, ritual participation

2. **Scrum Master/Team Lead**
   - Goals: Optimize team performance, reduce coordination overhead
   - Technical proficiency: Moderate
   - System usage: Ritual facilitation, knowledge organization, process improvement

3. **Developer/Engineer**
   - Goals: Focus on challenging problems, reduce repetitive tasks
   - Technical proficiency: High
   - System usage: Knowledge contribution, AI interaction, technical documentation

4. **Designer/UX Professional**
   - Goals: Maintain design consistency, access relevant feedback
   - Technical proficiency: Moderate
   - System usage: Design context documentation, process documentation

5. **IT Administrator**
   - Goals: Maintain security, enable innovation
   - Technical proficiency: High
   - System usage: System deployment, configuration, monitoring

### 2.4 Constraints

1. **Technical Constraints**
   - Local LLM performance limited by available hardware
   - Manual integration between components in Phase 1
   - Network constraints in corporate environments
   - Limited customization of third-party components

2. **Organizational Constraints**
   - Team adoption rates and change management
   - Integration with existing tools and processes
   - Time allocation for ritual execution
   - Knowledge management discipline and consistency

3. **Data Constraints**
   - Limited import/export capabilities between components
   - Manual synchronization requirements
   - Potential version control conflicts
   - Context limitations of LLMs

### 2.5 Assumptions and Dependencies

1. **Assumptions**
   - Teams have basic technical capabilities for deployment
   - Organizations permit local LLM deployment
   - Teams can allocate time for ritual execution
   - Basic hardware requirements can be met

2. **Dependencies**
   - Availability and stability of open source components
   - Git infrastructure for knowledge versioning
   - Team's existing development environment
   - Network access for component installation

## 3. System Architecture

### 3.1 Architectural Overview

TIP Phase 1 employs a component-based architecture with focused, single-purpose tools connected through manual integration in this initial phase. The architecture is designed to be:

1. **Modular**: Individual components can be replaced or upgraded
2. **Open**: Based entirely on open-source tools
3. **Extensible**: Prepared for more advanced integration in later phases
4. **Accessible**: Deployable with minimal technical expertise

The architecture consists of four main layers:

1. **User Interface Layer**: How team members interact with the system
2. **Component Layer**: Core functional services
3. **Integration Layer**: Connections between components (primarily manual in Phase 1)
4. **Deployment Layer**: Infrastructure options for running the system

### 3.2 Component Diagram

```
+----------------------------------------+
|           TEAM INTERFACES              |
|                                        |
| Open-webui | Obsidian | HedgeDoc       |
+----------------------------------------+
                    |
+----------------------------------------+
|         INTEGRATION LAYER              |
|                                        |
| Phase 1: Manual connections with       |
| minimal automation                     |
+----------------------------------------+
            |           |           
 +-----------------+ +----------------+ 
 | KNOWLEDGE REPO  | | AI INTERACTION | 
 |                 | |                | 
 | Obsidian        | | Ollama         | 
 | Git Version Ctrl| | Open-webui     | 
 | Templates       | | (Opt) LangFlow | 
 +-----------------+ +----------------+ 
            |                |                
 +--------------------------------------------------+
 |              DEPLOYMENT OPTIONS                  |
 | Local | Docker | Simple Server                   |
 +--------------------------------------------------+
```

Core components:

1. **Knowledge Management**
   - Obsidian: Primary knowledge repository
   - Git: Version control and history tracking

2. **AI Interaction**
   - Ollama: Local LLM deployment
   - Open-webui: User interface for AI interaction

3. **Collaboration**
   - HedgeDoc: Collaborative documentation
   - Git: Shared access to knowledge

4. **Workflow Automation (Optional)**
   - LangFlow: Visual workflow building for AI processes

### 3.3 Deployment Options

TIP Phase 1 supports three deployment models, with specific technical requirements for each:

#### 3.3.1 Local Deployment

Individual team members install components on their personal machines with Git synchronization for shared repositories.

**Technical Requirements:**
- Modern CPU (minimum 4 cores recommended)
- 16GB RAM minimum (32GB recommended)
- 20GB available storage
- Git client
- Docker (optional, for containerized components)
- Admin rights for software installation

**Recommended for:**
- Individual practitioners
- Small teams (2-5 members)
- Initial testing and evaluation

#### 3.3.2 Docker Deployment

All components deployed as containers on a shared server accessible to the team.

**Technical Requirements:**
- Modern CPU (minimum 8 cores recommended)
- 32GB RAM minimum
- 50GB available storage
- Docker and Docker Compose
- Network access for team members
- Port availability for services

**Recommended for:**
- Mid-sized teams (5-15 members)
- Standard implementation
- Controlled environments

#### 3.3.3 Simple Server Deployment

Native installation of components on a shared server without containerization.

**Technical Requirements:**
- Modern CPU (minimum 8 cores recommended)
- 32GB RAM minimum
- 50GB available storage
- Access for software installation
- Network access for team members
- Port availability for services

**Recommended for:**
- Environments with Docker restrictions
- Specialized deployment needs
- Existing server infrastructure

### 3.4 Data Flow

TIP Phase 1 employs three primary data flow patterns:

#### 3.4.1 Knowledge Management Flow

```
Team Member --> Obsidian --> Git --> Shared Repository --> Team Access
```

Process:
1. Team members capture context in Obsidian
2. Git provides version control and history
3. Shared repository enables team access
4. Cross-linking creates knowledge network

#### 3.4.2 AI Interaction Flow

```
Team Member --> Open-webui --> Ollama --> LLM Processing --> Results --> Knowledge Capture
```

Process:
1. Team member interacts with AI via Open-webui
2. Ollama manages LLM execution
3. LLM processes the input
4. Results returned to team member
5. Valuable outputs manually captured in knowledge repository

#### 3.4.3 Documentation Flow

```
Meeting --> HedgeDoc --> Raw Notes --> AI Processing --> Structured Summary --> Knowledge Repository
```

Process:
1. Meeting notes captured in HedgeDoc
2. Raw notes processed by AI (via Open-webui or LangFlow)
3. AI generates structured summary
4. Summary reviewed and refined
5. Final version committed to knowledge repository

### 3.5 Integration Points

Phase 1 focuses on simple, manual integration with minimal technical overhead:

#### 3.5.1 Primary Integration Points

1. **Obsidian to Git**
   - Integration Type: File-based
   - Method: Manual Git operations or Obsidian Git plugin
   - Data: Markdown files and attachments
   - Frequency: Daily or per significant update

2. **HedgeDoc to AI Processing**
   - Integration Type: Copy/paste or file export
   - Method: Manual transfer of content
   - Data: Markdown-formatted meeting notes
   - Frequency: After each documented meeting

3. **AI Output to Knowledge Repository**
   - Integration Type: Manual transfer
   - Method: Copy/paste or file creation
   - Data: Processed summaries, generated content
   - Frequency: After each significant AI interaction

#### 3.5.2 Optional Advanced Integration

1. **LangFlow to Open-webui**
   - Integration Type: API-based
   - Method: Simple HTTP requests
   - Data: Prompts and responses
   - Frequency: On-demand during workflow execution

2. **Git to Obsidian**
   - Integration Type: File-based
   - Method: Automated using Obsidian Git plugin
   - Data: Repository updates
   - Frequency: Scheduled or manual pull operations

## 4. System Requirements

### 4.1 Functional Requirements

#### 4.1.1 Knowledge Repository Management

1. **FR-KR-01: Knowledge Structure Creation**
   - The system shall provide templates for creating a structured knowledge repository
   - The structure shall accommodate team context, decisions, meeting notes, and prompts
   - Templates shall be customizable to team needs

2. **FR-KR-02: Knowledge Version Control**
   - The system shall support Git-based version control of all knowledge assets
   - Version history shall be accessible to all team members
   - Conflicts shall be resolvable through standard Git processes

3. **FR-KR-03: Knowledge Linking**
   - The knowledge system shall support cross-linking between related items
   - Links shall be creatable, editable, and navigable
   - Link validity shall be maintained during repository evolution

4. **FR-KR-04: Knowledge Search**
   - The repository shall be searchable by content, tags, and metadata
   - Search results shall be relevance-ranked
   - Full-text search shall be supported

5. **FR-KR-05: Knowledge Templates**
   - The system shall provide templates for common knowledge types
   - Templates shall be accessible within the knowledge system
   - Template usage shall be consistent across team members

#### 4.1.2 AI Interaction

1. **FR-AI-01: Local LLM Deployment**
   - The system shall support local deployment of open LLMs
   - Multiple models shall be selectable based on task requirements
   - Model loading, unloading, and switching shall be supported

2. **FR-AI-02: AI Chat Interface**
   - The system shall provide a user-friendly interface for AI interaction
   - The interface shall support conversation history
   - Conversations shall be savable and shareable

3. **FR-AI-03: Prompt Management**
   - The system shall support creation and storage of prompt templates
   - Prompt templates shall be categorized and searchable
   - Prompt effectiveness shall be documentable

4. **FR-AI-04: Basic Workflow Automation (Optional)**
   - The system shall optionally support visual workflow creation for AI processes
   - Workflows shall be savable and reusable
   - Workflows shall support basic branching and decision logic

5. **FR-AI-05: Output Formatting**
   - AI outputs shall be formattable as plain text, markdown, or structured data
   - Output format shall be specifiable in prompts
   - Standard formatting templates shall be available

#### 4.1.3 Collaboration Support

1. **FR-CS-01: Collaborative Editing**
   - The system shall support real-time collaborative document editing
   - Multiple users shall be able to edit simultaneously
   - Changes shall be visible in real-time to all participants

2. **FR-CS-02: Meeting Documentation**
   - The system shall provide templates for meeting documentation
   - Documentation shall be processable by AI for summarization
   - Meeting notes shall be exportable to the knowledge repository

3. **FR-CS-03: Team Access**
   - All components shall support multi-user access
   - Access shall be controllable through basic authentication
   - Simultaneous usage by team members shall be supported

4. **FR-CS-04: Shared Context**
   - Knowledge repository shall be accessible to all team members
   - Content changes shall be visible across the team
   - History of changes shall be preserved and viewable

#### 4.1.4 Ritual Support

1. **FR-RS-01: Context Curation Support**
   - The system shall provide templates for daily and weekly context curation
   - Templates shall guide the curation process
   - Curation outputs shall be storable in the knowledge repository

2. **FR-RS-02: Prompt Development Support**
   - The system shall support prompt creation and refinement
   - Prompt templates shall be available in the knowledge repository
   - Prompt effectiveness shall be documentable

3. **FR-RS-03: AI-Assisted Documentation Support**
   - The system shall support AI processing of meeting notes
   - Processing shall generate structured summaries
   - Summaries shall be reviewable and editable before finalization

### 4.2 Non-Functional Requirements

#### 4.2.1 Performance

1. **NFR-P-01: LLM Response Time**
   - Local LLM shall respond within 5 seconds for typical requests
   - Performance shall be optimized for available hardware
   - Performance limitations shall be clearly documented

2. **NFR-P-02: Repository Search Speed**
   - Knowledge repository searches shall return results within 3 seconds
   - Search performance shall scale with repository size
   - Indexing shall be automatic and transparent

3. **NFR-P-03: Collaborative Editing Responsiveness**
   - Collaborative editing shall have latency under 500ms
   - System shall support at least 10 simultaneous editors
   - Performance shall degrade gracefully under load

#### 4.2.2 Usability

1. **NFR-U-01: Installation Simplicity**
   - System installation shall require no more than 30 minutes for a technical user
   - Installation shall be scriptable
   - Installation errors shall provide clear guidance

2. **NFR-U-02: Ritual Execution Clarity**
   - Ritual templates shall be self-explanatory
   - Templates shall include step-by-step guidance
   - Example content shall be provided

3. **NFR-U-03: Knowledge Navigation**
   - Knowledge repository shall be navigable via links and search
   - Navigation shall be intuitive and consistent
   - Context shall be maintained during navigation

4. **NFR-U-04: AI Interaction Accessibility**
   - AI interface shall be accessible to non-technical users
   - Interface shall provide clear guidance on effective interaction
   - Error states shall be handled gracefully with clear messaging

#### 4.2.3 Reliability

1. **NFR-R-01: Knowledge Persistence**
   - Knowledge repository shall preserve all content reliably
   - Version history shall be maintained
   - Backup mechanisms shall be available

2. **NFR-R-02: Component Stability**
   - System components shall operate stably under normal conditions
   - Crash recovery shall be automatic where possible
   - Failure in one component shall not affect others

3. **NFR-R-03: Offline Accessibility**
   - Knowledge repository shall be accessible offline
   - Changes made offline shall synchronize when connectivity returns
   - Conflict resolution shall be available for synchronization issues

#### 4.2.4 Scalability

1. **NFR-S-01: Team Size Scaling**
   - System shall support teams from 2 to 20 members
   - Performance shall degrade gracefully with increased team size
   - Resource requirements shall be clearly documented for different team sizes

2. **NFR-S-02: Knowledge Volume Scaling**
   - Repository shall handle up to 10,000 knowledge items efficiently
   - Search and navigation shall remain responsive with large repositories
   - Storage requirements shall scale linearly with content volume

#### 4.2.5 Security

1. **NFR-SE-01: Authentication**
   - All components shall support basic authentication
   - Passwords shall be stored securely
   - Authentication shall be configurable

2. **NFR-SE-02: Data Privacy**
   - All data shall remain within the organizational boundary
   - No data shall be sent to external services without explicit configuration
   - Local LLM deployment shall ensure prompt and response privacy

3. **NFR-SE-03: Access Control**
   - Repository access shall be controllable at the repository level
   - Component access shall be configurable per installation
   - Network access shall be limited to authorized users

## 5. Component Specifications

### 5.1 LLM Runtime & Interface

#### 5.1.1 Ollama

**Purpose:** Local deployment and execution of Large Language Models

**Version:** Latest stable (minimum 0.1.17)

**Deployment Method:**
- Local installation via script
- Docker container

**Functional Requirements:**
1. Support for multiple open LLMs
2. Local execution without external API calls
3. Model management (download, removal)
4. REST API for integrations
5. Performance optimization for available hardware

**Configuration Parameters:**
- `OLLAMA_HOST`: IP for API binding (default: 127.0.0.1)
- `OLLAMA_MODELS`: Path to model storage directory

**Resource Requirements:**
- CPU: 4+ cores recommended
- RAM: 8GB minimum, 16GB+ recommended
- Storage: 10GB+ for models
- GPU: Optional, CUDA-compatible for acceleration

**Implementation Notes:**
- Models should include at minimum: Llama3, Mistral
- Local file paths must be accessible for serving models
- Port 11434 must be available for the API

#### 5.1.2 Open-webui

**Purpose:** User interface for interacting with Ollama LLMs

**Version:** Latest stable (minimum 0.1.113)

**Deployment Method:**
- Docker container

**Functional Requirements:**
1. Connection to Ollama API
2. Conversation interface with history
3. Prompt library management
4. Conversation export/import
5. Multi-user support

**Configuration Parameters:**
- `PORT`: Web interface port (default: 3000)
- `OLLAMA_API_URL`: URL of Ollama API (default: http://host.docker.internal:11434)
- `DATA_DIRECTORY`: Path for persistent storage

**Resource Requirements:**
- Minimal beyond Docker requirements
- Network access to Ollama API

**Implementation Notes:**
- Docker host gateway must be configured for container-to-host communication
- Persistent volume required for configuration and history

### 5.2 Knowledge Management

#### 5.2.1 Obsidian

**Purpose:** Knowledge repository management and navigation

**Version:** Latest stable (minimum 1.4.16)

**Deployment Method:**
- Local installation per user

**Functional Requirements:**
1. Markdown-based note creation and editing
2. Note linking and backlinking
3. Graph visualization of knowledge
4. Template support
5. Search functionality
6. Plugin support (especially Git integration)

**Configuration Parameters:**
- Vault location: Path to shared repository
- Template folder: Path within vault for templates

**Resource Requirements:**
- Modern web browser
- Local storage for vault content

**Implementation Notes:**
- Git plugin recommended for version control integration
- Templater plugin recommended for advanced templates
- Standard naming conventions required across team

#### 5.2.2 Git

**Purpose:** Version control and sharing of knowledge assets

**Version:** Latest stable (minimum 2.30.0)

**Deployment Method:**
- Local installation per user
- Integration with Obsidian via plugin

**Functional Requirements:**
1. Repository initialization and cloning
2. Commit, push, pull operations
3. Branch and merge capabilities
4. Conflict resolution
5. History tracking and browsing

**Configuration Parameters:**
- Repository URL: Location of shared repository
- User credentials: Authentication information

**Resource Requirements:**
- Minimal beyond basic installation
- Network access to repository host

**Implementation Notes:**
- Simple branching strategy recommended for Phase 1
- Direct integration with Obsidian recommended
- Clear commit message conventions required

### 5.3 Collaboration Tools

#### 5.3.1 HedgeDoc

**Purpose:** Collaborative documentation and note-taking

**Version:** Latest stable (minimum 1.9.9)

**Deployment Method:**
- Docker container

**Functional Requirements:**
1. Real-time collaborative editing
2. Markdown support
3. Document publishing and sharing
4. User authentication
5. Document export

**Configuration Parameters:**
- `PORT`: Web interface port (default: 3001)
- `CMD_DB_URL`: Database connection string
- `CMD_DOMAIN`: Server domain name
- `CMD_URL_ADDPORT`: Whether to add port to URLs

**Resource Requirements:**
- 1GB RAM minimum
- 100MB storage plus document growth

**Implementation Notes:**
- Persistent volume required for uploads and database
- Database can be SQLite for simplicity in Phase 1
- External authentication recommended for production

### 5.4 Workflow Automation (Optional)

#### 5.4.1 LangFlow

**Purpose:** Visual workflow building for LLM processes

**Version:** Latest stable (minimum 0.6.0)

**Deployment Method:**
- Docker container

**Functional Requirements:**
1. Visual workflow creation
2. Integration with Ollama
3. Workflow execution
4. Component library for LLM operations
5. Workflow export and import

**Configuration Parameters:**
- `PORT`: Web interface port (default: 7860)
- `LANGFLOW_HOST`: Host binding (default: 0.0.0.0)
- `LANGFLOW_API_KEY`: API authentication key

**Resource Requirements:**
- 2GB RAM minimum
- 500MB storage plus workflow growth

**Implementation Notes:**
- Optional component for Phase 1
- Integration with Ollama requires network access
- Simple workflows recommended for initial implementation

### 5.5 Integration Layer

#### 5.5.1 Manual Integration

**Purpose:** Connect components with minimal technical overhead

**Implementation Method:**
- Manual processes documented in guides
- Simple scripts for routine operations

**Functional Requirements:**
1. Clear documentation of integration points
2. Step-by-step guides for manual processes
3. Template-based consistency

**Implementation Notes:**
- Focus on process clarity over automation in Phase 1
- Document all integration points comprehensively
- Prepare for increased automation in later phases

#### 5.5.2 Basic Integration Scripts

**Purpose:** Automate routine integration tasks

**Implementation Method:**
- Simple bash/Python scripts
- Documentation for usage

**Functional Requirements:**
1. Knowledge repository synchronization
2. Meeting note processing
3. Template application

**Implementation Notes:**
- Scripts should be simple and focused
- Error handling should be comprehensive
- Documentation should be clear for non-technical users

## 6. Data Specifications

### 6.1 Knowledge Structure

The knowledge repository follows a standardized structure to ensure consistency and navigability:

#### 6.1.1 Root Structure

```
tip-vault/
├── .git/                     # Git repository
├── context/                  # Team knowledge
│   ├── domain/               # Domain-specific knowledge
│   ├── process/              # Process documentation
│   └── technical/            # Technical knowledge
├── decisions/                # Decision records
│   ├── project/              # Project decisions
│   └── team/                 # Team process decisions
├── meetings/                 # Meeting documentation
│   ├── daily/                # Daily curation logs
│   ├── retro/                # Retrospective documentation
│   ├── planning/             # Planning session notes
│   └── other/                # Other meeting types
├── prompts/                  # Prompt library
│   ├── context/              # Context management prompts
│   ├── meetings/             # Meeting facilitation prompts
│   └── templates/            # Reusable prompt templates
└── templates/                # Obsidian templates
    ├── curation/             # Context curation templates
    ├── decision/             # Decision documentation templates
    └── meeting/              # Meeting note templates
```

#### 6.1.2 File Naming Conventions

1. **Context Files:**
   - Format: `[category]-[topic]-[subtopic].md`
   - Example: `technical-authentication-oauth2.md`

2. **Decision Records:**
   - Format: `[date]-[decision-topic].md`
   - Example: `2025-04-15-api-authentication-approach.md`

3. **Meeting Notes:**
   - Format: `[date]-[meeting-type]-[topic].md`
   - Example: `2025-04-12-sprint-planning-sprint-23.md`

4. **Prompts:**
   - Format: `[purpose]-[version].md`
   - Example: `meeting-summary-v2.md`

5. **Templates:**
   - Format: `[usage]-template.md`
   - Example: `daily-curation-template.md`

### 6.2 Template Formats

#### 6.2.1 Context Curation Templates

**Daily Quick Capture Template**
```markdown
# Daily Context Curation - {{date}}

## Participants
- [List of team members present]

## New Context Elements
- [Team Member 1]: [Context element]
- [Team Member 2]: [Context element]
- [Team Member 3]: [Context element]

## Decisions
- Accept/Reject: [Context element] - [Rationale]
- Accept with modification: [Context element] → [Modified version]

## Action Items
- [ ] [Action description] (@owner) (due: [date])
- [ ] [Action description] (@owner) (due: [date])

## Notes
[Any additional notes or observations]
```

**Weekly Structured Review Template**
```markdown
# Weekly Context Curation - {{date}}

## Participants
- [List of team members present]

## Context Health Assessment
- Total knowledge items: [number]
- New items this week: [number]
- Accessed items this week: [number]
- Coverage areas: [list key areas]
- Identified gaps: [list gaps]

## Priority Improvement Areas
1. [Area 1] - [Specific improvements needed]
2. [Area 2] - [Specific improvements needed]
3. [Area 3] - [Specific improvements needed]

## Action Items
- [ ] [Action description] (@owner) (due: [date])
- [ ] [Action description] (@owner) (due: [date])

## Discussion Summary
[Summary of key discussion points]
```

#### 6.2.2 Meeting Documentation Templates

**Meeting Notes Template**
```markdown
# [Meeting Type] - {{date}}

## Participants
- [List of attendees]

## Agenda
1. [Agenda item 1]
2. [Agenda item 2]
3. [Agenda item 3]

## Discussion
### [Agenda item 1]
[Raw notes]
#decision [Any decisions made]
#action [Any actions identified]

### [Agenda item 2]
[Raw notes]
#decision [Any decisions made]
#action [Any actions identified]

### [Agenda item 3]
[Raw notes]
#decision [Any decisions made]
#action [Any actions identified]

## Next Steps
- [Next step 1]
- [Next step 2]
```

**AI-Generated Summary Template**
```markdown
# Summary: [Meeting Type] - {{date}}

## Overview
[Brief 1-2 sentence overview of the meeting purpose and outcome]

## Key Decisions
- [Decision 1 with context]
- [Decision 2 with context]
- [Decision 3 with context]

## Action Items
- [ ] [Action 1] (@owner) (due: [date])
- [ ] [Action 2] (@owner) (due: [date])
- [ ] [Action 3] (@owner) (due: [date])

## Discussion Summary
### [Topic 1]
[Concise summary of discussion, key points, and context]

### [Topic 2]
[Concise summary of discussion, key points, and context]

## Related Context
- [Link to related knowledge item 1]
- [Link to related knowledge item 2]

## Follow-up Scheduled
[Date and time of any follow-up meetings]
```

#### 6.2.3 Prompt Development Templates

**Prompt Workshop Preparation Template**
```markdown
# Prompt Workshop Preparation - {{date}}

## Target Workflow
[Description of workflow needing prompt improvement]

## Current Prompt
```
[Exact text of current prompt]
```

## Current Limitations
- [Limitation 1]
- [Limitation 2]
- [Limitation 3]

## Example Outputs
### Successful Example
[Example of successful output]

### Unsuccessful Example
[Example of problematic output]

## Desired Improvements
- [Improvement 1]
- [Improvement 2]
- [Improvement 3]

## References
- [Link to relevant context]
- [Link to related prompts]
```

**Prompt Documentation Template**
```markdown
# Prompt: [Name]

## Version
[Version number] - [Date]

## Purpose
[Clear description of what this prompt is designed to accomplish]

## Use Cases
- [Use case 1]
- [Use case 2]
- [Use case 3]

## Prompt Text
```
[Full prompt text]
```

## Input Requirements
- [Requirement 1]
- [Requirement 2]

## Expected Output
[Description of expected output format and content]

## Example Input/Output
### Input
[Example input]

### Output
[Example output]

## Performance Notes
- Success rate: [percentage]
- Common issues: [list]
- Best practices: [list]

## Changelog
- [Version] ([Date]): [Changes]
```

### 6.3 Prompt Library

The initial prompt library includes core prompts for Phase 1 rituals:

#### 6.3.1 Context Curation Prompts

**Context Extraction Prompt**
```
You are an AI assistant helping a software development team extract and organize key context elements from their discussions. Your task is to identify important context elements from the following text.

Context elements include:
1. Domain knowledge (business rules, terminology, customer requirements)
2. Technical decisions (architecture, patterns, technology choices)
3. Process knowledge (how the team works, who does what)
4. Historical context (why certain decisions were made)

For each context element you identify, format it as follows:
- **Category | Name**: Brief description (1-2 sentences maximum)

The output should be a list of the most important context elements, each formatted according to the structure above. Aim to identify 3-5 key elements.

Text to analyze:
[TEXT]
```

**Context Organization Prompt**
```
You are an AI assistant helping a software development team organize their knowledge repository. Your task is to suggest appropriate categorization and linking for the following context element.

Context element:
[CONTEXT ELEMENT]

Please answer the following questions:
1. What main category should this element belong to? (Technical, Domain, Process, or Historical)
2. What subcategory would be most appropriate?
3. What related context elements might this connect to? (Consider what other knowledge it might relate to)
4. What metadata or tags would be useful for this element?
5. Is this element complete or does it need additional information?

Format your response as direct answers to these five questions, keeping explanations brief and practical.
```

#### 6.3.2 Meeting Documentation Prompts

**Meeting Summary Prompt**
```
You are an AI assistant helping a software development team create structured summaries of their meetings. Your task is to analyze the raw meeting notes below and generate a clear, concise summary.

The summary should include:
1. A brief overview (1-2 sentences)
2. Key decisions made (formatted as bullet points)
3. Action items with owners (formatted as tasks with @mentions)
4. A concise summary of key discussion points by topic
5. References to any related documentation or context

Format the summary using Markdown with clear headings and structure. Be comprehensive but concise, focusing on the most important information. Maintain technical accuracy and use the team's terminology.

Raw meeting notes:
[NOTES]
```

**Action Item Extraction Prompt**
```
You are an AI assistant helping a software development team track action items from meetings. Your task is to extract all action items from the following meeting notes.

For each action item:
1. Identify the specific task to be done
2. Identify the owner (person responsible)
3. Extract or infer the due date if present
4. Note any dependencies or related context

Format each action item as:
- [ ] [Task description] (@owner) (due: [date]) [dependency/context]

If any information is missing, use the format "(@unassigned)" for missing owners or "(due: TBD)" for missing dates.

Meeting notes:
[NOTES]
```

#### 6.3.3 General Assistance Prompts

**Documentation Improvement Prompt**
```
You are an AI assistant helping a software development team improve their documentation. Your task is to analyze the following document and suggest specific improvements.

Focus on:
1. Clarity - Is the information presented clearly?
2. Completeness - Is critical information missing?
3. Structure - Is the organization logical and navigable?
4. Consistency - Does it follow team standards?
5. Actionability - Can readers understand what to do?

For each area that needs improvement, provide a specific suggestion with an example of how to implement it. Be concrete and practical rather than theoretical.

Document:
[DOCUMENT]
```

**Terminology Standardization Prompt**
```
You are an AI assistant helping a software development team standardize terminology in their documentation. Your task is to identify terminology in the following text and suggest standardization.

For each term you identify:
1. Note the term as used in the document
2. Indicate if it's used consistently
3. Suggest a standard form if inconsistent
4. Note if it should be added to the team glossary

Format your response as a table with columns for Term, Consistency, Suggested Standard, and Glossary Addition.

Only include terms that are:
- Domain-specific
- Technical and potentially ambiguous
- Used in multiple ways within the team
- Important for shared understanding

Text:
[TEXT]
```

### 6.4 Data Flow Specifications

#### 6.4.1 Knowledge Creation Flow

1. Team member creates content in Obsidian
2. Content is saved as Markdown file
3. Git tracks changes
4. Team member commits changes with descriptive message
5. Changes are pushed to shared repository
6. Other team members pull updates
7. Content appears in their local repositories

**Technical Implementation:**
- Files stored in standard Markdown format
- Git provides version control and synchronization
- Linking via Obsidian wiki-style links ([[link]])
- Media stored in dedicated assets folder

#### 6.4.2 Meeting Documentation Flow

1. Team conducts meeting with notes in HedgeDoc
2. Raw notes exported as Markdown
3. Notes processed by AI (via Open-webui or LangFlow)
4. AI generates structured summary
5. Facilitator reviews and refines summary
6. Summary saved to Obsidian repository
7. Summary committed and pushed to shared repository

**Technical Implementation:**
- HedgeDoc provides real-time collaborative editing
- Export via HedgeDoc Markdown export
- AI processing via direct prompt or workflow
- Manual saving to Obsidian repository
- Git provides version control and sharing

#### 6.4.3 Prompt Development Flow

1. Team identifies prompt needs
2. Preparation document created in HedgeDoc or Obsidian
3. Team workshop refines prompt
4. Testing conducted in Open-webui
5. Final prompt documented in Obsidian
6. Prompt added to library in repository
7. Prompt committed and pushed to shared repository

**Technical Implementation:**
- Collaborative editing in HedgeDoc or Obsidian
- Testing through Open-webui interface
- Documentation in standard Markdown format
- Categorization according to repository structure
- Git provides version control and sharing

## 7. Installation and Setup

### 7.1 Prerequisites

Before installation, ensure the following prerequisites are met:

- **Hardware Requirements:**
  - CPU: 4+ cores recommended (8+ for team server)
  - RAM: 16GB minimum (32GB recommended for team server)
  - Storage: 20GB available
  - GPU: Optional, but beneficial for LLM performance

- **Software Prerequisites:**
  - Git client installed
  - Docker and Docker Compose (for containerized deployment)
  - Bash-compatible shell (for installation scripts)
  - Admin/sudo access for local installations

- **Network Requirements:**
  - Internet access for initial downloads
  - Ports 3000, 3001, 7860, and 11434 available
  - Network connectivity between team members for shared repositories

- **Account Requirements:**
  - GitHub account or similar for repository hosting
  - Permissions to create and manage repositories

### 7.2 Installation Script

The following installation script (`install.sh`) performs a complete setup of TIP Phase 1 components:

```bash
#!/bin/bash
# Team Intelligence Platform (TIP) - Phase 1 Installation Script
# Version: 1.0.0
# License: Apache 2.0

# Configuration variables
TIP_BASE_DIR="$HOME/tip"
TIP_DATA_DIR="$TIP_BASE_DIR/data"
TIP_CONFIG_DIR="$TIP_BASE_DIR/configs"
TIP_SCRIPTS_DIR="$TIP_BASE_DIR/scripts"
TIP_VAULT_DIR="$HOME/tip-vault"
OLLAMA_PORT=11434
OPENWEBUI_PORT=3000
HEDGEDOC_PORT=3001
LANGFLOW_PORT=7860

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Team Intelligence Platform (TIP) - Phase 1${NC}"
echo -e "${BLUE}Installation Script${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check for required tools
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check for Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git is required but not installed.${NC}"
    echo "Please install Git and run this script again."
    exit 1
else
    echo -e "${GREEN}Git is installed.${NC}"
fi

# Check for Docker if not skipping container deployment
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker is not installed. Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}Docker installed. You may need to log out and back in for group changes to take effect.${NC}"
    echo "After logging back in, please run this script again."
    exit 0
else
    echo -e "${GREEN}Docker is installed.${NC}"
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${YELLOW}Docker Compose not found. Installing...${NC}"
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        echo -e "${GREEN}Docker Compose installed.${NC}"
    else
        echo -e "${GREEN}Docker Compose is installed.${NC}"
    fi
fi

# Create directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p "$TIP_DATA_DIR"/{ollama,openwebui,hedgedoc,langflow}
mkdir -p "$TIP_CONFIG_DIR"
mkdir -p "$TIP_SCRIPTS_DIR"
echo -e "${GREEN}Directories created.${NC}"

# Deploy Ollama
echo -e "${YELLOW}Deploying Ollama...${NC}"
curl -fsSL https://ollama.ai/install.sh | sh
echo -e "${GREEN}Ollama installed.${NC}"

# Pull initial models
echo -e "${YELLOW}Pulling initial LLM models (this may take some time)...${NC}"
ollama pull llama3 && echo -e "${GREEN}Llama3 model pulled.${NC}"
ollama pull mistral && echo -e "${GREEN}Mistral model pulled.${NC}"

# Create docker-compose.yml
echo -e "${YELLOW}Creating Docker Compose configuration...${NC}"
cat > "$TIP_CONFIG_DIR/docker-compose.yml" << EOL
version: '3'

services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: openwebui
    volumes:
      - ${TIP_DATA_DIR}/openwebui:/app/backend/data
    ports:
      - "${OPENWEBUI_PORT}:8080"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped

  hedgedoc:
    image: hedgedoc/hedgedoc:latest
    container_name: hedgedoc
    volumes:
      - ${TIP_DATA_DIR}/hedgedoc:/hedgedoc/public/uploads
    ports:
      - "${HEDGEDOC_PORT}:3000"
    environment:
      - CMD_DB_URL=sqlite:///data/hedgedoc.db
      - CMD_DOMAIN=localhost
      - CMD_URL_ADDPORT=true
      - CMD_URL_PROTOCOL=http
      - CMD_ALLOW_ANONYMOUS=true
    restart: unless-stopped

  langflow:
    image: logspace/langflow:latest
    container_name: langflow
    volumes:
      - ${TIP_DATA_DIR}/langflow:/root/.cache/langflow
    ports:
      - "${LANGFLOW_PORT}:7860"
    restart: unless-stopped
EOL
echo -e "${GREEN}Docker Compose configuration created.${NC}"

# Start Docker containers
echo -e "${YELLOW}Starting Docker containers...${NC}"
cd "$TIP_CONFIG_DIR"
docker-compose up -d
echo -e "${GREEN}Docker containers started.${NC}"

# Create knowledge repository
echo -e "${YELLOW}Setting up knowledge repository...${NC}"
mkdir -p "$TIP_VAULT_DIR"/{context/{domain,process,technical},decisions/{project,team},meetings/{daily,retro,planning,other},prompts/{context,meetings,templates},templates/{curation,decision,meeting}}

# Initialize Git repository
cd "$TIP_VAULT_DIR"
git init
echo "# Team Intelligence Platform Knowledge Repository" > README.md
cat > .gitignore << EOL
.obsidian/workspace*
.obsidian/cache
.DS_Store
EOL

# Create initial templates
echo -e "${YELLOW}Creating initial templates...${NC}"

# Daily curation template
cat > "$TIP_VAULT_DIR/templates/curation/daily-curation-template.md" << EOL
# Daily Context Curation - {{date:YYYY-MM-DD}}

## Participants
- [List of team members present]

## New Context Elements
- [Team Member 1]: [Context element]
- [Team Member 2]: [Context element]
- [Team Member 3]: [Context element]

## Decisions
- Accept/Reject: [Context element] - [Rationale]
- Accept with modification: [Context element] → [Modified version]

## Action Items
- [ ] [Action description] (@owner) (due: [date])
- [ ] [Action description] (@owner) (due: [date])

## Notes
[Any additional notes or observations]
EOL

# Weekly curation template
cat > "$TIP_VAULT_DIR/templates/curation/weekly-curation-template.md" << EOL
# Weekly Context Curation - {{date:YYYY-MM-DD}}

## Participants
- [List of team members present]

## Context Health Assessment
- Total knowledge items: [number]
- New items this week: [number]
- Accessed items this week: [number]
- Coverage areas: [list key areas]
- Identified gaps: [list gaps]

## Priority Improvement Areas
1. [Area 1] - [Specific improvements needed]
2. [Area 2] - [Specific improvements needed]
3. [Area 3] - [Specific improvements needed]

## Action Items
- [ ] [Action description] (@owner) (due: [date])
- [ ] [Action description] (@owner) (due: [date])

## Discussion Summary
[Summary of key discussion points]
EOL

# Meeting notes template
cat > "$TIP_VAULT_DIR/templates/meeting/meeting-notes-template.md" << EOL
# {{title}} - {{date:YYYY-MM-DD}}

## Participants
- [List of attendees]

## Agenda
1. [Agenda item 1]
2. [Agenda item 2]
3. [Agenda item 3]

## Discussion
### [Agenda item 1]
[Raw notes]
#decision [Any decisions made]
#action [Any actions identified]

### [Agenda item 2]
[Raw notes]
#decision [Any decisions made]
#action [Any actions identified]

### [Agenda item 3]
[Raw notes]
#decision [Any decisions made]
#action [Any actions identified]

## Next Steps
- [Next step 1]
- [Next step 2]
EOL

# Initial prompt templates
cat > "$TIP_VAULT_DIR/prompts/meetings/meeting-summary-prompt.md" << EOL
# Prompt: Meeting Summary

## Version
1.0 - {{date:YYYY-MM-DD}}

## Purpose
Generate a structured summary of meeting notes, extracting key decisions, action items, and discussion points.

## Prompt Text
\`\`\`
You are an AI assistant helping a software development team create structured summaries of their meetings. Your task is to analyze the raw meeting notes below and generate a clear, concise summary.

The summary should include:
1. A brief overview (1-2 sentences)
2. Key decisions made (formatted as bullet points)
3. Action items with owners (formatted as tasks with @mentions)
4. A concise summary of key discussion points by topic
5. References to any related documentation or context

Format the summary using Markdown with clear headings and structure. Be comprehensive but concise, focusing on the most important information. Maintain technical accuracy and use the team's terminology.

Raw meeting notes:
[NOTES]
\`\`\`

## Expected Output
A well-structured meeting summary with overview, decisions, actions, and discussion points.

## Example Input/Output
### Input
Raw meeting notes from a sprint planning session.

### Output
A structured summary with decisions, action items with assignees, and key discussion points.
EOL

# Commit initial repository
git add .
git commit -m "Initial knowledge repository structure"
echo -e "${GREEN}Knowledge repository initialized.${NC}"

# Create startup script
echo -e "${YELLOW}Creating startup script...${NC}"
cat > "$TIP_SCRIPTS_DIR/start-tip.sh" << EOL
#!/bin/bash
# TIP Environment Startup Script

# Start Ollama server if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama server..."
    ollama serve &
    # Wait for server to start
    sleep 3
fi

# Start Docker containers if not running
cd "${TIP_CONFIG_DIR}"
docker-compose up -d

echo "TIP environment started. Access points:"
echo "- Ollama API: http://localhost:${OLLAMA_PORT}"
echo "- Open-webui: http://localhost:${OPENWEBUI_PORT}"
echo "- HedgeDoc: http://localhost:${HEDGEDOC_PORT}"
echo "- LangFlow: http://localhost:${LANGFLOW_PORT}"
echo ""
echo "Knowledge repository: ${TIP_VAULT_DIR}"
EOL

chmod +x "$TIP_SCRIPTS_DIR/start-tip.sh"
echo -e "${GREEN}Startup script created.${NC}"

# Print success message
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "TIP environment has been set up with the following components:"
echo "- Ollama (LLM runtime): http://localhost:${OLLAMA_PORT}"
echo "- Open-webui (AI interface): http://localhost:${OPENWEBUI_PORT}"
echo "- HedgeDoc (Collaborative editing): http://localhost:${HEDGEDOC_PORT}"
echo "- LangFlow (Optional workflow builder): http://localhost:${LANGFLOW_PORT}"
echo ""
echo "Knowledge repository: ${TIP_VAULT_DIR}"
echo ""
echo "Next steps:"
echo "1. Open Obsidian and create a vault pointing to: ${TIP_VAULT_DIR}"
echo "2. Connect the Git repository to a remote (GitHub, GitLab, etc.)"
echo "3. Follow the First-Time Setup Guide in the documentation"
echo ""
echo "To start the TIP environment in the future, run:"
echo "${TIP_SCRIPTS_DIR}/start-tip.sh"
echo ""
```

### 7.3 Docker Deployment

For team environments, the following Docker Compose configuration can be used for deploying all containerized components:

```yaml
version: '3'

services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: openwebui
    volumes:
      - ./data/openwebui:/app/backend/data
    ports:
      - "3000:8080"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped

  hedgedoc:
    image: hedgedoc/hedgedoc:latest
    container_name: hedgedoc
    volumes:
      - ./data/hedgedoc:/hedgedoc/public/uploads
    ports:
      - "3001:3000"
    environment:
      - CMD_DB_URL=sqlite:///data/hedgedoc.db
      - CMD_DOMAIN=localhost
      - CMD_URL_ADDPORT=true
      - CMD_URL_PROTOCOL=http
      - CMD_ALLOW_ANONYMOUS=true
    restart: unless-stopped

  langflow:
    image: logspace/langflow:latest
    container_name: langflow
    volumes:
      - ./data/langflow:/root/.cache/langflow
    ports:
      - "7860:7860"
    restart: unless-stopped
```

Usage:
```bash
# Start all components
docker-compose up -d

# View component status
docker-compose ps

# Stop all components
docker-compose down
```

### 7.4 Configuration

#### 7.4.1 Obsidian Configuration

1. Install Obsidian from [https://obsidian.md/](https://obsidian.md/)
2. Create a new vault pointing to the TIP knowledge repository
3. Enable recommended community plugins:
   - Git
   - Templater
   - Dataview
   - Kanban (optional)

Configuration:
```json
{
  "baseFontSize": 16,
  "theme": "moonstone",
  "enabledPlugins": [
    "obsidian-git",
    "templater-obsidian",
    "dataview"
  ],
  "newFileLocation": "folder",
  "newFileFolderPath": "context/technical",
  "attachmentFolderPath": "assets",
  "alwaysUpdateLinks": true,
  "defaultViewMode": "source"
}
```

#### 7.4.2 Open-webui Configuration

Access Open-webui at http://localhost:3000 and perform initial setup:

1. Connect to Ollama at http://host.docker.internal:11434
2. Select default models (Llama3, Mistral)
3. Configure basic settings:
   - System name: "TIP Assistant"
   - Default temperature: 0.7
   - Default max tokens: 4096

#### 7.4.3 HedgeDoc Configuration

Access HedgeDoc at http://localhost:3001 and perform initial setup:

1. Create an admin account
2. Configure basic settings:
   - Allow anonymous access (or configure team authentication)
   - Enable history feature
   - Configure synchronization mode

## 8. First-Time Setup Guide

### 8.1 Knowledge Repository Setup

#### 8.1.1 Initial Structure Setup

1. **Setup Obsidian Vault**
   - Open Obsidian
   - Select "Open folder as vault"
   - Navigate to the TIP knowledge repository folder
   - Open the folder

2. **Configure Obsidian Settings**
   - Go to Settings → Files & Links
   - Enable "Default location for new notes" and set to "In the folder specified below"
   - Set "context/technical" as the default folder
   - Enable "Always update internal links"

3. **Configure Templater Plugin**
   - Go to Settings → Templater
   - Set template folder to "templates"
   - Enable "Trigger templater on new file creation"

4. **Connect to Remote Repository**
   - Open terminal or command prompt
   - Navigate to knowledge repository folder
   - Run the following commands:
     ```bash
     git remote add origin https://github.com/your-organization/your-repo.git
     git push -u origin main
     ```

#### 8.1.2 Initial Content Creation

1. **Team Information**
   - Create "context/team/members.md" with team member information
   - Create "context/team/roles.md" with role definitions
   - Create "context/process/communication-channels.md" with communication information

2. **Project Information**
   - Create "context/domain/project-overview.md" with project description
   - Create "context/domain/terminology.md" with key terms and definitions
   - Create "context/domain/requirements.md" with high-level requirements

3. **Technical Foundation**
   - Create "context/technical/architecture.md" with system architecture
   - Create "context/technical/technologies.md" with key technologies
   - Create "context/technical/standards.md" with coding and documentation standards

### 8.2 Team Ritual Implementation

#### 8.2.1 Context Curation Setup

1. **Schedule Regular Sessions**
   - Add 15-minute daily curation session to team calendar
   - Add 30-minute weekly review to team calendar
   - Assign initial facilitator role

2. **Prepare Templates**
   - Ensure daily and weekly templates are available in the repository
   - Customize templates if needed for team context
   - Create process document explaining the ritual

3. **Conduct First Session**
   - Follow the daily curation template
   - Have each team member contribute one knowledge element
   - Document the session using the template
   - Commit the results to the repository

#### 8.2.2 AI-Assisted Documentation Setup

1. **HedgeDoc Template Creation**
   - Create standard meeting note template in HedgeDoc
   - Ensure template includes tagging conventions (#decision, #action)
   - Share template with team

2. **Process Documentation**
   - Create "context/process/ai-documentation-process.md"
   - Document step-by-step process for meeting documentation
   - Include examples of good documentation

3. **First Meeting Implementation**
   - Apply process to the next team meeting
   - Capture notes in HedgeDoc
   - Process with AI using the meeting summary prompt
   - Review, refine, and commit to repository

#### 8.2.3 Prompt Development Workshop Setup

1. **Workshop Preparation**
   - Schedule first bi-weekly prompt workshop (45 minutes)
   - Identify 2-3 initial use cases for prompt development
   - Create preparation document for each use case

2. **Prepare Environment**
   - Ensure Open-webui is configured and accessible
   - Have examples of current prompts and outputs
   - Create "prompts/templates/prompt-template.md" as a standard format

3. **Conduct Initial Workshop**
   - Follow prompt development process
   - Document created prompts in the repository
   - Test prompts with realistic scenarios
   - Commit results to repository

### 8.3 Initial Prompt Library

Establish initial prompt library with essential prompts for Phase 1:

1. **Documentation Prompts**
   - Meeting summary prompt
   - Action item extraction prompt
   - Decision documentation prompt

2. **Context Management Prompts**
   - Context extraction prompt
   - Context organization prompt
   - Knowledge gap identification prompt

3. **General Assistance Prompts**
   - Documentation improvement prompt
   - Clarity enhancement prompt
   - Terminology standardization prompt

For each prompt:
1. Create a file in the appropriate subdirectory of "prompts/"
2. Follow the prompt documentation template
3. Include example inputs and outputs
4. Test with Open-webui before finalizing

### 8.4 Workflow Integration

#### 8.4.1 Basic Workflow Integration

1. **Git Integration Workflow**
   - Document process for pushing and pulling repository changes
   - Create simple cheat sheet for common Git operations
   - Establish branch strategy if needed

2. **Documentation Flow**
   - Document process from meeting to knowledge repository
   - Create workflow diagram showing tool connections
   - Define responsibilities for each step

3. **Knowledge Update Flow**
   - Document process for updating existing knowledge
   - Establish review process for significant changes
   - Define conflict resolution approach

#### 8.4.2 LangFlow Workflows (Optional)

If using LangFlow for workflow automation:

1. **Meeting Summary Workflow**
   - Create workflow for processing meeting notes
   - Connect to Ollama for LLM processing
   - Add prompt templates as components
   - Test with sample meeting notes

2. **Context Extraction Workflow**
   - Create workflow for identifying context elements
   - Connect to prompt library
   - Add filtering for relevant elements
   - Test with sample discussions

3. **Documentation Export Workflow**
   - Create workflow for exporting processed content
   - Format according to repository standards
   - Prepare for manual import to Obsidian
   - Test with representative content

## 9. Testing Requirements

### 9.1 Component Testing

Each component should be tested individually to verify functionality:

#### 9.1.1 Ollama Testing

1. **Base Functionality Test**
   - Verify Ollama server is running
   - Confirm API accessibility
   - Test basic model loading

2. **Model Performance Test**
   - Verify model response quality
   - Measure response time
   - Assess memory usage

3. **API Reliability Test**
   - Test API under multiple requests
   - Verify error handling
   - Test recovery from failures

#### 9.1.2 Open-webui Testing

1. **Interface Functionality Test**
   - Verify UI accessibility
   - Test conversation functionality
   - Confirm history persistence

2. **Prompt Management Test**
   - Create and save prompts
   - Test prompt effectiveness
   - Verify prompt library access

3. **Integration Test**
   - Verify Ollama connection
   - Test model switching
   - Confirm response formatting

#### 9.1.3 Knowledge Repository Testing

1. **Obsidian Functionality Test**
   - Verify vault access
   - Test template usage
   - Confirm linking functionality

2. **Git Integration Test**
   - Test commit operations
   - Verify push/pull functionality
   - Confirm conflict resolution

3. **Structure Test**
   - Verify folder structure integrity
   - Test file naming conventions
   - Confirm template accessibility

### 9.2 Integration Testing

Test end-to-end workflows to verify component integration:

#### 9.2.1 Context Curation Workflow

1. **Daily Curation Test**
   - Follow daily curation process
   - Verify template application
   - Test knowledge capture
   - Confirm Git operations

2. **Weekly Review Test**
   - Execute weekly review process
   - Verify metrics collection
   - Test repository assessment
   - Confirm documentation update

#### 9.2.2 Documentation Workflow

1. **Meeting Documentation Test**
   - Capture notes in HedgeDoc
   - Process with AI assistance
   - Transfer to knowledge repository
   - Verify format and organization

2. **AI Summary Test**
   - Test AI summarization quality
   - Verify decision and action extraction
   - Confirm format compliance
   - Measure time efficiency

#### 9.2.3 Prompt Development Workflow

1. **Workshop Process Test**
   - Execute prompt development process
   - Test collaborative refinement
   - Verify prompt effectiveness
   - Confirm documentation quality

2. **Prompt Usage Test**
   - Apply developed prompts to real scenarios
   - Measure success rate
   - Verify consistency across team members
   - Test prompt reusability

### 9.3 User Acceptance Testing

Validate the complete system from a user perspective:

#### 9.3.1 Developer Experience Testing

1. **Knowledge Access Test**
   - Measure time to find specific information
   - Test search effectiveness
   - Verify link navigation
   - Assess overall usability

2. **Documentation Efficiency Test**
   - Measure time to document a meeting
   - Compare AI-assisted vs. manual documentation
   - Assess quality of resulting documentation
   - Gather developer feedback

3. **LLM Interaction Test**
   - Test prompt effectiveness
   - Measure response quality
   - Assess overall user experience
   - Identify usability improvements

#### 9.3.2 Team Lead Experience Testing

1. **Ritual Facilitation Test**
   - Test ritual template clarity
   - Assess time required for facilitation
   - Measure team participation
   - Gather facilitator feedback

2. **Knowledge Management Test**
   - Assess repository organization
   - Test knowledge discovery
   - Verify version control effectiveness
   - Measure team-wide usage

3. **Process Improvement Test**
   - Identify pain points in current implementation
   - Test potential improvements
   - Measure impact on efficiency
   - Gather team feedback

## 10. Security Considerations

### 10.1 Authentication and Authorization

#### 10.1.1 Knowledge Repository

1. **Git Authentication**
   - Use HTTPS or SSH for repository access
   - Implement personal access tokens for automation
   - Configure appropriate permissions on repository

2. **Obsidian Security**
   - Local vault without cloud sync (unless explicitly configured)
   - No direct authentication (relies on OS-level security)
   - Consider file encryption for sensitive information

#### 10.1.2 Collaborative Tools

1. **HedgeDoc Authentication**
   - Configure user accounts for team members
   - Enable email verification if needed
   - Set appropriate access controls for documents
   - Consider LDAP/OAuth integration for enterprise environments

2. **Open-webui Authentication**
   - Basic authentication configuration
   - API key management for integration
   - Session management and timeout settings

### 10.2 Data Privacy

#### 10.2.1 LLM Interaction Privacy

1. **Local LLM Advantages**
   - All processing occurs locally
   - No data sent to external services
   - Complete control over data usage

2. **Prompt and Response Privacy**
   - Conversations stored locally
   - History accessible only to team members
   - No external logging or monitoring

3. **Sensitive Information Handling**
   - Guidance for not including sensitive data in prompts
   - Process for sanitizing examples and test cases
   - Clear documentation of privacy boundaries

#### 10.2.2 Knowledge Repository Privacy

1. **Repository Access Control**
   - Private Git repository
   - Team-specific access permissions
   - No public exposure of internal content

2. **Sensitive Content Management**
   - Guidelines for content appropriate for the repository
   - Process for handling potentially sensitive information
   - Regular review for inadvertent exposure

### 10.3 Network Security

#### 10.3.1 Local Deployment

1. **Network Isolation**
   - Components run on localhost by default
   - No external network exposure
   - Firewall configuration for local-only access

2. **Port Security**
   - Default ports only accessible on localhost
   - Document port usage for firewall configuration
   - No unnecessary port exposure

#### 10.3.2 Team Server Deployment

1. **Server Hardening**
   - Basic server security configuration
   - Regular updates and patches
   - Minimal service exposure

2. **Access Control**
   - HTTPS for all web interfaces
   - VPN or internal network requirement
   - IP-based access restrictions where possible

3. **Data Transmission**
   - Encrypted connections for all services
   - Certificate management for HTTPS
   - Secure Git communication (HTTPS/SSH)

## 11. Appendices

### 11.1 Ritual Templates

See Section 6.2 for detailed ritual templates.

### 11.2 Knowledge Organization Templates

#### 11.2.1 Domain Knowledge Template
```markdown
# [Domain Concept]

## Definition
[Clear, concise definition of the concept]

## Key Characteristics
- [Characteristic 1]
- [Characteristic 2]
- [Characteristic 3]

## Relationships
- Related to: [[Other Concept 1]], [[Other Concept 2]]
- Part of: [[Larger Concept]]
- Contains: [[Smaller Concept 1]], [[Smaller Concept 2]]

## Examples
- [Example 1]
- [Example 2]

## Additional Resources
- [Resource 1]
- [Resource 2]

## Notes
[Any additional information or context]
```

#### 11.2.2 Technical Knowledge Template
```markdown
# [Technical Element]

## Purpose
[What this technology/component/pattern is used for]

## Implementation Details
[Key technical specifications or implementation notes]

## Usage Guidelines
[How and when to use this technical element]

## Examples
```[language]
[Example code or configuration]
```

## Dependencies
- Requires: [[Dependency 1]], [[Dependency 2]]
- Used by: [[Component 1]], [[Component 2]]

## Alternatives
- [[Alternative 1]]: [Brief comparison]
- [[Alternative 2]]: [Brief comparison]

## Decision Context
[Link to decision record if applicable]

## Notes
[Any additional technical details or caveats]
```

#### 11.2.3 Decision Record Template
```markdown
# Decision: [Title]

## Date
[Decision date]

## Status
[Proposed | Accepted | Deprecated | Superseded by [link]]

## Context
[Description of the problem and why a decision was needed]

## Options Considered
### Option 1: [Option title]
- Pros: [List of advantages]
- Cons: [List of disadvantages]

### Option 2: [Option title]
- Pros: [List of advantages]
- Cons: [List of disadvantages]

## Decision
[The option chosen with justification]

## Consequences
[Positive and negative consequences of the decision]

## Implementation
[Brief notes on implementation details or requirements]

## Related Decisions
- [Link to related decision 1]
- [Link to related decision 2]

## Notes
[Any additional information or context]
```

### 11.3 Common Prompts Library

See Section 6.3 for detailed prompt library templates.

### 11.4 Docker Compose Configuration

See Section 7.3 for Docker Compose configuration.

### 11.5 Troubleshooting Guide

#### 11.5.1 Installation Issues

**Problem: Docker installation fails**
- **Solution 1:** Check system requirements
- **Solution 2:** Try manual Docker installation from official website
- **Solution 3:** Verify user permissions and group membership

**Problem: Ollama models won't download**
- **Solution 1:** Check internet connection and firewall settings
- **Solution 2:** Verify disk space availability
- **Solution 3:** Try downloading a smaller model first

**Problem: Docker containers won't start**
- **Solution 1:** Check port conflicts with existing services
- **Solution 2:** Verify Docker service is running
- **Solution 3:** Check container logs with `docker logs <container_name>`

#### 11.5.2 Knowledge Repository Issues

**Problem: Git synchronization errors**
- **Solution 1:** Check network connectivity to repository
- **Solution 2:** Verify credentials and access permissions
- **Solution 3:** Resolve merge conflicts according to Git documentation

**Problem: Obsidian plugin issues**
- **Solution 1:** Update plugins to latest versions
- **Solution 2:** Check plugin compatibility with Obsidian version
- **Solution 3:** Reinstall problematic plugins

**Problem: Template application fails**
- **Solution 1:** Verify template folder configuration
- **Solution 2:** Check template format and syntax
- **Solution 3:** Restart Obsidian and try again

#### 11.5.3 LLM Performance Issues

**Problem: Slow LLM responses**
- **Solution 1:** Check system resource usage during operation
- **Solution 2:** Try a smaller model if available
- **Solution 3:** Optimize prompt length and complexity

**Problem: Low-quality LLM outputs**
- **Solution 1:** Refine prompts with more specific instructions
- **Solution 2:** Try a different model if available
- **Solution 3:** Break complex tasks into smaller steps

**Problem: Memory issues with LLM**
- **Solution 1:** Restart Ollama service
- **Solution 2:** Check for other memory-intensive applications
- **Solution 3:** Consider a smaller model or hardware upgrade
