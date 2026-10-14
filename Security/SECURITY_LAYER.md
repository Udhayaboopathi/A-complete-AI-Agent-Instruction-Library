# AGENT INSTRUCTIONS — Full-Stack Security Layer

> **HOW TO USE THIS FILE**
> Drop this file into your project root alongside `FASTAPI_ORM_STRUCTURE.md` and `NEXTJS_FRONTEND_STRUCTURE.md`.
> When starting a new chat, say:
> _"Read `SECURITY_LAYER.md` deeply and apply every security rule to all code you generate."_
> This file applies to ALL frontends (Next.js, React, Angular) and ALL backends (FastAPI, ASP.NET Core, Spring Boot).
> These rules override any default behavior. No exceptions.

---

## YOUR SECURITY IDENTITY

You are a security-first full-stack engineer.
- Sensitive data is encrypted over every untrusted network; use TLS internally too when trust boundaries require it
- The backend origin/port is not directly reachable from the public internet; the public proxy address is expected to be visible
- Every protected request is authenticated and authorized; public health/login routes are narrowly scoped and rate-limited
- Every response strips sensitive fields before leaving the server
- All security is enforced at the infrastructure level — not left to individual developers

---

## THREAT MODEL — WHAT YOU ARE PROTECTING AGAINST

```
Threat 1: Network sniffing       → attacker reads data in transit
Threat 2: Backend IP exposure    → attacker knows your server IP and attacks it directly
Threat 3: Request forgery        → attacker sends fake requests to your API
Threat 4: Token theft            → attacker steals JWT and impersonates user
Threat 5: Replay attacks         → attacker replays captured requests
Threat 6: Brute force            → attacker hammers login endpoint
Threat 7: XSS                    → malicious script steals tokens or data
Threat 8: Clickjacking           → attacker embeds your app in iframe
Threat 9: Information leakage    → error messages expose server details
Threat 10: Oversized payloads    → attacker crashes server with huge request body
```

---

## ARCHITECTURE — THE ONLY ALLOWED PATTERN

```
                    INTERNET
                       │
                       │  HTTPS only (port 443)
                       ▼
              ┌─────────────────┐
              │  Reverse Proxy  │   ← Nginx / Caddy / Cloudflare
              │  api.domain.com │   ← This is ALL the browser ever sees
              └────────┬────────┘
                       │  localhost:8000 only
                       │  (internal — never public)
                       ▼
              ┌─────────────────┐
              │    Backend      │   ← FastAPI / ASP.NET / Spring Boot
              │ internal :8000  │   ← private network only; no public port
              └─────────────────┘
```

**Why this matters:**
- Browser developer tools show the proxy origin, never a separately reachable backend origin/port
- Backend server is invisible to the internet — it cannot be attacked directly
- TLS is terminated at the proxy; use a private network for the upstream hop or re-encrypt/mTLS when it crosses a trust boundary
- If the proxy goes down, the backend is still unreachable from outside

---

## LAYER 1 — REVERSE PROXY (Nginx)

Every project MUST have this. This is what hides the backend IP.

### `nginx/nginx.conf`

```nginx
# nginx/nginx.conf

# ── Redirect all HTTP to HTTPS ─────────────────────────────────────────
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$host$request_uri;
}

# ── Main HTTPS server ──────────────────────────────────────────────────
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # TLS certificate (use Let's Encrypt / Certbot)
    ssl_certificate     /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Only allow modern TLS — no TLS 1.0 or 1.1
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers   ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    # HSTS — tell browsers: ALWAYS use HTTPS for 1 year
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Remove headers that expose server info
    server_tokens off;
    proxy_hide_header X-Powered-By;
    proxy_hide_header Server;

    # Security headers
    add_header X-Frame-Options           "DENY"                              always;
    add_header X-Content-Type-Options    "nosniff"                           always;
    add_header Referrer-Policy           "strict-origin-when-cross-origin"   always;
    add_header Permissions-Policy        "camera=(), microphone=(), geolocation=()" always;

    # Reject oversized request bodies before they hit the backend
    client_max_body_size 10m;

    # Rate limiting — 10 requests per second per IP
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req      zone=api burst=20 nodelay;
    limit_req_status 429;

    # ── Proxy all requests to backend on localhost ─────────────────────
    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_http_version 1.1;

        # Forward real client IP to backend (for logging, rate limiting)
        proxy_set_header   X-Real-IP        $remote_addr;
        proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto https;
        proxy_set_header   Host             $host;

        # Remove headers that expose internal info
        proxy_hide_header  X-Powered-By;
        proxy_hide_header  Server;

        # Timeouts
        proxy_connect_timeout 10s;
        proxy_send_timeout    30s;
        proxy_read_timeout    30s;
    }
}
```

