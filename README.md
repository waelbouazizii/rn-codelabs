# rn-codelabs

Course site for "Développement multiplateforme avec React Native (Expo)" — IAM2,
2e année Master Développement Mobile, Prof. Wael Bouaziz.

One self-contained HTML codelab per session (`docs/session-00.html` to
`docs/session-07.html`), published with GitHub Pages from the `docs/` folder of
the `main` branch. Students follow the pages on a Windows PC and test every app
on their own phone with Expo Go (Expo SDK 57).

## Repository layout

| Path | Purpose |
|---|---|
| `docs/` | Published site: `index.html`, one `session-XX.html` per session, `.nojekyll` |
| `templates/codelab-template.html` | Skeleton copied for every new session |
| `scripts/check.py` | Validator for every page in `docs/` (standard library only) |
| `prompts/` | Claude Code prompts used to generate and revise sessions |
| `CLAUDE.md` | Permanent authoring rules |
| `session-guidelines.md` | How to apply the rules, proof workflow, items still to verify |
| `rn-conventions.md` | Versions, packages and code patterns (React Native, Expo) |
| `rn-course-plan.md` | Session content, sequencing (Concept Index), assessment |

## Local preview

```bash
python -m http.server -d docs 8000
```

Then open http://localhost:8000.

## Checks

```bash
python scripts/check.py
python scripts/check.py --self-test
```

`check.py` exits with code 1 when a page has a problem (emoji, dead step link,
incomplete code, pattern that does not run in Expo Go, missing step card,
quiz error, missing Cours/Atelier sections).

## Adding a session

1. Copy `templates/codelab-template.html` to `docs/session-XX.html` and fill in
   the sidebar entries and step panels (see `CLAUDE.md` and
   `session-guidelines.md`).
2. Turn the session's card in `docs/index.html` into a link with the status
   "Disponible".
3. Run `python scripts/check.py`, then commit with the message `Add session XX`.
