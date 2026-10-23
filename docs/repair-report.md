# Guided research and reference UI update

Completed locally on 23 October 2026 for the requested TAAI-inspired interface and review-before-PDF workflow.

## Changes

- Replaced the earlier dark interface with a light reference-inspired design: Poppins, cream hero, yellow highlights, pink/blue cards, square borders and offset shadows. Research.AI identity is retained. See DESIGN.md for reference evidence and approximations.
- Added real AI topic recommendations at POST /recommendations. Planning does not run searches, save a report or export a PDF.
- Added checkbox selection, select/deselect-all, custom topics and a 12-topic limit. Empty selections disable the research button and are rejected by the API.
- Selected topics become the actual search plan. Deselected topics are stored and passed to report generation as excluded scope. A source can incidentally mention other subjects; exclusion controls the requested scope, not every word in external search results.
- Added a review page with the summary, requested angles, deselected topics, AI-assessed evidence gaps and an explanation of the source-excerpt method. The full report and sources are expandable. Export occurs only when Generate PDF or Markdown is clicked.
- Saved reports retain selection and gap metadata and reopen through My Research. Legacy reports show an honest missing-assessment message.
- Removed simulated per-agent completion progress. The live request has an elapsed timer; upstream free services may throttle or fail.
- Reused the existing Groq free configuration and repaired export pipeline. No credential is embedded in the frontend or archive.

## Verification

50 automated tests pass, including recommendation-only behavior, rejection of empty/oversized selection, selected-scope search propagation, evidence-gap preservation, history and PDF export. Production build and ESLint pass. Mobile (375 CSS px) and desktop (1265 CSS px) layouts showed no horizontal overflow.

A real browser acceptance run used Groq and public search, with no mock server: topic Solar energy benefits and limitations. AI suggested five angles. Three were unchecked and a custom India-applications angle was added. The final persisted session 32743265-f680-44ec-b831-b516eab796b0 contained exactly three selected topics, three excluded topics, three corresponding search queries, five sources, five insights and five evidence gaps. The browser displayed the summary and those scope/gap lists before export. Generate PDF downloaded a six-page report; all pages were rendered and visually inspected. The report is not a fact-check certification: it summarizes retrieved excerpts and explicitly records missing evidence.

## Dark mode, local accounts and credits

- Added a persisted light/dark toggle and adapted the hero, cards, forms, review, tables, library and account dialog for both themes.
- Header GitHub icon and footer source link target the supplied repository.
- Footer: Made with ❤️ by Sudhanshu Singh, Himanshu Chauhan, Tanmay Pahuja. Built with ❤️ using React · FastAPI · LangGraph · Groq.
- Browser-local signup/login uses salted PBKDF2-SHA256 hashes (150,000 iterations), and stores the account/session in localStorage. No Google auth or server account service was added. This is a local demo login, not protection for the API; the installation's saved research remains shared.
- Each signup receives 100 app tokens; recommendations cost 2, research 10, and exports 0. The client reserves tokens and refunds failed operations once. These app credits are separate from Groq tokens/quotas and are not secure server-enforced metering.
- Four frontend account/ledger tests pass in addition to the 50 backend tests. Build and lint pass. Tests cover signup/duplicate email/password rejection, salted hash storage, persistence, separate balances, insufficient funds and idempotent refunds.
- Real browser checks: local signup granted 100; successful Groq recommendations left 98; a subsequent research search failed because public search returned no usable sources, and the reserved 10 tokens were refunded to 98. Logout and login preserved 98. A saved report exported as PDF without consuming tokens. Dark mode and session survived refresh.

## Delivery

Local app: http://127.0.0.1:4173/ ; backend: http://127.0.0.1:8000/ . The final source archive excludes the local .env, generated research, node_modules and the Python environment. Follow README.md to install on another machine and configure a key locally.

The remote GitHub repository and existing deployment have not been updated because the connected account reported no push permission. Search availability varies: Wikipedia returns 403 in this environment, and public web engines sometimes throttle requests. Available web search still completed the real acceptance run.

This release adds topic recommendations and a research preview. It does not add uploaded-PDF reading, OCR, Gamma integration or PowerPoint generation.