### `nginx/nginx-dev.conf` (local development — HTTP only)

```nginx
# nginx/nginx-dev.conf  — development only, never use in production
server {
    listen 8080;
    server_name localhost;

    client_max_body_size 10m;

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   X-Real-IP       $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   Host            $host;
    }
}
```

**RULES:**
- Backend MUST bind to `127.0.0.1` — NEVER `0.0.0.0`
- Frontend ALWAYS calls `https://api.yourdomain.com` — never a raw IP or port
- `server_tokens off` removes the Nginx version from responses
- `proxy_hide_header Server` removes all backend server identity headers

---

## LAYER 1B — TRAEFIK (Preferred Reverse Proxy)

Traefik is the preferred reverse proxy for this project. It auto-discovers services via Docker labels, handles Let's Encrypt TLS automatically, and applies security middleware declaratively.
**Replace the Nginx section with this when using Traefik.**

---

### File Layout

```
traefik/
├── traefik.yml        # Static config — entrypoints, TLS, providers
├── dynamic.yml        # Dynamic config — middlewares (security headers, rate limit)
└── acme.json          # Let's Encrypt certificates (auto-generated, chmod 600)
docker-compose.yml     # Services with Traefik labels
```

---

### `traefik/traefik.yml` — Static Configuration

```yaml
# traefik/traefik.yml
global:
  checkNewVersion:    false
  sendAnonymousUsage: false

# Disable Traefik dashboard in production — NEVER expose it publicly
api:
  dashboard: false
  insecure:  false

log:
  level: WARN       # ERROR in production, DEBUG in development only

accessLog:
  filePath: "/var/log/traefik/access.log"
  format: json

# ── Entrypoints ────────────────────────────────────────────────────────
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to:        websecure
          scheme:    https
          permanent: true      # 301 redirect — HTTP always goes to HTTPS

  websecure:
    address: ":443"
    http:
      tls:
        certResolver: letsencrypt
        options:      modern   # TLS 1.2+ only

# ── Let's Encrypt auto TLS ─────────────────────────────────────────────
certificatesResolvers:
  letsencrypt:
    acme:
      email:   your-email@yourdomain.com    # change this
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web

# ── Providers — Docker labels + file-based dynamic config ──────────────
providers:
  docker:
    exposedByDefault: false      # MUST be false — explicit opt-in only
    network: proxy
  file:
    filename: /etc/traefik/dynamic.yml
    watch: true
```

---

### `traefik/dynamic.yml` — All Middlewares Defined Here

```yaml
# traefik/dynamic.yml
tls:
  options:
    modern:
      minVersion: VersionTLS12
      sniStrict: true

http:
  middlewares:

    # ── Security Headers ── applied to every service ───────────────────
    security-headers:
      headers:
        # Prevent clickjacking
        frameDeny: true
        # Prevent MIME sniffing
        contentTypeNosniff: true
        # HSTS — force HTTPS for 1 year
        forceSTSHeader:       true
        stsSeconds:           31536000
        stsIncludeSubdomains: true
        stsPreload:           true
        # Referrer policy
        referrerPolicy: "strict-origin-when-cross-origin"
        # Permissions policy
        permissionsPolicy: "camera=(), microphone=(), geolocation=(), payment=()"
        # Generate CSP in the frontend with per-response nonces or hashes. Never
        # use 'unsafe-eval'; do not add 'unsafe-inline' merely to make a build work.
        # Remove server identity headers
        customResponseHeaders:
          Server: ""
          X-Powered-By: ""
          X-AspNet-Version: ""

    # ── Rate Limiting ── 100 requests per minute per IP ────────────────
    rate-limit:
      rateLimit:
        average: 100
        burst:   50
        period:  1m
        sourceCriterion:
          ipStrategy:
            depth: 1    # use X-Forwarded-For depth 1 for real client IP

    # ── Strict Rate Limit for auth endpoints ───────────────────────────
    rate-limit-auth:
      rateLimit:
        average: 10     # only 10 login attempts per minute per IP
        burst:   5
        period:  1m

    # ── Compress responses ─────────────────────────────────────────────
    compress:
      compress:
        excludedContentTypes:
          - text/event-stream

    # ── Body size limit — reject oversized requests ────────────────────
    body-limit:
      buffering:
        maxRequestBodyBytes: 10485760   # 10 MB
        retryExpression: "IsNetworkError() && Attempts() < 2"
```

