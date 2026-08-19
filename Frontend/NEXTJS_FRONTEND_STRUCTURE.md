# AGENT INSTRUCTIONS — Next.js Frontend

> **HOW TO USE THIS FILE**
> Drop this file into your project root. When starting a new chat, say one of:
>
> **Starting from nothing:**
> _"Read `NEXTJS_FRONTEND_STRUCTURE.md` deeply and follow every instruction in it for all code you generate."_
>
> **You already have a project (any shape, any stack):**
> _"Read `NEXTJS_FRONTEND_STRUCTURE.md` deeply, then execute the MIGRATION PROTOCOL on this repository. Reorganize the entire project into the structure defined in this file — refactor, do not just rename."_
>
> This file is the single source of truth. No exceptions.

---

## OPERATING MODES

Decide your mode **before writing a single line of code**, and state which mode you picked in your first reply.

| What you find in the repository | Mode |
|---|---|
| Empty directory, or nothing but untouched `create-next-app` boilerplate | **MODE A — GREENFIELD** |
| Any existing application source code, of any stack, any size, any quality | **MODE B — MIGRATION** |

**MODE A — GREENFIELD**
Scaffold the FOLDER STRUCTURE below exactly as written, wire the CODE BLUEPRINTS, then build each feature with the 12-step feature workflow.

**MODE B — MIGRATION**
Execute the **MIGRATION PROTOCOL** section in full, phase by phase, in order. Do not improvise your own order and do not skip phases.

**The finish line is identical in both modes:** a repository that is indistinguishable from one built greenfield under this file. A reviewer must not be able to tell that MODE B ever happened — no leftovers, no orphan folders, no "legacy" corner, no file that survived only because moving it was easier than fixing it.

---

## MODE B — THE PRIME DIRECTIVE

**Renaming is not migrating. Moving is not migrating.**

A migration is finished when every file in the tree could plausibly have been written from scratch against this document.

| ❌ This is NOT a migration | ✅ This IS a migration |
|---|---|
| `mv src/components/UserTable.jsx components/pages/users/components/UserList.tsx` and stopping there | The 340-line `UserTable.jsx` is read, understood, and split into `UserList.tsx` (JSX), `useUsers.ts` (TanStack Query), `user.schema.ts` (Zod), `user.types.ts` (types), and a `ENDPOINTS.users` entry |
| Keeping `utils.js` and renaming it `utils.ts` | Each function in it is routed to `lib/utils/format.ts`, `lib/utils/cn.ts`, a feature `constants.ts`, or deleted as dead code |
| Leaving `fetch("/api/users")` inside a component because it "works" | The call moves to a hook, the URL moves to `ENDPOINTS`, the response goes through `normalizePaginated()` |
| Adding `// @ts-nocheck` or `any` to make a moved file compile | Real types are written in `lib/types/{domain}.types.ts` and the file compiles under `strict: true` |
| Creating the new tree and leaving the old `src/` beside it | The old tree is deleted; nothing imports from it because nothing needs it |
| Renaming `Component1.tsx` to `Component1Card.tsx` | The component is read, its actual job is identified, and it is named for that job: `InvoiceSummaryCard.tsx` |

**Behavior is preserved.** A migration changes structure, not product behavior. Every screen, route, form, and API call that worked before must work after. The only intentional behavior changes allowed are the ones this file mandates (centralized auth header, normalized errors, toast placement, role gating). If you find a genuine bug while migrating, do not silently fix it and do not silently keep it — list it in `MIGRATION_REPORT.md` under "Bugs found, not fixed" and ask.

**Nothing is lost.** Every piece of business logic in the source — validation rule, permission check, formatting quirk, edge-case branch — must exist somewhere in the target. If you delete something, it is because it is provably dead, and it is listed in the report.

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

This is the complete tree — application code **and** repo scaffolding. Everything a project needs has a place here; nothing belongs outside it. A project is not production-ready because `app/` is tidy — it is production-ready when routes, components, infrastructure, assets, CI, env handling, and repo hygiene are all in place.

`(pagename)`, `{Page}`, and `{feature}` are placeholders — replace them with real domain names (see NAMING CONVENTIONS). Files marked *optional* are added only when the project actually needs them.

