# CLAUDE.md

Permanent rules for this repository. Read this before creating or editing any
course session. These rules do not change between sessions; if a new request
conflicts with a rule here, flag the conflict instead of silently overriding it.

Also read:

- `session-guidelines.md`: how to apply these rules (page structure, copy
  blocks, callouts, proof workflow). If it conflicts with this file, this
  file wins.
- `rn-conventions.md`: versions, packages and code patterns. When an older
  tutorial disagrees, it wins.
- `rn-course-plan.md`: session content and the Concept Index (sequencing).

## Course

Développement multiplateforme avec React Native (Expo) — IAM2, 2e année
Master Développement Mobile, Prof. Wael Bouaziz. Vendredi 8:30-11:40: Cours
8:30-10:00 (salle 13), Atelier 10:10-11:40 (C2I). Students know Kotlin and
Flutter, and are new to React.

## Site structure (fixed)

- The published site lives entirely in `docs/` (GitHub Pages serves the
  `main` branch's `/docs` folder; `docs/.nojekyll` disables Jekyll).
- The reusable skeleton lives in `templates/codelab-template.html`.
- Every session is **one self-contained file**: `docs/session-XX.html`, where
  `XX` is a two-digit number from `00` to `07`.
- Exception: screenshots. They live in `docs/img/sXX/`, are referenced with a
  relative path, and have a French alt text, `width` and `height`,
  `loading="lazy"` and a `figcaption`.
- A new session is created by copying `templates/codelab-template.html` to
  `docs/session-XX.html` and filling in the sidebar entries and the step
  panels. **Never change the skeleton markup, the navigation JavaScript, the
  quiz CSS and JavaScript, or the pinned asset versions** when authoring a
  session. Any change to the skeleton happens in the template file, as a
  deliberate, separate commit.

## Language

- French for explanations, headings, UI text inside the apps, quiz
  questions, captions and alt texts.
- English for code, identifiers, code comments, commands, file and folder
  names, commit messages and Git tags.
- Every page has `<html lang="fr">`.

## Zero emojis

No emoji characters anywhere in the site, in code samples or in the apps the
students build (titles, body text, code comments, UI strings, commit
messages). Icons come exclusively from **Font Awesome 6.4.0** (pinned in the
template). Decorative icons get `aria-hidden="true"`. Icon-only buttons (no
visible text label) get an `aria-label` describing the action.

## Target stack (details in rn-conventions.md)

- Expo SDK 57 (React Native 0.86, React 19.2), New Architecture only. Lines
  marked [SDK] in `rn-conventions.md` may change with SDK 58; flag every
  SDK-dependent instruction on the page.
- TypeScript strict. `npx tsc --noEmit` must pass on every code sample. No
  `any`, no `@ts-ignore` (only the documented Firebase persistence
  workaround with `@ts-expect-error` and a comment).
- Expo Router with routes in `src/app` (`_layout.tsx`, `(tabs)`, `[id].tsx`).
  No React Navigation imports in app code.
- Install Expo modules with `npx expo install <pkg>`; `npm install` only for
  pure-JS packages unknown to Expo (`mqtt`).
- **Expo Go only.** No development build, no `expo prebuild`, no Android
  Studio, no emulator. Forbidden in labs: react-native-mmkv,
  `@react-native-firebase/*`, push tokens, MQTT over `mqtt://` or port 1883.
- Screens never call `fetch`, SQL, Firestore or MQTT directly; they use hooks
  from `src/features`, which use `src/lib` and `src/db`.
- If you are unsure that an API exists in the pinned SDK, say so on the
  instructor side (session spec or prompt report), never guess in a page.

## Sequencing

Respect the Concept Index of `rn-course-plan.md`: a session may only use
concepts introduced in the same or an earlier session, even when
`rn-conventions.md` shows a later pattern.

## Student pages

- A student alone with a PC and a phone must be able to finish the page.
  Pair work exists only where `rn-course-plan.md` requires it (S4, two
  phones on one board); the page then says how to do it alone with two
  devices or two accounts.
- No "Plan de secours" cards. Instructor contingencies belong in the session
  spec's RISKS section. The labelled `--tunnel` block is the only
  student-facing network fallback.

## Code blocks

- Use `<pre><code class="language-tsx">`, `language-ts`, `language-bash`,
  `language-powershell`, `language-json` or `language-cpp` (and
  `language-markup` for HTML or XML if ever needed).
- Code text is HTML-escaped (`&lt;`, `&gt;`, `&amp;`).
- Code is always **complete and copy-paste ready** — never truncated with
  `...` or a placeholder comment. Spread syntax (`...rest`) is code, not a
  placeholder.
- A file is shown in full when it is created or restructured. When a later
  step changes only a few lines, show those lines with their exact position,
  followed by the complete file in
  `<details><summary>Voir le fichier complet à ce stade</summary>`.
- Copy-block rules (one terminal per block, long-running command last,
  "Seulement si ..." labels) are in `session-guidelines.md`.

## Every guided step must contain

Guided steps have a title starting with `Étape N — ` (with the accent) and
these cards:

1. Objectif
2. Commandes
3. Code complet
4. Résultat attendu
5. Vérification (with a check on the phone)
6. À retenir (`fa-lightbulb`), with a "Pourquoi ?" callout and, where
   useful, an "Erreurs fréquentes" callout

"Résultat attendu" and "Vérification" may share one card titled
"Résultat et vérification" (`fa-list-check`, items with `fa-regular fa-square`).

## Session structure

Sessions 01 to 07, sidebar section "Cours" then section "Atelier":

1. Prérequis & objectifs (timing table, "Avant la séance" box)
2. Cours — 90 min: concepts, diagrams, annotated code, Compose/Flutter
   comparisons, 3-5 exam-style quiz questions
3. Atelier — Étapes guidées: 65 min
4. Défi: 15 min, unguided extension
5. Checklist d'évaluation (only work done before it)
6. Livrable: 10 min — commit, tag `s0X-submit`, README with a phone
   screenshot and the `npx expo-doctor@latest` output (07: project kickoff)

Session 00 is homework (about 1 h): table of setup steps, no Cours/Atelier
split, no Défi; deliverable = phone screenshot of w0-hello posted before S1,
no tag. Details in `session-guidelines.md`.

## Quiz

- 1 to 3 questions per card, 3 options each, exactly one correct.
- Question ids follow `quiz-sXX-qNN`, are unique in the page, and are never
  reused or renumbered once published.
- Every question has an explanation (`.quiz-explain`). Never put a display
  utility class on `.quiz-feedback` or `.quiz-explain`.
- Questions test understanding or ask to predict a result, never recall of a
  command name. No points, no grade.

## Diagrammes et figures

- Prefer an HTML figure with Tailwind utilities or a real table, then a
  hand-written inline SVG, then an image in `docs/img/sXX/` (screenshots only).
- Every figure is a `<figure>` with a French `<figcaption>` numbered
  "Figure S.n" that states the takeaway.
- Inline SVG has `role="img"`, `aria-labelledby` pointing to a French
  `<title>` and `<desc>`, ids prefixed `sXX-`, a `viewBox` with `width` and
  `height`, the classes `w-full h-auto`, text of 11 px or more, and a
  `min-w-[...]` class inside `div.overflow-x-auto` when wide.
- Colour is never the only cue. No animation, no external diagram library.

## After creating a session

1. Update `docs/index.html`: turn the session's card into a link to
   `session-XX.html` with the status "Disponible".
2. Run `python scripts/check.py` and fix every reported issue before
   committing.
3. Commit only that session's files (`docs/session-XX.html`,
   `docs/index.html`, `docs/img/sXX/` if any) with the message
   `Add session XX`. Do not push.