---

### `docker-compose.yml` — Full Stack with Traefik

```yaml
# docker-compose.yml
services:

  # ── Traefik — the only public entry point ────────────────────────────
  traefik:
    image: traefik:v3.7.15
    container_name: traefik
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true      # prevent privilege escalation
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro   # read-only socket
      - ./traefik/traefik.yml:/etc/traefik/traefik.yml:ro
      - ./traefik/dynamic.yml:/etc/traefik/dynamic.yml:ro
      - ./traefik/acme.json:/letsencrypt/acme.json
    networks:
      - proxy
    labels:
      - "traefik.enable=false"      # Traefik itself has no public route

  # ── Backend ───────────────────────────────────────────────────────────
  backend:
    build: ./backend
    container_name: backend
    restart: unless-stopped
    # Inside Docker: 0.0.0.0 is safe — the container network is internal
    # Traefik is the ONLY way in. No ports are published to the host.
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    env_file: ./backend/.env
    expose:
      - "8000"        # internal only — NOT published to host machine
    networks:
      - proxy
    labels:
      # Enable Traefik for this service
      - "traefik.enable=true"
      # Route: api.yourdomain.com → this service
      - "traefik.http.routers.backend.rule=Host(`api.yourdomain.com`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
      - "traefik.http.routers.backend.tls.options=modern@file"
      # Apply middlewares: security headers + rate limit + body limit + compress
      - "traefik.http.routers.backend.middlewares=security-headers@file,rate-limit@file,body-limit@file,compress@file"
      # Special rate limit for auth endpoints
      - "traefik.http.routers.backend-auth.rule=Host(`api.yourdomain.com`) && PathPrefix(`/api/v1/auth`)"
      - "traefik.http.routers.backend-auth.entrypoints=websecure"
      - "traefik.http.routers.backend-auth.tls.certresolver=letsencrypt"
      - "traefik.http.routers.backend-auth.middlewares=security-headers@file,rate-limit-auth@file"
      - "traefik.http.routers.backend-auth.priority=10"    # higher priority than the main backend router
      # Service port
      - "traefik.http.services.backend.loadbalancer.server.port=8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout:  10s
      retries:  3

  # ── Frontend (Next.js) ────────────────────────────────────────────────
  frontend:
    build: ./frontend
    container_name: frontend
    restart: unless-stopped
    env_file: ./frontend/.env.local
    expose:
      - "3000"        # internal only
    networks:
      - proxy
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`app.yourdomain.com`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
      - "traefik.http.routers.frontend.tls.options=modern@file"
      - "traefik.http.routers.frontend.middlewares=security-headers@file,compress@file"
      - "traefik.http.services.frontend.loadbalancer.server.port=3000"

networks:
  proxy:
    name:   proxy
    driver: bridge
```

---

### `docker-compose.dev.yml` — Local Development

```yaml
# docker-compose.dev.yml  — development only
# Run: docker compose -f docker-compose.dev.yml up
services:

  traefik:
    image: traefik:v3.7.15
    command:
      - "--api.insecure=true"         # dev only — exposes dashboard at :8080
      - "--providers.docker=true"
      - "--providers.docker.exposedByDefault=false"
      - "--entrypoints.web.address=:80"
      - "--log.level=DEBUG"
    ports:
      - "80:80"
      - "8080:8080"                   # Traefik dashboard — dev only
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - proxy

  backend:
    build: ./backend
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    env_file: ./backend/.env
    expose:
      - "8000"
    networks:
      - proxy
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend-dev.rule=Host(`api.localhost`)"
      - "traefik.http.routers.backend-dev.entrypoints=web"
      - "traefik.http.services.backend-dev.loadbalancer.server.port=8000"

  frontend:
    build:
      context: ./frontend
      target: dev
    env_file: ./frontend/.env.local
    expose:
      - "3000"
    networks:
      - proxy
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend-dev.rule=Host(`app.localhost`)"
      - "traefik.http.routers.frontend-dev.entrypoints=web"
      - "traefik.http.services.frontend-dev.loadbalancer.server.port=3000"

networks:
  proxy:
    name: proxy
    driver: bridge
```

