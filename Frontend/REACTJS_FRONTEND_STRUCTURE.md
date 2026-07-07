# AGENT INSTRUCTIONS — React.js Frontend (Vite + SPA)

> **HOW TO USE THIS FILE**
> Drop this file into your project root. When starting a new chat, say:
> _"Read `REACTJS_FRONTEND_STRUCTURE.md` deeply and follow every instruction in it for all code you generate."_
> This file is the single source of truth. No exceptions.

---

## YOUR IDENTITY

You are a senior React frontend engineer building enterprise-grade SPAs with Vite.
This app connects to a REST API backend — FastAPI, ASP.NET Core, or Spring Boot.
Every file you generate MUST follow the exact structure, patterns, and rules in this document.
You have creative freedom only over feature UI and business logic — never over architecture.

---

## TECH STACK — USE EXACTLY THESE

```
Build Tool     : Vite 6              (not CRA — never Create React App)
Framework      : React 19            (functional components + hooks only)
Language       : TypeScript 5        (strict: true — always on)
Routing        : React Router v6     (createBrowserRouter + Outlet)
Styling        : Tailwind CSS 4      + your own ui/ primitives
Server State   : TanStack Query v5   (all API data lives here)
Client State   : Zustand 5           (UI-only state)
Forms          : React Hook Form 7   + Zod resolver
Validation     : Zod 3
HTTP Client    : Axios 1.x           (one instance, one file)
Auth           : JWT (in-memory store — never localStorage)
Icons          : lucide-react
Dates          : date-fns
```

---

## MANDATORY FOLDER STRUCTURE

```
frontend/
│
├── public/
│
└── src/
    │
    ├── router/                               # Routing config — all routes defined here
    │   ├── index.tsx                         # createBrowserRouter — root router
    │   ├── ProtectedRoute.tsx                # Auth guard wrapper component
    │   └── GuestRoute.tsx                    # Redirect logged-in users away from login
    │
    ├── pages/                                # Thin page shells — maps 1:1 with routes
    │   ├── auth/
    │   │   ├── LoginPage.tsx                 # Renders LoginForm from features
    │   │   └── RegisterPage.tsx
    │   └── dashboard/
    │       ├── DashboardPage.tsx
    │       └── {feature}/
    │           ├── {Feature}ListPage.tsx     # Renders feature component from components/pages
    │           └── {Feature}DetailPage.tsx
    │
    ├── components/
    │   │
    │   ├── ui/                               # Primitive building blocks — zero business rules
    │   │   ├── Button.tsx
    │   │   ├── Input.tsx
    │   │   ├── Modal.tsx
    │   │   ├── ConfirmDialog.tsx
    │   │   ├── Card.tsx
    │   │   ├── Badge.tsx
    │   │   ├── EmptyState.tsx
    │   │   ├── Skeleton.tsx
    │   │   └── StatCard.tsx
    │   │
    │   ├── layout/                           # App shell components
    │   │   ├── AppShell.tsx
    │   │   ├── AuthenticatedLayout.tsx       # Wraps all protected pages
    │   │   ├── Sidebar.tsx
    │   │   ├── MobileNav.tsx
    │   │   └── PageHeader.tsx
    │   │
    │   ├── shared/                           # Composites used by 2+ features
    │   │   ├── DataTable.tsx
    │   │   ├── RoleGate.tsx
    │   │   └── ErrorBoundary.tsx
    │   │
    │   └── pages/                            # Feature modules — one folder per feature
    │       └── {feature}/
    │           ├── {Feature}Page.tsx         # Top-level feature component
    │           ├── index.ts                  # Barrel — exports page-level only
    │           ├── constants.ts
    │           ├── hooks/                    # TanStack Query hooks (PRIVATE)
    │           │   └── use{Feature}.ts
    │           ├── schemas/                  # Zod schemas (PRIVATE)
    │           │   └── {feature}.schema.ts
    │           └── components/              # Sub-components (PRIVATE to this feature)
    │               ├── {Feature}List.tsx
    │               ├── {Feature}CreateForm.tsx
    │               └── {Feature}Card.tsx
    │
    ├── hooks/                                # Shared hooks — used by 2+ features
    │   ├── usePaginatedList.ts
    │   ├── useDebounce.ts
    │   └── useLocalStorage.ts
    │
    ├── lib/                                  # Infrastructure — no JSX
    │   ├── api/
    │   │   ├── client.ts                     # Axios instance + interceptors
    │   │   ├── endpoints.ts                  # ALL backend URLs
    │   │   └── adapters.ts                   # Normalize backend response shapes
    │   ├── query/
    │   │   ├── client.ts                     # QueryClient singleton
    │   │   └── keys.ts                       # Query key factory
    │   ├── auth/
    │   │   ├── token-store.ts                # In-memory token (never localStorage)
    │   │   └── auth-service.ts               # login/logout/refresh
    │   ├── store/
    │   │   ├── ui.store.ts                   # Sidebar, theme (Zustand)
    │   │   └── auth.store.ts                 # Cached user (Zustand — not persisted)
    │   ├── types/
    │   │   ├── common.types.ts               # PaginatedResponse<T>, ApiError
    │   │   └── {feature}.types.ts            # One file per domain
    │   ├── permissions.ts
    │   ├── nav.ts
    │   └── utils/
    │       ├── cn.ts
    │       └── format.ts
    │
    ├── main.tsx                              # App entry — mounts <App />
    └── App.tsx                               # Providers wrapper + RouterProvider
```

