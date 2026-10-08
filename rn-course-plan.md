# rn-course-plan.md

Développement multiplateforme avec React Native (Expo) — IAM2, 2e année Master Développement Mobile.
7 sessions of 3h on Friday: Course 8:30-10:00 (room 13) + Atelier 10:10-11:40 (C2I).
This file is the sequencing authority: a session may only use concepts introduced in the same or an earlier session (see Concept Index).

## Audience and constraints

- Students know Kotlin/Android Studio and Flutter/Dart. They know JavaScript basics only and have never used React.
- TypeScript from day 1 (strict mode). Teach React by mapping to Compose/Flutter, not from zero.
- Develop on Windows PCs, test on personal phones with Expo Go over the same Wi-Fi. No development builds, no Android Studio, no emulator.
- Everything in labs must run in Expo Go. Forbidden in labs: react-native-mmkv, @react-native-firebase/*, remote push tokens, any library requiring `expo prebuild`.
- Language: French for explanations and UI text; English for code, identifiers, commands, file names.

## Format of every session (one file docs/session-0X.html)

| Part | Time | Content |
|---|---|---|
| Prérequis & objectifs | — | Packages, accounts, outcomes |
| Cours | 90 min | Concepts, diagrams, annotated code, Compose/Flutter comparisons, 3-5 quiz questions (exam-style) |
| Pause / change of room | 10 min | — |
| Atelier — guided steps | 65 min | Build the mini-app step by step, each step with expected result and phone check |
| Défi | 15 min | Unguided extension |
| Livrable | 10 min | Commit, tag, README with screenshot |

## Repository and submission conventions

- One GitHub repo per student: `iam2-rn-<firstname>-<lastname>`, one folder per session app: `s1-profile-contacts/`, `s2-expenses/`, `s3-mini-shop/`, `s4-taskboard/`, `s5-offline-shop/`, `s6-iot-dashboard/`, `project/`.
- Each session app is created fresh with `npx create-expo-app@latest <folder> --template default@sdk-57` (or the SDK the store Expo Go supports that week; see conventions).
- Tag per submission: `s1-submit` ... `s6-submit`, `project-submit`. Deadline: Thursday 23:59 after the session. The tag is graded.
- Each app README: what was built, screenshot or GIF from the phone, output of `npx expo-doctor`, SDK version.
- `.env` is never committed; commit `.env.example`.
- Shared folder convention inside each app: `src/app` (routes), `src/features`, `src/lib`, `src/db`, `src/components`.

## Overview

| # | Title | Atelier mini-app | Tag |
|---|---|---|---|
| S0 | (homework) Préparation de l'environnement | w0-hello | — |
| S1 | TypeScript et React pour développeurs Kotlin/Flutter, Expo Router | Profile & Contacts | s1-submit |
| S2 | Persistance locale avec SQLite | Offline Expense Tracker | s2-submit |
| S3 | Consommer une API REST avec TanStack Query | Mini-Shop (DummyJSON) | s3-submit |
| S4 | Firebase : authentification et Firestore temps réel | Shared Task Board | s4-submit |
| S5 | Offline-first, cache local et notifications | Offline-ready Shop + reminders | s5-submit |
| S6 | IoT : consommer un appareil via MQTT | IoT Dashboard (ESP32 / Wokwi) | s6-submit |
| S7 | Architecture, préparation à l'examen, atelier projet | Final project kickoff | project-submit (later) |

---

### S0 — Préparation de l'environnement (homework before S1, ~1h)
- Install Node.js LTS (24.x, or 22.13+; never odd versions), Git, VS Code (+ Expo Tools, ESLint, Prettier).
- Create a free Expo account; `npx expo login` on the PC and log in inside Expo Go with the same account (required on iOS for SDK 57).
- Install Expo Go from the store; check its SDK version in the app.
- Create a Firebase project (Authentication: Email/Password enabled; Firestore in production mode). Not used before S4, but created now to avoid S4 delays.
- Create the GitHub repo `iam2-rn-<firstname>-<lastname>`.
- Smoke test: `npx create-expo-app@latest w0-hello --template default@sdk-57`, `cd w0-hello`, `npx expo start`, scan, edit a text, see Fast Refresh.
- Deliverable: screenshot of the phone running w0-hello, posted before S1.

### S1 — TypeScript et React pour développeurs Kotlin/Flutter, Expo Router
- Course outcomes:
  1. Use TypeScript essentials: types vs interfaces, unions, generics in signatures, optional chaining, strict null checks.
  2. Explain the React model: component = function of props and state; state change triggers re-render; one-way data flow.
  3. Use JSX, props, `useState`, `useEffect` (dependencies, cleanup) and the rules of hooks; map them to `@Composable`/`remember`/`LaunchedEffect` and Flutter `Widget`/`setState`/`initState`.
  4. Explain Expo Go vs development builds and why some libraries cannot run in Expo Go.
  5. Describe Expo Router file-based routing: `src/app`, `_layout.tsx`, groups `(tabs)`, dynamic `[id].tsx`.
- Atelier — Profile & Contacts: tabs layout (Profile, Contacts), `FlatList` of typed hard-coded contacts with `keyExtractor`, a reusable `ContactRow` component with typed props, `contact/[id].tsx` detail with `useLocalSearchParams<{ id: string }>()`, a favorite toggle with `useState`.
- Challenge: search filter on the contacts list (controlled `TextInput`).
- Key commands: `npx create-expo-app@latest s1-profile-contacts --template default@sdk-57`, `npm run reset-project`, `npx expo start`, `npx tsc --noEmit`.
- Not covered yet: forms with validation, persistence, Context.
- Reuses: S0 environment.

### S2 — Persistance locale avec SQLite
- Course outcomes:
  1. Choose a local storage: AsyncStorage / `expo-sqlite/kv-store` (key-value) vs SQLite (relational); compare with Room and sqflite.
  2. Use `SQLiteProvider` + `onInit`, `useSQLiteContext`, `execAsync`, `runAsync`, `getAllAsync`, `getFirstAsync`, `withTransactionAsync`.
  3. Write versioned migrations with `PRAGMA user_version`.
  4. Apply the repository pattern (`expenseRepo(db)`) and a custom hook (`useExpenses`) to keep SQL out of screens.
  5. Build controlled forms (`TextInput`, numeric input parsing, simple validation).
- Atelier — Offline Expense Tracker: list, add, edit, delete expenses; category filter; total via `SUM()`; data survives app restart.
- Challenge: migration v2 adding a `note` column without losing data.
- Key commands: `npx expo install expo-sqlite`.
- Bonus (optional, not required): Drizzle ORM with `drizzle-orm/expo-sqlite`.
- Reuses: S1 components, routing, hooks.

### S3 — Consommer une API REST avec TanStack Query
- Course outcomes:
  1. Write a typed fetch client (`api<T>()`) with base URL, JSON parsing, `ApiError` with status code, Bearer token header.
  2. Explain server state vs client state and why `useEffect` + `fetch` is not enough (race conditions, caching, retries, deduplication).
  3. Use TanStack Query v5: `QueryClientProvider`, `useQuery`, query keys, `staleTime`, `useInfiniteQuery` with `initialPageParam`/`getNextPageParam`, `useMutation`, invalidation.
  4. Handle loading, error, empty and refreshing states (`RefreshControl`), using DummyJSON `?delay=` to simulate a slow network.
  5. Store an auth token securely with `expo-secure-store` and share the session with React Context.
- Atelier — Mini-Shop (DummyJSON): product catalog with infinite scroll (`/products?limit&skip`), category chips (`/products/categories`, `/products/category/{slug}`), debounced search (`/products/search?q=`), product detail route `product/[id].tsx`, login (`POST /auth/login`, token in SecureStore, `/auth/me` profile), cart stored locally in SQLite (reuses S2).
- Challenge: "Add to cart" mutation to `POST /carts/add` with optimistic UI; explain why DummyJSON writes are simulated and not persisted.
- Key commands: `npx expo install @tanstack/react-query expo-secure-store expo-sqlite`.
- Not covered yet: persistence of the query cache (S5), offline mode (S5).
- Reuses: S1 routing/components, S2 SQLite repository.

### S4 — Firebase : authentification et Firestore temps réel
- Course outcomes:
  1. Explain BaaS vs custom REST backend (compare with S3); Firebase JS SDK vs React Native Firebase (and why only the JS SDK runs in Expo Go).
  2. Initialize Firebase with `EXPO_PUBLIC_*` env vars; Auth with `initializeAuth` + `getReactNativePersistence(AsyncStorage)`.
  3. Build an auth gate in the root layout using `onAuthStateChanged` + Context; redirect with Expo Router.
  4. Use Firestore: `addDoc`, `updateDoc`, `deleteDoc`, `serverTimestamp`, queries, and realtime `onSnapshot` with unsubscribe in the effect cleanup.
  5. Write and test security rules (`request.auth`, ownership checks). The web config is not a secret; the rules are the security.
- Atelier — Shared Task Board: register/login/logout, a board of tasks synced in real time between two phones (pair work), owner-only edit/delete enforced by rules.
- Challenge: task assignment to another user + filter "my tasks".
- Key commands: `npx expo install firebase @react-native-async-storage/async-storage`, restart `npx expo start` after editing `.env`.
- Reuses: S1-S3 Context, routing, forms.

### S5 — Offline-first, cache local et notifications
- Course outcomes:
  1. Define offline-first, stale-while-revalidate, cache invalidation, and the trade-offs of each storage layer.
  2. Explain why the Firestore JS SDK on React Native has only a memory cache (no IndexedDB): data does not survive an offline app restart.
  3. Persist the TanStack Query cache with `PersistQueryClientProvider` + `createAsyncStoragePersister`; relate `gcTime` and `maxAge`.
  4. Wire `onlineManager` to NetInfo and `focusManager` to `AppState`; paused mutations resume when back online.
  5. Schedule local notifications with `expo-notifications`: permissions, Android channel, time-interval and date triggers, cancel/list.
- Atelier — Offline-ready Shop: upgrade the S3 Mini-Shop (copied into `s5-offline-shop/`): catalog and product details survive airplane mode + app kill, offline banner, "last updated" indicator, a "rappelle-moi" button that schedules a price-check reminder notification.
- Challenge: cache selected Firestore data from S4 in SQLite so the task list opens offline (stretch goal).
- Key commands: `npx expo install @tanstack/query-async-storage-persister @tanstack/react-query-persist-client @react-native-community/netinfo @react-native-async-storage/async-storage expo-notifications`.
- Reuses: S3 app and query layer, S2 SQLite, S4 Firestore knowledge.

### S6 — IoT : consommer un appareil via MQTT
- Course outcomes:
  1. Explain publish/subscribe vs request/response (REST) vs realtime database listeners (Firestore); when each fits.
  2. Use MQTT concepts: broker, client ID, topics and wildcards (`+`, `#`), QoS 0/1/2, retained messages, Last Will and Testament, keep-alive, clean session.
  3. Explain why Expo Go needs MQTT over WebSockets (`wss://`) while the ESP32 uses TCP (1883), with the broker bridging both.
  4. Write a `useMqtt` hook with MQTT.js: connect, subscribe, publish, reconnect, connection status, cleanup with `client.end()`.
  5. Design topic hierarchies and JSON payloads for a device (`iset/iam2/<name>/sensors`, `/status`, `/cmd/led`).
- Device: ESP32 + DHT22 simulated in Wokwi (or a real ESP32 provided by the instructor) publishing every 5 s, subscribing to an LED command topic, with an LWT `offline` retained status.
- Atelier — IoT Dashboard: live temperature/humidity cards, device online/offline badge from the retained status, LED toggle that publishes a command and reflects the device acknowledgement, readings history saved in SQLite (reuses S2) and shown as a simple list or sparkline.
- Challenge: threshold alert that schedules a local notification when temperature exceeds a user-set value (reuses S5).
- Key commands: `npm install mqtt` (pure JS; verify version on lab PC), `npx expo install expo-sqlite expo-notifications`.
- Reuses: S2 SQLite, S5 notifications, S1-S3 hooks and components.

### S7 — Architecture, préparation à l'examen, atelier projet
- Course outcomes:
  1. Layered architecture: screens → hooks → repositories/services → data sources (SQLite, REST, Firestore, MQTT).
  2. Choose state location: local state, Context, server cache (TanStack Query), persistent storage; introduce Zustand as an option for shared client state.
  3. Compare data sources seen in the course: latency, offline behaviour, security, cost.
  4. Review of exam-style questions from S1-S6.
  5. Limits of Expo Go and the path to production: development builds, EAS Build, remote push.
- Atelier: final project kickoff (scaffold, data model, first commit, rubric walkthrough, individual validation of the project idea by the instructor).
- Reuses: everything.

---

## Final mini-project (due 10 days after S7, tag `project-submit`)

One original app (student chooses the theme, validated in S7) with at least:
- Firebase Auth login and one Firestore collection with security rules;
- one REST API consumed with TanStack Query (public API or DummyJSON);
- one SQLite table with a migration;
- offline restart support for at least one screen (persisted query cache or SQLite);
- one scheduled local notification;
- optional bonus: an MQTT feature.
3-6 screens, README with architecture diagram, rules, screenshots, limitations.

## Assessment (adjust to institutional rules)

| Component | Weight |
|---|---|
| Weekly labs S1-S6 (6 x 5%) | 30% |
| Final mini-project | 30% |
| Written exam | 40% |

Lab rubric (/10): runs in Expo Go from a clean clone (3), required features (4), TypeScript strict with `npx tsc --noEmit` clean and no `any` (1), structure: repository/hooks, no data access in screens (1), README with phone screenshot (1).

## Written exam topics

React rendering model and rules of hooks; `useEffect` dependencies and cleanup; props vs state vs Context; Expo Router conventions; Expo Go vs development builds; SQLite migrations and transactions; REST client design and TanStack Query (`staleTime` vs `gcTime`, query keys, infinite queries, invalidation); Firebase Auth persistence, `onSnapshot` vs `getDocs`, reading security rules; why Firestore JS has no persistent cache on React Native; offline-first strategies; local vs remote notifications and Android channels; MQTT pub/sub, QoS, retained messages, LWT, topic design; choosing between REST, Firestore and MQTT for a scenario.

## Concept Index (first introduction)

| Concept | First session |
|---|---|
| TypeScript essentials, JSX, props, `useState`, `useEffect`, `FlatList`, Expo Router (tabs, stack, `[id]`) | S1 |
| Controlled forms, SQLite, migrations, transactions, repository pattern, custom hooks | S2 |
| Typed fetch client, TanStack Query (`useQuery`, `useInfiniteQuery`, `useMutation`), SecureStore, React Context | S3 |
| Env vars `EXPO_PUBLIC_*`, Firebase Auth, auth gate, Firestore CRUD, `onSnapshot`, security rules | S4 |
| Query persistence, `onlineManager`, `focusManager`, NetInfo, local notifications | S5 |
| MQTT (MQTT.js over WSS), QoS, retained, LWT, topic design | S6 |
| Zustand (mention), layered architecture, EAS/dev builds (theory only) | S7 |

## Points to verify on a lab PC / student phones

- Store Expo Go SDK version on one Android and one iPhone; `--template default@sdk-57` still valid; switch to SDK 58 template when the store Expo Go moves.
- Expo Go login on iOS (and Android if now enforced).
- LAN mode on the C2I Wi-Fi with Windows Firewall set to Private network; `--tunnel` fallback.
- `getReactNativePersistence` TypeScript error with `npx tsc --noEmit` and the chosen workaround.
- MQTT.js import and `wss://` connection from Expo Go (Android + iOS), `payload.toString()` behaviour.
- Wokwi ESP32 sketch reaching the chosen broker; broker WebSocket port/path.
- DummyJSON responsiveness with a full class (no published rate limits).
- TanStack persister restore after airplane mode + app kill.
- `npx expo-doctor` clean for each session package set.
