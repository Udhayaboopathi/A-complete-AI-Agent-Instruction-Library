# AGENT INSTRUCTIONS — Next.js Frontend

> **HOW TO USE THIS FILE**
> Drop this file into your project root. When starting a new chat, say:
> _"Read `NEXTJS_FRONTEND_STRUCTURE.md` deeply and follow every instruction in it for all code you generate."_
> This file is the single source of truth. No exceptions.

---

## YOUR IDENTITY

You are a senior Next.js frontend engineer.
This app is a dashboard that connects to a REST API backend — **FastAPI**, **ASP.NET Core**, or **Spring Boot**. You do not care which one. You only speak HTTP.
Follow every rule in this file for every file you generate.

---

## TECH STACK

```
Framework     : Next.js 15        App Router only — never Pages Router
Language      : TypeScript 5      strict: true — always on
Styling       : Tailwind CSS 4    + your own ui/ primitives
Server State  : TanStack Query v5 all API data lives here
Client State  : Zustand 5         UI-only state (sidebar, theme, modals)
Forms         : React Hook Form 7 + Zod resolver
Validation    : Zod 3             all form schemas + API response shapes
HTTP Client   : Axios 1.x         one instance, one file, interceptors only
Auth          : next-auth v5      JWT — backend issues the token
Icons         : lucide-react
Dates         : date-fns
```

---

## FOLDER STRUCTURE

```
frontend/
│
├── app/                                   # Routes only — thin shells, zero logic
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   │
│   ├── (dashboard)/
│   │   ├── layout.tsx                     # Imports AppShell — nothing else
│   │   ├── page.tsx                       # /dashboard home
│   │   └── {pagename}/                    # One folder per page/feature
│   │       ├── page.tsx                   # List/index view
│   │       └── [id]/
│   │           └── page.tsx               # Detail view
│   │
│   ├── api/
│   │   └── auth/[...nextauth]/route.ts
│   ├── error.tsx
│   ├── not-found.tsx
│   ├── globals.css
│   └── layout.tsx                         # Root — mounts Providers only
│
├── components/
│   │
│   ├── ui/                                # Primitive building blocks — zero business rules
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
│   ├── layout/                            # App shell — used by every authenticated page
│   │   ├── AppShell.tsx
│   │   ├── AuthenticatedLayout.tsx
│   │   ├── Sidebar.tsx
│   │   ├── MobileNav.tsx
│   │   └── PageHeader.tsx
│   │
│   ├── shared/                            # Composites used by 2+ features
│   │   ├── DataTable.tsx
│   │   ├── RoleGate.tsx
│   │   ├── ErrorBoundary.tsx
│   │   └── Providers.tsx
│   │
│   └── pages/                             # Feature modules — one folder per page
│       └── {pagename}/
│           ├── {Page}Page.tsx             # Top-level component — used by app/{pagename}/page.tsx
│           ├── {Page}DetailPage.tsx       # Detail view (if needed)
│           ├── index.ts                   # Barrel — exports only what app/ needs
│           ├── constants.ts               # Local constants for this feature
│           │
│           ├── hooks/                     # TanStack Query hooks — PRIVATE to this feature
│           │   └── use{Page}.ts
│           │
│           ├── schemas/                   # Zod schemas — PRIVATE to this feature
│           │   └── {page}.schema.ts
│           │
│           └── components/               # Sub-components — PRIVATE to this feature only
│               ├── {Page}List.tsx
│               ├── {Page}Card.tsx
│               ├── {Page}CreateForm.tsx
│               └── {Page}EditForm.tsx
│
├── hooks/                                 # Shared hooks — used by 2+ features
│   ├── usePaginatedList.ts
│   ├── useDebounce.ts
│   └── useLocalStorage.ts
│
└── lib/                                   # Infrastructure — no JSX, no React hooks
    ├── api/
    │   ├── client.ts                      # Axios instance + interceptors
    │   ├── endpoints.ts                   # Every backend URL — one source of truth
    │   └── adapters.ts                    # Normalize FastAPI / ASP.NET / Spring Boot responses
    ├── query/
    │   ├── client.ts                      # QueryClient singleton
    │   └── keys.ts                        # Query key factory
    ├── auth/
    │   └── config.ts                      # next-auth providers + JWT callbacks
    ├── store/
    │   ├── ui.store.ts                    # Sidebar open, theme
    │   └── auth.store.ts                  # Cached session user
    ├── types/
    │   ├── common.types.ts                # PaginatedResponse<T>, ApiError
    │   └── {feature}.types.ts             # One file per domain — never one global types.ts
    ├── permissions.ts                     # Role → allowed actions map
    ├── nav.ts                             # Navigation items
    └── utils/
        ├── cn.ts                          # clsx + tailwind-merge
        └── format.ts                      # formatDate, formatCurrency, formatBytes
```

---

## COMPONENT VISIBILITY RULES

This is the most important architectural rule. Every component has a scope.

