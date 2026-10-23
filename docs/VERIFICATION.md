# Verification record

## Automated checks

The structured release was checked with Python 3.12 and Node 24:

- Backend: 50 regression tests passed, including malformed AI responses,
  essential failures, persistence, scoped research and PDF/Markdown export.
- Ruff lint and formatting checks passed.
- Frontend: local account, password hashing, session persistence, token
  reservation/refund and storage failure tests passed.
- Frontend ESLint and production Vite build passed.

Run the current commands in CONTRIBUTING.md. These checks isolate provider
responses; they do not claim that public search or Groq is always available.

## Manual checks

A real Groq research session on solar energy produced five sources, five
insights and advisory evidence gaps with three selected and three excluded
angles. The six-page PDF was downloaded and visually inspected. Suggestions,
selected scope, summary review and explicit export were exercised in-browser.
Local signup, logout/login, persistent theme, credits and failed-request refunds
were also checked. Light, dark and review screenshots are in `docs/screenshots`.

The code organization was then refactored without changing the workflow or
visual design. Release checks and browser review are repeated before packaging.

## Practical limits

Free model availability and provider quotas can change. Search engines can
return rate limits or unusable evidence. The application reports failures and
allows retries; it does not manufacture success. Local accounts/credits are a
demo, not server authorization or Groq billing quotas. Browser progress is an
estimate. Hosting must provide a working backend and writable session storage.
