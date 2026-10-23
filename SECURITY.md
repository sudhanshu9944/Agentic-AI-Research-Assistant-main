# Security and privacy

Browser accounts and credits are not server authentication or API quotas.
Local installations share a file-based research library. On Vercel, signed
anonymous workspace cookies restrict reports to separate private Blob prefixes.
This protects report lookup across browser workspaces, but does not prevent API
quota abuse or provide verified user identities. Keep provider limits enabled
and add server authentication and rate limits before unrestricted paid usage.

## Credential handling

- Put the provider key only in the root `.env` or backend host environment.
- `.env`, research history and reports are ignored by Git and excluded from
  Docker build contexts and source exports. Only `.env.example` is distributable.
- Never place secrets under a `VITE_` variable: those values reach the browser.
- Backend log formatting redacts the configured key and common token formats.
  API failures return generic messages rather than upstream exception details.

## Local and browser boundaries

The default direct server bind and Docker published ports use loopback.
`ALLOWED_ORIGINS` accepts exact origins; defaults cover local development,
preview and Docker UI. Unknown browser origins are rejected before API work.
This does not prevent a non-browser client from forging or omitting Origin.
Incoming API bodies are limited to 32 KiB, including streamed bodies.

React text rendering and HTML-disabled Markdown prevent raw generated HTML
from becoming executable markup. Source and PDF links allow only HTTP/HTTPS
without embedded credentials. Generated Markdown images render as text rather
than automatically loading third-party resources. Vercel/Nginx configuration
adds browser security headers. Exported Markdown remains untrusted content:
render it in a safe viewer rather than enabling raw HTML or scripts.

## Data leaving the app

Local account names, email addresses, salted password hashes and app credits
stay in that browser's localStorage. They are not sent to the backend for
authentication. Research topics, chosen scope and retrieved evidence are sent
to the configured AI provider and public search services to perform research.
Hosted research reports are stored privately in the connected Vercel Blob store.
The workspace cookie is Secure, HttpOnly and SameSite=Lax; clearing it loses
access to that library, and changing SESSION_SECRET invalidates old cookies.
Google Fonts requests load the UI font. No additional analytics is configured.
Do not use the demo as a private document or credential store.

## Integrity and dependencies

Use `npm ci` with the checked-in lockfile. Runtime Python dependencies are
pinned in `requirements.txt`; development checks are in README.md.
Dependency audits report known advisories at the time queried, not a guarantee
against all vulnerabilities.

Report suspected issues privately to a repository maintainer through GitHub.
Do not open a public issue containing credentials or private reports. Rotate
any exposed secret before discussing its redacted details.
