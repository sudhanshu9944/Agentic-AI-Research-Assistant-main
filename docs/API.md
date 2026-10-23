# API reference

FastAPI exposes interactive documentation at `http://127.0.0.1:8000/docs`.
The paths below are backend paths; the frontend development proxy adds `/api`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness and whether a provider key is configured; does not validate the key with Groq. |
| POST | `/recommendations` | AI outline suggestions without running research or exporting a file. |
| POST | `/research` | Run research, persist the completed session, return its preview and report. |
| GET | `/history` | List saved sessions in the configured memory directory. |
| GET | `/report/{session_id}` | Retrieve a saved report and scope metadata. |
| POST | `/export/pdf` | Download a saved session as PDF. |
| POST | `/export/markdown` | Download a saved session as Markdown. |

Research request example:

```json
{
  "query": "Solar energy benefits and limitations",
  "model": "openai/gpt-oss-120b",
  "temperature": 0.3,
  "selected_topics": ["Environmental benefits", "Storage limitations"],
  "excluded_topics": ["Policy incentives"]
}
```

For recommendations, send `query`, optionally `model` and `temperature`.
Omitting `selected_topics` on research keeps automatic planning for API clients.
An explicitly empty selection is rejected. Selected scope determines the search
plan; excluded scope is recorded and sent to report generation as a constraint.

Research responses include `session_id`, `research_plan`, `sources`, `insights`,
`summary`, `final_report`, `selected_topics`, `excluded_topics`, `evidence_gaps`,
`logs`, and `created_at`. Evidence gaps are advisory AI assessments.

Exports accept `{"session_id": "saved-session-id"}`. They return binary PDF or
UTF-8 Markdown with a Unicode-safe download filename. Unknown sessions return 404.
Invalid requests return 422, missing provider configuration 503, and failed AI
recommendations 502. Essential research failures stop the request instead of
returning a fabricated successful report. Consult `/docs` for exact field limits.

The API currently has no server authentication or per-user authorization.
Browser demo accounts and credits do not protect these endpoints. History is
shared within the backend instance. Do not treat it as private multi-user storage.