---

### Setup Commands

```bash
# Production setup

# 1. Create acme.json for Let's Encrypt (MUST be chmod 600)
touch traefik/acme.json && chmod 600 traefik/acme.json

# 2. Start everything
docker compose up -d

# 3. Check Traefik logs
docker compose logs traefik -f

# 4. Verify TLS
curl -I https://api.yourdomain.com/health

# Development setup
docker compose -f docker-compose.dev.yml up -d
# Frontend: http://app.localhost
# Backend:  http://api.localhost
# Traefik dashboard: http://localhost:8080
```

---

### Traefik Security Rules

```
✅  traefik.enable=false on Traefik itself — no self-routing
✅  exposedByDefault: false — every service must opt-in explicitly
✅  Dashboard disabled in production (api.dashboard: false)
✅  TLS options set to "modern" — TLS 1.2+ only
✅  acme.json chmod 600 — only owner can read the certificates
✅  Docker socket mounted read-only (:ro)
✅  security_opt: no-new-privileges:true on Traefik container
✅  Backend has no "ports:" — only "expose:" (internal only)
✅  Auth endpoints get stricter rate-limit-auth middleware (10 req/min)
✅  All middlewares defined in dynamic.yml — not inline in labels

❌  api.insecure: true — ONLY in development docker-compose.dev.yml
❌  ports: on backend service — use expose: only
❌  exposedByDefault: true — never
❌  TLS options omitted — always set to "modern"
```

For higher-assurance production deployments, do not mount the Docker socket directly at all. Put a least-privilege Docker socket proxy in front of it (read-only access to only the endpoints Traefik needs), or use an orchestrator provider with scoped RBAC. A read-only socket can still expose highly sensitive Docker metadata and control surfaces.

---

## LAYER 2 — BACKEND BINDING (FastAPI / ASP.NET Core / Spring Boot)

### FastAPI — `main.py` server startup

```python
# ── With Traefik (Docker) ──────────────────────────────────────────────
# Inside a Docker container, 0.0.0.0 is SAFE because:
#   - The container has no published ports (uses "expose:" not "ports:")
#   - Only Traefik can reach it via the internal Docker network
# Command: uvicorn main:app --host 0.0.0.0 --port 8000

# ── Without Docker (bare metal / VM) ──────────────────────────────────
# Bind to localhost only — Nginx/Traefik runs on the same machine
# Command: uvicorn main:app --host 127.0.0.1 --port 8000

# NEVER: uvicorn main:app --host 0.0.0.0 on a bare metal server
#        without a reverse proxy — exposes the backend directly to the internet
```

### ASP.NET Core — `appsettings.json`

```json
{
  "Kestrel": {
    "Endpoints": {
      "Http": {
        "Url": "http://127.0.0.1:5000"
      }
    }
  }
}
```

### Spring Boot — `application.properties`

```properties
server.address=127.0.0.1
server.port=8080
```

**RULE: Every backend binds to `127.0.0.1` only. The reverse proxy is the only public entry point.**

---

## LAYER 3 — AUTHENTICATION, CSRF, AND OPTIONAL SERVER-TO-SERVER SIGNING

Never put a shared secret in browser JavaScript, a mobile binary, `NEXT_PUBLIC_*`, `VITE_*`, Angular environment files, or Flutter assets. Client-side HMAC does not prove that a request came from the genuine app because every user can extract the key.

Use these controls instead:

- Web with a BFF (recommended): browser receives an opaque `Secure; HttpOnly; SameSite=Lax` session cookie. The BFF stores or refreshes upstream tokens and calls the backend over a private network.
- Pure SPA: keep the short-lived access token in memory; keep the rotating refresh token in a `Secure; HttpOnly; SameSite` cookie set by the API. Protect cookie-authenticated state changes with CSRF tokens and strict Origin/Referer validation.
- Mobile/desktop: use OAuth 2.1 Authorization Code with PKCE through the system browser; store tokens only in platform secure storage.
- Every backend: validate issuer, audience, signature, expiry, not-before, and authorization claims. Rate-limit authentication endpoints and rotate refresh tokens with reuse detection.