---

## COMPONENT VISIBILITY RULES

```
┌─────────────────────────────────────────────────────────────────┐
│  components/ui/          importable by: EVERYONE                │
│  components/layout/      importable by: EVERYONE                │
│  components/shared/      importable by: ANY feature page        │
│  components/pages/{x}/   importable by: ONLY files inside {x}/  │
└─────────────────────────────────────────────────────────────────┘

Sub-components are PRIVATE — one feature CANNOT import another feature's sub-components.
Used in 1 feature → stays in components/pages/{feature}/components/
Used in 2+ features → promote to components/shared/
```

---

## THE 3 LAWS

```
LAW 1 — pages/ is for ROUTES ONLY
  Every page component = one import + one return. Max 10 lines.
  Zero hooks. Zero logic. Zero API calls.

LAW 2 — components/ is JSX ONLY
  Every file inside components/ returns JSX.
  Hook files (use*.ts) live in hooks/ — either feature-level or root hooks/.
  NEVER put a .ts hook file inside components/.

LAW 3 — lib/ is INFRASTRUCTURE ONLY
  No JSX. No React hooks. Pure TypeScript.
```

---

## LAYER 1 — `src/main.tsx` and `src/App.tsx`

```tsx
// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

```tsx
// src/App.tsx
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools }   from "@tanstack/react-query-devtools";
import { RouterProvider }        from "react-router-dom";
import { Toaster }               from "sonner";
import { queryClient }           from "@/lib/query/client";
import { router }                from "@/router";

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <Toaster position="top-right" richColors closeButton />
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  );
}
```

---

## LAYER 2 — `src/router/index.tsx` — All Routes Defined Here

```tsx
// src/router/index.tsx
import { createBrowserRouter, Navigate } from "react-router-dom";
import { AuthenticatedLayout }  from "@/components/layout/AuthenticatedLayout";
import { ProtectedRoute }        from "./ProtectedRoute";
import { GuestRoute }            from "./GuestRoute";

