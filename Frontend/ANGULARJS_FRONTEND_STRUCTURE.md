# AGENT INSTRUCTIONS — Angular Frontend (v18+ Standalone)

> **HOW TO USE THIS FILE**
> Drop this file into your project root. When starting a new chat, say:
> _"Read `ANGULARJS_FRONTEND_STRUCTURE.md` deeply and follow every instruction in it for all code you generate."_
> This file is the single source of truth. No exceptions.

---

## YOUR IDENTITY

You are a senior Angular frontend engineer building enterprise-grade SPAs.
This app connects to a REST API backend — FastAPI, ASP.NET Core, or Spring Boot.
Every file you generate MUST follow the exact structure, patterns, and rules in this document.
You have creative freedom only over feature UI and business logic — never over architecture.

---

## TECH STACK — USE EXACTLY THESE

```
Framework      : Angular 18+          (standalone components — NO NgModules)
Language       : TypeScript 5         (strict: true — always on)
Styling        : Tailwind CSS 4       + your own shared components
HTTP Client    : Angular HttpClient   + functional interceptors
State          : Angular Signals      (built-in — no NgRx for simple apps)
Forms          : Angular Reactive Forms + Zod validation
Validation     : Zod 3
Server State   : TanStack Query v5 for Angular (@tanstack/angular-query-experimental)
Auth           : JWT (in-memory — never localStorage)
Icons          : lucide-angular
Dates          : date-fns
Build          : Angular CLI 18
```

---

## MANDATORY FOLDER STRUCTURE

```
src/
│
├── app/
│   │
│   ├── app.config.ts                        # provideRouter, provideHttpClient, interceptors
│   ├── app.routes.ts                        # All root route definitions
│   ├── app.component.ts                     # Root component (router-outlet only)
│   │
│   ├── core/                                # Singleton services — providedIn: 'root'
│   │   ├── api/
│   │   │   ├── api.service.ts               # HttpClient wrapper (one service)
│   │   │   ├── endpoints.ts                 # ALL backend URLs
│   │   │   └── adapters.ts                  # Normalize backend responses
│   │   ├── auth/
│   │   │   ├── auth.service.ts              # login/logout/token management
│   │   │   ├── token-store.ts               # In-memory token (never localStorage)
│   │   │   └── auth.guard.ts                # CanActivateFn guard
│   │   ├── interceptors/
│   │   │   ├── auth.interceptor.ts          # Attach Bearer token
│   │   │   ├── signing.interceptor.ts       # HMAC-SHA256 request signing
│   │   │   └── error.interceptor.ts         # Global 401/error handling
│   │   ├── store/
│   │   │   ├── ui.store.ts                  # Signal-based UI state
│   │   │   └── auth.store.ts                # Signal-based auth state
│   │   └── query/
│   │       ├── client.ts                    # QueryClient singleton
│   │       └── keys.ts                      # Query key factory
│   │
│   ├── shared/                              # Standalone components used by 2+ features
│   │   ├── components/
│   │   │   ├── data-table/
│   │   │   │   ├── data-table.component.ts
│   │   │   │   └── data-table.component.html
│   │   │   ├── confirm-dialog/
│   │   │   │   └── confirm-dialog.component.ts
│   │   │   ├── empty-state/
│   │   │   │   └── empty-state.component.ts
│   │   │   └── loading-spinner/
│   │   │       └── loading-spinner.component.ts
│   │   └── pipes/
│   │       ├── format-date.pipe.ts
│   │       └── format-currency.pipe.ts
│   │
│   ├── layout/                              # App shell components
│   │   ├── app-shell/
│   │   │   └── app-shell.component.ts
│   │   ├── sidebar/
│   │   │   └── sidebar.component.ts
│   │   ├── navbar/
│   │   │   └── navbar.component.ts
│   │   └── page-header/
│   │       └── page-header.component.ts
│   │
│   └── features/                           # ONE FOLDER PER FEATURE
│       └── {feature}/
│           ├── {feature}.routes.ts          # Lazy-loaded child routes
│           ├── {feature}.service.ts         # API calls + TanStack Query hooks
│           ├── models/
│           │   └── {feature}.model.ts       # TypeScript interfaces + Zod schemas
│           ├── pages/                       # Route-level page components (thin)
│           │   ├── {feature}-list/
│           │   │   ├── {feature}-list.component.ts
│           │   │   └── {feature}-list.component.html
│           │   └── {feature}-detail/
│           │       ├── {feature}-detail.component.ts
│           │       └── {feature}-detail.component.html
│           └── components/                 # Sub-components — PRIVATE to this feature
│               ├── {feature}-form/
│               │   ├── {feature}-form.component.ts
│               │   └── {feature}-form.component.html
│               └── {feature}-card/
│                   └── {feature}-card.component.ts
│
├── environments/
│   ├── environment.ts                       # Development
│   └── environment.prod.ts                  # Production
│
├── index.html
├── main.ts
├── angular.json
└── tsconfig.json
```

