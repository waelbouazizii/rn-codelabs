# React Native (Expo) Conventions – IAM2 Multiplateforme

Reference for all generated sessions (state as of October 2026). When older tutorials disagree, this file wins. If you are unsure that an API exists in the pinned SDK, say so instead of guessing. Lines marked [SDK] may change when SDK 58 becomes stable.

## 1. Versions

| Item | Rule |
|---|---|
| Expo SDK | 57 (`expo@^57.0.17`, React Native 0.86, React 19.2). [SDK] Create new session apps on SDK 58 once the store Expo Go supports it; never mix SDKs inside one app. |
| Architecture | New Architecture only (mandatory since SDK 55). Never mention `newArchEnabled`. |
| Node.js | 24 LTS (>= 24.3) or 22 (>= 22.13). Never 23 or 25. |
| TypeScript | Strict mode (template default). `npx tsc --noEmit` must pass. No `any`. |
| Firebase | `firebase@^12` (JS SDK only). |
| TanStack Query | `@tanstack/react-query@^5`. |
| MQTT | `mqtt` (MQTT.js v5) over `wss://` only. |
| Other packages | Always install with `npx expo install <pkg>` so versions match the SDK. Use `npm install` only for pure-JS packages not known to Expo (e.g. `mqtt`). |

## 2. What runs in Expo Go