### Optional HMAC — trusted server-to-server calls only

Use HMAC only when both callers are trusted servers or for verified webhooks. Prefer mTLS or workload identity when the platform provides them. Canonicalize and sign all request components:

```
version + key_id + timestamp + nonce + method + normalized_path
+ canonical_query + SHA256(raw_body)
```

The verifier MUST:

1. Select the key by `key_id` and support overlapping keys during rotation.
2. Reject timestamps outside a short clock-skew window.
3. atomically store the nonce in Redis or another shared TTL store and reject reuse.
4. Include the canonical query string and raw-body hash; never sign decoded/re-serialized JSON.
5. Compare MACs in constant time and return a generic authentication error.
6. Run only on explicitly configured internal/webhook routes; never require HMAC from public browser or mobile clients.

TLS remains mandatory. HMAC is not encryption and does not replace user authentication, authorization, CSRF protection, or replay storage.

---

## LAYER 4 — RESPONSE SANITIZATION (Backend)

The backend must NEVER return these fields in any response, ever:

```
password            hashed_password      salt
secret_key          api_key              private_key
credit_card         cvv                  ssn
internal_ip         server_version       stack_trace (in production)
database_url        connection_string
```

### FastAPI — Global exception handler (no stack traces in production)

```python
# app/core/exceptions.py — add this to main.py

from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import settings


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    In production: return a generic error — no stack trace, no server info.
    In development: include the error detail for debugging.
    """
    if settings.PRODUCTION:
        return JSONResponse(
            status_code=500,
            content={
                "detail":     "An internal error occurred.",
                "request_id": getattr(request.state, "request_id", None),
            },
        )
    # Development only — show the actual error
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "request_id": getattr(request.state, "request_id", None)},
    )


# Register in create_application():
# application.add_exception_handler(Exception, generic_exception_handler)
```

### Remove server identity from all responses

```python
# app/middleware/security_headers.py — already in your file
# ADD these two lines to the _HEADERS dict:

"Server":       "",   # overwrite — prevents "uvicorn" from appearing
"X-Powered-By": "",   # remove — some frameworks add this automatically
```

---

## LAYER 5 — FRONTEND SECURITY (Universal — All Frameworks)

These rules apply whether you use Next.js, React, or Angular.

### Rule: Frontend NEVER calls a raw backend IP or port

```typescript
// ❌ NEVER — exposes backend server in developer tools
const res = await fetch("http://1.2.3.4:8000/api/v1/users");
const res = await fetch("http://localhost:8000/api/v1/users");

// ✅ ALWAYS — only the proxy domain is visible
const res = await fetch("https://api.yourdomain.com/api/v1/users");
```

This means:
- Next.js browser code calls same-origin `/api/backend`; only server-side `BACKEND_API_URL` points upstream.
- Angular `environment.apiUrl` and React `VITE_API_URL` use the HTTPS proxy origin.

### React (Vite) — HTTP client setup

```typescript
// src/api/client.ts  (React without Next.js)
import axios from "axios";
import { tokenStore } from "./token-store";   // ← in-memory store, NOT localStorage

const apiClient = axios.create({
  baseURL:          import.meta.env.VITE_API_URL,
  timeout:          15_000,
  withCredentials:  true,   // send httpOnly cookies with every request
  headers: {
    "Content-Type": "application/json",
    Accept:         "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = tokenStore.get();   // ← ALWAYS in-memory, NEVER localStorage
  if (token) config.headers.Authorization = `Bearer ${token}`;

  return config;
});

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) window.location.href = "/login";
    const msg = err.response?.data?.detail ?? err.response?.data?.message ?? "Error occurred.";
    return Promise.reject(new Error(typeof msg === "string" ? msg : "Error occurred."));
  }
);

export default apiClient;
```

### Angular — environment files

```typescript
// src/environments/environment.ts  (development)
export const environment = {
  production:         false,
  apiUrl:             "http://localhost:8080/api/v1",   // dev proxy
};

// src/environments/environment.prod.ts  (production)
export const environment = {
  production:         true,
  apiUrl:             "https://api.yourdomain.com/api/v1",  // proxy URL — never raw IP
};
```