// Pages — thin shells
import { LoginPage }      from "@/pages/auth/LoginPage";
import { DashboardPage }  from "@/pages/dashboard/DashboardPage";
import { UsersListPage }  from "@/pages/dashboard/users/UsersListPage";
import { UserDetailPage } from "@/pages/dashboard/users/UserDetailPage";
// Add new pages here — one import per feature

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/dashboard" replace />,
  },
  {
    // Guest routes — redirect logged-in users
    element: <GuestRoute />,
    children: [
      { path: "/login",    element: <LoginPage /> },
      { path: "/register", element: <LoginPage /> },
    ],
  },
  {
    // Protected routes — redirect unauthenticated users to /login
    element: <ProtectedRoute />,
    children: [
      {
        element: <AuthenticatedLayout />,
        children: [
          { path: "/dashboard",     element: <DashboardPage /> },
          { path: "/users",         element: <UsersListPage /> },
          { path: "/users/:id",     element: <UserDetailPage /> },
          // Add new feature routes here
        ],
      },
    ],
  },
  { path: "*", element: <Navigate to="/dashboard" replace /> },
]);
```

```tsx
// src/router/ProtectedRoute.tsx
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { tokenStore } from "@/lib/auth/token-store";

export function ProtectedRoute() {
  const location = useLocation();
  const token    = tokenStore.get();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return <Outlet />;
}
```

```tsx
// src/router/GuestRoute.tsx
import { Navigate, Outlet } from "react-router-dom";
import { tokenStore } from "@/lib/auth/token-store";

export function GuestRoute() {
  const token = tokenStore.get();
  if (token) return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}
```

---

## LAYER 3 — `src/pages/` — Thin Route Shells

```tsx
// src/pages/dashboard/users/UsersListPage.tsx — max 8 lines
import { UsersPage } from "@/components/pages/users";

export function UsersListPage() {
  return <UsersPage />;
}
```

```tsx
// src/pages/dashboard/users/UserDetailPage.tsx
import { useParams } from "react-router-dom";
import { UserDetailPage as UserDetail } from "@/components/pages/users";

export function UserDetailPage() {
  const { id } = useParams<{ id: string }>();
  return <UserDetail userId={id!} />;
}
```

---

## LAYER 4 — `lib/api/client.ts` — The Only Axios Instance

```typescript
// src/lib/api/client.ts
import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { tokenStore }    from "@/lib/auth/token-store";
import { normalizeError } from "./adapters";

const apiClient = axios.create({
  baseURL:         import.meta.env.VITE_API_URL,
  timeout:         15_000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    Accept:         "application/json",
  },
});

// Attach token automatically on every request
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    const token = tokenStore.get();
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (err) => Promise.reject(err)
);

// Global error handling — never handle 401 in a component
apiClient.interceptors.response.use(
  (res) => res,
  (err: AxiosError) => {
    if (err.response?.status === 401) {
      tokenStore.clear();
      window.location.href = "/login";
      return Promise.reject(err);
    }
    return Promise.reject(new Error(normalizeError(err.response?.data)));
  }
);

export default apiClient;
```

---

## LAYER 5 — `lib/auth/token-store.ts` — In-Memory Token (Never localStorage)

```typescript
// src/lib/auth/token-store.ts
// Token lives in memory ONLY — never written to localStorage or sessionStorage.
// Lost on page refresh — user must log in again (acceptable for security).
// For "remember me": use httpOnly cookies on the backend instead.

let _accessToken:  string | null = null;
let _refreshToken: string | null = null;

export const tokenStore = {
  get:          ()              => _accessToken,
  getRefresh:   ()              => _refreshToken,
  set:          (access: string, refresh?: string) => {
    _accessToken  = access;
    if (refresh) _refreshToken = refresh;
  },
  clear:        () => { _accessToken = null; _refreshToken = null; },
  isLoggedIn:   () => _accessToken !== null,
};
```

---

## LAYER 6 — `lib/auth/auth-service.ts`

```typescript
// src/lib/auth/auth-service.ts
import apiClient   from "@/lib/api/client";
import { ENDPOINTS } from "@/lib/api/endpoints";
import { tokenStore }  from "./token-store";
import { useAuthStore } from "@/lib/store/auth.store";

interface LoginPayload { email: string; password: string; }
interface TokenData    { access_token?: string; accessToken?: string; token?: string; }