```
frontend/
│
├── .github/                               # Repo automation — never application code
│   ├── workflows/
│   │   ├── ci.yml                         # typecheck + lint + build on every PR
│   │   └── deploy.yml                     # deploy on merge to main (self-hosted only)
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS
│   └── dependabot.yml                     # weekly dependency PRs
│
├── .vscode/                               # Shared editor defaults — commit these
│   ├── settings.json                      # format on save, default formatter
│   └── extensions.json                    # recommend eslint, prettier, tailwind
│
├── .husky/                                # Git hooks — optional
│   └── pre-commit                         # lint-staged
│
├── app/                                   # Routes only — thin shells, zero logic
│   ├── (pagename)/
│   │   └── page.tsx
│   │
│   ├── (pagename)/
│   │   ├── [ID]
│   │   │   └── page.tsx
│   │   └── page.tsx
│   │
│   ├── api/
│   │   └── auth/[...nextauth]/route.ts
│   ├── error.tsx                          # Route-segment error boundary
│   ├── loading.tsx                        # Streaming fallback
│   ├── not-found.tsx                      # 404 page
│   ├── favicon.ico                        # Browser tab icon
│   ├── opengraph-image.png                # Social share preview — optional
│   ├── robots.ts                          # Generated robots.txt — public apps
│   ├── sitemap.ts                         # Generated sitemap.xml — public apps
│   ├── globals.css                        # Tailwind import + @theme tokens
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
│           └── components/                # Sub-components — PRIVATE to this feature only
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
├── lib/                                   # Infrastructure — no JSX, no React hooks
│   ├── api/
│   │   ├── client.ts                      # Axios instance + interceptors
│   │   ├── endpoints.ts                   # Every backend URL — one source of truth
│   │   └── adapters.ts                    # Normalize FastAPI / ASP.NET / Spring Boot responses
│   ├── query/
│   │   ├── client.ts                      # QueryClient singleton
│   │   └── keys.ts                        # Query key factory
│   ├── auth/
│   │   ├── config.ts                      # next-auth providers + JWT callbacks
│   │   └── types.d.ts                     # Session / JWT type augmentation
│   ├── store/
│   │   ├── ui.store.ts                    # Sidebar open, theme
│   │   └── auth.store.ts                  # Cached session user
│   ├── types/
│   │   ├── common.types.ts                # PaginatedResponse<T>, ApiError
│   │   └── {feature}.types.ts             # One file per domain — never one global types.ts
│   ├── permissions.ts                     # Role → allowed actions map
│   ├── nav.ts                             # Navigation items
│   └── utils/
│       ├── cn.ts                          # clsx + tailwind-merge
│       └── format.ts                      # formatDate, formatCurrency, formatBytes
│
├── public/                                # Served at the domain root — WORLD-READABLE
│   ├── images/
│   │   ├── brand/
│   │   │   ├── logo.svg
│   │   │   ├── logo-dark.svg
│   │   │   └── logo-mark.svg
│   │   ├── home/                          # One folder per page that owns the imagery
│   │   │   ├── hero.webp
│   │   │   └── feature-dashboard.webp
│   │   └── illustrations/
│   │       ├── empty-state.svg
│   │       └── error-404.svg
│   ├── icons/                             # Standalone SVGs not covered by lucide-react
│   ├── fonts/                             # ONLY self-hosted fonts — prefer next/font
│   ├── robots.txt                         # static — or generate via app/robots.ts
│   └── site.webmanifest                   # static — or generate via app/manifest.ts
│
├── .editorconfig                          # Whitespace rules every editor honours
├── .env                                   # Shared non-secret defaults — COMMITTED
├── .env.example                           # Template of every required var — COMMITTED
├── .env.local                             # Real local secrets — NEVER COMMITTED
├── .env.production                        # Non-secret production defaults — COMMITTED
├── .gitattributes                         # Line endings, linguist, LFS
├── .gitignore
├── .nvmrc                                 # Pinned Node version — CI reads this file
├── .prettierrc
├── .prettierignore
├── .dockerignore                          # Required whenever a Dockerfile exists
├── Dockerfile                             # Only if the app is self-hosted
├── LICENSE
├── README.md                              # Setup, scripts, env vars, architecture
├── eslint.config.mjs                      # Flat config (next/core-web-vitals)
├── middleware.ts                          # Auth guard + security headers
├── next.config.ts                         # HSTS, CSP, images, redirects
├── next-env.d.ts                          # Generated — commit it, never edit it
├── package.json
├── package-lock.json                      # Commit the lockfile. Always.
├── postcss.config.mjs                     # @tailwindcss/postcss
└── tsconfig.json                          # strict: true, "@/*": ["./*"]
```

**Tailwind CSS 4 note:** v4 is CSS-first. Theme tokens live in `app/globals.css` under `@theme`, and `tailwind.config.ts` is optional — create it only when a plugin requires one. Never port a v3 config file across unchanged.

**Nothing outside this tree.** There is no `src/`, no `utils/` at the root, no `containers/`, no `views/`, no `services/`, no second components folder. If you are about to create a top-level folder that is not in this tree, you have misclassified the file — re-read the destination table in PHASE 2.

---

### APP ROUTER SPECIAL FILES

These are Next.js conventions, not free-form files. They live inside `app/`, and Next.js discovers them by name — never rename them.

| File | Purpose | Required? |
|---|---|---|
| `app/layout.tsx` | Root layout — mounts `<Providers>` | **Required** |
| `app/globals.css` | Tailwind import + `@theme` tokens | **Required** |
| `app/favicon.ico` | Browser tab icon | **Required** |
| `app/error.tsx` | Route-segment error boundary | **Required** |
| `app/not-found.tsx` | 404 page | **Required** |
| `app/loading.tsx` | Streaming fallback | Strongly recommended |
| `app/icon.png` / `app/apple-icon.png` | Generated app icons | Recommended |
| `app/opengraph-image.png` | Social share preview | Recommended |
| `app/robots.ts` | Generated `robots.txt` | Recommended |
| `app/sitemap.ts` | Generated `sitemap.xml` | Recommended for public pages |
| `app/manifest.ts` | Generated web manifest (PWA) | Only if installable |
| `app/(group)/layout.tsx` | Per-shell layout, e.g. `(dashboard)` | Per route group |
| `app/api/auth/[...nextauth]/route.ts` | next-auth handler | Required with auth |

Use **either** `app/robots.ts` **or** `public/robots.txt` — never both. Same for the manifest. Generated wins when the value depends on the environment.

---

### `public/` RULES

`public/` is served at the domain root and is **world-readable by anyone**. Treat it as published, not as storage.

```
✓  Organize by purpose:  images/brand/, images/{page}/, icons/, fonts/
✓  kebab-case file names:  hero-banner.webp,  logo-dark.svg,  empty-state.svg
✓  Photos and screenshots → .webp (or .avif). Never ship a 4 MB .png hero.
✓  Icons and logos → .svg, optimized (no editor metadata, no embedded rasters)
✓  Reference with a root-absolute path:  /images/brand/logo.svg
✓  Render through next/image with explicit width, height, and alt

✗  NEVER prefix a folder with its parent:  public/public-logo/  →  public/images/brand/
✗  NEVER put .env files, backups, exports, invoices, or internal docs in public/
✗  NEVER put .ts/.tsx/.js source files in public/ — they are shipped unminified
✗  NEVER import from public/ — it is fetched by URL, not bundled
✗  NEVER leave unreferenced assets behind after a migration
✗  NEVER use spaces, capitals, or copy suffixes:  "Hero Image (1).PNG"
```

| Asset | Where it goes | Why |
|---|---|---|
| Logo, wordmark, brand marks | `public/images/brand/` | Static, cached, reused everywhere |
| Marketing/page-specific imagery | `public/images/{page}/` | Grouped by the page that uses it |
| Empty-state / error illustrations | `public/images/illustrations/` | Shared across features |
| One-off SVG icons | `public/icons/` | lucide-react covers the rest |
| Self-hosted font files | `public/fonts/` | Prefer `next/font` — no file needed |
| User-uploaded content | **Nowhere** — the backend serves it | `public/` is build-time only |

