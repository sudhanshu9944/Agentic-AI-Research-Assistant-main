# Configuration

The backend reads the root `.env` through `backend/config.py`. Settings load when the process starts: restart the backend after changing them. The source ZIP contains `.env.example`, never a working secret.

## Backend

| Variable | Purpose / default |
|---|---|
| `GROQ_API_KEY` | Private Groq key. Change this line to switch keys. |
| `OPENROUTER_API_KEY` | Legacy alias, used only if `GROQ_API_KEY` is absent. |
| `OPENROUTER_BASE_URL` | `https://api.groq.com/openai/v1`; legacy name retained for compatible providers. |
| `DEFAULT_MODEL` | `openai/gpt-oss-120b`. Must be accessible to the account. |
| `RERANKER_MODEL` | `openai/gpt-oss-20b`. Used for optional batch ranking. |
| `GROQ_TOKEN_BUDGET` | `8000`; request/completion budgeting, not a purchased allocation. |
| `BACKEND_PORT` | `8000`; hosting platforms may supply `PORT`. |
| `BACKEND_HOST` | `127.0.0.1` for local use. Docker/hosting explicitly bind their internal interface. |
| `ALLOWED_ORIGINS` | Comma-separated exact browser origins. Defaults to localhost/127.0.0.1 on ports 5173, 4173 and 80; set your actual frontend origin when hosting. Wildcard entries are ignored. |
| `MEMORY_DIR` | Root `memory/`; use persistent storage on a hosted backend. |
| `REPORTS_DIR` | Root `reports/`; file-export storage. |
| `DEBUG` | `false`; extra development logging when true. |

Changing the provider key needs a backend restart, not a frontend rebuild. Verify access with a real research request: `/health` checks presence only.

An Origin check is a browser boundary, not authentication. Non-browser clients
can omit or forge the header. Keep this demo private/local until server-side
authentication, per-user authorization and quotas are implemented.

## Frontend

`frontend/.env.example` documents `VITE_API_BASE_URL`. Leave it unset locally to use Vite's `/api` proxy. Set it to the public HTTPS backend URL on Vercel and rebuild. This value is public: never put a key in a `VITE_` variable.

| Change | File |
|---|---|
| Repository link, contributor names and stack credits | `frontend/src/config/project.js` |
| Model dropdown and example topics | `frontend/src/features/research/config.js` |
| Signup grant and app-token prices | `frontend/src/features/account/services/localAccounts.js`, `TOKEN_RULES` |
| Colors / typography | `frontend/src/styles/tokens.css`; dark surfaces in `themes.css` |
| Research page layouts | `frontend/src/features/research/components/` |

Frontend source changes update in the dev server. Rebuild for preview or deployment.

## Local accounts and app tokens

Each signup gets 100 demo app tokens; suggestions cost 2, research 10, exports 0. Failed operations refund a reservation once. These are browser-local credits, separate from Groq's token quota. The ledger is not server-enforced metering.

The browser stores the account, salted PBKDF2 password hash, session, theme and ledger in localStorage. Clearing site storage removes them. These accounts do not secure API endpoints. Saved research belongs to the installation.
