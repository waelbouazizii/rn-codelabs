# session-guidelines.md

How to author, check and proof the session pages of "Développement multiplateforme avec React Native (Expo)" (IAM2).
Created 8 October 2026, before any session page exists. Read this file together with:

- `CLAUDE.md` for the hard rules;
- `rn-conventions.md` for code (versions, packages, patterns);
- `rn-course-plan.md` for sequencing (Concept Index) and session content.

If this file conflicts with `CLAUDE.md`, `CLAUDE.md` wins and the conflict is flagged. This file explains how to apply the rules so that students are not confused.

## 1. Verified facts about the lab stack

Nothing has been verified on a lab PC or a student phone yet. Until a fact moves here with a date, treat every item of `rn-conventions.md` section 14 and section 5 of this file as unverified, and keep the wording of the pages neutral about it (no exact Expo Go screen text, no exact CLI prompt text).

Facts taken from `rn-conventions.md` (October 2026, documentation only):

- Expo SDK 57 (React Native 0.86, React 19.2), New Architecture only. Projects are created with `npx create-expo-app@latest <folder> --template default@sdk-57`.
- Node.js 24 LTS (>= 24.3) or 22 (>= 22.13). Never an odd major version.
- Expo Go on iOS (SDK 57) requires the same Expo account in the CLI (`npx expo login`) and in the app.
- On iPhone only the store version of Expo Go runs. If the store Expo Go moves to SDK 58, every new session app is created on SDK 58 and the page says so in its "Avant la séance" box.

## 2. Do

### Page files and structure

- One self-contained file per session: `docs/session-00.html` to `docs/session-07.html`, created by copying `templates/codelab-template.html`.
- Sessions 01 to 07: the sidebar has two sections, each introduced by a non-link heading `<li>` with `data-nav-section`:
  - `data-nav-section="cours"`, label "Cours (90 min)": the Prérequis & objectifs panel, then the course panels.
  - `data-nav-section="atelier"`, label "Atelier (90 min)": the guided steps (65 min in total), the "Défi" panel (15 min), the "Checklist d'évaluation" panel, then the "Livrable" panel (10 min).
- The first panel of sessions 01 to 07 shows the timing table:

  | Partie | Durée |
  |---|---|
  | Cours | 90 min |
  | Pause et changement de salle | 10 min |
  | Atelier : étapes guidées | 65 min |
  | Défi | 15 min |
  | Livrable | 10 min |

- Panel titles (`data-title`, sidebar text):
  - course panels: `Cours — <sujet>`;
  - guided steps: `Étape N — <action>` (with the accent and an em dash);
  - challenge: `Défi — <sujet>`;
  - deliverable: `Livrable — commit et tag s0X-submit` (07: `Livrable — lancement du projet`).
- Every guided step contains the cards, in this order: Objectif, Commandes, Code complet, Résultat attendu, Vérification (or one merged card "Résultat et vérification"), À retenir. A step without a command still has a Commandes card that says which command stays running (for example `npx expo start`) and what to do on the phone.
- Every Vérification card includes a check on the phone in Expo Go, not only in the terminal.
- Session 00 exception (homework, about 1 hour): no Cours/Atelier split, no Défi. The first panel holds a table of setup steps with an estimated duration each (total about 1 h). The guided setup steps still use `Étape N — ` and the six cards. The deliverable is a phone screenshot of w0-hello posted before S1. No tag.
- Deliverable for 01 to 06: commit, tag `s0X-submit`, and a README in the session app folder with a phone screenshot, the output of `npx expo-doctor@latest` and the SDK version. Session 07: project kickoff (scaffold, data model, first commit); the `project-submit` tag comes 10 days later.

### "Avant la séance" box

- Every page (00 to 07) has an "Avant la séance" callout (Info style) in its first panel, telling the student to:
  - open Expo Go from the store on their phone and read its SDK version;
  - compare it with the SDK pinned in `rn-conventions.md` (currently 57) and with the `--template default@sdk-XX` used on the page;
  - on iPhone, remember that only the store version of Expo Go runs, so a mismatch means waiting for the page update, not installing another Expo Go.

### Course part (01 to 07)

