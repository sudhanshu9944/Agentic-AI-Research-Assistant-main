# Security and integrity review — 23 October 2026

## Scope and findings

Reviewed tracked source, documentation/screenshots, the source ZIP, built
frontend assets and locally available Git history. Checked configured secret
values and common provider/GitHub token/private-key patterns without printing
their values. No configured secret, credential-pattern match or personal
computer path was found in the scanned release/history. Email-pattern matches
were test fixtures and upstream font/dependency metadata. Requested public
credits and existing Git attribution were preserved.

Confirmed that `.env`, browser account data, generated report history,
virtual environments, node_modules and Git credentials are excluded from the
source archive. The previously used one-time publishing token was revoked;
its follow-up authenticated request returned HTTP 401. No old credential was
reused during this review.

## Repairs

- Replaced wildcard CORS with explicit configurable origins and reject unknown
  browser origins before research/history access.
- Default local server/Docker exposure is loopback; Docker backend runs as an
  unprivileged user, and build contexts exclude secrets and generated data.
- Bound streamed/request bodies to 32 KiB and validate export/report IDs.
- Removed internal exception details from research, history and export errors.
  Application log formatting redacts configured/provider credential formats.
- Restricted citation and PDF links to HTTP/HTTPS without embedded credentials.
  Disabled raw Markdown HTML and automatic external report images.
- Added browser security headers for the API, Vercel frontend and Nginx.

## Validation

56 backend tests and 6 frontend tests passed, including origin rejection,
streamed-body limits, error redaction, invalid session IDs and unsafe PDF links.
Ruff, ESLint, formatting and the production frontend build passed.
After restarting the hardened backend, the saved report rendered in-browser
and a real PDF download succeeded.

`npm audit` reported zero known vulnerabilities across the lockfile's 278
dependency entries. `pip-audit -r requirements.txt` resolved/audited 61 packages
and reported zero known vulnerabilities. These are time-specific advisory
checks; Python transitive packages are resolved during installation rather
than all being locked in this release.

## Remaining deployment boundary

Local signup is deliberately browser-only. Direct API callers are not
authenticated; saved history is shared by the backend installation. CORS,
request limits and demo tokens do not change that. A public/private-user
production release still requires server identity, authorization and quotas.
This review is not a penetration-test certification or an assurance that no
unknown issue exists.

References: [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/) and
[react-markdown security](https://github.com/remarkjs/react-markdown#security).