```
┌─────────────────────────────────────────────────────────────────┐
│  components/ui/          importable by: EVERYONE                │
│  components/layout/      importable by: EVERYONE                │
│  components/shared/      importable by: ANY feature page        │
│  components/pages/{x}/   importable by: ONLY files inside {x}/  │
└─────────────────────────────────────────────────────────────────┘
```

**Sub-components are PRIVATE.** A sub-component inside `components/pages/users/components/` can only be imported by files inside `components/pages/users/`. No other feature can touch it.

```
✅  UsersPage.tsx      imports  UserList.tsx        (same feature — OK)
✅  OrdersPage.tsx     imports  DataTable.tsx        (from shared/ — OK)
✅  Sidebar.tsx        imports  Button.tsx           (from ui/ — OK)

❌  OrdersPage.tsx     imports  UserList.tsx         (different feature — FORBIDDEN)
❌  DashboardPage.tsx  imports  UserCreateForm.tsx   (different feature — FORBIDDEN)
```

**When to promote a sub-component to `shared/`:**

```
Used in only 1 feature   → stays in components/pages/{feature}/components/
Used in 2+ features      → move to components/shared/
```

---

## THE 3 LAWS

```
LAW 1 — app/ is ROUTES ONLY
  Every page.tsx = metadata + one import + one return. Max 8 lines.
  Zero hooks. Zero logic. Zero API calls.

LAW 2 — components/ is JSX ONLY
  Every file inside components/ returns JSX.
  Hook files (use*.ts) live in hooks/ — either inside the feature folder or root hooks/.
  NEVER put a .ts hook file inside components/.

LAW 3 — lib/ is INFRASTRUCTURE ONLY
  No JSX. No React hooks. Pure TypeScript.
  Safe to import from both Server Components and Client Components.
```

---

## SERVER vs CLIENT COMPONENTS

```
DEFAULT = Server Component — no directive needed

Add "use client" ONLY when a file uses:
  ✓ useState / useReducer / useEffect
  ✓ Any event handler (onClick, onChange, onSubmit)
  ✓ TanStack Query hooks (useQuery, useMutation)
  ✓ Zustand store
  ✓ React Hook Form
  ✓ Browser APIs (window, localStorage)

NEVER add "use client" to:
  ✗ app/(dashboard)/*/page.tsx
  ✗ app/layout.tsx  or  app/(dashboard)/layout.tsx
  ✗ Any file inside lib/
```

---

## CODE BLUEPRINTS

### `middleware.ts`

```typescript
// middleware.ts
import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";

const PROTECTED = ["/dashboard", "/settings"];   // add every protected prefix here
const AUTH_ONLY = ["/login", "/register"];

export async function middleware(req: NextRequest): Promise<NextResponse> {
  const { pathname } = req.nextUrl;
  const token = await getToken({ req, secret: process.env.NEXTAUTH_SECRET });

  if (PROTECTED.some((p) => pathname.startsWith(p)) && !token) {
    const url = new URL("/login", req.url);
    url.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(url);
  }

  if (AUTH_ONLY.some((p) => pathname.startsWith(p)) && token) {
    return NextResponse.redirect(new URL("/dashboard", req.url));
  }

  const res = NextResponse.next();
  res.headers.set("X-Frame-Options",        "DENY");
  res.headers.set("X-Content-Type-Options", "nosniff");
  res.headers.set("Referrer-Policy",        "strict-origin-when-cross-origin");
  res.headers.set("Permissions-Policy",     "camera=(), microphone=(), geolocation=()");
  res.headers.set("X-Request-ID",           crypto.randomUUID());
  return res;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)" ],
};
```

---

### `next.config.ts`

```typescript
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,

  images: {
    remotePatterns: [{ protocol: "https", hostname: "**.yourdomain.com" }],
  },

  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          // HSTS — force HTTPS for 1 year (only works over HTTPS, safe to add always)
          { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains; preload" },
          // Content Security Policy — tighten per project
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' blob: data: https:",
              "font-src 'self'",
              "connect-src 'self' https://api.yourdomain.com",
              "frame-ancestors 'none'",
            ].join("; "),
          },
        ],
      },
    ];
  },
};

export default nextConfig;
```

**NOTE:** `next.config.ts` adds HSTS and CSP. `middleware.ts` adds X-Frame-Options, X-Content-Type-Options, etc. Both are needed together — they cover different layers.

---

### `app/layout.tsx` and `app/(dashboard)/layout.tsx`

```typescript
// app/layout.tsx — Server Component
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Providers } from "@/components/shared/Providers";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], display: "swap" });

export const metadata: Metadata = {
  title: { default: "App", template: "%s | App" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

```typescript
// app/(dashboard)/layout.tsx — Server Component
import { AppShell } from "@/components/layout/AppShell";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
```

```typescript
// app/(dashboard)/{pagename}/page.tsx — Server Component — 8 lines max
import type { Metadata } from "next";
import { UsersPage } from "@/components/pages/users";     // ← real name here

export const metadata: Metadata = { title: "Users" };