export const authService = {
  async login(payload: LoginPayload): Promise<void> {
    const { data } = await apiClient.post<TokenData>(ENDPOINTS.auth.login, payload);

    // Handles FastAPI, ASP.NET Core, and Spring Boot token field names
    const token = data.access_token ?? data.accessToken ?? data.token;
    if (!token) throw new Error("No access token in response.");
    tokenStore.set(token);

    // Fetch and cache user profile
    const { data: user } = await apiClient.get(ENDPOINTS.auth.me);
    useAuthStore.getState().setUser(user);
  },

  logout(): void {
    tokenStore.clear();
    useAuthStore.getState().clearUser();
    window.location.href = "/login";
  },
};
```

---

## LAYER 7 — `lib/api/endpoints.ts`

```typescript
// src/lib/api/endpoints.ts
const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export const ENDPOINTS = {
  auth: {
    login:   `${BASE}/auth/login`,
    me:      `${BASE}/auth/me`,
    logout:  `${BASE}/auth/logout`,
    refresh: `${BASE}/auth/refresh`,
  },
  users: {
    list:   `${BASE}/users`,
    create: `${BASE}/users`,
    detail: (id: string) => `${BASE}/users/${id}`,
    update: (id: string) => `${BASE}/users/${id}`,
    delete: (id: string) => `${BASE}/users/${id}`,
  },
  // Template — add endpoints for every new feature:
  // {feature}: {
  //   list:   `${BASE}/{feature}`,
  //   create: `${BASE}/{feature}`,
  //   detail: (id: string) => `${BASE}/{feature}/${id}`,
  //   update: (id: string) => `${BASE}/{feature}/${id}`,
  //   delete: (id: string) => `${BASE}/{feature}/${id}`,
  // },
} as const;
```

---

## LAYER 8 — `lib/api/adapters.ts` — Backend-Agnostic

```typescript
// src/lib/api/adapters.ts
type Backend = "fastapi" | "aspnet" | "springboot";
const BACKEND = (import.meta.env.VITE_BACKEND_TYPE ?? "fastapi") as Backend;

export interface PaginatedResponse<T> {
  items: T[]; total: number; page: number; size: number;
}

export function normalizePaginated<T>(raw: unknown): PaginatedResponse<T> {
  const r = raw as Record<string, unknown>;
  switch (BACKEND) {
    case "fastapi":    return { items: r.items    as T[], total: r.total         as number, page: r.page       as number, size: r.size     as number };
    case "aspnet":     return { items: r.data     as T[], total: r.totalCount    as number, page: r.pageNumber as number, size: r.pageSize  as number };
    case "springboot": return { items: r.content  as T[], total: r.totalElements as number, page: (r.number as number) + 1, size: r.size   as number };
  }
}

export function normalizeError(data: unknown): string {
  const e = data as Record<string, unknown> | undefined;
  if (!e) return "An unexpected error occurred.";
  if (typeof e.detail  === "string") return e.detail;
  if (typeof e.message === "string") return e.message;
  if (Array.isArray(e.detail))       return (e.detail as { msg: string }[])[0]?.msg ?? "Error";
  return "An unexpected error occurred.";
}
```

---

## LAYER 9 — `lib/query/`

```typescript
// src/lib/query/client.ts
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries:   { staleTime: 1000 * 60 * 5, gcTime: 1000 * 60 * 10, retry: 1, refetchOnWindowFocus: false },
    mutations: { retry: 0 },
  },
});
```

```typescript
// src/lib/query/keys.ts
export const queryKeys = {
  users: {
    all:    ()           => ["users"]               as const,
    lists:  ()           => ["users", "list"]       as const,
    list:   (p: object)  => ["users", "list", p]    as const,
    detail: (id: string) => ["users", "detail", id] as const,
  },
  // Template — add keys for every new feature:
  // {feature}: {
  //   all:    ()           => ["{feature}"]                   as const,
  //   lists:  ()           => ["{feature}", "list"]           as const,
  //   list:   (p: object)  => ["{feature}", "list", p]        as const,
  //   detail: (id: string) => ["{feature}", "detail", id]     as const,
  // },
} as const;
```

---

## LAYER 10 — Feature `hooks/use{Feature}.ts`

```typescript
// src/components/pages/users/hooks/useUsers.ts
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast }                from "sonner";
import apiClient                from "@/lib/api/client";
import { normalizePaginated }   from "@/lib/api/adapters";
import { ENDPOINTS }            from "@/lib/api/endpoints";
import { queryKeys }            from "@/lib/query/keys";
import type { PaginatedResponse } from "@/lib/api/adapters";
import type { User, UserCreate, UserListParams, UserUpdate } from "@/lib/types/user.types";

