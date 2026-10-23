<div align="center">

# Research.AI

**Choose the scope. Review the findings. Export when ready.**

A research workspace built with React, FastAPI, LangGraph and Groq.

[![Quality checks](https://github.com/sudhanshu9944/Agentic-AI-Research-Assistant-main/actions/workflows/quality.yml/badge.svg)](https://github.com/sudhanshu9944/Agentic-AI-Research-Assistant-main/actions/workflows/quality.yml)

[Getting started](#getting-started) · [How it works](#how-it-works) · [Architecture](docs/ARCHITECTURE.md) · [Deployment](docs/DEPLOYMENT.md)

</div>

![Research.AI workspace in light mode](docs/screenshots/workspace-light.png)

## Overview

Research.AI turns a topic into a report you can inspect before downloading.
Choose from suggested research angles, add your own, and review the summary,
sources and evidence gaps before generating a PDF or Markdown file.

| Feature | What you can do |
| --- | --- |
| Guided research | Choose suggested angles with checkboxes or add a custom topic. |
| Review before export | Read the summary, selected scope, excluded topics and evidence gaps. |
| Source references | Inspect the public search excerpts used in the report. |
| PDF and Markdown | Download the reviewed report in either format. |
| Research library | Reopen reports saved by the backend installation. |
| Light and dark mode | Keep your preferred theme across visits. |
| Local accounts | Sign up in your browser and track demo app tokens. |

<details>
<summary><strong>Dark mode</strong></summary>

![Research.AI workspace in dark mode](docs/screenshots/workspace-dark.png)

</details>

<details>
<summary><strong>Research preview</strong></summary>

![Research summary and scope review](docs/screenshots/research-preview.png)

</details>

## Getting started

Install **Python 3.12** and **Node.js 24**, then open a terminal in the project root.

**1. Install the backend**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

**2. Configure the API key**

Copy `.env.example` to `.env` if the file does not already exist. Open `.env`
and set `GROQ_API_KEY` to your own Groq key. Keep this file private.

**3. Start the backend**

```powershell
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

**4. Start the frontend in a second terminal**

```powershell
cd frontend
npm ci
npm run dev
```

Open **http://127.0.0.1:5173**. Keep both terminals running.

See the [local setup guide](docs/LOCAL_SETUP.md) for macOS/Linux, daily startup,
API-key replacement, configuration and troubleshooting. The backend's API
reference is available at **http://127.0.0.1:8000/docs** while it is running.

## How it works

1. Create a browser-local account or log in to an existing one.
2. Enter a topic and request suggested research angles.
3. Select the angles to include; add a custom angle if needed.
4. Run the research and review the findings, sources and limitations.
5. Choose **Generate PDF** or **Markdown** when the report is ready.

| Demo app tokens | Amount |
| --- | ---: |
| New account | 100 |
| Topic recommendations | 2 |
| Research | 10 |
| PDF / Markdown export | 0 |

Failed operations refund their reserved app tokens. These browser-local credits
are separate from the AI provider's actual quota.

## Project structure

```text
backend/
  api/              Request validation and HTTP routes
  agents/           Planning, research, analysis and report generation
  graph/            Workflow composition
  services/         Model calls and relevance ranking
  tools/            Public search adapters
  memory/           Saved research sessions
  export/           PDF, Markdown and bundled fonts
frontend/
  src/app/          App composition and workflow state
  src/features/     Research, local accounts and theme
  src/components/   Shared interface components
  src/services/     API client, downloads and link validation
  src/styles/       Layout, components, themes and responsive styles
  tests/            Frontend behavior tests
tests/              Backend regression and security tests
docs/               Setup, architecture and deployment
```

The [architecture guide](docs/ARCHITECTURE.md) explains the request flow and
module boundaries.

## Development

From the project root:

```powershell
.venv\Scripts\python.exe -m ruff check backend tests
.venv\Scripts\python.exe -m ruff format --check backend tests
.venv\Scripts\python.exe -m pytest -q
```

From `frontend`:

```sh
npm run format:check
npm run lint
npm test
npm run build
```

The same checks run through GitHub Actions on pushes and pull requests.

## Deployment and privacy

The current hosting configuration uses a Vercel frontend with a separate
FastAPI backend. Follow the [deployment guide](docs/DEPLOYMENT.md) for build
settings, the backend URL and allowed browser origins.

Accounts and demo credits are stored in your browser. They do not authenticate
API calls; the backend library is shared by its installation. Keep the demo
local/private until server-side authentication, report ownership and quotas
are implemented. See [SECURITY.md](SECURITY.md) for the security boundaries.

Research uses public search excerpts. It does not ingest uploaded PDFs or run
OCR. Search availability and free-provider quotas can affect results.

---

<div align="center">

Made with ❤️ by **Sudhanshu Singh, Himanshu Chauhan, Tanmay Pahuja**

*Built with ❤️ using* React · FastAPI · LangGraph · Groq

</div>