---

## COMPONENT VISIBILITY RULES

```
┌──────────────────────────────────────────────────────────────────┐
│  shared/components/       importable by: ANY feature             │
│  layout/                  importable by: ANY component           │
│  features/{x}/components/ importable by: ONLY files inside {x}/ │
└──────────────────────────────────────────────────────────────────┘

Sub-components inside features/{x}/components/ are PRIVATE.
Used in 2+ features → promote to shared/components/.
```

---

## THE 3 LAWS

```
LAW 1 — pages/ inside features are ROUTE COMPONENTS ONLY
  Page components contain minimal logic — delegate to services and child components.

LAW 2 — ALL components are standalone
  NEVER use NgModule. Every component declares its own imports array.
  import { CommonModule } is FORBIDDEN — import specific directives (NgIf, NgFor, etc.)

LAW 3 — core/ is SINGLETON SERVICES ONLY
  All services in core/ use providedIn: 'root'.
  No components, no directives in core/.
```

---

## LAYER 1 — `app.config.ts` — App Bootstrap

```typescript
// src/app/app.config.ts
import {
  ApplicationConfig,
  provideZoneChangeDetection,
} from "@angular/core";
import { provideRouter, withComponentInputBinding } from "@angular/router";
import {
  provideHttpClient,
  withFetch,
  withInterceptors,
} from "@angular/common/http";
import {
  provideTanStackQuery,
  QueryClient,
} from "@tanstack/angular-query-experimental";

import { routes }              from "./app.routes";
import { authInterceptor }     from "./core/interceptors/auth.interceptor";
import { signingInterceptor }  from "./core/interceptors/signing.interceptor";
import { errorInterceptor }    from "./core/interceptors/error.interceptor";

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(
      withFetch(),
      withInterceptors([
        authInterceptor,      // ① attach token
        signingInterceptor,   // ② HMAC sign
        errorInterceptor,     // ③ handle 401/errors
      ])
    ),
    provideTanStackQuery(new QueryClient({
      defaultOptions: {
        queries: {
          staleTime:            1000 * 60 * 5,
          gcTime:               1000 * 60 * 10,
          retry:                1,
          refetchOnWindowFocus: false,
        },
      },
    })),
  ],
};
```

---

## LAYER 2 — `app.routes.ts` — Root Routes

```typescript
// src/app/app.routes.ts
import { Routes } from "@angular/router";
import { authGuard } from "./core/auth/auth.guard";
import { guestGuard } from "./core/auth/auth.guard";

export const routes: Routes = [
  {
    path: "",
    redirectTo: "dashboard",
    pathMatch: "full",
  },
  {
    path: "login",
    canActivate: [guestGuard],
    loadComponent: () =>
      import("./features/auth/pages/login/login.component")
        .then((m) => m.LoginComponent),
  },
  {
    path: "dashboard",
    canActivate: [authGuard],
    loadComponent: () =>
      import("./layout/app-shell/app-shell.component")
        .then((m) => m.AppShellComponent),
    children: [
      {
        path: "",
        loadComponent: () =>
          import("./features/dashboard/pages/dashboard-home/dashboard-home.component")
            .then((m) => m.DashboardHomeComponent),
      },
      {
        path: "users",
        loadChildren: () =>
          import("./features/users/users.routes")
            .then((m) => m.usersRoutes),
      },
      // Add new feature lazy routes here
    ],
  },
  { path: "**", redirectTo: "dashboard" },
];
```

---

## LAYER 3 — `core/auth/auth.guard.ts`

```typescript
// src/app/core/auth/auth.guard.ts
import { inject }       from "@angular/core";
import { CanActivateFn, Router } from "@angular/router";
import { tokenStore }   from "./token-store";

export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  if (tokenStore.isLoggedIn()) return true;
  return router.createUrlTree(["/login"], {
    queryParams: { returnUrl: state.url },
  });
};

export const guestGuard: CanActivateFn = () => {
  const router = inject(Router);
  if (!tokenStore.isLoggedIn()) return true;
  return router.createUrlTree(["/dashboard"]);
};
```