export function useUsers(params?: UserListParams) {
  return useQuery({
    queryKey: queryKeys.users.list(params ?? {}),
    queryFn:  async () => {
      const { data } = await apiClient.get(ENDPOINTS.users.list, { params });
      return normalizePaginated<User>(data) as PaginatedResponse<User>;
    },
  });
}

export function useUser(id: string) {
  return useQuery({
    queryKey: queryKeys.users.detail(id),
    queryFn:  async () => {
      const { data } = await apiClient.get<User>(ENDPOINTS.users.detail(id));
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: UserCreate) => {
      const { data } = await apiClient.post<User>(ENDPOINTS.users.create, payload);
      return data;
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: queryKeys.users.lists() }); toast.success("Created."); },
    onError:   (err: Error) => toast.error(err.message),
  });
}

export function useUpdateUser(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: UserUpdate) => {
      const { data } = await apiClient.patch<User>(ENDPOINTS.users.update(id), payload);
      return data;
    },
    onSuccess: (updated) => {
      qc.setQueryData(queryKeys.users.detail(id), updated);
      qc.invalidateQueries({ queryKey: queryKeys.users.lists() });
      toast.success("Updated.");
    },
    onError: (err: Error) => toast.error(err.message),
  });
}

export function useDeleteUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => { await apiClient.delete(ENDPOINTS.users.delete(id)); },
    onSuccess: () => { qc.invalidateQueries({ queryKey: queryKeys.users.lists() }); toast.success("Deleted."); },
    onError:   (err: Error) => toast.error(err.message),
  });
}
```

---

## LAYER 11 — Feature Schema + Page Component

```typescript
// src/components/pages/users/schemas/user.schema.ts
import { z } from "zod";

export const createUserSchema = z.object({
  email:     z.string().email("Invalid email"),
  full_name: z.string().min(2).max(100),
  password:  z.string().min(8).max(128)
               .regex(/[A-Z]/, "Needs uppercase").regex(/[0-9]/, "Needs a number"),
  role:      z.enum(["admin", "manager", "staff", "viewer"]),
});

export type CreateUserInput = z.infer<typeof createUserSchema>;
```

```tsx
// src/components/pages/users/UsersPage.tsx
import { useState } from "react";
import { PageHeader }     from "@/components/layout/PageHeader";
import { Button }         from "@/components/ui/Button";
import { Modal }          from "@/components/ui/Modal";
import { UserList }       from "./components/UserList";
import { UserCreateForm } from "./components/UserCreateForm";
import { useUsers }       from "./hooks/useUsers";