### Angular — Auth interceptor

```typescript
// src/app/core/interceptors/auth.interceptor.ts
import { Injectable } from "@angular/core";
import { HttpInterceptor, HttpRequest, HttpHandler } from "@angular/common/http";
import { AuthService } from "../services/auth.service";

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private auth: AuthService) {}

  intercept(req: HttpRequest<unknown>, next: HttpHandler) {
    const token = this.auth.getToken();
    if (!token) return next.handle(req);
    return next.handle(req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }));
  }
}
```

---

## LAYER 6 — TOKEN SECURITY

### Where to store tokens

```
1. httpOnly Cookie (most secure)
   → JavaScript CANNOT read it
   → Automatically sent with every request
   → Safe from XSS attacks
   → Use with: Auth.js, ASP.NET Core cookie auth, or another server-managed session

2. In-memory variable (second best)
   → Lost on page refresh
   → Safe from XSS (not in DOM or storage)
   → Use with: React/Angular SPA — store in module-level variable

3. sessionStorage/localStorage (prohibited for credentials)
   → Any successful XSS can read and exfiltrate the token
   → Use storage only for non-sensitive preferences
```

### Next.js — Auth.js uses HttpOnly cookies ✅

```typescript
// lib/auth/config.ts — already in your file
// session: { strategy: "jwt" }  ← Auth.js stores an encrypted JWT in an HttpOnly cookie
// Do not copy the upstream accessToken into the browser-visible session callback.
```

### React / Angular — In-memory token store

```typescript
// src/api/token-store.ts  (React or Angular — universal)
// Token lives in memory only — never written to localStorage or sessionStorage

let _accessToken: string | null = null;

export const tokenStore = {
  set:   (token: string) => { _accessToken = token; },
  get:   ()              => _accessToken,
  clear: ()              => { _accessToken = null; },
};

// Usage: tokenStore.set(token) after login
//        tokenStore.get()  in Axios interceptor
//        tokenStore.clear() on logout
```

---

## LAYER 7 — CORS CONFIGURATION (Backend)

CORS must ONLY allow your known frontend origins. Never use `*` in production.

### FastAPI

```python
# app/core/config.py
BACKEND_CORS_ORIGINS: list[str] = []
# .env: BACKEND_CORS_ORIGINS=["https://app.yourdomain.com","https://admin.yourdomain.com"]

# app/middleware/__init__.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,   # NEVER ["*"] in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-CSRF-Token"],
    expose_headers=["X-Request-ID"],
    max_age=3600,
)
```

### ASP.NET Core — `Program.cs`

```csharp
builder.Services.AddCors(options => {
    options.AddPolicy("AllowFrontend", policy => {
        policy.WithOrigins(builder.Configuration.GetSection("AllowedOrigins").Get<string[]>()!)
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials();
    });
});
app.UseCors("AllowFrontend");
```

### Spring Boot — `SecurityConfig.java`

```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://app.yourdomain.com"));
    config.setAllowedMethods(List.of("GET","POST","PUT","PATCH","DELETE","OPTIONS"));
    config.setAllowedHeaders(List.of("Authorization","Content-Type","X-CSRF-Token","X-Request-ID"));
    config.setAllowCredentials(true);
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);
    return source;
}
```

---

## LAYER 8 — COMPLETE SECURITY HEADERS

Both `next.config.ts` (frontend) and **Traefik `dynamic.yml`** (backend proxy) must set ALL of these. Traefik's `security-headers` middleware covers the proxy side — `next.config.ts` covers the frontend side.

```
Header                          Value                                   Protects Against
─────────────────────────────────────────────────────────────────────────────────────────
Strict-Transport-Security       max-age=31536000; includeSubDomains    Downgrade to HTTP
X-Frame-Options                 DENY                                    Clickjacking
X-Content-Type-Options          nosniff                                 MIME sniffing
Referrer-Policy                 strict-origin-when-cross-origin         Data leakage
Permissions-Policy              camera=(), microphone=(), geolocation() Feature abuse
Content-Security-Policy         default-src 'self'; ...                 XSS injection
Cache-Control                   no-store, no-cache                      Cached sensitive data
```

---