---

## LAYER 4 — `core/auth/token-store.ts`

```typescript
// src/app/core/auth/token-store.ts
// Token lives in memory ONLY — never localStorage or sessionStorage.

let _token: string | null = null;

export const tokenStore = {
  get:        ()              => _token,
  set:        (t: string)     => { _token = t; },
  clear:      ()              => { _token = null; },
  isLoggedIn: ()              => _token !== null,
};
```

---

## LAYER 5 — `core/interceptors/`

```typescript
// src/app/core/interceptors/auth.interceptor.ts
import { HttpInterceptorFn } from "@angular/common/http";
import { tokenStore }        from "../auth/token-store";

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = tokenStore.get();
  if (!token) return next(req);

  return next(req.clone({
    setHeaders: { Authorization: `Bearer ${token}` },
  }));
};
```

```typescript
// src/app/core/interceptors/error.interceptor.ts
import { HttpInterceptorFn } from "@angular/common/http";
import { inject }            from "@angular/core";
import { Router }            from "@angular/router";
import { catchError, throwError } from "rxjs";
import { tokenStore }        from "../auth/token-store";
import { normalizeError }    from "../api/adapters";

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);

  return next(req).pipe(
    catchError((err) => {
      if (err.status === 401) {
        tokenStore.clear();
        router.navigate(["/login"]);
        return throwError(() => err);
      }
      const message = normalizeError(err.error);
      return throwError(() => new Error(message));
    })
  );
};
```

```typescript
// src/app/core/interceptors/signing.interceptor.ts
import { HttpInterceptorFn } from "@angular/common/http";
import { from, switchMap }   from "rxjs";
import { environment }       from "../../../environments/environment";

async function hmacSHA256(secret: string, message: string): Promise<string> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(message));
  return Array.from(new Uint8Array(sig)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

export const signingInterceptor: HttpInterceptorFn = (req, next) => {
  const secret = environment.signingSecret;
  if (!secret) return next(req);

  const timestamp = Date.now().toString();
  const path      = new URL(req.url, "http://x").pathname;
  const body      = req.body ? JSON.stringify(req.body) : "";
  const message   = `${timestamp}${req.method.toUpperCase()}${path}${body}`;

  return from(hmacSHA256(secret, message)).pipe(
    switchMap((signature) =>
      next(req.clone({
        setHeaders: {
          "X-Timestamp": timestamp,
          "X-Signature": signature,
        },
      }))
    )
  );
};
```

---

## LAYER 6 — `core/api/` — HTTP Service

```typescript
// src/app/core/api/api.service.ts
import { Injectable }       from "@angular/core";
import { HttpClient }       from "@angular/common/http";
import { Observable }       from "rxjs";
import { map }              from "rxjs/operators";
import { normalizePaginated, type PaginatedResponse } from "./adapters";

@Injectable({ providedIn: "root" })
export class ApiService {
  constructor(private http: HttpClient) {}

  get<T>(url: string, params?: object): Observable<T> {
    return this.http.get<T>(url, { params: params as Record<string, string> });
  }

  getPaginated<T>(url: string, params?: object): Observable<PaginatedResponse<T>> {
    return this.http.get<unknown>(url, { params: params as Record<string, string> })
      .pipe(map((raw) => normalizePaginated<T>(raw)));
  }

  post<T>(url: string, body: unknown): Observable<T> {
    return this.http.post<T>(url, body);
  }

  patch<T>(url: string, body: unknown): Observable<T> {
    return this.http.patch<T>(url, body);
  }

  delete<T>(url: string): Observable<T> {
    return this.http.delete<T>(url);
  }
}
```

---

## LAYER 7 — Feature Queries + Mutations

> **IMPORTANT:** `injectQuery` and `injectMutation` MUST be called in the **Angular injection
> context** — i.e., as class fields or inside `constructor()`, NEVER inside regular methods.
> The correct pattern is to define queries and mutations directly in the **component** as fields,
> not inside an `@Injectable` service. The service holds only the API call functions.

