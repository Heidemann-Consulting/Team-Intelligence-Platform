# Table of Contents

- [Table of Contents](#table-of-contents)
- [Contributing to Team Intelligence Platform (TIP)](#contributing-to-team-intelligence-platform-tip)
  - [Table of Contents](#table-of-contents-1)
  - [Introduction](#introduction)
  - [Ways to Contribute](#ways-to-contribute)
    - [Code Contributions](#code-contributions)
    - [Documentation Contributions](#documentation-contributions)
    - [Ritual Templates and Knowledge Architecture](#ritual-templates-and-knowledge-architecture)
    - [Community Support](#community-support)
    - [Implementation Experiences](#implementation-experiences)
  - [Architecture Overview](#architecture-overview)
  - [Technical Features](#technical-features)
  - [Prerequisites](#prerequisites)
  - [Project Structure](#project-structure)
  - [Setup and Configuration](#setup-and-configuration)
  - [Deployment](#deployment)
  - [Stopping the Application](#stopping-the-application)
  - [Troubleshooting](#troubleshooting)
  - [Detailed Product Requirements Document](#detailed-product-requirements-document)
  - [Detailed Software Requirements Specification](#detailed-software-requirements-specification)
  - [Executing Backend Tests (Work in progress)](#executing-backend-tests-work-in-progress)
    - [Navigate to the Backend Directory:](#navigate-to-the-backend-directory)
    - [Ensure Dependencies are Installed:](#ensure-dependencies-are-installed)
    - [Run Pytest:](#run-pytest)
  - [Executing Frontend Tests (Work in progress)](#executing-frontend-tests-work-in-progress)
    - [Navigate to the Frontend Directory:](#navigate-to-the-frontend-directory)
    - [Ensure Dependencies are Installed:](#ensure-dependencies-are-installed-1)
    - [Base tests in watch mode](#base-tests-in-watch-mode)
    - [GUI Mode](#gui-mode)
    - [Headless Mode](#headless-mode)
  - [Contribution Process](#contribution-process)
    - [1. Finding an Issue](#1-finding-an-issue)
    - [2. Issue Discussion](#2-issue-discussion)
    - [3. Development](#3-development)
    - [4. Pull Request](#4-pull-request)
    - [5. After Merge](#5-after-merge)
  - [Phase-Specific Contributions](#phase-specific-contributions)
    - [Phase 1: The Cognitive Foundation](#phase-1-the-cognitive-foundation)
    - [Phase 2: The Collaborative Acceleration](#phase-2-the-collaborative-acceleration)
    - [Phase 3: The Transformative Intelligence](#phase-3-the-transformative-intelligence)
  - [Code Standards and Guidelines](#code-standards-and-guidelines)
    - [General Principles](#general-principles)
    - [Language-Specific Guidelines](#language-specific-guidelines)
    - [Commit Guidelines](#commit-guidelines)
  - [Documentation Guidelines](#documentation-guidelines)
    - [Structure](#structure)
    - [Content](#content)
    - [Technical Documentation](#technical-documentation)
    - [User Documentation](#user-documentation)
  - [Testing Requirements](#testing-requirements)
    - [Unit Tests](#unit-tests)
    - [Integration Tests](#integration-tests)
    - [End-to-End Tests](#end-to-end-tests)
  - [Community and Communication](#community-and-communication)
    - [Discussion Forums](#discussion-forums)
    - [Synchronous Communication](#synchronous-communication)
    - [Asynchronous Communication](#asynchronous-communication)
  - [Governance Model](#governance-model)
    - [Project Structure](#project-structure-1)
    - [Decision Making Process](#decision-making-process)
    - [Becoming a Maintainer](#becoming-a-maintainer)
  - [Recognition and Acknowledgment](#recognition-and-acknowledgment)
  - [Enterprise Contribution Model](#enterprise-contribution-model)
    - [Contribution Agreements](#contribution-agreements)
    - [Secure Contribution Workflow](#secure-contribution-workflow)
    - [Enterprise Use Case Program](#enterprise-use-case-program)
    - [Enterprise Contribution Opportunities](#enterprise-contribution-opportunities)
  - [Thank You!](#thank-you)

# Contributing to Team Intelligence Platform (TIP)

First off, thank you for considering contributing to the Team Intelligence Platform! TIP is an open-source project designed to transform how product development teams integrate AI into their collaborative workflows, enabling AI to become a true team member rather than merely an individual productivity tool.

This document provides guidelines and instructions for contributing to TIP. By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Table of Contents

1. [Introduction](#introduction)
2. [Ways to Contribute](#ways-to-contribute)
3. [Development Environment Setup](#development-environment-setup)
4. [Contribution Process](#contribution-process)
5. [Phase-Specific Contributions](#phase-specific-contributions)
6. [Code Standards and Guidelines](#code-standards-and-guidelines)
7. [Documentation Guidelines](#documentation-guidelines)
8. [Testing Requirements](#testing-requirements)
9. [Community and Communication](#community-and-communication)
10. [Governance Model](#governance-model)
11. [Recognition and Acknowledgment](#recognition-and-acknowledgment)
12. [Enterprise Contribution Model](#enterprise-contribution-model)

## Introduction

The Team Intelligence Platform (TIP) is an innovative solution designed to transform how product development teams integrate AI into their collaborative workflows. Unlike traditional approaches where AI is used as an individual productivity tool, TIP enables "AI Co-Management" – a paradigm where AI becomes an integrated team member contributing to collective intelligence.

TIP has a phased implementation framework:
1. **The Cognitive Foundation** - Essential rituals for capturing, preserving, and leveraging team knowledge with basic AI assistance
2. **The Collaborative Acceleration** - Intermediate rituals that deepen AI integration into team workflows and decision-making
3. **The Transformative Intelligence** - Advanced rituals that create breakthrough team performance through sophisticated human-AI collaboration

As an open-source project, we welcome contributions from individuals and organizations of all kinds. Whether you're fixing bugs, adding features, improving documentation, or sharing your implementation experiences, your contributions are valuable to the TIP community.

## Ways to Contribute

There are many ways to contribute to TIP, regardless of your technical expertise:

### Code Contributions
- Implementing new features
- Fixing bugs and issues
- Improving performance and scalability
- Extending integrations with other tools and systems
- Writing automated tests

### Documentation Contributions
- Improving existing documentation
- Creating tutorials and guides
- Translating documentation
- Adding code comments and examples
- Creating diagrams and visual aids

### Ritual Templates and Knowledge Architecture
- Creating templates for team rituals
- Developing knowledge organization patterns
- Sharing effective prompt structures
- Creating LangFlow workflow templates
- Documenting effective team practices

### Community Support
- Answering questions in discussions and issues
- Reviewing pull requests
- Mentoring new contributors
- Testing new releases and providing feedback
- Sharing success stories and case studies

### Implementation Experiences
- Documenting your organization's TIP implementation
- Sharing metrics and outcomes
- Creating adaptation guides for specific industries
- Developing custom integrations
- Providing feedback on challenges and solutions

## Architecture Overview

This application consists of:

* **Frontend:** A React Single-Page Application (SPA) providing the user interface.
* **Backend:** A FastAPI (Python) application providing the API, business logic, and orchestrating interactions.
* **Database:** A PostgreSQL database for persistent storage.
* **AI Server:** Integration with a local Ollama server for LLM capabilities.

## Technical Features

* Team-based accounts for collaboration.
* Management of Documents, Templates, and Process Workflows.
* In-app Markdown editor with versioning (Save, Undo/Load Previous, Redo/Load Next).
* Process Workflow execution using local Ollama models.
* Content sharing (global read-only visibility).
* Content duplication.
* Full-text search (basic implementation).
* Admin interface for team management.
* Dockerized deployment via `docker-compose`.

## Prerequisites

See [README.md](README.md).

## Project Structure

See [README.md](README.md).

## Setup and Configuration

See [README.md](README.md).

## Deployment

See [README.md](README.md).

## Stopping the Application

See [README.md](README.md).

## Troubleshooting

See [README.md](README.md).

## Detailed Product Requirements Document

See [TIP Product Requirements Document](docs/tip-prd.md).

## Detailed Software Requirements Specification

See [TIP Software Requirements Specification](docs/tip-srs.md).

## Executing Backend Tests (Work in progress)

Here's how you can run all the tests:

### Navigate to the Backend Directory:

Open your terminal or command prompt and change your current directory to the root of the backend application:

```bash
cd ./ulacm_backend
```

### Ensure Dependencies are Installed:

Make sure all dependencies, including development dependencies (like pytest, pytest-asyncio, freezegun, httpx), are installed. If you haven't already, run:

```bash
poetry env use python3.11
poetry install --with dev --no-root
```

### Run Pytest:

Execute the pytest command in your terminal from the ulacm_backend directory:

```bash
poetry run pytest
```

pytest will automatically discover all files named test_*.py or *_test.py and all functions prefixed with test_ within the tests directory and its subdirectories.
It will execute each test function.
You will see output indicating the progress and results (e.g., dots . for passed tests, F for failures, E for errors).
A summary will be printed at the end showing the total number of tests run, passed, failed, etc.
Example Output (Simplified):

============================= test session starts ==============================
platform linux -- Python 3.10.x, pytest-8.x.x, pluggy-1.x.x
rootdir: /path/to/your/project/ULACM2/ulacm_backend
plugins: asyncio-0.23.x
collected XX items

tests/core/test_security.py ........                                      [ 10%]
tests/crud/test_crud_content_item.py .........                            [ 25%]
tests/crud/test_crud_content_version.py .....                             [ 35%]
tests/crud/test_crud_search.py .....                                      [ 45%]
tests/crud/test_crud_team.py ........                                     [ 58%]
tests/db/test_models.py .....                                             [ 68%]
tests/services/test_ollama_service.py .......                             [ 80%]
tests/services/test_workflow_parser.py ..........                         [ 95%]
tests/services/test_workflow_service.py ....                              [100%]

============================== XX passed in X.XXs ===============================

If you want to repeat the tests after fixes it is a good idea to clean the caches:

```bash
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

## Executing Frontend Tests (Work in progress)

Here's how you can run all the tests:

### Navigate to the Frontend Directory:

Open your terminal or command prompt and change your current directory to the root of the backend application:

```bash
cd ./ulacm_frontend
```

### Ensure Dependencies are Installed:

Make sure all dependencies, including development dependencies, are installed. If you haven't already, run:

```bash
npm install
```

### Base tests in watch mode

To automatically re-run tests whenever you save a file, you can run Jest in watch mode:

```bash
npm test -- --watch
# or 'npm test -- --watchAll'
# Note the extra '--' needed with npm run to pass arguments to the script
```

Watch mode is very useful as it provides instant feedback as you develop components and their corresponding tests.

Jest will output the results directly to your terminal, showing:
* Which test suites (files) passed or failed.
* How many individual tests passed or failed.
* Details about any failing tests, including error messages and code snippets.
* A test coverage summary.

### GUI Mode

Run

```bash
npm run cypress:open
```

This opens the Cypress Test Runner, where you can select and run specific E2E tests interactively.
Make sure your frontend development server (yarn dev or npm run dev) is running first.

### Headless Mode

Run

```bash
npm run cypress:run.
```

This executes all E2E tests in a headless browser (usually Electron by default) and outputs results to the console. This is typically used in CI environments.
Your frontend server needs to be running for this as well, unless you configure Cypress to start it.

## Contribution Process

### 1. Finding an Issue

- Browse existing [issues](https://github.com/organization/team-intelligence-platform/issues) to find something to work on
- Look for issues labeled `good first issue` if you're new to the project
- Feel free to ask questions in issue comments if something is unclear
- If you want to work on something that doesn't have an issue yet, create one first to discuss

### 2. Issue Discussion

Before starting work on a significant change:

- Comment on the issue to let others know you're working on it
- Discuss your approach to get feedback
- Understand acceptance criteria and expected outcomes
- For major features, creating a design document may be necessary

### 3. Development

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement Your Changes**
   - Follow the code standards and guidelines
   - Keep changes focused on the specific issue
   - Add tests for new functionality
   - Update documentation as needed

3. **Commit Your Changes**
   ```bash
   git commit -m "Descriptive commit message"
   ```

   Please use conventional commit messages with the following format:
   ```
   type(scope): description

   [optional body]

   [optional footer]
   ```

   Types include:
   - feat: A new feature
   - fix: A bug fix
   - docs: Documentation changes
   - style: Code style changes (formatting, etc.)
   - refactor: Code changes that neither fix bugs nor add features
   - perf: Performance improvements
   - test: Adding or updating tests
   - chore: Maintenance tasks

4. **Stay Up to Date**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

### 4. Pull Request

1. **Push Your Changes**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**
   - Go to the repository on GitHub
   - Create a new Pull Request
   - Use the PR template and fill in all required information
   - Link to the related issue(s)

3. **Code Review Process**
   - Maintainers will review your PR
   - Address any feedback or requested changes
   - CI checks must pass before merging
   - At least one maintainer approval is required

4. **Merge**
   - Once approved, a maintainer will merge your PR
   - Squash merging is preferred for most contributions

### 5. After Merge

- Your contribution will be included in the next release
- You'll be added to the contributors list
- Consider helping review other PRs

## Phase-Specific Contributions

TIP is implemented in three phases, each with specific contribution opportunities:

### Phase 1: The Cognitive Foundation

Key contribution areas:
- Knowledge structure templates
- Base ritual facilitation guides
- Documentation for basic installation and configuration

### Phase 2: The Collaborative Acceleration

Key contribution areas:
- Measurement frameworks and dashboards
- Templates for advanced rituals
- Knowledge relationship mapping patterns
- Case studies and implementation guides

### Phase 3: The Transformative Intelligence

Key contribution areas:
- Custom middleware for seamless integration
- Advanced workflows for complex analysis and decision-making
- Cross-team knowledge sharing mechanisms
- Enterprise deployment patterns and guidance
- Strategic impact assessment frameworks
- Advanced AI collaboration patterns

## Code Standards and Guidelines

### General Principles

- Write clean, readable, and maintainable code
- Follow the SOLID principles
- Keep functions and methods small and focused
- Write self-documenting code with clear variable and function names
- Include comments for complex logic

### Language-Specific Guidelines

**JavaScript/TypeScript:**
- Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use ES6+ features appropriately
- Prefer async/await over promise chains
- Use TypeScript types and interfaces

**Python:**
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints
- Write docstrings for functions and classes
- Use virtual environments

**Markdown:**
- Use consistent headers (# for title, ## for sections, etc.)
- Include a table of contents for longer documents
- Use syntax highlighting for code blocks
- Check links to ensure they work

### Commit Guidelines

- Use descriptive commit messages
- Reference issue numbers when applicable
- Keep commits focused on single changes
- Squash multiple commits if they represent a single logical change

## Documentation Guidelines

Good documentation is critical for TIP's success. Please follow these guidelines:

### Structure

- Use clear, descriptive titles and headings
- Include a table of contents for longer documents
- Group related information logically
- Use consistent formatting throughout

### Content

- Write in clear, concise language
- Include step-by-step instructions where applicable
- Provide examples for complex concepts
- Update existing documentation when adding new features

### Technical Documentation

- Document API endpoints with parameters and responses
- Include configuration options and their defaults
- Explain architecture decisions and patterns
- Provide troubleshooting guidance

### User Documentation

- Focus on the user's perspective and goals
- Include screenshots and visuals where helpful
- Provide both quick-start and detailed guides
- Document best practices and common patterns

## Testing Requirements

### Unit Tests

- All new code should have unit tests
- Aim for high test coverage, especially for core functionality
- Tests should be fast and independent
- Mock external dependencies

### Integration Tests

- Write tests for API endpoints
- Test integration between components
- Include happy path and error scenarios
- Test with realistic data

### End-to-End Tests

- Cover critical user flows
- Test deployment processes
- Include performance testing for key features
- Validate cross-component integration

## Community and Communication

### Discussion Forums

- GitHub Discussions for feature ideas and general questions
- Issue tracker for bugs and specific tasks
- Regular community calls (see schedule in [COMMUNITY.md](COMMUNITY.md))

### Synchronous Communication

- Monthly contributor calls (first Thursday of each month)
- Quarterly roadmap planning sessions
- Implementation workshops (announced on the project website)

### Asynchronous Communication

- Project mailing list for announcements
- Discord server for casual discussion and quick questions
- Project blog for longer-form content and updates

## Governance Model

### Project Structure

- **Initial Stewardship:** Heidemann Consulting serves as the initial project steward
- **Technical Steering Committee (TSC):** Makes decisions about project direction and standards
- **Maintainers:** Review and merge contributions for specific components
- **Contributors:** Anyone who contributes to the project

### Decision Making Process

- Most decisions are made through consensus
- For significant changes, we use a Request for Comments (RFC) process
- The TSC has final decision-making authority when consensus cannot be reached
- We strive for transparency in all decision-making

### Becoming a Maintainer

- Consistent, quality contributions to the project
- Demonstrated understanding of the project goals and standards
- Regular participation in code reviews and discussions
- Nomination by existing maintainers and approval by the TSC

For more details, see [GOVERNANCE.md](GOVERNANCE.md).

## Recognition and Acknowledgment

We value all contributions and recognize contributors in several ways:

- All contributors are listed in our [CONTRIBUTORS.md](CONTRIBUTORS.md) file
- Significant contributions are highlighted in release notes
- Regular contributors may be invited to become maintainers
- We showcase case studies and implementation stories on our website

## Enterprise Contribution Model

For enterprise contributors, we provide additional resources and processes:

### Contribution Agreements

- Standard individual Contributor License Agreement (CLA)
- Corporate CLA for organizational contributions
- Special attribution options for significant corporate contributions

### Secure Contribution Workflow

- Guidance for enterprise code review processes
- Security considerations for enterprise contributors
- Compliance documentation and guidance

### Enterprise Use Case Program

- Framework for documenting enterprise implementations
- Anonymous case study options
- Impact measurement templates
- Enterprise implementation advisory group

### Enterprise Contribution Opportunities

- Sponsoring specific feature development
- Contributing enterprise integration patterns
- Sharing implementation best practices
- Participating in enterprise focus groups

## Thank You!

Your contributions help make TIP a powerful tool for transforming how teams work with AI. We're excited to see what you build and learn from your experiences!

If you have any questions or need assistance, please don't hesitate to reach out to the maintainers or the community.

---

_This document is maintained by the TIP Technical Steering Committee and will evolve as the project grows._