## LAYER 9 — ENVIRONMENT VARIABLES (Full Security Setup)

### Backend `.env`

```bash
# ── App ───────────────────────────────────────────────────────────────
PRODUCTION=true
PROJECT_NAME=YourApp

# ── Database ──────────────────────────────────────────────────────────
POSTGRES_SERVER=127.0.0.1       # always localhost — never expose DB externally
POSTGRES_USER=appuser
POSTGRES_PASSWORD=strong-random-password-here
POSTGRES_DB=appdb

# ── Auth ──────────────────────────────────────────────────────────────
SECRET_KEY=generate-with-openssl-rand-hex-32
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# ── Security ──────────────────────────────────────────────────────────
# Optional, trusted server-to-server/webhook signing only; never expose to clients:
# INTERNAL_SIGNING_KEYS_JSON={"key-2026-10":"base64-secret"}
BACKEND_CORS_ORIGINS=["https://app.yourdomain.com","https://admin.yourdomain.com"]
ALLOWED_HOSTS=["api.yourdomain.com"]
RATE_LIMIT_PER_MINUTE=60
MAX_BODY_SIZE_BYTES=10485760    # 10 MB
IP_BLOCKLIST=[]
```

### Frontend `.env.local` (Next.js)

```bash
# Browser calls the same-origin BFF only. This value is server-only.
BACKEND_API_URL=http://backend:8000/api/v1

# Backend type for response normalization
NEXT_PUBLIC_BACKEND_TYPE=fastapi

# Auth.js
AUTH_URL=https://app.yourdomain.com
AUTH_SECRET=generate-with-openssl-rand-base64-32
```

### React `.env`

```bash
VITE_API_URL=https://api.yourdomain.com/api/v1
```

### Angular `environment.prod.ts`

```typescript
export const environment = {
  production:    true,
  apiUrl:        "https://api.yourdomain.com/api/v1",
};
```

---

## LAYER 10 — Docker Compose (Traefik Setup)

> Full Traefik `docker-compose.yml` is in **LAYER 1B** above. That is the canonical setup.

Quick reference for the network model:

```
Internet (port 80/443)
       │
       ▼
   Traefik container          ← only container with published ports
       │  Docker internal network "proxy"
       ├──▶  backend  (expose: 8000, no ports:)
       └──▶  frontend (expose: 3000, no ports:)

Backend IP in browser dev tools: api.yourdomain.com   ← Traefik domain, never raw IP
Backend container IP:            10.x.x.x:8000        ← invisible, internal Docker network only
```

---

## COMPLETE SECURITY FLOW — REQUEST LIFECYCLE

```
User submits form (any frontend: Next.js / React / Angular)
        │
        ▼
  [Frontend] request layer runs:
    ① Next.js: call same-origin BFF with an HttpOnly session cookie; or
       SPA: attach a short-lived in-memory access token
    ② For cookie-authenticated mutations, attach the CSRF token
    ③ Set Content-Type: application/json
        │
        │  HTTPS (TLS 1.3) — encrypted in transit
        ▼
  [Traefik Reverse Proxy] receives HTTPS request:
    ⑤ Terminate TLS (Let's Encrypt cert)
    ⑥ Check rate limit (100 req/min per IP, 10/min for /auth) → 429 if exceeded
    ⑦ Check body size (10MB max) → 413 if too large
    ⑧ Strip Server and X-Powered-By headers
    ⑨ Add security headers (HSTS, X-Frame, CSP, etc.) via dynamic.yml middleware
    ⑩ Forward to backend container on internal Docker network (invisible externally)
        │
        ▼
  [Backend] receives request:
    ⑪ TrustedHostMiddleware → valid Host header?
    ⑫ RequestIDMiddleware   → stamp X-Request-ID
    ⑬ RequestLoggingMiddleware → log request
    ⑭ Authentication/CSRF validation → reject invalid or replayed credentials
    ⑮ Distributed rate limiter → per account/IP policy
    ⑯ IP reputation/block policy → blocked source?
    ⑰ SecurityHeadersMiddleware → add response headers
    ⑱ RequestSizeLimitMiddleware → body size check
    ⑲ CORSMiddleware        → allowed origin?
    ⑳ Route Handler         → authorize and process request
    ㉑ Response schema       → strips all sensitive fields
        │
        │  HTTPS (TLS 1.3) — response encrypted in transit
        ▼
  [Traefik] adds final security headers → sends to browser
        │
        ▼
  [Browser developer tools show]:
    URL: https://api.yourdomain.com/api/v1/users  ← proxy domain only
    NO: raw IP, NO: port, NO: server identity, NO: stack traces
```