- Teach React by mapping to Compose and Flutter. Use a real table (`<th scope="row">` in the first column) with three columns: Compose, Flutter, React Native.
- 3 to 5 exam-style quiz questions per session, spread over the course panels, using the template quiz component. They test understanding or ask to predict a result (re-render, effect order, cache state, MQTT retained message), never the recall of a command name.
- Diagrams follow the section "Diagrammes et figures" of `CLAUDE.md`.

### Toolchain coherence

- Every tool a step uses is installed or checked earlier: Node.js, Git, VS Code, Expo Go, Expo account (S0).
- Every package is installed with `npx expo install` in the step that first uses it, except pure-JS packages unknown to Expo (`mqtt`), which use `npm install`.
- A cross-reference must lead to a visible command: if step X says "à l'Étape Y, lancez Z", step Y shows Z in a code block.

### Copy blocks

- One block means one terminal, running its commands from top to bottom.
- A long-running command (`npx expo start`, `npx expo start --tunnel`) is always the last line of its block. Two long-running commands never share a block; use "Terminal 1" and "Terminal 2".
- A command that must run after a manual edit goes in its own block, placed after the sentence that tells the student to edit and save.
- A conditional command gets its own block labelled "Seulement si …" (for example "Seulement si le QR code ne se connecte pas : mode tunnel").
- Every block has a label: "Bash et PowerShell (identique) :" or the two shell-specific labels. Most `npx` commands are identical in both shells.
- File content shown for reading is reproduced literally. The no-truncation rule targets code students write.
- A file is shown in full when it is created or restructured. A later change to a few lines shows only those lines with their exact position, followed by the complete file in `<details><summary>Voir le fichier complet à ce stade</summary>`.

### Insights

- End every guided step with an "À retenir" card (icon `fa-lightbulb`). Do the same for the Défi and the Livrable.
  - A "Pourquoi ?" callout explains the concept behind the step.
  - An "Erreurs fréquentes" callout, where useful, gives the exact error text a student will see (red screen, Metro, `tsc`), in `<code>`, and what it means.
- Keep each callout to 2-4 sentences.

### Quiz

- Wrong options must be plausible mistakes that Kotlin/Flutter developers actually make (for example "useState updates the value immediately", "useEffect without dependencies runs once").
- Vary the position of the correct answer from one question to the next.
- One idea per question. Count about 1 minute per question; quiz time is included in the course time.
- Ids follow `quiz-sXX-qNN` and are never reused or renumbered on a published page (answers are stored in the browser under the id).

### Markup and accessibility

- Wrap every table in `div.overflow-x-auto`. Key/value tables use `<th scope="row">` in the first column.
- Callout classes:

  | Callout | Border and background | Icon | Text |
  |---|---|---|---|
  | Info | `border-blue-500 bg-blue-50` | `fa-circle-info` | default |
  | Warning | `border-amber-500 bg-amber-50` | `fa-triangle-exclamation` | default |
  | Pourquoi ? | `border-indigo-500 bg-indigo-50` | `fa-lightbulb text-indigo-500` | `text-sm text-indigo-900` |
  | Erreurs fréquentes | `border-rose-500 bg-rose-50` | `fa-bug text-rose-500` | `text-sm text-rose-900` |
  | Danger (mandatory security action only) | `border-red-600 bg-red-50` | `fa-triangle-exclamation text-red-600` | `text-sm text-red-900` |

  Every callout also uses `border-l-4 p-4 rounded flex gap-3`, and every icon has `aria-hidden="true"`.
- Checklist items use empty boxes: `fa-regular fa-square`.

### Secrets and accounts

- `.env` is never committed; the page shows `.env.example` with empty values and the `.gitignore` line.
- The Firebase web config is not a secret, but it still lives in `.env` (`EXPO_PUBLIC_*`) so that each student uses their own project. The page says that the security comes from the rules.
- MQTT: every topic starts with the student's own prefix `iset/iam2/<student>/`.

## 3. Don't