---

### `.github/workflows/ci.yml`

Every project gets CI. A structure rule that nothing enforces is a suggestion.

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm

      - name: Install
        run: npm ci

      - name: Type check
        run: npx tsc --noEmit

      - name: Lint
        run: npm run lint

      - name: Build
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL:      ${{ vars.NEXT_PUBLIC_API_URL }}
          NEXT_PUBLIC_BACKEND_TYPE: ${{ vars.NEXT_PUBLIC_BACKEND_TYPE }}
          NEXTAUTH_URL:             ${{ vars.NEXTAUTH_URL }}
          NEXTAUTH_SECRET:          ${{ secrets.NEXTAUTH_SECRET }}
```

**Workflow rules:**
- Secrets come from `${{ secrets.* }}`, non-secret config from `${{ vars.* }}`. Never inline a real value in YAML.
- The Node version comes from `.nvmrc` so CI and laptops cannot drift.
- CI runs the same three gates as PHASE 9: `tsc --noEmit`, `lint`, `build`. A migration is not finished until CI is green.
- Never add `continue-on-error: true` to a quality gate.
- If the host (Vercel, Netlify, Amplify) already builds on push, `deploy.yml` is unnecessary — do not add a second deploy path.

---

### ENVIRONMENT FILE MATRIX

Next.js loads several env files with a defined precedence. Get this wrong and secrets leak or builds break.

| File | Loaded when | Commit? | May contain secrets? |
|---|---|---|---|
| `.env` | Always, lowest priority | ✅ Yes | ❌ Never |
| `.env.development` | `next dev` | ✅ Yes | ❌ Never |
| `.env.production` | `next build` / `next start` | ✅ Yes | ❌ Never |
| `.env.local` | Always except `test`, overrides the above | ❌ **Never** | ✅ Yes |
| `.env.development.local` | `next dev`, highest priority | ❌ **Never** | ✅ Yes |
| `.env.production.local` | production, highest priority | ❌ **Never** | ✅ Yes |
| `.env.example` | Never loaded — documentation only | ✅ Yes | ❌ Never (empty values) |

```
Precedence:  .env.{mode}.local  >  .env.local  >  .env.{mode}  >  .env
```

**Rules:**
- Committed env files hold **non-secret defaults only** — public API base URLs, feature flags, backend type. Anything that would hurt if it appeared on GitHub belongs in `.env.local` or in the hosting platform's secret store.
- `NEXTAUTH_SECRET`, API keys, and database URLs never live in a committed file. In production they come from the host's environment settings, not from `.env.production`.
- Every variable that appears in any env file must also appear in `.env.example` with an empty value.
- `NEXT_PUBLIC_*` is compiled into the browser bundle and is readable by every visitor. Never prefix a secret with it.
- `.gitignore` must contain `.env*.local` (and must NOT ignore `.env.example`).

---

### `.gitignore` BASELINE

```gitignore
# dependencies
node_modules/
.pnp
.pnp.js

# next.js
.next/
out/
build/
next-env.d.ts.bak

# env — local files only; .env / .env.example / .env.production stay tracked
.env*.local

# testing & coverage
coverage/

# misc
.DS_Store
*.pem
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.vercel
*.tsbuildinfo
```

---

### `package.json` SCRIPTS BASELINE

```json
{
  "scripts": {
    "dev":        "next dev",
    "build":      "next build",
    "start":      "next start",
    "lint":       "next lint",
    "typecheck":  "tsc --noEmit",
    "format":     "prettier --write .",
    "verify":     "npm run typecheck && npm run lint && npm run build"
  }
}
```

`npm run verify` is the single command that reproduces CI locally. Run it before declaring any migration or feature complete.

---

### `README.md` MINIMUM CONTENTS

A README that says "run npm install" is not documentation.

```
1. What this app is        one paragraph, and which backend it talks to
2. Prerequisites           Node version (matches .nvmrc), package manager
3. Setup                   clone → cp .env.example .env.local → fill → npm ci → npm run dev
4. Environment variables   a table: name | required | example | what it does
5. Scripts                 what each npm script does
6. Architecture            a short pointer to this structure file — do not duplicate it
7. Deployment              where it deploys, what triggers it
```

---

### OPTIONAL — ADD ONLY WHEN THE PROJECT ACTUALLY NEEDS IT

Do not scaffold these by reflex. An empty folder is clutter, and clutter is what this document exists to prevent.

| Folder / file | Add when |
|---|---|
| `Dockerfile` + `.dockerignore` | The app is self-hosted rather than deployed to Vercel/Netlify |
| `.husky/` + `lint-staged` config | The team wants pre-commit enforcement |
| `tests/` or co-located `*.test.tsx` | A test runner is actually part of the stack |
| `.github/dependabot.yml` | The repo is long-lived and maintained |
| `CHANGELOG.md` | The project is versioned and released |
| `CONTRIBUTING.md` | More than one team contributes |
| `tailwind.config.ts` | A Tailwind plugin requires a JS config under v4 |
| `instrumentation.ts` | Sentry / OpenTelemetry is wired up |

---

### MODE B — MIGRATING THE ROOT LAYER

The root layer is migrated in PHASE 3 and cleaned in PHASE 8. It is part of the file ledger, not an afterthought.

```
CI          Port the old pipeline's real steps into .github/workflows/ci.yml.
            Delete CircleCI / Travis / Jenkins / GitLab configs once CI is green.
            Never carry two CI systems forward.

Assets      Move every referenced asset into the public/ tree above, renaming to
            kebab-case and fixing wrong extensions on the way. Convert oversized
            PNG/JPG heroes to .webp. Update every reference in the same commit.
            Delete unreferenced assets — list them in the report.

Env         Merge every old env file (.env, .env.development, REACT_APP_*,
            VITE_*) into the matrix above, renaming browser-exposed vars to
            NEXT_PUBLIC_*. Audit for secrets that were committed: if a real
            secret exists in git history, say so plainly in the report and tell
            the user to rotate it — removing the file does not un-leak it.

Configs     Replace CRA / Vite / Babel / webpack configs with the blueprints
            here. Old ESLint and Prettier configs are replaced, not merged.