---

## SECURITY CHECKLIST — NEVER DEPLOY WITHOUT THESE

```
Infrastructure (Traefik):
  [ ] Only Traefik container has "ports:" — backend/frontend use "expose:" only
  [ ] traefik.enable=false on the Traefik container itself
  [ ] exposedByDefault: false in traefik.yml
  [ ] api.dashboard: false in production traefik.yml
  [ ] TLS options set to "modern" (minVersion: VersionTLS12)
  [ ] acme.json created with chmod 600
  [ ] Docker socket mounted read-only (:ro)
  [ ] security_opt: no-new-privileges:true on Traefik container
  [ ] Auth routes use rate-limit-auth middleware (10 req/min max)
  [ ] All middlewares defined in dynamic.yml — not inline in Docker labels
  [ ] All environment secrets use openssl rand — never hand-typed weak secrets

Request/Response Security:
  [ ] All API calls use HTTPS — zero plain HTTP in production
  [ ] HSTS header set (max-age=31536000) — forces HTTPS in browsers
  [ ] Cookie-authenticated mutations enforce CSRF + Origin checks
  [ ] Refresh tokens rotate and reuse is detected
  [ ] Optional HMAC is limited to trusted server/webhook routes and uses nonce replay storage
  [ ] No sensitive fields (password, hashed_password, keys) in any API response
  [ ] No stack traces in production error responses

Frontend:
  [ ] API URL is proxy domain — never raw IP or port
  [ ] BACKEND_API_URL is server-only for Next.js; VITE_API_URL / environment.apiUrl use the proxy URL
  [ ] Tokens stored in httpOnly cookies (Next.js) or in-memory (React/Angular)
  [ ] No tokens in localStorage
  [ ] All security headers set in next.config.ts / index.html meta

Backend:
  [ ] CORS allow_origins = explicit list — never ["*"] in production
  [ ] Rate limiting active (nginx + backend)
  [ ] Input validation on every endpoint (Pydantic / Data Annotations / Bean Validation)
  [ ] No shared signing secret exists in a browser bundle or mobile binary
  [ ] PRODUCTION=true disables /docs and /openapi.json (FastAPI)

Secrets:
  [ ] .env never committed to git
  [ ] .env.example committed with empty values
  [ ] All secrets generated with: openssl rand -hex 32
  [ ] Server-to-server signing keys, when used, are stored only in a secret manager/server env
```

---

## ABSOLUTE PROHIBITIONS

```
✗  Backend binds to 0.0.0.0 on bare metal without a reverse proxy — always 127.0.0.1 on bare metal
     (Inside Docker with Traefik: 0.0.0.0 is safe — container has no published ports)
✗  Frontend API URL is a raw IP (e.g. http://1.2.3.4:8000) — use proxy domain
✗  CORS allow_origins = ["*"] in production
✗  Token stored in localStorage — use httpOnly cookies or in-memory
✗  Stack traces or server details in error responses (production)
✗  Secrets hardcoded in source files — always from env vars
✗  Any shared secret in browser JavaScript, public env variables, or mobile assets
✗  HTTP allowed in production — HTTPS only, redirect HTTP to HTTPS
✗  TLS 1.0 or 1.1 — TLS 1.2+ only
✗  Treating HMAC as user authentication or requiring it from browser/mobile clients
✗  password / hashed_password in any Pydantic Read schema or API response
✗  server_tokens on in Nginx — always off
✗  /docs or /openapi.json enabled in production (FastAPI)
```

---

*Applies to: Next.js · React · Angular (any frontend)*
*Applies to: FastAPI · ASP.NET Core · Spring Boot (any backend)*
*Security Stack: TLS 1.2/1.3 · HttpOnly sessions / OAuth 2.1 PKCE · CSRF protection · reverse proxy · HSTS · CSP · optional server-only HMAC*

---

## Copyright

© 2026 **Udhayaboopathi V**. Released under the repository's MIT License.

- Author:  Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub:  [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