- **No concept before its session**, even when `rn-conventions.md` shows it. The Concept Index of `rn-course-plan.md` wins (for example no Context in S1 or S2, no TanStack Query before S3, no `EXPO_PUBLIC_*` before S4).
- **No library that needs a development build:** react-native-mmkv, `@react-native-firebase/*`, `expo prebuild`, push tokens (`getExpoPushTokenAsync`), MQTT over `mqtt://` or port 1883 from the phone. S7 may name them in prose as theory only, never in a code block.
- **No React Navigation imports** in app code; Expo Router only. No `NativeTabs`.
- **No class components, no `any`, no `@ts-ignore`** (the documented Firebase persistence workaround with `@ts-expect-error` is the only exception).
- **No emulator, Android Studio or JDK instructions.** The phone with Expo Go is the only target.
- **No "Plan de secours" cards on student pages.** Instructor contingencies belong in the RISKS section of the session spec. The only student-facing fallback is the labelled `--tunnel` block.
- **No checklist item about something done later on the page.**

## 4. Review ("proof") workflow

- **Review the exact committed file**, using the latest commit SHA in the raw URL, not `/main/` (cached).
- **Run `python scripts/check.py` on every round.** It enforces: no emoji; every in-page link resolves; no `...` placeholder in code (spread syntax and literal text such as `Chargement...` are allowed); no forbidden Expo Go pattern in a `<pre><code>` block; no step title starting with `Etape` without the accent; quiz CSS and script identical to the template; quiz question structure; required cards in every `Étape` panel; for sessions 01 to 07, sidebar sections Cours and Atelier and a `Défi` panel.
- **Then check by hand or grep:**
  - CSS, markup outside the panels and navigation JavaScript identical to `templates/codelab-template.html`;
  - every `<i>` has `aria-hidden="true"`, every copy button has an `aria-label`, `<div>` tags are balanced;
  - a sequencing grep adapted to the session (for example `useQuery`, `createContext`, `SQLiteProvider`, `onSnapshot`, `mqtt` before their session);
  - a forbidden-phrase grep: "plan de secours", "android studio", "emulat", "newArchEnabled";
  - an SDK grep: every `--template default@sdk-` and every mention of the SDK number matches `rn-conventions.md`;
  - every code sample type-checks: paste it into the session app and run `npx tsc --noEmit`;
  - every `<svg>` has `role="img"`, a `<title>` and a `<desc>`, and every `<figure>` has a `<figcaption>`.
- **Run the app on two phones** (one Android, one iPhone) for each guided step before publishing.
- **Check `docs/index.html`** against the Overview table of `rn-course-plan.md` (titles, mini-apps, status).
- **Claude Code prompts** are plain-text files `prompts/session-0X.md`, run with "Read prompts/session-0X.md and execute it exactly." They start with "Read CLAUDE.md, rn-conventions.md, rn-course-plan.md and templates/codelab-template.html, then create docs/session-0X.html".

## 5. Still to verify on a lab PC and on phones

- The SDK of the store Expo Go on Android and iPhone in the week of each session; `--template default@sdk-57` still valid.
- Whether Expo Go on Android now also requires the Expo login.
- LAN mode on the C2I Wi-Fi with the Windows Firewall set to Private network; `--tunnel` fallback speed with a full class.
- The exact output of `npm run reset-project` in the SDK 57 template (folder names `app-example`, `src/app`).
- `getReactNativePersistence` typing (TS2305) with `npx tsc --noEmit` and the chosen workaround.
- MQTT.js import and `wss://` connection from Expo Go on Android and iOS; broker WebSocket port and path.
- Wokwi ESP32 sketch reaching the broker from `Wokwi-GUEST`.
- DummyJSON responsiveness with a full class.
- TanStack persister restore after airplane mode and app kill.
- `npx expo-doctor@latest` clean for each session package set.

## 6. Theory and figures

- The course part of each session opens with one figure that places the session's data source in the layered architecture (screen → hook → repository/service → data source). S7 shows the complete version. Later sessions reuse the same layout and only move the highlight.
- A comparison with Compose and Flutter is a real table, not a figure.
- Reference tables are introduced as "Aide-mémoire, à consulter pendant les étapes".
- State the misconception the theory targets, and test it in the quiz: "setState changes the variable now", "useEffect is onCreate", "Expo Go runs every npm package", "staleTime and gcTime are the same", "Firestore caches on disk on React Native", "QoS 1 means delivered once".
- Code shown inside a figure uses `<code class="block ... whitespace-nowrap overflow-x-auto">`, never `<pre>` (no copy button on illustrative code), and never contains a forbidden pattern.
- After a rule file or the template changes, copy it to the claude.ai project knowledge so that future session prompts use the current version.