export default function Page() {
  return <UsersPage />;
}
```

---

### `components/shared/Providers.tsx`

```typescript
// components/shared/Providers.tsx
"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools }   from "@tanstack/react-query-devtools";
import { SessionProvider }      from "next-auth/react";
import { Toaster }              from "sonner";
import { queryClient }          from "@/lib/query/client";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <QueryClientProvider client={queryClient}>
        {children}
        <Toaster position="top-right" richColors closeButton />
        {process.env.NODE_ENV === "development" && <ReactQueryDevtools initialIsOpen={false} />}
      </QueryClientProvider>
    </SessionProvider>
  );
}
```

---

### `lib/api/adapters.ts` — Normalize Any Backend

```typescript
// lib/api/adapters.ts
// Change BACKEND to match the current project — everything else is automatic.

type Backend = "fastapi" | "aspnet" | "springboot";
const BACKEND = (process.env.NEXT_PUBLIC_BACKEND_TYPE ?? "fastapi") as Backend;

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page:  number;
  size:  number;
}

export function normalizePaginated<T>(raw: unknown): PaginatedResponse<T> {
  const r = raw as Record<string, unknown>;
  switch (BACKEND) {
    case "fastapi":     return { items: r.items    as T[], total: r.total         as number, page: r.page   as number, size: r.size     as number };
    case "aspnet":      return { items: r.data     as T[], total: r.totalCount    as number, page: r.pageNumber as number, size: r.pageSize  as number };
    case "springboot":  return { items: r.content  as T[], total: r.totalElements as number, page: (r.number as number) + 1, size: r.size as number };
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

### `lib/api/client.ts`

```typescript
// lib/api/client.ts
import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { getSession, signOut } from "next-auth/react";
import { normalizeError } from "./adapters";

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 15_000,
  headers: { "Content-Type": "application/json", Accept: "application/json" },
});

apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    const session = await getSession();
    if (session?.accessToken) config.headers.Authorization = `Bearer ${session.accessToken}`;

    // Forward X-Request-ID for end-to-end tracing (set by middleware.ts)
    // In browser, read from the last response header stored in a module-level variable
    if (typeof window !== "undefined" && (window as { __requestId?: string }).__requestId) {
      config.headers["X-Request-ID"] = (window as { __requestId?: string }).__requestId;
    }
    return config;
  },
  (err) => Promise.reject(err)
);

// Silent refresh queue — prevents multiple simultaneous refresh calls
let _isRefreshing = false;
let _queue: Array<{ resolve: () => void; reject: (e: unknown) => void }> = [];

apiClient.interceptors.response.use(
  (res) => res,
  async (err: AxiosError) => {
    const original = err.config as typeof err.config & { _retry?: boolean };

    if (err.response?.status === 401 && !original?._retry) {
      if (_isRefreshing) {
        return new Promise<void>((resolve, reject) => _queue.push({ resolve, reject }))
          .then(() => apiClient(original!));
      }
      original!._retry = true;
      _isRefreshing    = true;

      try {
        // next-auth automatically handles token refresh via the session
        const session = await getSession();
        if (session?.accessToken) {
          _queue.forEach(({ resolve }) => resolve());
          _queue = [];
          return apiClient(original!);   // retry with refreshed token
        }
      } catch {
        _queue.forEach(({ reject: rej }) => rej(err));
        _queue = [];
      } finally {
        _isRefreshing = false;
      }

      await signOut({ callbackUrl: "/login" });
      return Promise.reject(err);
    }

    return Promise.reject(new Error(normalizeError(err.response?.data)));
  }
);

export default apiClient;
```

---

### `lib/api/endpoints.ts`

```typescript
// lib/api/endpoints.ts
// ALL backend URLs live here. Add new feature endpoints here first — before any other file.

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export const ENDPOINTS = {
  auth: {
    login:   `${BASE}/auth/login`,
    me:      `${BASE}/auth/me`,
    logout:  `${BASE}/auth/logout`,
    refresh: `${BASE}/auth/refresh`,
  },

  // Template — copy this block for every new feature:
  // {feature}: {
  //   list:   `${BASE}/{feature}`,
  //   create: `${BASE}/{feature}`,
  //   detail: (id: string) => `${BASE}/{feature}/${id}`,
  //   update: (id: string) => `${BASE}/{feature}/${id}`,
  //   delete: (id: string) => `${BASE}/{feature}/${id}`,
  // },

  users: {
    list:   `${BASE}/users`,
    create: `${BASE}/users`,
    detail: (id: string) => `${BASE}/users/${id}`,
    update: (id: string) => `${BASE}/users/${id}`,
    delete: (id: string) => `${BASE}/users/${id}`,
  },
} as const;
```

---

### `lib/query/client.ts` and `lib/query/keys.ts`

```typescript
// lib/query/client.ts
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries:   { staleTime: 1000 * 60 * 5, gcTime: 1000 * 60 * 10, retry: 1, refetchOnWindowFocus: false },
    mutations: { retry: 0 },
  },
});
```

```typescript
// lib/query/keys.ts
// Add a block for every feature. Always factory functions — never bare strings.

export const queryKeys = {
  // Template:
  // {feature}: {
  //   all:    ()           => ["{feature}"]               as const,
  //   lists:  ()           => ["{feature}", "list"]       as const,
  //   list:   (p: object)  => ["{feature}", "list", p]    as const,
  //   detail: (id: string) => ["{feature}", "detail", id] as const,
  // },

  users: {
    all:    ()             => ["users"]                as const,
    lists:  ()             => ["users", "list"]        as const,
    list:   (p: object)    => ["users", "list", p]     as const,
    detail: (id: string)   => ["users", "detail", id]  as const,
  },
} as const;
```

---

### `lib/types/common.types.ts`

```typescript
// lib/types/common.types.ts
export interface ApiError {
  message:     string;
  statusCode:  number;
  requestId?:  string;
}

// FastAPI:      { items, total, page, size }
// ASP.NET Core: { data, totalCount, pageNumber, pageSize }
// Spring Boot:  { content, totalElements, number, size }
// → normalized to this shape everywhere in the frontend:
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page:  number;
  size:  number;
}
```

---

### `lib/types/{feature}.types.ts` — One File Per Domain

```typescript
// lib/types/user.types.ts
export type UserRole = "admin" | "manager" | "staff" | "viewer";  // adjust per project

export interface User {
  id:         string;
  email:      string;
  full_name:  string;
  role:       UserRole;
  is_active:  boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email:     string;
  full_name: string;
  role:      UserRole;
  password:  string;
}

export interface UserUpdate {
  email?:     string;
  full_name?: string;
  role?:      UserRole;
  is_active?: boolean;
  password?:  string;
}

export interface UserListParams {
  skip?:   number;
  limit?:  number;
  search?: string;
  role?:   UserRole;
}
```

---

### `components/pages/{feature}/schemas/{feature}.schema.ts`

```typescript
// components/pages/users/schemas/user.schema.ts
import { z } from "zod";

export const createUserSchema = z.object({
  email:     z.string().email("Invalid email"),
  full_name: z.string().min(2, "At least 2 characters").max(100),
  role:      z.enum(["admin", "manager", "staff", "viewer"]),
  password:  z.string().min(8, "At least 8 characters").max(128)
               .regex(/[A-Z]/, "Needs an uppercase letter")
               .regex(/[0-9]/, "Needs a number"),
});

export const updateUserSchema = z.object({
  email:     z.string().email().optional(),
  full_name: z.string().min(2).max(100).optional(),
  role:      z.enum(["admin", "manager", "staff", "viewer"]).optional(),
  is_active: z.boolean().optional(),
  password:  z.string().min(8).max(128).optional(),
});

export type CreateUserInput = z.infer<typeof createUserSchema>;
export type UpdateUserInput = z.infer<typeof updateUserSchema>;
```

---

### `components/pages/{feature}/hooks/use{Feature}.ts`

```typescript
// components/pages/users/hooks/useUsers.ts
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import apiClient from "@/lib/api/client";
import { normalizePaginated } from "@/lib/api/adapters";
import { ENDPOINTS } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/query/keys";
import type { PaginatedResponse } from "@/lib/types/common.types";
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
    onSuccess: () => { qc.invalidateQueries({ queryKey: queryKeys.users.lists() }); toast.success("Created successfully."); },
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

### `components/pages/{feature}/{Feature}Page.tsx`

```typescript
// components/pages/users/UsersPage.tsx
"use client";

import { useState } from "react";
import { PageHeader }      from "@/components/layout/PageHeader";
import { Button }          from "@/components/ui/Button";
import { Modal }           from "@/components/ui/Modal";
import { UserList }        from "./components/UserList";
import { UserCreateForm }  from "./components/UserCreateForm";
import { useUsers }        from "./hooks/useUsers";

export function UsersPage() {
  const [open, setOpen] = useState(false);
  const [params, setParams] = useState({ skip: 0, limit: 20 });
  const { data, isLoading, isError } = useUsers(params);

  return (
    <div className="space-y-6">
      <PageHeader title="Users" description="Manage system users.">
        <Button onClick={() => setOpen(true)}>Add User</Button>
      </PageHeader>

      {isError && <p className="text-sm text-red-500">Failed to load. Please refresh.</p>}

      <UserList
        items={data?.items ?? []}
        total={data?.total ?? 0}
        isLoading={isLoading}
        onPaginationChange={setParams}
      />

      <Modal open={open} onClose={() => setOpen(false)} title="Add User">
        <UserCreateForm onSuccess={() => setOpen(false)} />
      </Modal>
    </div>
  );
}
```

---

### `components/pages/{feature}/components/{Feature}CreateForm.tsx`

Every form in this codebase uses **React Hook Form + Zod resolver**. This is the pattern — no exceptions.

```typescript
// components/pages/users/components/UserCreateForm.tsx
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button }   from "@/components/ui/Button";
import { Input }    from "@/components/ui/Input";
import { createUserSchema, type CreateUserInput } from "../schemas/user.schema";
import { useCreateUser } from "../hooks/useUsers";

interface Props {
  onSuccess?: () => void;
}

export function UserCreateForm({ onSuccess }: Props) {
  const { mutate: createUser, isPending } = useCreateUser();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CreateUserInput>({
    resolver: zodResolver(createUserSchema),
    defaultValues: { email: "", full_name: "", role: "staff", password: "" },
  });

  function onSubmit(values: CreateUserInput) {
    createUser(values, {
      onSuccess: () => {
        reset();
        onSuccess?.();
      },
    });
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">

      <div className="space-y-1">
        <label className="text-sm font-medium">Email</label>
        <Input type="email" placeholder="user@example.com" {...register("email")} />
        {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}
      </div>

      <div className="space-y-1">
        <label className="text-sm font-medium">Full Name</label>
        <Input placeholder="Jane Doe" {...register("full_name")} />
        {errors.full_name && <p className="text-xs text-red-500">{errors.full_name.message}</p>}
      </div>

      <div className="space-y-1">
        <label className="text-sm font-medium">Password</label>
        <Input type="password" {...register("password")} />
        {errors.password && <p className="text-xs text-red-500">{errors.password.message}</p>}
      </div>

      <Button type="submit" disabled={isPending} className="w-full">
        {isPending ? "Creating..." : "Create User"}
      </Button>

    </form>
  );
}
```

**Form rules:**
- ALWAYS use `zodResolver(schema)` — never write manual if/else validation
- ALWAYS show per-field errors with `{errors.field?.message}`
- ALWAYS disable submit button while `isPending`
- `onSuccess` callback closes the modal — the component does NOT manage its own modal state
- `toast` is in `useCreateUser` — NEVER call `toast` directly inside the form component

---

### `components/pages/{feature}/index.ts`

```typescript
// components/pages/users/index.ts
// Export ONLY what app/(dashboard)/{route}/page.tsx needs
export { UsersPage }       from "./UsersPage";
export { UserDetailPage }  from "./UserDetailPage";
```

---

### `lib/store/ui.store.ts`

```typescript
// lib/store/ui.store.ts
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

### `lib/store/auth.store.ts`

```typescript
// lib/store/auth.store.ts
// Caches the logged-in user for fast UI reads (role checks, display name).
// Source of truth is still next-auth session — this is a read cache only.
// Always sync from useSession() on mount; never write passwords or tokens here.

import { create } from "zustand";

interface AuthUser {
  id:        string;
  email:     string;
  full_name: string;
  role:      string;
}

interface AuthState {
  user:      AuthUser | null;
  setUser:   (user: AuthUser | null) => void;
  clearUser: () => void;
}

export const useAuthStore = create<AuthState>()((set) => ({
  user:      null,
  setUser:   (user) => set({ user }),
  clearUser: () => set({ user: null }),
}));
```

**RULES for stores:**
- `ui.store.ts` → persisted to localStorage (sidebar, theme)
- `auth.store.ts` → NOT persisted — cleared on sign-out, repopulated from session
- NEVER store tokens, passwords, or sensitive fields in Zustand
- NEVER use Zustand to cache API list data — TanStack Query owns that

---

### `lib/utils/`

```typescript
// lib/utils/cn.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
export function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }
```

```typescript
// lib/utils/format.ts
import { format, formatDistanceToNow, parseISO } from "date-fns";

export const formatDate     = (iso: string) => format(parseISO(iso), "MMM d, yyyy");
export const formatDateTime = (iso: string) => format(parseISO(iso), "MMM d, yyyy 'at' h:mm a");
export const formatRelative = (iso: string) => formatDistanceToNow(parseISO(iso), { addSuffix: true });
export const formatCurrency = (n: number, currency = "USD") =>
  new Intl.NumberFormat("en-US", { style: "currency", currency }).format(n);
export const formatBytes = (b: number) => {
  if (!b) return "0 B";
  const s = ["B","KB","MB","GB","TB"], i = Math.floor(Math.log(b) / Math.log(1024));
  return `${(b / 1024 ** i).toFixed(1)} ${s[i]}`;
};
```

---

### `lib/auth/config.ts` — Works with Any Backend

```typescript
// lib/auth/config.ts
import type { NextAuthConfig } from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { z } from "zod";
import { ENDPOINTS } from "@/lib/api/endpoints";
import { normalizeError } from "@/lib/api/adapters";

const loginSchema = z.object({
  email:    z.string().email(),
  password: z.string().min(1),
});

export const authConfig: NextAuthConfig = {
  providers: [
    Credentials({
      async authorize(credentials) {
        const parsed = loginSchema.safeParse(credentials);
        if (!parsed.success) return null;

        try {
          // ── FastAPI uses form-urlencoded (username field, not email) ──
          // const res = await fetch(ENDPOINTS.auth.login, {
          //   method:  "POST",
          //   headers: { "Content-Type": "application/x-www-form-urlencoded" },
          //   body:    new URLSearchParams({ username: parsed.data.email, password: parsed.data.password }),
          // });

          // ── ASP.NET Core and Spring Boot use JSON ─────────────────────
          const res = await fetch(ENDPOINTS.auth.login, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ email: parsed.data.email, password: parsed.data.password }),
          });

          if (!res.ok) return null;

          const tokenData = await res.json();

          // Each backend uses a different field name for the token:
          // FastAPI      → access_token
          // ASP.NET Core → token  or  accessToken
          // Spring Boot  → accessToken
          const accessToken =
            tokenData.access_token ??
            tokenData.accessToken  ??
            tokenData.token;

          if (!accessToken) return null;

          // Fetch the logged-in user's profile
          const meRes = await fetch(ENDPOINTS.auth.me, {
            headers: { Authorization: `Bearer ${accessToken}` },
          });
          if (!meRes.ok) return null;
          const user = await meRes.json();

          return { ...user, accessToken };
        } catch {
          return null;
        }
      },
    }),
  ],

  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = (user as { accessToken: string }).accessToken;
        token.id          = user.id;
        token.role        = (user as { role?: string }).role ?? "viewer";
        token.full_name   = (user as { full_name?: string }).full_name ?? "";
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken  = token.accessToken as string;
      session.user.id      = token.id          as string;
      session.user.role    = token.role         as string;
      session.user.full_name = token.full_name  as string;
      return session;
    },
  },

  pages: {
    signIn: "/login",
    error:  "/login",
  },

  session: { strategy: "jwt" },
};
```

---

### `app/api/auth/[...nextauth]/route.ts`

```typescript
// app/api/auth/[...nextauth]/route.ts
// This is the required catch-all route that next-auth uses internally.
// Never add logic here — all config lives in lib/auth/config.ts.

import NextAuth from "next-auth";
import { authConfig } from "@/lib/auth/config";

const { handlers } = NextAuth(authConfig);

export const { GET, POST } = handlers;
```

**next-auth TypeScript extension** — add this to `lib/auth/types.d.ts` so `session.user.role` and `session.accessToken` are typed:

```typescript
// lib/auth/types.d.ts
import "next-auth";
import "next-auth/jwt";

declare module "next-auth" {
  interface Session {
    accessToken: string;
    user: {
      id:         string;
      role:       string;
      full_name:  string;
      email:      string;
      name?:      string;
      image?:     string;
    };
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    accessToken: string;
    role:        string;
    full_name:   string;
  }
}
```

---

### `hooks/usePaginatedList.ts`

```typescript
// hooks/usePaginatedList.ts
import { useCallback, useState } from "react";

export function usePaginatedList(defaultLimit = 20) {
  const [pagination, setPagination] = useState({ skip: 0, limit: defaultLimit });
  const goToPage = useCallback(
    (page: number) => setPagination((p) => ({ ...p, skip: (page - 1) * p.limit })),
    []
  );
  return { pagination, setPagination, goToPage, currentPage: Math.floor(pagination.skip / pagination.limit) + 1 };
}
```

---

### `app/error.tsx` and `app/loading.tsx`

```typescript
// app/error.tsx — Client Component (required by Next.js for error boundaries)
"use client";
import { useEffect } from "react";
import { Button }    from "@/components/ui/Button";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => { console.error(error); }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4">
      <h2 className="text-xl font-semibold text-destructive">Something went wrong</h2>
      <p className="text-sm text-muted-foreground">{error.message}</p>
      <Button onClick={reset}>Try again</Button>
    </div>
  );
}
```

```typescript
// app/loading.tsx — Shown while a page is streaming
export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  );
}
```

---

### `lib/permissions.ts`

```typescript
// lib/permissions.ts
// Central role-permission map.
// RoleGate component uses this. Always add a new feature's permissions here.
// Roles: adjust the UserRole type to match your project's backend roles.

export type UserRole = "admin" | "manager" | "staff" | "viewer";

type ResourceKey = keyof typeof PERMISSIONS;
type ActionKey   = "view" | "create" | "edit" | "delete";

export const PERMISSIONS: Record<string, Partial<Record<ActionKey, UserRole[]>>> = {
  // ── Template ─────────────────────────────────────────────────────────
  // {feature}: {
  //   view:   ["admin", "manager", "staff", "viewer"],
  //   create: ["admin", "manager"],
  //   edit:   ["admin", "manager"],
  //   delete: ["admin"],
  // },

  users: {
    view:   ["admin", "manager"],
    create: ["admin"],
    edit:   ["admin"],
    delete: ["admin"],
  },
  settings: {
    view:   ["admin", "manager", "staff", "viewer"],
    edit:   ["admin"],
  },
};

/**
 * Check if a role has permission for a given action on a resource.
 * Usage: can("admin", "create", "users") → true
 */
export function can(role: UserRole, action: ActionKey, resource: string): boolean {
  return PERMISSIONS[resource]?.[action]?.includes(role) ?? false;
}
```

---

### `lib/nav.ts`

```typescript
// lib/nav.ts
// All navigation items in one place.
// Sidebar and MobileNav import from here — no hardcoded links in components.
// Add a new feature's nav entry here as STEP 11 when adding a new feature.

import type { LucideIcon } from "lucide-react";
import {
  LayoutDashboard,
  Users,
  Settings,
  ShieldCheck,
} from "lucide-react";
import type { UserRole } from "@/lib/permissions";

export interface NavItem {
  label:        string;            // display text
  href:         string;            // route path
  icon:         LucideIcon;        // lucide-react icon
  allowedRoles: UserRole[];        // who can see this item
  children?:    NavItem[];         // nested nav (optional)
}

export const NAV_ITEMS: NavItem[] = [
  {
    label:        "Dashboard",
    href:         "/dashboard",
    icon:         LayoutDashboard,
    allowedRoles: ["admin", "manager", "staff", "viewer"],
  },
  {
    label:        "Users",
    href:         "/users",
    icon:         Users,
    allowedRoles: ["admin", "manager"],
  },
  {
    label:        "Settings",
    href:         "/settings",
    icon:         Settings,
    allowedRoles: ["admin"],
  },

  // ── Template for new features ─────────────────────────────────────────
  // {
  //   label:        "{FeatureLabel}",
  //   href:         "/{feature}",
  //   icon:         {LucideIcon},
  //   allowedRoles: ["admin", "manager"],
  // },
];
```

---

## NAMING CONVENTIONS

| What | Rule | Example |
|------|------|---------|
| Feature page component | `{Feature}Page.tsx` | `UsersPage.tsx` |
| Feature detail component | `{Feature}DetailPage.tsx` | `UserDetailPage.tsx` |
| Sub-components | `{Feature}{Name}.tsx` | `UserCreateForm.tsx`, `UserList.tsx` |
| UI primitives | `PascalCase.tsx` | `Button.tsx`, `Modal.tsx` |
| Feature hooks file | `use{Feature}.ts` | `useUsers.ts` |
| Root shared hooks | `use{Name}.ts` | `usePaginatedList.ts` |
| Schema file | `{feature}.schema.ts` | `user.schema.ts` |
| Type file | `{feature}.types.ts` | `user.types.ts` |
| Zustand stores | `{name}.store.ts` | `ui.store.ts` |
| Barrel | always `index.ts` | page-level exports only |
| Constants | always `constants.ts` | inside feature folder |
| Query keys | `queryKeys.{feature}.{scope}(params)` | `queryKeys.users.list(p)` |
| Endpoints | `ENDPOINTS.{feature}.{action}` | `ENDPOINTS.users.detail(id)` |
| Folders | `lowercase` or `camelCase` | `pages/`, `shared/`, `ui/` |
| Public env | `NEXT_PUBLIC_UPPER_SNAKE` | `NEXT_PUBLIC_API_URL` |

---

## WHEN ADDING A NEW FEATURE

Follow ALL 12 steps. Do not skip any.

```
STEP 1   lib/types/{feature}.types.ts
         → {Feature}, {Feature}Create, {Feature}Update, {Feature}ListParams

STEP 2   lib/api/endpoints.ts
         → add {feature}: { list, create, detail(id), update(id), delete(id) }

STEP 3   lib/query/keys.ts
         → add {feature}: { all, lists, list(p), detail(id) }

STEP 4   components/pages/{feature}/schemas/{feature}.schema.ts
         → create{Feature}Schema, update{Feature}Schema, inferred types

STEP 5   components/pages/{feature}/hooks/use{Feature}.ts
         → use{Feature}s, use{Feature}(id), useCreate, useUpdate, useDelete

STEP 6   components/pages/{feature}/components/
         → {Feature}List.tsx, {Feature}CreateForm.tsx (+ others as needed)

STEP 7   components/pages/{feature}/{Feature}Page.tsx
         → "use client" — state + layout + hooks + sub-components

STEP 8   components/pages/{feature}/index.ts
         → barrel export

STEP 9   app/(dashboard)/{feature}/page.tsx
         → metadata + import + return (≤ 8 lines)

STEP 10  middleware.ts
         → add "/{feature}" to PROTECTED array

STEP 11  lib/nav.ts
         → add navigation entry

STEP 12  lib/permissions.ts  (if role-gated)
         → add {feature}: { view, create, edit, delete } with allowed roles
```

---

## ENVIRONMENT VARIABLES

### `.env.local` (never commit — local secrets only)

```bash
# ── Backend ──────────────────────────────────────────────────────────
# Base URL of your REST API — no trailing slash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Which backend is this project using?  fastapi | aspnet | springboot
NEXT_PUBLIC_BACKEND_TYPE=fastapi

# ── next-auth ─────────────────────────────────────────────────────────
# Full URL of the Next.js app (required by next-auth)
NEXTAUTH_URL=http://localhost:3000

# Random secret — generate with: openssl rand -base64 32
NEXTAUTH_SECRET=replace-this-with-a-long-random-string

# ── Optional: OAuth providers ─────────────────────────────────────────
# GOOGLE_CLIENT_ID=
# GOOGLE_CLIENT_SECRET=
```

### `.env.example` (commit this — tells teammates what vars are needed)

```bash
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_BACKEND_TYPE=fastapi
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=
```

**Rules:**
- NEVER commit `.env.local` — add it to `.gitignore`
- ALWAYS commit `.env.example` with empty values
- Variables exposed to the browser MUST start with `NEXT_PUBLIC_`
- Secret keys (NEXTAUTH_SECRET, API keys) MUST NOT start with `NEXT_PUBLIC_`
- NEVER hardcode any of these values in source code

---

## `tsconfig.json`

```json
{
  "compilerOptions": {
    "target":            "ES2022",
    "lib":               ["dom", "dom.iterable", "esnext"],
    "allowJs":           true,
    "skipLibCheck":      true,
    "strict":            true,
    "noEmit":            true,
    "esModuleInterop":   true,
    "module":            "esnext",
    "moduleResolution":  "bundler",
    "resolveJsonModule": true,
    "isolatedModules":   true,
    "jsx":               "preserve",
    "incremental":       true,
    "plugins":           [{ "name": "next" }],
    "baseUrl":           ".",
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

**`@/*` maps to the project root** (where `components/`, `lib/`, `hooks/` sit).
Always import with `@/` prefix:

```typescript
// ✅ Correct
import apiClient from "@/lib/api/client";
import { UsersPage } from "@/components/pages/users";
import { useDebounce } from "@/hooks/useDebounce";

// ❌ Wrong — never use relative paths for cross-folder imports
import apiClient from "../../lib/api/client";
```

---

## BACKEND COMPATIBILITY

| | FastAPI | ASP.NET Core | Spring Boot |
|-|---------|-------------|-------------|
| `NEXT_PUBLIC_BACKEND_TYPE` | `fastapi` | `aspnet` | `springboot` |
| Login body format | `form-urlencoded` | `JSON` | `JSON` |
| Token field | `access_token` | `token` / `accessToken` | `accessToken` |
| Paginated list | `items / total / page / size` | `data / totalCount / pageNumber / pageSize` | `content / totalElements / number / size` |
| Error field | `detail` | `message` | `message` |

**To switch backends:** change `NEXT_PUBLIC_BACKEND_TYPE` in `.env.local`. Only `adapters.ts` is aware of the difference. No other file changes.

---

## ABSOLUTE PROHIBITIONS

```
✗  Logic or hooks inside app/*/page.tsx
✗  "use client" on page.tsx or layout.tsx
✗  Hook files (use*.ts) inside components/
✗  One feature importing sub-components from another feature
✗  import axios directly — always import apiClient
✗  Hardcoded backend URLs — always use ENDPOINTS.*
✗  Authorization header set manually — the interceptor handles it
✗  401/403 handling inside a component — the interceptor handles it
✗  new QueryClient() in any component — import from lib/query/client.ts
✗  Zustand for API/server data — TanStack Query owns it
✗  One global lib/types.ts — one file per domain in lib/types/
✗  toast.success/error in components — only in mutation onSuccess/onError
✗  Multiple Toaster instances — one in Providers only
✗  Multiple apiClient instances — one in lib/api/client.ts only
✗  moment.js — use date-fns
✗  Redux or React Context for state
✗  style={{}} inline styles — Tailwind only
✗  Capital letter folder names — all folders lowercase
✗  .txt files — components are .tsx, hooks/utils/types are .ts
```

---

## PRE-COMPLETION CHECKLIST

```
[ ] app/*/page.tsx is ≤ 8 lines: metadata + one import + one return
[ ] No "use client" on page.tsx or layout.tsx
[ ] All 12 feature steps completed
[ ] No hook file inside components/ folder
[ ] No cross-feature sub-component imports
[ ] All URLs in ENDPOINTS — no hardcoded strings
[ ] All query keys in queryKeys — no hardcoded arrays
[ ] Forms: React Hook Form + Zod zodResolver
[ ] Toasts only in mutation onSuccess / onError
[ ] normalizePaginated() used for all list API calls
[ ] New protected route added to middleware.ts PROTECTED array
[ ] New type in lib/types/{domain}.types.ts
[ ] New nav entry in lib/nav.ts
[ ] TypeScript strict — no `any` without a comment
```

---

## DATA FLOW (Quick Reference)

```
User submits a form
  → Component calls mutate(values) from use{Feature} hook
  → apiClient.post(ENDPOINTS.{feature}.create, payload)
  → interceptor injects Authorization: Bearer {token}
  → backend responds (FastAPI / ASP.NET / Spring Boot)
  → interceptor normalizes error on failure
  → onSuccess: invalidateQueries → list re-fetches → UI updates
  → toast.success(...)

User navigates to /{feature}
  → middleware.ts (Edge) → checks JWT → redirect if missing
  → app/(dashboard)/{feature}/page.tsx → <{Feature}Page />
  → {Feature}Page mounts → use{Feature}s() fires
  → apiClient.get + normalizePaginated → PaginatedResponse<T>
  → list renders
```

---

*Next.js 15 · TypeScript 5 · TanStack Query v5 · Zustand 5 · Zod 3 · React Hook Form 7 · next-auth v5 · Tailwind CSS 4*
*Works with: FastAPI · ASP.NET Core · Spring Boot*

---

## Copyright

© 2026 **Udhayaboopathi V**. All rights reserved.

- Author:  Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub:  [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
