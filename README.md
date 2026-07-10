# MedIntel AI CRM

Production-ready AI-first CRM for healthcare professionals. Medical representatives can manage HCPs, log structured interactions, or use a LangGraph-powered assistant to extract meeting details, store CRM records, plan follow-ups, and search prior activity.

## Architecture

- **Frontend:** React 19, TypeScript, Redux Toolkit, React Router, React Hook Form, Axios, Tailwind CSS, Recharts, Framer Motion, Lucide icons.
- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, JWT auth, repository and service layers.
- **AI:** LangGraph workflow with intent detection, entity extraction, tool selection, tool execution, and response generation using Groq Llama 3.3 70B by default.
- **Deployment:** Docker Compose with PostgreSQL, API, and Vite-built frontend.

## Quick Start

```bash
cp .env.example .env
# Add GROQ_API_KEY in .env for live AI responses.
docker-compose up --build
```

Open the frontend at `http://localhost:5173` and the API docs at `http://localhost:8000/docs`.

Demo credentials after seeding:

- Email: `rep@medintel.ai`
- Password: `Password123!`

## Folder Structure

```text
backend/app/api          REST routers
backend/app/agents       LangGraph CRM agent
backend/app/auth         JWT and password security
backend/app/models.py    SQLAlchemy relational schema
backend/app/repositories Data access layer
backend/app/services     Business logic
frontend/src/components  Reusable UI and layout
frontend/src/pages       Application pages
frontend/src/redux       Store and slices
frontend/src/services    Axios API client
```

## LangGraph Workflow

1. User message
2. Intent detection
3. Entity extraction with Pydantic structured output
4. Tool selection
5. Tool execution
6. Response generation
7. Structured JSON response

Implemented tools: log interaction, edit interaction, search interaction, HCP summary, follow-up planner, meeting preparation, and analytics generator.

## Database Schema

Core tables include users, HCPs, products, materials, samples, interactions, follow-ups, interaction history, and audit logs. Each table uses UUID primary keys, timestamps, soft delete columns, foreign keys, relationships, and useful indexes.

## Environment Variables

See `.env.example` for all supported values. Required in production: `DATABASE_URL`, `JWT_SECRET_KEY`, `GROQ_API_KEY`, and `FRONTEND_URL`.

## API Documentation

FastAPI exposes OpenAPI and Swagger at `/docs`. Main route groups:

- `/api/v1/auth`
- `/api/v1/users`
- `/api/v1/hcp`
- `/api/v1/interactions`
- `/api/v1/history`
- `/api/v1/dashboard`
- `/api/v1/analytics`
- `/api/v1/ai/chat`
- `/api/v1/tools`

## Testing

```bash
cd backend && pytest
cd frontend && npm test
```

## Sample Prompts And Screenshots

Assistant prompts live in `docs/sample-prompts.md`. Capture product screenshots from the running dashboard, HCP directory, interaction assistant, and analytics pages for portfolio use.

## Resume Highlights

- Built multi-node LangGraph CRM assistant with tool orchestration and structured outputs.
- Designed production-style FastAPI architecture with repository and service layers.
- Implemented healthcare CRM workflows with relational PostgreSQL schema and auditability.
- Created enterprise dashboard UI with protected routing, Redux state, analytics charts, empty/error/loading states, and dark mode.

## Future Improvements

- Real-time token streaming through Server-Sent Events.
- Calendar integrations for follow-up scheduling.
- Organization-level multi-tenancy and SSO.
- Fine-grained compliance exports and PHI redaction workflows.
