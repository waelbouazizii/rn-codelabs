Bootstrap this repository as the course site for "Développement multiplateforme avec React Native (Expo)" — IAM2, 2e année Master Développement Mobile, Prof. Wael Bouaziz. The template and checker were copied from C:\projects\laravel-codelabs and still contain Laravel content and rules. Do the steps in order, show me the result of each, and stop if something is ambiguous.

0. Read rn-course-plan.md, rn-conventions.md, templates/codelab-template.html and scripts/check.py fully. Also read ..\laravel-codelabs\CLAUDE.md and ..\laravel-codelabs\session-guidelines.md if they exist, as structural models only (their content is Laravel-specific). List every rule check.py enforces before changing anything.

1. Create session-guidelines.md (React Native version), keeping the same structure as the Laravel one where it exists:
   - Session pages docs/session-00.html to docs/session-07.html.
   - Sessions 01-07: two sidebar sections "Cours" (90 min) and "Atelier" (Étapes guidées 65 min, Défi 15 min, Livrable 10 min), timing table at the top.
   - Every guided step title starts with "Étape N — " (with accent) and contains the cards: Objectif, Commandes, Code complet, Résultat, À retenir.
   - Course part: Compose/Flutter comparisons where relevant, 3-5 exam-style quiz questions using the template quiz component.
   - Session 00 exception: homework format, table of setup steps (~1h total), no Cours/Atelier split, no Défi, deliverable = phone screenshot posted before S1 (no tag).
   - Deliverable for 01-06: commit + tag s0X-submit + README with phone screenshot and npx expo-doctor output; 07: project kickoff.
   - Every page includes a "Avant la séance" box: check the Expo Go SDK version in the store app (iPhone only runs the store version) against the pinned SDK in rn-conventions.md.

2. Create CLAUDE.md: language rules (French explanations/UI, English code/commands/file names, html lang="fr"); zero emojis; Font Awesome 6.4.0 only with aria rules; code must follow rn-conventions.md (SDK 57, TypeScript strict, Expo Router src/app, npx expo install, Expo Go only); respect the Concept Index in rn-course-plan.md; follow session-guidelines.md; code blocks <pre><code class="language-tsx|ts|bash|powershell|json|cpp"> HTML-escaped and complete; after creating a session: update docs/index.html, run python scripts/check.py, commit only that session's files.

3. Clean templates/codelab-template.html:
   - Replace the <title>, header label ("IAM2 - React Native"), and all Laravel/PHP sample content (php artisan samples, PHP quiz questions, Laravel links) with neutral React Native placeholders: one Cours step, one "Étape 1 — " step containing all five cards, one quiz question.
   - Use "Étape" with the accent everywhere.
   - Keep the quiz CSS and quiz JS byte-identical; do not touch navigation JS or asset versions.
   - Make sure Prism highlights tsx, ts, powershell, json and cpp (autoloader).
   - Show me a diff summary.

4. Adapt scripts/check.py:
   - Keep the existing rules (emojis, dead step links, "..." in code blocks, required cards, quiz CSS/JS identical to the template).
   - Replace Laravel-specific rules (php.new / Herd links, references to Laravel files) with RN ones: fail if a code block contains react-native-mmkv, @react-native-firebase, expo prebuild, getExpoPushTokenAsync, or mqtt:// .
   - Fail if any step title starts with "Etape" without the accent, so the card check cannot be bypassed.
   - Allow session-00.html to skip the Cours/Atelier and Défi checks.
   - Point any file references to this repo's CLAUDE.md and session-guidelines.md.

5. Create docs/index.html in the template's visual style: one card per session S0 to S7 (title and mini-app from rn-course-plan.md), sessions not yet built greyed out with "Bientôt", course info (IAM2, vendredi 8:30-11:40, salle 13 puis C2I). Create docs/.nojekyll and README.md (purpose, local preview: python -m http.server -d docs 8000).

6. Smoke test: run python scripts/check.py (must pass with only index.html in docs), then temporarily copy the template to docs/session-99.html, run check.py, confirm it passes the card and quiz checks, delete docs/session-99.html.

7. git add everything, commit "Initial course scaffolding", stop. Do not push.