| Allowed in labs | Forbidden in labs (needs a development build) |
|---|---|
| expo-sqlite, expo-sqlite/kv-store, expo-secure-store, @react-native-async-storage/async-storage, @react-native-community/netinfo, expo-network, firebase (JS SDK), @tanstack/react-query + persisters, expo-notifications (local only), mqtt (MQTT.js over WSS), react-native-svg | react-native-mmkv, @react-native-firebase/*, remote push (`getExpoPushTokenAsync`, FCM), raw TCP sockets (MQTT on 1883 from the phone), anything requiring `npx expo prebuild` |

## 3. Environment (Windows)

```powershell
winget install OpenJS.NodeJS.LTS
winget install Git.Git
winget install Microsoft.VisualStudioCode
node -v
npx expo login
```

- No Android Studio, emulator or JDK needed.
- Expo Go on iOS (SDK 57) requires being logged in with the same Expo account in the CLI and in the app. [SDK] Android may enforce the same later.
- Network: allow Node.js on Private networks in the Windows Firewall prompt, set the Wi-Fi profile to Private, Metro port 8081. If LAN fails, use `npx expo start --tunnel`.

## 4. Project creation and daily commands

```bash
npx create-expo-app@latest s1-profile-contacts --template default@sdk-57
cd s1-profile-contacts
npm run reset-project        # blank src/app, starter moved to app-example
npx expo start               # scan QR with Expo Go (iOS: Camera app)
npx expo start -c            # clear Metro cache
npx expo start --tunnel      # fallback if LAN blocked
npx expo install --fix       # align dependencies with the SDK
npx expo-doctor@latest       # health check, include output in README
npx tsc --noEmit             # type check
```

If Expo Go reports an SDK mismatch: on Android, let Expo CLI install the matching Expo Go or download it from expo.dev/go; on iPhone, only the store version works, so the project must use the SDK the store Expo Go supports.

## 5. Folder layout (every app)

```
src/app/_layout.tsx              root Stack + providers
src/app/(tabs)/_layout.tsx       Tabs
src/app/(tabs)/index.tsx
src/app/item/[id].tsx            dynamic route
src/components/                  presentational components
src/features/<feature>/          hooks + screens logic per feature
src/lib/                         api client, firebase, query client, mqtt
src/db/                          SQLite migrations and repositories
```

Rules: screens never call `fetch`, SQL, Firestore or MQTT directly; they use hooks from `src/features` which use `src/lib` / `src/db`.

## 6. React mapping for Kotlin/Flutter developers (S1)

| Compose / Flutter | React Native |
|---|---|
| `@Composable fun` / `Widget build()` | function component returning JSX |
| parameters / constructor fields | props with a `type Props` |
| `remember { mutableStateOf() }` / `setState` | `const [x, setX] = useState<T>()` |
| `LaunchedEffect(key)` / `initState` + `dispose` | `useEffect(() => { ...; return cleanup }, [deps])` |
| `ViewModel` + `StateFlow` / `ChangeNotifier` + `Provider` | custom hook + Context (Zustand mentioned in S7) |
| `LazyColumn` / `ListView.builder` | `FlatList` (`data`, `renderItem`, `keyExtractor`) |
| NavHost / GoRouter | Expo Router (files are routes) |

React Compiler is enabled in the default template: do not drill `useMemo`/`useCallback`, but enforce the rules of hooks.

## 7. Expo Router (S1)

```tsx
// src/app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';

export default function TabsLayout() {
  return (
    <Tabs>
      <Tabs.Screen name="index" options={{ title: 'Profil' }} />
      <Tabs.Screen name="contacts" options={{ title: 'Contacts' }} />
    </Tabs>
  );
}
```

```tsx
// navigation and params
import { Link, useLocalSearchParams } from 'expo-router';
<Link href={{ pathname: '/contact/[id]', params: { id: contact.id } }}>{contact.name}</Link>
const { id } = useLocalSearchParams<{ id: string }>();
```

Use JS `Tabs`, not `NativeTabs`. [SDK] SDK 58 reworks the router core; check imports if upgrading.

## 8. SQLite (S2)

```tsx
// src/app/_layout.tsx
import { Stack } from 'expo-router';
import { SQLiteProvider } from 'expo-sqlite';
import { migrateDbIfNeeded } from '@/db/migrations';

export default function RootLayout() {
  return (
    <SQLiteProvider databaseName="app.db" onInit={migrateDbIfNeeded}>
      <Stack />
    </SQLiteProvider>
  );
}
```

```ts
// src/db/migrations.ts
import type { SQLiteDatabase } from 'expo-sqlite';

const DATABASE_VERSION = 2;

export async function migrateDbIfNeeded(db: SQLiteDatabase): Promise<void> {
  const row = await db.getFirstAsync<{ user_version: number }>('PRAGMA user_version');
  let version = row?.user_version ?? 0;
  if (version >= DATABASE_VERSION) return;
  if (version === 0) {
    await db.execAsync(`
      PRAGMA journal_mode = 'wal';
      CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        created_at INTEGER NOT NULL
      );
    `);
    version = 1;
  }
  if (version === 1) {
    await db.execAsync('ALTER TABLE expenses ADD COLUMN note TEXT;');
    version = 2;
  }
  await db.execAsync(`PRAGMA user_version = ${DATABASE_VERSION}`);
}
```

```ts
// src/db/expenseRepo.ts
import type { SQLiteDatabase } from 'expo-sqlite';

export type Expense = { id: number; label: string; amount: number; category: string; created_at: number; note: string | null };

export const expenseRepo = (db: SQLiteDatabase) => ({
  all: (category?: string) =>
    category
      ? db.getAllAsync<Expense>('SELECT * FROM expenses WHERE category = ? ORDER BY created_at DESC', category)
      : db.getAllAsync<Expense>('SELECT * FROM expenses ORDER BY created_at DESC'),
  total: async () =>
    (await db.getFirstAsync<{ total: number | null }>('SELECT SUM(amount) AS total FROM expenses'))?.total ?? 0,
  add: (e: Pick<Expense, 'label' | 'amount' | 'category'>) =>
    db.runAsync('INSERT INTO expenses (label, amount, category, created_at) VALUES (?, ?, ?, ?)', e.label, e.amount, e.category, Date.now()),
  update: (id: number, e: Pick<Expense, 'label' | 'amount' | 'category'>) =>
    db.runAsync('UPDATE expenses SET label = ?, amount = ?, category = ? WHERE id = ?', e.label, e.amount, e.category, id),
  remove: (id: number) => db.runAsync('DELETE FROM expenses WHERE id = ?', id),
});
```

Always use `?` parameters, never string interpolation of user input. Use `useSQLiteContext()` in hooks. Multi-step writes go in `db.withTransactionAsync`.

## 9. REST client and TanStack Query (S3)

DummyJSON base URL `https://dummyjson.com`. Useful endpoints: `/products?limit=&skip=`, `/products/search?q=`, `/products/categories`, `/products/category/{slug}`, `/products/{id}`, `POST /auth/login` (returns `accessToken`), `GET /auth/me`, `POST /carts/add`. `?delay=1500` simulates a slow network. Writes are simulated and never persisted. Use demo credentials listed on the DummyJSON users endpoint.

```ts
// src/lib/api.ts
const BASE_URL = 'https://dummyjson.com';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export async function api<T>(path: string, options: RequestInit & { token?: string | null } = {}): Promise<T> {
  const { token, headers, ...rest } = options;
  const res = await fetch(`${BASE_URL}${path}`, {
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  });
  if (!res.ok) {
    throw new ApiError(res.status, `HTTP ${res.status} on ${path}`);
  }
  return (await res.json()) as T;
}
```

```ts
// src/features/products/useProducts.ts
import { useInfiniteQuery, useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export type Product = { id: number; title: string; price: number; thumbnail: string; category: string };
type ProductPage = { products: Product[]; total: number; skip: number; limit: number };

const PAGE_SIZE = 20;

export function useProducts(category?: string) {
  return useInfiniteQuery({
    queryKey: ['products', { category }],
    initialPageParam: 0,
    queryFn: ({ pageParam }) =>
      api<ProductPage>(
        category
          ? `/products/category/${category}?limit=${PAGE_SIZE}&skip=${pageParam}`
          : `/products?limit=${PAGE_SIZE}&skip=${pageParam}`,
      ),
    getNextPageParam: (last) => (last.skip + last.limit < last.total ? last.skip + last.limit : undefined),
  });
}

export function useProduct(id: string) {
  return useQuery({ queryKey: ['product', id], queryFn: () => api<Product>(`/products/${id}`) });
}
```

FlatList with infinite query: `data={query.data?.pages.flatMap((p) => p.products) ?? []}`, `onEndReached={() => query.hasNextPage && !query.isFetchingNextPage && query.fetchNextPage()}`, `refreshControl` bound to `refetch`.

Token storage: `expo-secure-store` (`setItemAsync`, `getItemAsync`, `deleteItemAsync`), exposed through an `AuthContext`. Never store tokens in AsyncStorage or SQLite.

## 10. Firebase (S4)

```ts
// src/lib/firebase.ts
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getApp, getApps, initializeApp } from 'firebase/app';
// getReactNativePersistence may raise a TS2305 type error depending on the version; see section 14.
import { getAuth, getReactNativePersistence, initializeAuth, type Auth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: process.env.EXPO_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.EXPO_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.EXPO_PUBLIC_FIREBASE_APP_ID,
};

export const app = getApps().length ? getApp() : initializeApp(firebaseConfig);

let auth: Auth;
try {
  auth = initializeAuth(app, { persistence: getReactNativePersistence(AsyncStorage) });
} catch {
  auth = getAuth(app);
}
export { auth };
export const db = getFirestore(app); // memory cache only on React Native
```

```ts
// realtime listener inside a hook
useEffect(() => {
  const q = query(collection(db, 'tasks'), orderBy('createdAt', 'desc'));
  const unsubscribe = onSnapshot(q, (snap) => {
    setTasks(snap.docs.map((d) => ({ id: d.id, ...(d.data() as Omit<Task, 'id'>) })));
  });
  return unsubscribe;
}, []);
```

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /tasks/{taskId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null && request.resource.data.ownerId == request.auth.uid;
      allow update, delete: if request.auth != null && resource.data.ownerId == request.auth.uid;
    }
  }
}
```

One Firebase project per student (or per pair in S4). Spark plan daily quotas apply; never call `onSnapshot` outside an effect with cleanup. Restart `npx expo start` after editing `.env`.

## 11. Offline-first (S5)

```tsx
// src/lib/query.tsx
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister';
import { focusManager, onlineManager, QueryClient } from '@tanstack/react-query';
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client';
import { useEffect, type ReactNode } from 'react';
import { AppState } from 'react-native';

onlineManager.setEventListener((setOnline) =>
  NetInfo.addEventListener((state) => setOnline(!!state.isConnected)),
);

const ONE_DAY = 1000 * 60 * 60 * 24;

export const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000, gcTime: ONE_DAY, retry: 2 } },
});

const persister = createAsyncStoragePersister({ storage: AsyncStorage });

export function QueryProvider({ children }: { children: ReactNode }) {
  useEffect(() => {
    const sub = AppState.addEventListener('change', (status) => focusManager.setFocused(status === 'active'));
    return () => sub.remove();
  }, []);
  return (
    <PersistQueryClientProvider client={queryClient} persistOptions={{ persister, maxAge: ONE_DAY }}>
      {children}
    </PersistQueryClientProvider>
  );
}
```

`gcTime` must be >= `maxAge`. In S3 use a plain `QueryClientProvider`; S5 replaces it with this provider.

Local notifications:

```ts
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowBanner: true,
    shouldShowList: true,
    shouldPlaySound: false,
    shouldSetBadge: false,
  }),
});

export async function scheduleReminder(title: string, body: string, seconds: number) {
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('reminders', {
      name: 'Rappels',
      importance: Notifications.AndroidImportance.HIGH,
    });
  }
  const { status } = await Notifications.requestPermissionsAsync();
  if (status !== 'granted') return null;
  return Notifications.scheduleNotificationAsync({
    content: { title, body },
    trigger: { type: Notifications.SchedulableTriggerInputTypes.TIME_INTERVAL, seconds, channelId: 'reminders' },
  });
}
```

Never call push-token APIs. [SDK] SDK 58 changes foreground display defaults.

## 12. MQTT (S6)

Broker options (WebSocket endpoint for the app, TCP for the ESP32):
- HiveMQ public broker: app `wss://broker.hivemq.com:8884/mqtt`, ESP32 `broker.hivemq.com:1883`. Public: anyone can read; always use a unique topic prefix.
- HiveMQ Cloud free tier: private, username/password, TLS; recommended if public brokers are unreliable or for the final project.

Topic convention: `iset/iam2/<student>/sensors` (JSON `{"t": 24.5, "h": 51, "ts": 1730000000}`), `iset/iam2/<student>/status` (retained `online`/`offline`, LWT), `iset/iam2/<student>/cmd/led` (`on`/`off`), `iset/iam2/<student>/state/led` (device acknowledgement, retained).

```ts
// src/lib/useMqtt.ts
import mqtt, { type MqttClient } from 'mqtt';
import { useEffect, useRef, useState } from 'react';

type Status = 'connecting' | 'connected' | 'reconnecting' | 'offline';

export function useMqtt(url: string, topics: string[], onMessage: (topic: string, payload: string) => void) {
  const clientRef = useRef<MqttClient | null>(null);
  const [status, setStatus] = useState<Status>('connecting');

  useEffect(() => {
    const client = mqtt.connect(url, {
      clientId: `iam2-app-${Math.random().toString(16).slice(2, 10)}`,
      clean: true,
      reconnectPeriod: 2000,
      connectTimeout: 10_000,
    });
    clientRef.current = client;
    client.on('connect', () => {
      setStatus('connected');
      client.subscribe(topics, { qos: 1 });
    });
    client.on('reconnect', () => setStatus('reconnecting'));
    client.on('offline', () => setStatus('offline'));
    client.on('message', (topic, payload) => onMessage(topic, payload.toString()));
    return () => {
      client.end(true);
    };
  }, [url, topics.join('|')]);

  const publish = (topic: string, message: string, retain = false) =>
    clientRef.current?.publish(topic, message, { qos: 1, retain });

  return { status, publish };
}
```

Import as `import mqtt from 'mqtt'` (SDK 54+ needs no Metro config). If the bundle fails, try `import mqtt from 'mqtt/dist/mqtt.esm.js'` and report it. Parse JSON payloads in a `try/catch` and ignore malformed messages.

ESP32 reference (Wokwi: ESP32 + DHT22 on pin 15, LED on pin 2, Wi-Fi `Wokwi-GUEST`, no password, library PubSubClient + DHT sensor library):

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

const char* WIFI_SSID = "Wokwi-GUEST";
const char* MQTT_HOST = "broker.hivemq.com";
const char* BASE = "iset/iam2/student01";   // change per student

WiFiClient net;
PubSubClient mqttClient(net);
DHT dht(15, DHT22);
unsigned long lastPublish = 0;

String topic(const char* suffix) { return String(BASE) + "/" + suffix; }

void onMessage(char* t, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  if (String(t) == topic("cmd/led")) {
    bool on = msg == "on";
    digitalWrite(2, on ? HIGH : LOW);
    mqttClient.publish(topic("state/led").c_str(), on ? "on" : "off", true);
  }
}

void connectMqtt() {
  while (!mqttClient.connected()) {
    String id = "esp32-" + String((uint32_t)ESP.getEfuseMac(), HEX);
    if (mqttClient.connect(id.c_str(), topic("status").c_str(), 1, true, "offline")) {
      mqttClient.publish(topic("status").c_str(), "online", true);
      mqttClient.subscribe(topic("cmd/led").c_str());
    } else {
      delay(2000);
    }
  }
}

void setup() {
  pinMode(2, OUTPUT);
  dht.begin();
  WiFi.begin(WIFI_SSID, "");
  while (WiFi.status() != WL_CONNECTED) delay(250);
  mqttClient.setServer(MQTT_HOST, 1883);
  mqttClient.setCallback(onMessage);
}

void loop() {
  if (!mqttClient.connected()) connectMqtt();
  mqttClient.loop();
  if (millis() - lastPublish > 5000) {
    lastPublish = millis();
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (!isnan(t) && !isnan(h)) {
      String json = "{\"t\":" + String(t, 1) + ",\"h\":" + String(h, 1) + ",\"ts\":" + String(millis() / 1000) + "}";
      mqttClient.publish(topic("sensors").c_str(), json.c_str());
    }
  }
}
```

## 13. Forbidden or outdated patterns

- Class components, `componentDidMount`, `this.setState`
- `useEffect` + `fetch` for server data after S3 (use TanStack Query)
- `onSnapshot` without unsubscribe
- AsyncStorage for tokens (use SecureStore)
- `react-native-mmkv`, `@react-native-firebase/*`, `expo prebuild`, push tokens
- MQTT URLs with `mqtt://` or port 1883 in the app
- `npm install` for Expo modules (use `npx expo install`)
- `any`, `@ts-ignore` (exception: documented Firebase persistence typing workaround with `@ts-expect-error` and a comment)
- React Navigation imports in app code (use Expo Router)
- Any emoji in generated content

## 14. Points to verify before each session

- Store Expo Go SDK on Android and iPhone; template tag still valid.
- Firebase `getReactNativePersistence` typing: if `npx tsc --noEmit` reports TS2305, apply the chosen workaround consistently.
- MQTT.js bundles and connects over `wss://` in Expo Go on both platforms; broker WebSocket port/path still valid.
- Wokwi simulation still reaches the broker from Wokwi-GUEST.
- `npx expo-doctor` clean with the session package set.