Docs        Rewrite README.md against the template above. A README describing
            the old structure is worse than no README.

Root junk   Delete: *.bak, *.old, "* copy.*", stray .txt notes, unused
            Dockerfiles, dead scripts in package.json, unused .vscode settings.
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

## MIGRATION PROTOCOL

> Run this section top to bottom whenever the repository already contains code (**MODE B**).
> Ten phases. Each phase has an exit condition. Do not start phase N+1 until phase N's exit condition is met.

```
PHASE 0   Safety & scope gate          → branch created, scope confirmed
PHASE 1   Inventory                    → full picture of what exists, read-only
PHASE 2   Domain map & migration plan  → MIGRATION_PLAN.md written and shown
PHASE 3   Scaffold the target skeleton → target tree + config files in place
PHASE 4   Infrastructure first (lib/)  → lib/ complete and type-checking
PHASE 5   Feature-by-feature refactor  → each feature fully rebuilt, one at a time
PHASE 6   Route layer                  → app/ is thin shells only
PHASE 7   Cross-cutting wiring         → shell, nav, permissions, providers
PHASE 8   Delete the old world         → zero legacy files, zero dead code
PHASE 9   Verification gates           → every automated gate passes
PHASE 10  Report                       → MIGRATION_REPORT.md handed over
```

---

### PHASE 0 — SAFETY & SCOPE GATE

```
0.1  Confirm this is a web frontend project.
     If the repository is a backend API, a mobile app, or a headless library,
     STOP. Tell the user which file from the library applies instead
     (Backend/*, Frontend/FLUTTER_STRUCTURE.md, ...). Never force this
     structure onto a project it was not written for.

0.2  Confirm the working tree is clean:  git status --porcelain
     If it is not clean, STOP and ask the user to commit or stash first.
     Never begin a migration on top of uncommitted work.

0.3  Create the working branch:  git checkout -b refactor/project-structure
     Never migrate directly on main / master.

0.4  Confirm the frontend root. In a monorepo, or when the frontend is nested
     (/client, /web, /ui, or inside the backend repo), this structure applies
     to that folder — it is "the project root" everywhere below. State the path
     you chose. Never touch files outside it.

0.5  Read, do not run. Do not execute build/dev/test scripts of unknown origin,
     and never run a destructive command (rm -rf, git clean, git reset --hard,
     git checkout --) without stating exactly what it deletes and getting a yes.
```

**Exit condition:** fresh branch, clean tree, frontend root identified and stated out loud.

---

### PHASE 1 — INVENTORY (READ-ONLY)

Change nothing in this phase. A migration planned from a partial reading of the code will strand logic.

```
1.1  Stack detection — read each if present:
     package.json ............ framework, versions, scripts, every dependency
     next.config.* ........... existing config, redirects, images, headers
     tsconfig / jsconfig ..... TypeScript or JavaScript? strict? path aliases?
     tailwind.config.* ....... Tailwind version, theme tokens, plugins
     .env* ................... every variable in use (never print secret VALUES)
     README / docs ........... intent, domain vocabulary, deploy target

1.2  Route detection:
     app/**/page.*   ......... App Router routes
     pages/**/*.*    ......... Pages Router routes
     src/App.* + router ...... SPA (React Router) routes
     Record for each: path, params, auth requirement, layout used.

1.3  Every network call — the highest-value scan in this phase:
     grep -rn "fetch(|axios|useQuery|useSWR|XMLHttpRequest" src app pages components
     Record: URL, method, request shape, response shape, calling file.

1.4  Every form and validation rule:
     grep -rn "onSubmit|useForm|yup|zod|joi|validate" src app pages components

1.5  Every state container:
     grep -rn "createContext|useReducer|redux|zustand|jotai|recoil|mobx" src app

1.6  Every auth / role check:
     grep -rn "token|localStorage|sessionStorage|Authorization|role|permission|isAdmin"

1.7  Size and shape:
     - Files over 200 lines .......... certain split candidates, list them
     - Duplicates .................... two Buttons, three modals, four date formatters
     - Dead files .................... no inbound imports anywhere
     - Junk .......................... *.bak, *.old, *copy*, *.txt, commented-out blocks

1.8  Assets and styles: public/, images, fonts, global CSS, CSS Modules,
     styled-components, SCSS. Note what must become Tailwind and what is
     genuinely global (globals.css).
```

**Exit condition:** you can name every route, every API endpoint, every form, and every state store in the source project without re-reading it.

---

### PHASE 2 — DOMAIN MAP & MIGRATION PLAN

This is the phase that separates a real migration from a file shuffle. **Features are discovered from the domain, never from the old folder names.**

#### 2.1 Derive the feature list

A feature is a **business noun the app manages**, not a folder that happens to exist. Find them by intersecting four sources:

```
Routes            /users, /orders, /orders/[id]        → users, orders
API endpoints     /api/v1/invoices, /api/v1/customers  → invoices, customers
Domain types      interface Product, class Invoice     → products, invoices
Screen titles     "Manage Suppliers"                   → suppliers
```

Merge synonyms into ONE canonical name. If `client`, `customer`, and `account` all describe the same entity, pick one and use it everywhere — folder, component prefix, type, endpoint, query key, nav label, permission key. Record that decision in the plan; consistency across the whole codebase depends on it.

#### 2.2 Classify every source file

Every source file gets exactly one destination and exactly one action. No file may end up unclassified — "leave it where it is" is not a valid outcome.

**Destination decision table**

