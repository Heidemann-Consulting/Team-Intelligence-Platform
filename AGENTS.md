# SWE Agent Guidelines

This document provides guidance for AI-based software engineers working on the Team Intelligence Platform (TIP).

## Project Overview

TIP is a self contained, Dockerized web application that enables "AI Co-Management". It allows teams to manage markdown documents, create and execute AI-powered workflows, and collaborate through a shared knowledge base. The platform uses:

- **Backend:** Python 3.11 with FastAPI.
- **Frontend:** React and TypeScript.
- **Database:** PostgreSQL with full-text search.
- **LLM:** A local Ollama server.

Relevant documents for deeper context are [docs/tip-prd.md](docs/tip-prd.md) and [docs/tip-srs.md](docs/tip-srs.md).

The README explains how to configure the environment, generate certificates, run Docker Compose, create database dumps, and restore them.

## Coding Standards

### Python
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/).
- Use type hints and docstrings.

### JavaScript/TypeScript
- Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript).
- Prefer `async/await` and provide TypeScript types.

### Markdown
- Use consistent headers (`#` for titles, `##` for sections, etc.).
- Include a table of contents for long documents.
- Use syntax highlighting for code blocks.

## Commit Messages

Use conventional commit messages:

```
type(scope): description

[optional body]
[optional footer]
```

Reference issue numbers when relevant and keep each commit focused on a single change.

## Testing

### Backend
1. `cd ulacm_backend`
2. `poetry env use python3.11`
3. `poetry install --with dev --no-root`
4. `poetry run pytest`

### Frontend
1. `cd ulacm_frontend`
2. `npm install`
3. `npm test -- --watch`
4. `npm run cypress:open` for the GUI test runner or `npm run cypress:run` for headless mode.

## Important Functionality

Key features described in the PRD and SRS include:

- **AI Co-Management support:** Shared context management, AI-assisted documentation, collaborative prompt creation, and AI-supported decision making.
- **Versioned Markdown documents** with search functionality.
- **Admin-defined templates and workflows** that allow different AI roles (Documentarian, Analyst, Facilitator, etc.).
- **Security best practices:** HTTPS connections, input validation, bcrypt password hashing, and separate admin authentication.

When adding features or fixing issues, ensure they align with the non-functional requirements such as responsiveness (<2s API calls, <3s search) and maintainability through modular code and externalized configuration.

## Deployment Notes

- Use `docker-compose up --build -d` to start the application.
- Environment variables for the backend and compose services are defined via `.env` files as described in the README.
- The Ollama service can be started within Docker Compose or connected externally.

## Further References

- For an overview and high-level description of TIP, see the README.
- Detailed requirements: [docs/tip-prd.md](docs/tip-prd.md) and [docs/tip-srs.md](docs/tip-srs.md).