```typescript
// src/app/features/users/users.service.ts
// ── Service owns API calls only — no injectQuery/injectMutation here ──
import { Injectable, inject }   from "@angular/core";
import { lastValueFrom }        from "rxjs";
import { ApiService }           from "../../core/api/api.service";
import { ENDPOINTS }            from "../../core/api/endpoints";
import type { User, UserCreate, UserListParams, UserUpdate }
                                from "./models/user.model";
import type { PaginatedResponse } from "../../core/api/adapters";

@Injectable({ providedIn: "root" })
export class UsersApiService {
  private api = inject(ApiService);

  getUsers(params?: UserListParams): Promise<PaginatedResponse<User>> {
    return lastValueFrom(this.api.getPaginated<User>(ENDPOINTS.users.list, params));
  }

  getUser(id: string): Promise<User> {
    return lastValueFrom(this.api.get<User>(ENDPOINTS.users.detail(id)));
  }

  createUser(payload: UserCreate): Promise<User> {
    return lastValueFrom(this.api.post<User>(ENDPOINTS.users.create, payload));
  }

  updateUser(id: string, payload: UserUpdate): Promise<User> {
    return lastValueFrom(this.api.patch<User>(ENDPOINTS.users.update(id), payload));
  }

  deleteUser(id: string): Promise<void> {
    return lastValueFrom(this.api.delete(ENDPOINTS.users.delete(id)));
  }
}
```

```typescript
// src/app/features/users/pages/users-list/users-list.component.ts
// ── injectQuery and injectMutation are class FIELDS — not method calls ──
"use client" // Angular components don't have this but for clarity:
import { Component, inject, signal }   from "@angular/core";
import {
  injectQuery,
  injectMutation,
  injectQueryClient,
} from "@tanstack/angular-query-experimental";
import { toast }               from "ngx-sonner";
import { UsersApiService }     from "../../users.service";
import { queryKeys }           from "../../../../core/query/keys";
import type { UserCreate, UserListParams } from "../../models/user.model";

@Component({
  selector:    "app-users-list",
  standalone:  true,
  templateUrl: "./users-list.component.html",
})
export class UsersListComponent {
  private usersApi = inject(UsersApiService);
  private qc       = injectQueryClient();

  params = signal<UserListParams>({ skip: 0, limit: 20 });

  // ── Queries defined as class fields ────────────────────────────────
  usersQuery = injectQuery(() => ({
    queryKey: queryKeys.users.list(this.params()),
    queryFn:  () => this.usersApi.getUsers(this.params()),
  }));

  // ── Mutations defined as class fields ───────────────────────────────
  createMutation = injectMutation(() => ({
    mutationFn: (payload: UserCreate) => this.usersApi.createUser(payload),
    onSuccess:  () => {
      this.qc.invalidateQueries({ queryKey: queryKeys.users.lists() });
      toast.success("User created.");
    },
    onError: (err: Error) => toast.error(err.message),
  }));

  deleteMutation = injectMutation(() => ({
    mutationFn: (id: string) => this.usersApi.deleteUser(id),
    onSuccess:  () => {
      this.qc.invalidateQueries({ queryKey: queryKeys.users.lists() });
      toast.success("User deleted.");
    },
    onError: (err: Error) => toast.error(err.message),
  }));
}
```
```

---

## LAYER 8 — Feature Model + Schema

```typescript
// src/app/features/users/models/user.model.ts
import { z } from "zod";

export type UserRole = "admin" | "manager" | "staff" | "viewer";

export interface User {
  id:         string;
  email:      string;
  full_name:  string | null;
  is_active:  boolean;
  role:       UserRole;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email:     string;
  full_name: string;
  password:  string;
  role:      UserRole;
}

export interface UserUpdate {
  email?:     string;
  full_name?: string;
  password?:  string;
  is_active?: boolean;
}

export interface UserListParams {
  skip?:  number;
  limit?: number;
  search?: string;
}

// Zod schema for form validation
export const createUserSchema = z.object({
  email:     z.string().email("Invalid email"),
  full_name: z.string().min(2).max(100),
  password:  z.string().min(8, "At least 8 characters").max(128)
               .regex(/[A-Z]/, "Needs uppercase").regex(/[0-9]/, "Needs a number"),
  role:      z.enum(["admin", "manager", "staff", "viewer"]),
});

export type CreateUserInput = z.infer<typeof createUserSchema>;
```

---

## LAYER 9 — Feature Page Component (Standalone)

```typescript
// src/app/features/users/pages/users-list/users-list.component.ts
import { Component, inject, signal } from "@angular/core";
import { CommonModule }              from "@angular/common";  // only for async pipe
import { UsersService }              from "../../users.service";
import { UserFormComponent }         from "../../components/user-form/user-form.component";
import { PageHeaderComponent }       from "../../../../layout/page-header/page-header.component";

