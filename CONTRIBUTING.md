# Contributing

Read [local setup](docs/LOCAL_SETUP.md) and [architecture](docs/ARCHITECTURE.md)
before making changes. Keep feature UI, orchestration, API access and backend
workflow responsibilities in their respective modules.

Use short functions with descriptive names. Comments should explain constraints
or decisions. Keep provider credentials out of browser code, screenshots and
commits. Add a regression test when fixing behavior that could break again.

Before submitting backend changes:

```sh
python -m pip install -r requirements-dev.txt
python -m ruff check backend tests
python -m ruff format --check backend tests
python -m pytest
```

Before submitting frontend changes, from `frontend`:

```sh
npm ci
npm run format:check
npm run lint
npm test
npm run build
```

Review visible changes in light/dark mode and at mobile width. For workflow
changes, test selected topics, excluded topics, failures and explicit export.
Do not replace a failed real provider call with a fake successful report.

Preserve original authorship and history. Credit real new contributions using
the contributor's GitHub-associated email; never rewrite historical commits to
change attribution. Describe the resulting behavior and validation in each PR.