| What the file actually is | Destination |
|---|---|
| A route entry point (page, screen, view) | `app/(group)/{route}/page.tsx` — thin shell only |
| The real content of a screen | `components/pages/{feature}/{Feature}Page.tsx` |
| A detail / edit screen for one record | `components/pages/{feature}/{Feature}DetailPage.tsx` |
| A piece used by exactly one feature | `components/pages/{feature}/components/{Feature}{Thing}.tsx` |
| A piece used by 2+ features, carries business meaning | `components/shared/` |
| A styling-only primitive with zero business rules | `components/ui/` |
| App chrome: shell, sidebar, navbar, page header | `components/layout/` |
| Data fetching for one feature | `components/pages/{feature}/hooks/use{Feature}.ts` |
| Reusable non-feature hook (debounce, storage, pagination) | `hooks/` |
| Validation rules for one feature's forms | `components/pages/{feature}/schemas/{feature}.schema.ts` |
| Domain interfaces / DTO shapes | `lib/types/{domain}.types.ts` |
| A backend URL, anywhere | `lib/api/endpoints.ts` |
| HTTP setup, interceptors, retries, headers | `lib/api/client.ts` |
| Backend-shape differences (pagination, errors) | `lib/api/adapters.ts` |
| Cache keys / query keys | `lib/query/keys.ts` |
| Auth config, providers, JWT callbacks | `lib/auth/config.ts` |
| UI-only client state (sidebar, theme, modals) | `lib/store/{name}.store.ts` |
| Role → action rules, `isAdmin` checks | `lib/permissions.ts` |
| Menu / nav definitions, hardcoded sidebar links | `lib/nav.ts` |
| Pure helpers: formatting, class merging | `lib/utils/` |
| Magic strings / numbers used by one feature | `components/pages/{feature}/constants.ts` |
| Route protection, security headers | `middleware.ts` |
| Static files served as-is | `public/` |
| Dead, duplicated, or superseded by a blueprint | **DELETE** |

**Action vocabulary** — tag every file with exactly one:

```
REWRITE          Rebuild against the blueprint in this file. The default for
                 anything infrastructure-shaped (http client, auth, stores).
SPLIT            One file → several, each with a single responsibility.
EXTRACT-HOOK     Data fetching pulled out of JSX into a TanStack Query hook.
EXTRACT-SCHEMA   Manual / yup / joi validation converted to a Zod schema.
EXTRACT-TYPES    Inline or implicit shapes promoted to lib/types/{domain}.types.ts.
PROMOTE          Feature-local file used by 2+ features → shared/ or ui/.
DEMOTE           "Shared" file used by exactly one feature → into that feature.
PORT             Logic kept, surface rewritten (JS→TS, CSS→Tailwind, Pages→App).
MOVE             Copied across unchanged. Legal ONLY for a file that already
                 obeys every rule in this document. Expect this to be rare.
DELETE           Dead, duplicate, junk, or replaced by a blueprint.
```

#### 2.3 Write `MIGRATION_PLAN.md`

Create it at the frontend root with these ten sections:

```
1.  Source assessment     stack, size, TS/JS, state libs, quality notes
2.  Target confirmation   the TECH STACK table + any deviation you must flag
                          (e.g. "project has no auth → next-auth omitted")
3.  Feature list          canonical names + the vocabulary decisions made
4.  Route map             old route → new route (+ route group, + auth needed)
5.  File ledger           every source file → destination + action + one-line note
6.  Endpoint ledger       every discovered URL → ENDPOINTS.{feature}.{action}
7.  Dependency changes    to add / to remove, each with a reason
8.  Risk list             biggest files, tangled logic, anything ambiguous
9.  Open questions        everything you had to guess
10. Commit sequence       the order features will be migrated in
```

#### 2.4 STOP-AND-CONFIRM GATE

**Present `MIGRATION_PLAN.md` and wait for approval before modifying any existing file.** This is the one mandatory pause in the protocol. If the user has already said "just do it", still write the plan and still surface the feature list and open questions — then proceed without waiting.

**Exit condition:** `MIGRATION_PLAN.md` exists, every source file appears in the ledger exactly once, the user has seen it.

---

### PHASE 3 — SCAFFOLD THE TARGET SKELETON

Create the target tree from the FOLDER STRUCTURE section — real folders, not placeholders — then put the config layer in place:

```
3.1  tsconfig.json      exactly as specified (strict: true, "@/*": ["./*"])
3.2  next.config.ts     from the blueprint (HSTS + CSP)
3.3  middleware.ts      from the blueprint (PROTECTED starts empty, filled in Phase 6)
3.4  .env.example       committed, empty values
3.5  .env.local         real values carried over from the old env file(s)
3.6  .gitignore         must contain .env.local, node_modules, .next
3.7  app/globals.css    Tailwind layers + design tokens
3.8  package.json       add the exact TECH STACK; queue forbidden libraries for
                        removal (redux, moment, yup/joi, styled-components,
                        bespoke fetch wrappers) — remove them in Phase 8, once
                        nothing imports them
3.9  public/            the asset tree from FOLDER STRUCTURE; move and rename
                        every asset as it is referenced
3.10 .github/workflows/ci.yml   typecheck + lint + build on every PR
3.11 Root defaults      .editorconfig, .nvmrc, .prettierrc, .gitattributes,
                        eslint.config.mjs, postcss.config.mjs, LICENSE
3.12 app/ metadata      favicon.ico, error.tsx, not-found.tsx, loading.tsx,
                        robots.ts / sitemap.ts when the app has public pages
3.13 README.md          rewritten against the template — never left describing
                        the old structure
```

Rules for this phase:
- Build the new tree **alongside** the old code, never on top of it. The old code keeps compiling until Phase 8 deletes it.
- Do not create a folder this project will never use. Every folder that exists at the end must hold real files.
- No `.gitkeep` graveyard.

**Exit condition:** target folders exist, config files match the blueprints, `npx tsc --noEmit` runs (old code may still report errors).

---

### PHASE 4 — INFRASTRUCTURE FIRST (`lib/`)

Nothing in `components/` can be built correctly until `lib/` is right. Build in exactly this order — each step depends on the one above it:

```
4.1  lib/types/common.types.ts     ApiError, PaginatedResponse<T>
4.2  lib/types/{domain}.types.ts   one file per feature noun from Phase 2.
                                   Harvest real shapes from the old code and
                                   from actual API responses. Never `any`,
                                   never one global types.ts.
4.3  lib/api/endpoints.ts          EVERY URL found in Phase 1.3. After this
                                   step, no URL string may exist anywhere else.
4.4  lib/api/adapters.ts           from the blueprint; set BACKEND to match
4.5  lib/api/client.ts             from the blueprint. Replaces every old fetch
                                   wrapper, axios instance, and hand-rolled
                                   auth-header helper.
4.6  lib/query/client.ts + keys.ts one key block per feature
4.7  lib/auth/config.ts + types.d.ts   port the old login flow into the
                                   Credentials provider; token handling that
                                   used localStorage moves into the JWT callback
4.8  lib/store/ui.store.ts         only the UI state that survived triage
     lib/store/auth.store.ts       read cache only — never tokens
4.9  lib/utils/cn.ts + format.ts   deduplicate every formatter found in Phase 1
4.10 lib/permissions.ts            every isAdmin / role check from Phase 1.6
                                   collapses into this one map
4.11 lib/nav.ts                    every hardcoded sidebar / menu link
```