@Component({
  selector: "app-users-list",
  standalone: true,
  imports: [CommonModule, UserFormComponent, PageHeaderComponent],
  templateUrl: "./users-list.component.html",
})
export class UsersListComponent {
  private usersService = inject(UsersService);

  showCreateModal = signal(false);
  params          = signal({ skip: 0, limit: 20 });

  usersQuery  = this.usersService.queryUsers(this.params());
  createUser  = this.usersService.createUser();
}
```

```html
<!-- users-list.component.html -->
<app-page-header title="Users" description="Manage system users.">
  <button (click)="showCreateModal.set(true)" class="btn-primary">
    Add User
  </button>
</app-page-header>

@if (usersQuery.isError()) {
  <p class="text-sm text-red-500">Failed to load users. Please refresh.</p>
}

@if (usersQuery.isLoading()) {
  <app-loading-spinner />
} @else {
  <!-- User list table here -->
}

@if (showCreateModal()) {
  <app-user-form
    (formSubmit)="createUser.mutate($event); showCreateModal.set(false)"
    (cancel)="showCreateModal.set(false)"
  />
}
```

---

## LAYER 10 — Feature Routes (Lazy-Loaded)

```typescript
// src/app/features/users/users.routes.ts
import { Routes } from "@angular/router";

export const usersRoutes: Routes = [
  {
    path: "",
    loadComponent: () =>
      import("./pages/users-list/users-list.component")
        .then((m) => m.UsersListComponent),
  },
  {
    path: ":id",
    loadComponent: () =>
      import("./pages/user-detail/user-detail.component")
        .then((m) => m.UserDetailComponent),
  },
];
```

---

## LAYER 11 — `core/store/` — Angular Signals State

```typescript
// src/app/core/store/ui.store.ts
import { Injectable, signal, computed } from "@angular/core";

@Injectable({ providedIn: "root" })
export class UIStore {
  private _sidebarOpen = signal(true);
  private _theme       = signal<"light" | "dark" | "system">("system");

  sidebarOpen = this._sidebarOpen.asReadonly();
  theme       = this._theme.asReadonly();

  toggleSidebar() { this._sidebarOpen.update((v) => !v); }
  setTheme(t: "light" | "dark" | "system") { this._theme.set(t); }
}
```

---

## LAYER 12 — `environments/`

```typescript
// src/environments/environment.ts  (development)
export const environment = {
  production:    false,
  apiUrl:        "http://localhost:8000/api/v1",  // dev — goes through proxy
  backendType:   "fastapi" as const,
  signingSecret: "dev-secret-change-in-prod",
};

// src/environments/environment.prod.ts  (production)
export const environment = {
  production:    true,
  apiUrl:        "https://api.yourdomain.com/api/v1",  // ALWAYS proxy URL — never raw IP
  backendType:   "fastapi" as const,
  signingSecret: "",   // injected by CI/CD at build time
};
```

```typescript
// angular.json — fileReplacements for prod build (excerpt)
// "configurations": {
//   "production": {
//     "fileReplacements": [{
//       "replace": "src/environments/environment.ts",
//       "with":    "src/environments/environment.prod.ts"
//     }]
//   }
// }
```

---

## LAYER 13 — `core/api/adapters.ts` and `core/api/endpoints.ts`

```typescript
// src/app/core/api/adapters.ts
import { environment } from "../../../environments/environment";

export interface PaginatedResponse<T> {
  items: T[]; total: number; page: number; size: number;
}