export function UsersPage() {
  const [open,   setOpen]   = useState(false);
  const [params, setParams] = useState({ skip: 0, limit: 20 });
  const { data, isLoading, isError } = useUsers(params);

  return (
    <div className="space-y-6">
      <PageHeader title="Users" description="Manage system users.">
        <Button onClick={() => setOpen(true)}>Add User</Button>
      </PageHeader>

      {isError && <p className="text-sm text-red-500">Failed to load. Please refresh.</p>}

      <UserList items={data?.items ?? []} total={data?.total ?? 0}
        isLoading={isLoading} onPaginationChange={setParams} />

      <Modal open={open} onClose={() => setOpen(false)} title="Add User">
        <UserCreateForm onSuccess={() => setOpen(false)} />
      </Modal>
    </div>
  );
}
```

---

## LAYER 12 — `lib/store/` — Zustand + `lib/permissions.ts` + `lib/nav.ts`

```typescript
// src/lib/store/ui.store.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface UIState {
  sidebarOpen:   boolean;
  theme:         "light" | "dark" | "system";
  toggleSidebar: () => void;
  setTheme:      (t: "light" | "dark" | "system") => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen:   true,
      theme:         "system",
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      setTheme:      (theme) => set({ theme }),
    }),
    { name: "ui-prefs" }
  )
);
```

---

```typescript
// src/lib/permissions.ts
export type UserRole = "admin" | "manager" | "staff" | "viewer";

export const PERMISSIONS: Record<string, Partial<Record<"view"|"create"|"edit"|"delete", UserRole[]>>> = {
  users:    { view: ["admin","manager"], create: ["admin"], edit: ["admin"], delete: ["admin"] },
  settings: { view: ["admin","manager","staff","viewer"], edit: ["admin"] },
};

export function can(role: UserRole, action: "view"|"create"|"edit"|"delete", resource: string): boolean {
  return PERMISSIONS[resource]?.[action]?.includes(role) ?? false;
}
```

```typescript
// src/lib/nav.ts
import type { LucideIcon } from "lucide-react";
import { LayoutDashboard, Users, Settings } from "lucide-react";
import type { UserRole } from "./permissions";

export interface NavItem { label: string; path: string; icon: LucideIcon; allowedRoles: UserRole[]; }

export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard, allowedRoles: ["admin","manager","staff","viewer"] },
  { label: "Users",     path: "/users",     icon: Users,           allowedRoles: ["admin","manager"] },
  { label: "Settings",  path: "/settings",  icon: Settings,        allowedRoles: ["admin"] },
];
```

```typescript
// src/lib/store/auth.store.ts
import { create } from "zustand";

interface AuthUser { id: string; email: string; full_name: string; role: string; }
interface AuthState { user: AuthUser | null; setUser: (u: AuthUser | null) => void; clearUser: () => void; }

export const useAuthStore = create<AuthState>()((set) => ({
  user:      null,
  setUser:   (user) => set({ user }),
  clearUser: () => set({ user: null }),
}));
```

---

## LAYER 13 — `vite.config.ts` + `.env`

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react  from "@vitejs/plugin-react";
import path   from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: {
    port: 3000,
    proxy: {
      // Dev proxy — hides backend port from browser
      "/api": {
        target:      "http://localhost:8000",
        changeOrigin: true,
        secure:       false,
      },
    },
  },
});
```

```bash
# .env.local  (never commit)
VITE_API_URL=https://api.yourdomain.com/api/v1
VITE_BACKEND_TYPE=fastapi

# .env.example  (commit this)
VITE_API_URL=
VITE_BACKEND_TYPE=fastapi
```

**Security Note:** In development, the Vite proxy forwards `/api/*` requests to the backend — the browser never sees the backend port. In production, all requests go through the Traefik/Nginx reverse proxy at the production URL.

---

## NAMING CONVENTIONS

| What | Convention | Example |
|------|-----------|---------|
| Feature page components | `{Feature}Page.tsx` | `UsersPage.tsx` |
| Route page shells | `{Feature}ListPage.tsx` | `UsersListPage.tsx` |
| Sub-components | `{Feature}{Name}.tsx` | `UserCreateForm.tsx` |
| UI primitives | `PascalCase.tsx` | `Button.tsx`, `Modal.tsx` |
| Feature hooks | `use{Feature}.ts` | `useUsers.ts` |
| Shared hooks | `use{Name}.ts` | `usePaginatedList.ts` |
| Schemas | `{feature}.schema.ts` | `user.schema.ts` |
| Types | `{feature}.types.ts` | `user.types.ts` |
| Stores | `{name}.store.ts` | `ui.store.ts` |
| Barrel files | `index.ts` | page-level exports only |
| Env vars | `VITE_UPPER_SNAKE` | `VITE_API_URL` |