Migration rules for this layer:

- **Tokens leave browser storage.** `localStorage.getItem("token")` and every manual `Authorization` header disappear; the next-auth session plus the request interceptor replace them. This is a mandated behavior change — record it in the report.
- **One HTTP client.** Every `api.js`, `http.js`, `request.ts`, `useFetch`, and bare `fetch` collapses into `apiClient`.
- **Shapes normalize at the edge.** Every list call goes through `normalizePaginated()`; components never see `totalElements` or `pageNumber`.
- **Duplicate helpers collapse.** Three date formatters become one `formatDate` — pick the most correct implementation, not the first one you found.

**Exit condition:** `lib/` type-checks, contains no JSX and no React hooks, and every endpoint from the Phase 2 ledger is present.

---

### PHASE 5 — FEATURE-BY-FEATURE REFACTOR

Migrate **one feature at a time**, in the Phase 2 commit sequence. Finish a feature completely — types through route — before starting the next. Never leave two features half-migrated at once.

For each feature, run the 12 steps from **WHEN ADDING A NEW FEATURE**, sourcing the content from the old code instead of inventing it.

#### 5.1 Decomposing a god component

Old projects concentrate everything in one big file. Read it fully, then take it apart along these lines:

| What you find inside the old file | Where it goes |
|---|---|
| `useEffect` + `fetch` + `setState` triple | `hooks/use{Feature}.ts` → `useQuery` |
| POST/PUT/PATCH/DELETE handler | `hooks/use{Feature}.ts` → `useMutation` |
| `if (!email.includes("@")) setError(...)` | `schemas/{feature}.schema.ts` → Zod |
| Inline `type Row = { ... }` for a domain object | `lib/types/{domain}.types.ts` |
| The `<table>` / list rendering | `components/{Feature}List.tsx` |
| The create form | `components/{Feature}CreateForm.tsx` |
| The edit form | `components/{Feature}EditForm.tsx` |
| A row/card presentation unit | `components/{Feature}Card.tsx` |
| Filter/search bar | `components/{Feature}Filters.tsx` |
| Modal shell with no business rules | `components/ui/Modal.tsx` (reuse, don't re-create) |
| Status/severity chip | `components/ui/Badge.tsx` |
| `const STATUSES = [...]` | `constants.ts` |
| Layout, orchestration, local UI state | `{Feature}Page.tsx` |
| `alert()` / `console.log` success messages | `toast` inside the mutation's `onSuccess` |
| `try/catch` around every call | deleted — the interceptor owns error handling |
| `if (user.role === "admin")` sprinkled inline | `lib/permissions.ts` + `<RoleGate>` |

**Splitting thresholds** — apply judgment, but these are the defaults:

```
Component file > 200 lines          → split
Component doing fetch + render      → split (hook + JSX)
Component with 3+ useState for      → likely two components
  unrelated concerns
A file whose name needs "and"       → split
  ("UserListAndFilters")
JSX nested more than 4 levels deep  → extract the inner block
```

Equally: **do not over-split.** A 30-line card used once does not need its own folder. The unit of extraction is a responsibility, not a line count.

#### 5.2 Rewrite rules applied to every migrated file

```
✓ "use client" added ONLY where the SERVER vs CLIENT rules require it
✓ Props typed with an explicit interface — no implicit any, no React.FC
✓ Every string that faces the user stays user-facing; no debug text ships
✓ Class names via Tailwind + cn(); inline style objects are removed
✓ Imports use "@/..." — every relative cross-folder path is rewritten
✓ Dead props, unused state, and commented-out code are removed, not carried
✓ Keys, ids, and list rendering fixed to use stable ids (never array index)
✓ Loading state uses Skeleton, empty state uses EmptyState — not raw text
✓ Accessibility kept or improved: labels tied to inputs, buttons are <button>
```

#### 5.3 Per-feature exit gate

Before moving to the next feature, all of these must hold:

```
[ ] npx tsc --noEmit passes for the migrated feature
[ ] The feature's route renders and its screens behave as they did before
[ ] No fetch/axios/URL string remains anywhere inside the feature
[ ] No hook file (use*.ts) sits inside a components/ JSX folder
[ ] Nothing outside the feature imports its private sub-components
[ ] git commit -m "refactor({feature}): migrate to standard structure"
```

**Exit condition:** every feature from the Phase 2 list has passed its own gate, each in its own commit.

---

### PHASE 6 — ROUTE LAYER

```
6.1  Recreate every route from the Phase 1.2 route map under app/.
     Old → new mapping:
       pages/users/index.jsx        → app/(dashboard)/users/page.tsx
       pages/users/[id].jsx         → app/(dashboard)/users/[id]/page.tsx
       <Route path="/users" .../>   → app/(dashboard)/users/page.tsx
       pages/_app.jsx               → app/layout.tsx + components/shared/Providers.tsx
       pages/_document.jsx          → app/layout.tsx
       pages/api/*                  → keep only what MUST run on the Next server;
                                      everything the backend already owns is deleted

6.2  Group routes by shell, not by feature:
       (auth)      login, register, forgot-password   — no app shell
       (dashboard) every authenticated screen         — AppShell
     Route groups never appear in the URL.

6.3  Every page.tsx: metadata + one import + one return. 8 lines maximum.

6.4  Add error.tsx, loading.tsx, not-found.tsx from the blueprints.

6.5  middleware.ts: fill PROTECTED with every authenticated route prefix,
     AUTH_ONLY with every login/register prefix.

6.6  Preserve URLs. If a path must change, add a redirect in next.config.ts
     and list it in the report. Silently breaking a bookmarked URL is a defect.
```

**Exit condition:** every old route resolves in the new app, no `page.tsx` exceeds 8 lines, no `page.tsx` carries `"use client"`.

---

### PHASE 7 — CROSS-CUTTING WIRING

```
7.1  components/shared/Providers.tsx     one QueryClientProvider, one Toaster,
                                         one SessionProvider — mounted once
7.2  components/layout/AppShell.tsx      the shell the old app had, rebuilt
7.3  components/layout/Sidebar.tsx       renders NAV_ITEMS from lib/nav.ts,
     components/layout/MobileNav.tsx     filtered by the session role
7.4  components/shared/RoleGate.tsx      wraps can() from lib/permissions.ts
7.5  components/shared/ErrorBoundary.tsx
7.6  components/ui/*                     the deduplicated primitive set: one
                                         Button, one Input, one Modal, one Card
7.7  Theme + globals.css                 tokens consistent with Tailwind config
```

**Exit condition:** no duplicated primitive remains, no hardcoded nav link exists in any component, no second `Toaster` or `QueryClient` exists.

---

### PHASE 8 — DELETE THE OLD WORLD

The migration is not real until the old code is gone.

```
8.1  Delete the legacy trees: src/, pages/, old components/, old utils/, and
     every file marked DELETE in the ledger.
8.2  Delete dead code: unreferenced components, unused exports, commented-out
     blocks, TODO stubs that were never implemented.
8.3  Delete junk: *.bak, *.old, *copy*, *.txt notes, unused images and fonts.
8.4  Remove now-unused dependencies from package.json, then reinstall so the
     lockfile matches.
8.5  Remove obsolete config: CRA/Vite configs, old ESLint/Babel configs, dead
     scripts in package.json, unused env vars in .env.example.
8.6  Confirm zero imports point at a deleted path.
8.7  Delete old CI (CircleCI, Travis, Jenkins, GitLab), root junk (*.bak,
     *.old, "* copy.*", stray .txt notes), and every unreferenced asset
     left in public/.
```

Never delete a file until its replacement compiles and its route renders. Delete in one dedicated commit — `chore: remove legacy structure` — so the diff is reviewable and revertible.

**Exit condition:** `git status` shows the legacy paths deleted, the build passes, nothing references a removed module.

---

### PHASE 9 — VERIFICATION GATES

All of these must pass. Fix, then re-run — never report a gate as passing without running it, and never disable a rule to make a gate green.

**Build gates**

```bash
npx tsc --noEmit        # zero errors, strict mode
npm run lint            # zero errors
npm run build           # production build succeeds
```

**Structure gates** — each search must return NOTHING:

```bash
# LAW 1 — no client directive or hooks in route files
grep -rn "use client" app --include=page.tsx --include=layout.tsx
grep -rn "useState\|useEffect\|useQuery" app --include=page.tsx

# LAW 2 — no hook files hiding inside components/
find components -name "use*.ts" -not -path "*/hooks/*"

# LAW 3 — no JSX or React hooks in lib/
grep -rn "useState\|useEffect\|return (" lib --include=*.tsx

# One HTTP client, no stray URLs
grep -rn "from \"axios\"" app components hooks lib --include=*.ts --include=*.tsx | grep -v "lib/api/client.ts"
grep -rn "fetch(\"http\|https\?://" app components hooks

# No relative cross-folder imports
grep -rn "from \"\.\./\.\./" app components hooks lib

# No forbidden libraries
grep -rn "moment\|redux\|styled-components\|yup\|joi" package.json app components lib

# No escape hatches
grep -rn "@ts-ignore\|@ts-nocheck\|: any\b" app components hooks lib

# No stray leftovers
find . -name "*.bak" -o -name "*copy*" -o -name "*.old" -not -path "./node_modules/*"

# Env hygiene — no local/secret env file may be tracked
git ls-files | grep -E "\.env" | grep -E "\.local$"
grep -rn "NEXT_PUBLIC_[A-Z_]*\(SECRET\|KEY\|PASSWORD\|TOKEN\)" .env* app components lib

# public/ hygiene — no code, no env files, no spaces in names
find public -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name ".env*" -o -name "* *"
```

**Presence gates** — each must exist and be correct:

```bash
test -f .github/workflows/ci.yml    # runs typecheck + lint + build
test -f .env.example                # every var documented, values empty
test -f .gitignore && grep -n "env\*.local" .gitignore
test -f README.md                   # rewritten, not the old one
test -f app/favicon.ico
test -f app/error.tsx
test -f app/not-found.tsx
```

**Manual gates**

```
[ ] Cross-feature import check: for each feature, confirm no file outside
    components/pages/{feature}/ imports anything inside its components/ folder
[ ] Every route from the Phase 1 route map resolves
[ ] Login → protected route → logout works end to end
[ ] Every form validates through Zod and shows per-field errors
[ ] Every list uses normalizePaginated()
[ ] Every file in the ledger reached its destination; nothing is orphaned
```

**Exit condition:** every command above is clean and every manual box is ticked.

---

### PHASE 10 — REPORT

Write `MIGRATION_REPORT.md` at the frontend root:

```
1.  Summary                  what the project was, what it is now, in 5 lines
2.  Structure before/after   two trees, side by side
3.  Feature ledger           feature → files created → source files consumed
4.  Route map                old URL → new URL, with any redirects added
5.  Behavior changes         every mandated change (auth storage, error handling,
                             toasts, role gating) and why
6.  Deleted                  files, dependencies, and dead code removed + reasons
7.  Bugs found, not fixed    anything broken in the source; nothing silently fixed
8.  Deviations               any place the structure could not be followed literally,
                             with justification
9.  Follow-ups               tests, a11y debt, TODOs the migration surfaced
10. Verification output      the result of every Phase 9 gate
```

Then summarize the same content in chat — do not make the user open the file to learn whether the migration succeeded.

**Exit condition:** report written, gates reported honestly, branch ready for review.

---

### SOURCE-SPECIFIC CONVERSION RULES

The protocol above is the same regardless of what you are handed. These are the extra rules per source type.

| Source | What changes |
|---|---|
| **Next.js App Router, messy** | Structure only. Keep the routes, apply Phases 2–9 to redistribute components, hooks, types, and infrastructure. |
| **Next.js Pages Router** | `pages/` → `app/` with route groups; `_app` → `layout.tsx` + `Providers`; `getServerSideProps` / `getStaticProps` → Server Components or TanStack Query; `next/router` → `next/navigation`; `pages/api/*` kept only where the Next server genuinely must own the call. |
| **CRA / Vite React SPA** | React Router routes → App Router folders; `index.html` → `app/layout.tsx`; env `REACT_APP_*` / `VITE_*` → `NEXT_PUBLIC_*`; browser-only components get `"use client"`; anything that can be a Server Component becomes one. |
| **JavaScript, no TypeScript** | Every file is ported to `.ts` / `.tsx` with real types derived from actual API payloads and prop usage. `any` is not a migration strategy; `@ts-nocheck` is never acceptable. |
| **CSS Modules / SCSS / styled-components** | Converted to Tailwind utilities plus `cn()`. Design tokens (colors, spacing, radii) move into the Tailwind theme. Only true globals stay in `globals.css`. |
| **Redux / MobX / Context state** | Server data → TanStack Query. UI-only state → Zustand. Derived state → computed at render. Most of the old store disappears; that reduction is the point. |
| **Class components** | Converted to function components with hooks. `componentDidMount` fetches become `useQuery`. |
| **A different framework entirely (Angular, Vue, Svelte)** | Treat the source as a specification, not as code to move. Extract routes, domain models, validation rules, permissions, and API contracts, then build the Next.js app fresh from this file. The file ledger maps source features to new files rather than source files to new files. |
| **Frontend nested in a backend repo** | Keep it in place unless asked; apply the structure inside that folder only. Never restructure the backend from this file. |

---

### MEANINGFUL NAMING — HOW TO NAME WHAT YOU MIGRATE

Old projects arrive with names that describe nothing. Every name you create must describe **what the thing is, in the language of the domain**.

**Banned outright** — if a source file carries one of these, renaming it meaningfully is part of the migration:

```
✗ Component1.tsx, Comp2.tsx, Test.tsx, Temp.tsx, New*.tsx, Old*.tsx, Final*.tsx
✗ utils2.ts, helpers.ts, misc.ts, common.ts, stuff.ts, functions.ts, index.ts (non-barrel)
✗ data.ts, list.tsx, item.tsx, form.tsx, page2.tsx, main.tsx, wrapper.tsx
✗ MyComponent, TheThing, Handler, Manager, Processor with no noun attached
✗ untitled, copy of, - Copy, v2, final_final
```

**Derivation rules**

```
Feature folder      plural, lowercase, canonical domain noun    users/  invoices/
Type / model        singular PascalCase                         User    Invoice
Type file           singular, lowercase                         user.types.ts
Component prefix    singular PascalCase feature name            UserList, InvoiceCard
Page component      {Feature}Page — feature name plural         UsersPage, InvoicesPage
Detail page         {Entity}DetailPage — entity singular        UserDetailPage
Hook file           use{Feature} — matches the feature folder   useUsers.ts
Route segment       plural, kebab-case if multi-word            /users  /purchase-orders
Endpoint key        matches the feature folder exactly          ENDPOINTS.purchaseOrders
Query key           matches the feature folder exactly          queryKeys.purchaseOrders
Permission key      matches the feature folder exactly          PERMISSIONS.purchaseOrders
```

**The consistency rule:** one entity, one word, everywhere. If the folder is `purchaseOrders`, then the type is `PurchaseOrder`, the file is `purchase-order.types.ts`, the component is `PurchaseOrdersPage`, the hook is `usePurchaseOrders`, the route is `/purchase-orders`, and the endpoint key is `purchaseOrders`. A reader who learns the name in one place must be able to predict it in all the others.

**Name for the job, not the shape.** `UserTableWrapper` describes markup; `UserList` describes purpose. `DataThing` describes nothing; `InvoiceSummaryCard` describes exactly one thing.

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
✗  Two structures living side by side after a migration — delete the old one
✗  Meaningless names carried over from the source — rename to the domain
✗  @ts-nocheck / @ts-ignore / `any` used to make migrated code compile
✗  Source files, .env files, or private documents inside public/
✗  A folder prefixed with its parent — public/public-logo/, components/components-ui/
✗  Secrets behind NEXT_PUBLIC_, or a real secret in a committed .env file
✗  Two CI systems, or a quality gate with continue-on-error: true
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
[ ] Root defaults present: .env.example, .gitignore, .nvmrc, README.md, LICENSE
[ ] CI workflow runs typecheck + lint + build, and is green
[ ] No secret in a committed env file; no secret behind NEXT_PUBLIC_
[ ] Assets under public/images|icons|fonts with kebab-case names, .webp photos
[ ] app/ metadata files present: favicon.ico, error.tsx, not-found.tsx
```

### MIGRATION EXIT CRITERIA (MODE B only — all of the above, plus)

```
[ ] MIGRATION_PLAN.md written, every source file in the ledger exactly once
[ ] MIGRATION_REPORT.md written and summarized in chat
[ ] Legacy trees deleted — no src/, no pages/, no parallel old structure
[ ] No file was merely moved: every migrated file obeys THE 3 LAWS
[ ] No file name carried over that does not describe what the file does
[ ] One entity = one word across folder, type, component, hook, route,
    endpoint key, query key, permission key
[ ] Every route from the old app resolves (or has a documented redirect)
[ ] Every old API call reaches the same backend endpoint as before
[ ] Every validation rule from the old code exists as a Zod rule
[ ] Every role check from the old code exists in lib/permissions.ts
[ ] localStorage/sessionStorage no longer holds tokens
[ ] Forbidden dependencies removed from package.json + lockfile refreshed
[ ] All Phase 9 gates run and clean — reported honestly, none disabled
[ ] Old CI configs removed — exactly one CI system remains
[ ] Every referenced asset moved into public/; unreferenced assets deleted
[ ] REACT_APP_* / VITE_* vars renamed to NEXT_PUBLIC_* and in .env.example
[ ] Any secret found in git history reported to the user for rotation
[ ] README.md rewritten — it describes the new structure, not the old one
[ ] Work is on refactor/project-structure with one commit per feature
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
