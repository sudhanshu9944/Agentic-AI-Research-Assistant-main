# Architecture

The browser runs React/Vite. FastAPI coordinates a LangGraph workflow, calls an
OpenAI-compatible Groq endpoint, gathers public search evidence and persists
completed sessions as JSON. PDF and Markdown are separate export requests.

## Request flow

1. TopicPage collects a topic and model.
2. `POST /recommendations` calls the planner and returns suggested angles.
3. OutlinePage lets the user select, exclude or add angles.
4. `POST /research` builds the selected scope, searches, analyzes evidence,
   summarizes, writes the report and atomically saves the completed session.
5. ReviewPage shows the summary, selected/excluded scope, sources and evidence gaps.
6. The user explicitly chooses PDF or Markdown export. Research never silently
   downloads a PDF.

Workflow: Planner → Researcher → Analyst → Summarizer → Reporter → Memory.
Selected topics determine the plan directly rather than being overwritten by
another recommendation. Automatic planning remains available to API clients
that omit selected topics. Essential generation/search/storage failures stop
completion; optional reranking failure preserves the original source order.

## Frontend boundaries

| Location | Responsibility |
| --- | --- |
| `src/app/App.jsx` | Compose the pages, header and footer. |
| `src/app/useWorkspace.js` | Coordinate research, history, account and export state. |
| `src/features/research/components` | Topic, outline, review, report and history views. |
| `src/features/account` | Local account dialog and browser storage service. |
| `src/features/theme` | Persist the light/dark preference. |
| `src/services` | HTTP requests and file downloads. |
| `src/config/project.js` | Repository URL, credits and stack text. |
| `src/styles` | Tokens, shared layout, feature styles, themes and responsive rules. |

## Backend boundaries

| Location | Responsibility |
| --- | --- |
| `backend/api/routes` | Health, research, history and export HTTP boundaries. |
| `backend/schemas` | Request/response validation. |
| `backend/graph` | Workflow state and graph composition. |
| `backend/agents` | Planner, researcher, analyst, summarizer, reporter. |
| `backend/tools` | Provider and public search adapters. |
| `backend/memory` | Session validation and atomic JSON persistence. |
| `backend/export` | PDF/Markdown rendering and bundled font assets. |
| `backend/config.py` | Backend environment configuration. |

## Evidence and storage

Evidence consists of bounded public search snippets/extracts, not full document
crawls. Wikipedia or search providers can fail or rate-limit requests. Sources
are deduplicated and bounded before analysis; evidence gaps are advisory.
The application does not ingest uploaded PDFs. Its PDF feature exports reports.

Each PDF owns its section numbering. Unicode fonts and shaping are bundled;
long content wraps, and oversized tables switch to a flowing labeled layout.
PDF creation runs outside the async event loop. Downloads have safe Unicode
filenames; Markdown frontmatter is serialized safely.

Browser accounts store salted PBKDF2 password hashes and demo credits locally.
They do not authenticate API calls. Clearing browser storage removes them.
The backend history is shared by its instance. The progress UI is an estimate
because research currently returns one final response, not streamed progress.
For public production use, add server identity, per-user storage, rate limits
and durable storage before treating this as a private service.