---

## WHEN ADDING A NEW FEATURE

```
STEP 1   src/lib/types/{feature}.types.ts
STEP 2   src/lib/api/endpoints.ts             → add {feature} endpoints
STEP 3   src/lib/query/keys.ts                → add {feature} keys
STEP 4   src/components/pages/{feature}/schemas/{feature}.schema.ts
STEP 5   src/components/pages/{feature}/hooks/use{Feature}.ts
STEP 6   src/components/pages/{feature}/components/{Feature}List.tsx
         src/components/pages/{feature}/components/{Feature}CreateForm.tsx
STEP 7   src/components/pages/{feature}/{Feature}Page.tsx
STEP 8   src/components/pages/{feature}/index.ts
STEP 9   src/pages/dashboard/{feature}/{Feature}ListPage.tsx (thin shell)
STEP 10  src/router/index.tsx → add route { path: "/{feature}", element: <...> }
STEP 11  src/lib/nav.ts → add navigation entry
STEP 12  src/lib/permissions.ts (if role-gated)
```

---

## ABSOLUTE PROHIBITIONS

```
✗  Logic or hooks inside src/pages/ — page shells only
✗  Hook files (use*.ts) inside components/
✗  One feature importing sub-components from another feature
✗  import axios directly — always import apiClient
✗  Hardcoded backend URLs — always use ENDPOINTS.*
✗  Token stored in localStorage — in-memory tokenStore only
✗  401 handling inside a component — interceptor handles it
✗  new QueryClient() in a component — import from lib/query/client.ts
✗  Zustand for API/server data — TanStack Query owns it
✗  toast.success/error in components — only in mutation onSuccess/onError
✗  Multiple Toaster instances — one in App.tsx only
✗  Multiple apiClient instances — one in lib/api/client.ts only
✗  moment.js — use date-fns
✗  style={{}} inline — Tailwind only
✗  Redux or React Context for state
✗  Class components — functional only
✗  Create React App (CRA) — Vite only
```

---

## PRE-COMPLETION CHECKLIST

```
[ ] src/pages/ shell is ≤ 8 lines: one import + one return
[ ] No hook files inside components/ folder
[ ] No cross-feature sub-component imports
[ ] All URLs in ENDPOINTS — no hardcoded strings
[ ] All query keys in queryKeys factory
[ ] Forms: React Hook Form + Zod zodResolver
[ ] Toasts only in mutation onSuccess / onError
[ ] normalizePaginated() for all list API calls
[ ] New route added to src/router/index.tsx
[ ] New feature added to lib/nav.ts
[ ] TypeScript strict — no `any` without comment
[ ] Token handled by tokenStore — never localStorage
```

---

## DATA FLOW

```
User submits form
  → {Feature}CreateForm → useCreate{Feature}().mutate(values)
  → apiClient.post(ENDPOINTS.{feature}.create, payload)
  → interceptor injects Authorization: Bearer {token}
  → backend responds → normalizeError on failure
  → onSuccess → invalidateQueries → list re-fetches
  → toast.success(...)

User navigates to /{feature}
  → React Router → ProtectedRoute checks tokenStore.get()
  → No token → redirect to /login
  → Token valid → renders {Feature}ListPage → {Feature}Page
  → use{Feature}s() fires → normalizePaginated → renders list
```

---

*Vite 6 · React 19 · TypeScript 5 · React Router v6 · TanStack Query v5 · Zustand 5 · Zod 3 · React Hook Form 7 · Tailwind CSS 4*
*Works with: FastAPI · ASP.NET Core · Spring Boot*

---

## Copyright

© 2026 **Udhayaboopathi V**. All rights reserved.

- Author:  Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub:  [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