export function normalizePaginated<T>(raw: unknown): PaginatedResponse<T> {
  const r = raw as Record<string, unknown>;
  switch (environment.backendType) {
    case "fastapi":    return { items: r.items   as T[], total: r.total         as number, page: r.page       as number, size: r.size    as number };
    case "aspnet":     return { items: r.data    as T[], total: r.totalCount    as number, page: r.pageNumber as number, size: r.pageSize as number };
    case "springboot": return { items: r.content as T[], total: r.totalElements as number, page: (r.number as number) + 1, size: r.size  as number };
    default:           throw new Error("Unknown backend type");
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

```typescript
// src/app/core/api/endpoints.ts
import { environment } from "../../../environments/environment";
const BASE = environment.apiUrl;

export const ENDPOINTS = {
  auth: {
    login:   `${BASE}/auth/login`,
    me:      `${BASE}/auth/me`,
    logout:  `${BASE}/auth/logout`,
  },
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

## NAMING CONVENTIONS

| What | Convention | Example |
|------|-----------|---------|
| Components | `kebab-case` selector + `PascalCase` class | `app-user-form`, `UserFormComponent` |
| Component files | `{name}.component.ts` | `users-list.component.ts` |
| Services | `{Name}Service` | `UsersService` |
| Guards | `{name}Guard` (functional) | `authGuard` |
| Interceptors | `{name}Interceptor` (functional) | `authInterceptor` |
| Models/Interfaces | `PascalCase` | `User`, `UserCreate` |
| Schemas (Zod) | `create{Resource}Schema` | `createUserSchema` |
| Routes files | `{feature}.routes.ts` | `users.routes.ts` |
| Store services | `{Name}Store` | `UIStore`, `AuthStore` |
| Signals | `camelCase` | `sidebarOpen`, `theme` |
| Template syntax | Angular 17+ control flow | `@if`, `@for` — never `*ngIf`, `*ngFor` |

---

## WHEN ADDING A NEW FEATURE

```
STEP 1   src/app/features/{feature}/models/{feature}.model.ts
         → interfaces + Zod schema

STEP 2   src/app/core/api/endpoints.ts
         → add {feature} endpoints

STEP 3   src/app/core/query/keys.ts
         → add {feature} query keys

STEP 4   src/app/features/{feature}/{feature}.service.ts
         → @Injectable service with injectQuery/injectMutation

STEP 5   src/app/features/{feature}/components/{feature}-form/
         → standalone form component

STEP 6   src/app/features/{feature}/pages/{feature}-list/
         → list page component

STEP 7   src/app/features/{feature}/{feature}.routes.ts
         → lazy-loaded child routes

STEP 8   src/app/app.routes.ts
         → add { path: "{feature}", loadChildren: ... }

STEP 9   Add navigation entry to core/store or layout/sidebar component
```

---

## ABSOLUTE PROHIBITIONS

```
✗  NgModule — always standalone components
✗  CommonModule imported broadly — import specific directives
✗  *ngIf, *ngFor, *ngSwitch — use @if, @for, @switch (Angular 17+)
✗  Token in localStorage — in-memory tokenStore only
✗  401 handling in components — error.interceptor handles it
✗  Authorization header set manually — auth.interceptor handles it
✗  Hardcoded backend URLs — always use ENDPOINTS.*
✗  Direct HttpClient in feature components — use ApiService only
✗  Business logic in components — services only
✗  Multiple ApiService instances — providedIn: 'root' is singleton
✗  moment.js — use date-fns
✗  One feature importing sub-components from another feature
✗  environment.prod.ts committed with real secrets
✗  Synchronous HTTP calls — always Observable + async pipe or lastValueFrom
✗  providedIn: 'any' or manual providers — always providedIn: 'root'
```

---

## PRE-COMPLETION CHECKLIST

```
[ ] Every component is standalone with its own imports array
[ ] No NgModule anywhere in the codebase
[ ] All new routes are lazy-loaded (loadComponent or loadChildren)
[ ] authGuard applied to all protected routes in app.routes.ts
[ ] No hardcoded URLs — all in ENDPOINTS
[ ] No query key strings — all in queryKeys factory
[ ] normalizePaginated() used for all list API calls
[ ] Token handled by tokenStore — never localStorage
[ ] 401 error handled only in error.interceptor
[ ] New feature registered in app.routes.ts
[ ] New nav entry added to sidebar component
[ ] TypeScript strict — no `any` without comment
[ ] @if / @for used — never *ngIf / *ngFor
[ ] All async HTTP calls use Observable (not Promise directly)
```

---

## DATA FLOW

```
User submits form
  → UserFormComponent emits (formSubmit) event
  → Parent component calls createUser().mutate(payload)
  → authInterceptor injects Authorization: Bearer {token}
  → signingInterceptor adds X-Timestamp + X-Signature
  → backend responds → normalizeError on failure
  → onSuccess → invalidateQueries → list query re-runs
  → toast.success(...)

User navigates to /dashboard/users
  → Angular Router → authGuard → tokenStore.isLoggedIn()
  → Not logged in → redirect to /login
  → Logged in → lazy loads UsersListComponent
  → usersService.queryUsers() fires via injectQuery
  → normalizePaginated → PaginatedResponse<User>
  → component renders list via @for
```

---

*Angular 18+ · TypeScript 5 · Standalone Components · Angular Signals · TanStack Query for Angular · Functional Interceptors · Zod · Tailwind CSS 4*
*Works with: FastAPI · ASP.NET Core · Spring Boot*

---

## Copyright

© 2026 **Udhayaboopathi V**. All rights reserved.

- Author:  Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub:  [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
