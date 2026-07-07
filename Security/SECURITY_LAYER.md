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
- Data NEVER travels as plain text — not in requests, not in responses
- The backend IP/port is NEVER visible in browser developer tools
- Every request is authenticated AND verified for integrity
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
              │  127.0.0.1:8000 │   ← Bound to localhost — NOT 0.0.0.0
              └─────────────────┘
```

**Why this matters:**
- Browser developer tools show `api.domain.com` — never `1.2.3.4:8000`
- Backend server is invisible to the internet — it cannot be attacked directly
- TLS is terminated at the proxy — backend handles plain HTTP internally (safe — localhost only)
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
    more_clear_headers Server;

    # Security headers
    add_header X-Frame-Options           "DENY"                              always;
    add_header X-Content-Type-Options    "nosniff"                           always;
    add_header Referrer-Policy           "strict-origin-when-cross-origin"   always;
    add_header Permissions-Policy        "camera=(), microphone=(), geolocation=()" always;
    add_header X-XSS-Protection          "1; mode=block"                     always;

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

# ── TLS options — modern only (no TLS 1.0 or 1.1) ─────────────────────
tls:
  options:
    modern:
      minVersion: VersionTLS12
      cipherSuites:
        - TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256
        - TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
      sniStrict: true

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
http:
  middlewares:

    # ── Security Headers ── applied to every service ───────────────────
    security-headers:
      headers:
        # Prevent clickjacking
        frameDeny: true
        # Prevent MIME sniffing
        contentTypeNosniff: true
        # XSS filter (legacy browsers)
        browserXssFilter: true
        # HSTS — force HTTPS for 1 year
        forceSTSHeader:       true
        stsSeconds:           31536000
        stsIncludeSubdomains: true
        stsPreload:           true
        # Referrer policy
        referrerPolicy: "strict-origin-when-cross-origin"
        # Permissions policy
        permissionsPolicy: "camera=(), microphone=(), geolocation=(), payment=()"
        # Content Security Policy — single line (YAML > folds newlines to spaces, valid but unclear)
        # Write as explicit single line to avoid YAML scalar confusion:
        contentSecurityPolicy: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data: https:; font-src 'self'; connect-src 'self' https://api.yourdomain.com; frame-ancestors 'none';"
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
    image: traefik:v3.0
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
      - traefik-certs:/letsencrypt
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
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
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

volumes:
  traefik-certs:
    name: traefik-certs

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
    image: traefik:v3.0
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
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
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

---

## LAYER 2 — BACKEND BINDING (FastAPI / ASP.NET Core / Spring Boot)

### FastAPI — `main.py` server startup

```python
# ── With Traefik (Docker) ──────────────────────────────────────────────
# Inside a Docker container, 0.0.0.0 is SAFE because:
#   - The container has no published ports (uses "expose:" not "ports:")
#   - Only Traefik can reach it via the internal Docker network
# Command: uvicorn app.main:app --host 0.0.0.0 --port 8000

# ── Without Docker (bare metal / VM) ──────────────────────────────────
# Bind to localhost only — Nginx/Traefik runs on the same machine
# Command: uvicorn app.main:app --host 127.0.0.1 --port 8000

# NEVER: uvicorn app.main:app --host 0.0.0.0 on a bare metal server
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

## LAYER 3 — REQUEST SIGNING (HMAC-SHA256)

Every API request carries a signature that proves it came from your app and has not been tampered with. This prevents request forgery and replay attacks.

### How it works

```
Frontend signs every request:
  signature = HMAC-SHA256( SIGNING_SECRET, timestamp + method + path + body )

Frontend sends headers:
  X-Timestamp: 1720335600000     (Unix ms — expires in 5 min)
  X-Signature: abc123def456...   (hex HMAC)

Backend verifies:
  1. Recompute the same HMAC
  2. Compare — if different → reject 401
  3. Check timestamp — if > 5 min old → reject 401 (replay attack blocked)
```

### ⚠️ Important Limitation — Signing Secret in Browser Apps

`NEXT_PUBLIC_*` variables are bundled into the client-side JavaScript bundle. Anyone can open DevTools → Sources and read them. This means the signing secret is technically not secret to a determined attacker.

**What request signing still protects against:**
- Automated scripts and simple bots that don't inspect your JS bundle
- Requests from tools like Postman/curl without the signing logic
- Basic API enumeration attacks

**What it does NOT protect against:**
- A determined attacker who reads your JS bundle and extracts the secret

**The correct solution for maximum security — Server-Side Signing Proxy:**

```
Browser → Next.js API Route (server-side, secret never exposed) → Backend
```

For Next.js, requests from the browser go to a Next.js API route, which adds the signature server-side (where the secret is safe), then forwards to the backend. The signing secret lives only on the server — never in the browser bundle.

For pure React/Angular SPAs without a server layer, client-side signing is "defense-in-depth" — not a cryptographic guarantee. Accept this trade-off knowingly.

---

### Frontend — Universal signing utility (works in Next.js, React, Angular)

```typescript
// lib/api/signing.ts  (works in any TypeScript/JavaScript frontend)

// Next.js: use a server-side env var (no NEXT_PUBLIC_ prefix) in API routes
// React/Angular: this IS in the client bundle — see limitation note above
const SIGNING_SECRET =
  // Next.js server-side (API routes, Server Actions — secret is safe here)
  process.env.REQUEST_SIGNING_SECRET
  // Next.js client-side / React / Angular (in browser bundle — limited security)
  ?? process.env.NEXT_PUBLIC_REQUEST_SIGNING_SECRET
  ?? (typeof window !== "undefined"
    ? (window as { __APP_CONFIG__?: { signingSecret?: string } }).__APP_CONFIG__?.signingSecret
    : "")
  ?? "";

/**
 * Compute HMAC-SHA256 using the Web Crypto API (available in all modern browsers
 * and Node.js 18+, Next.js Edge Runtime, and any modern Angular/React build).
 * No external libraries required.
 */
async function hmacSHA256(secret: string, message: string): Promise<string> {
  const enc     = new TextEncoder();
  const keyData = enc.encode(secret);
  const msgData = enc.encode(message);

  const cryptoKey = await crypto.subtle.importKey(
    "raw", keyData,
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );

  const signature = await crypto.subtle.sign("HMAC", cryptoKey, msgData);
  return Array.from(new Uint8Array(signature))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/**
 * Build the signing headers for a request.
 * Call this before every outgoing API request.
 */
export async function buildSignatureHeaders(
  method:  string,
  path:    string,
  body:    string = "",
): Promise<Record<string, string>> {
  const timestamp = Date.now().toString();
  const message   = `${timestamp}${method.toUpperCase()}${path}${body}`;
  const signature = await hmacSHA256(SIGNING_SECRET, message);

  return {
    "X-Timestamp": timestamp,
    "X-Signature": signature,
  };
}
```

### Frontend — Axios interceptor integration

```typescript
// lib/api/client.ts  — add signing to the existing request interceptor

import { buildSignatureHeaders } from "./signing";

apiClient.interceptors.request.use(
  async (config) => {
    // 1. Attach auth token
    const session = await getSession();
    if (session?.accessToken) {
      config.headers.Authorization = `Bearer ${session.accessToken}`;
    }

    // 2. Sign the request
    const url    = config.url ?? "";
    const method = config.method ?? "GET";
    const body   = config.data ? JSON.stringify(config.data) : "";
    const path   = url.startsWith("http") ? new URL(url).pathname : url;

    const sigHeaders = await buildSignatureHeaders(method, path, body);
    config.headers["X-Timestamp"] = sigHeaders["X-Timestamp"];
    config.headers["X-Signature"] = sigHeaders["X-Signature"];

    return config;
  },
  (err) => Promise.reject(err)
);
```

### Angular — HTTP Interceptor (equivalent)

```typescript
// src/app/core/interceptors/signing.interceptor.ts  (Angular)
import { Injectable } from "@angular/core";
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from "@angular/common/http";
import { Observable, from, switchMap } from "rxjs";
import { buildSignatureHeaders } from "../utils/signing";

@Injectable()
export class SigningInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const body = req.body ? JSON.stringify(req.body) : "";
    const path = new URL(req.url).pathname;

    return from(buildSignatureHeaders(req.method, path, body)).pipe(
      switchMap((sigHeaders) => {
        const signed = req.clone({
          setHeaders: {
            "X-Timestamp": sigHeaders["X-Timestamp"],
            "X-Signature": sigHeaders["X-Signature"],
          },
        });
        return next.handle(signed);
      })
    );
  }
}
```

### Backend — Request Signature Verification

#### FastAPI — `app/core/middleware/request_signing.py`

```python
# app/core/middleware/request_signing.py
import hashlib
import hmac
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from app.config import settings

# Paths that do NOT require signing (login must be exempt so the frontend
# can get a session before signing is active)
_EXEMPT_PATHS = frozenset({"/api/v1/auth/login", "/api/v1/auth/register", "/health", "/metrics"})
_MAX_AGE_SECONDS = 300  # 5 minutes — blocks replay attacks


class RequestSigningMiddleware(BaseHTTPMiddleware):
    """
    Validates X-Timestamp and X-Signature headers on every request.
    Rejects requests that:
      - Are missing the headers
      - Have a timestamp older than 5 minutes (replay attack)
      - Have an invalid HMAC signature (tampered or forged request)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in _EXEMPT_PATHS:
            return await call_next(request)

        timestamp = request.headers.get("X-Timestamp")
        signature = request.headers.get("X-Signature")

        if not timestamp or not signature:
            return JSONResponse(status_code=401, content={"detail": "Missing signature headers."})

        # Replay attack prevention — reject requests older than 5 minutes
        try:
            ts = int(timestamp)
            age = abs(time.time() - ts / 1000)
            if age > _MAX_AGE_SECONDS:
                return JSONResponse(status_code=401, content={"detail": "Request expired."})
        except ValueError:
            return JSONResponse(status_code=401, content={"detail": "Invalid timestamp."})

        # Read body for signing (must be re-consumed via request.body())
        body = await request.body()
        body_str = body.decode("utf-8") if body else ""

        # Recompute the expected signature
        method  = request.method.upper()
        path    = request.url.path
        message = f"{timestamp}{method}{path}{body_str}"

        expected = hmac.new(
            settings.REQUEST_SIGNING_SECRET.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Constant-time comparison prevents timing attacks
        if not hmac.compare_digest(expected, signature):
            return JSONResponse(status_code=401, content={"detail": "Invalid request signature."})

        return await call_next(request)
```

Add to `app/core/middleware/__init__.py` registration:

```python
# Add to register_middleware() — AFTER RequestIDMiddleware, BEFORE RateLimitMiddleware
app.add_middleware(RequestSigningMiddleware)    # ④ (shift existing numbers down)
```

Add to `app/config.py`:

```python
REQUEST_SIGNING_SECRET: str   # must be set in .env — no default
```

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
from app.config import settings


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
# app/core/middleware/security_headers.py — already in your file
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
- `NEXT_PUBLIC_API_URL` = `https://api.yourdomain.com` (proxy URL)
- `apiUrl` in Angular `environment.ts` = `https://api.yourdomain.com`
- `REACT_APP_API_URL` in React `.env` = `https://api.yourdomain.com`

### React (`create-react-app` / Vite) — HTTP client setup

```typescript
// src/api/client.ts  (React without Next.js)
import axios from "axios";
import { buildSignatureHeaders } from "./signing";
import { tokenStore } from "./token-store";   // ← in-memory store, NOT localStorage

const apiClient = axios.create({
  baseURL:          process.env.REACT_APP_API_URL ?? import.meta.env.VITE_API_URL,
  timeout:          15_000,
  withCredentials:  true,   // send httpOnly cookies with every request
  headers: {
    "Content-Type": "application/json",
    Accept:         "application/json",
  },
});

apiClient.interceptors.request.use(async (config) => {
  const token = tokenStore.get();   // ← ALWAYS in-memory, NEVER localStorage
  if (token) config.headers.Authorization = `Bearer ${token}`;

  const path   = config.url?.startsWith("http") ? new URL(config.url!).pathname : config.url ?? "";
  const body   = config.data ? JSON.stringify(config.data) : "";
  const sigHdr = await buildSignatureHeaders(config.method ?? "GET", path, body);
  config.headers["X-Timestamp"] = sigHdr["X-Timestamp"];
  config.headers["X-Signature"] = sigHdr["X-Signature"];

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
  signingSecret:      "dev-signing-secret-change-in-prod",
};

// src/environments/environment.prod.ts  (production)
export const environment = {
  production:         true,
  apiUrl:             "https://api.yourdomain.com/api/v1",  // proxy URL — never raw IP
  signingSecret:      "",   // injected at build time — never hardcoded
};
```

### Angular — Auth + Signing interceptors

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

### Where to store tokens (most secure to least secure)

```
1. httpOnly Cookie (most secure)
   → JavaScript CANNOT read it
   → Automatically sent with every request
   → Safe from XSS attacks
   → Use with: next-auth v5, ASP.NET Core cookie auth

2. In-memory variable (second best)
   → Lost on page refresh
   → Safe from XSS (not in DOM or storage)
   → Use with: React/Angular SPA — store in module-level variable

3. sessionStorage (acceptable)
   → Cleared when tab closes
   → Vulnerable to XSS — any script on the page can read it

4. localStorage (avoid for tokens)
   → Persists indefinitely
   → Vulnerable to XSS
   → Only use for non-sensitive preferences
```

### Next.js — next-auth automatically uses httpOnly cookies ✅

```typescript
// lib/auth/config.ts — already in your file
// session: { strategy: "jwt" }  ← next-auth stores the JWT in httpOnly cookie
// The browser NEVER has direct access to the token via JavaScript
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
# app/config.py
BACKEND_CORS_ORIGINS: list[str] = []
# .env: BACKEND_CORS_ORIGINS=["https://app.yourdomain.com","https://admin.yourdomain.com"]

# app/core/middleware/__init__.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,   # NEVER ["*"] in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Timestamp", "X-Signature"],
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
    config.setAllowedHeaders(List.of("Authorization","Content-Type","X-Timestamp","X-Signature","X-Request-ID"));
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
X-XSS-Protection                1; mode=block                           Reflected XSS
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
REQUEST_SIGNING_SECRET=generate-with-openssl-rand-hex-32   # must match frontend
BACKEND_CORS_ORIGINS=["https://app.yourdomain.com","https://admin.yourdomain.com"]
ALLOWED_HOSTS=["api.yourdomain.com"]
RATE_LIMIT_PER_MINUTE=60
MAX_BODY_SIZE_BYTES=10485760    # 10 MB
IP_BLOCKLIST=[]
```

### Frontend `.env.local` (Next.js)

```bash
# Backend — proxy URL only — NEVER a raw IP
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1

# Backend type for response normalization
NEXT_PUBLIC_BACKEND_TYPE=fastapi

# next-auth
NEXTAUTH_URL=https://app.yourdomain.com
NEXTAUTH_SECRET=generate-with-openssl-rand-base64-32

# Request signing — MUST match REQUEST_SIGNING_SECRET in backend .env
NEXT_PUBLIC_REQUEST_SIGNING_SECRET=same-value-as-backend-signing-secret
```

### React `.env`

```bash
REACT_APP_API_URL=https://api.yourdomain.com/api/v1
REACT_APP_SIGNING_SECRET=same-value-as-backend-signing-secret
```

### Angular `environment.prod.ts`

```typescript
export const environment = {
  production:    true,
  apiUrl:        "https://api.yourdomain.com/api/v1",
  signingSecret: "${SIGNING_SECRET}",   // injected by CI/CD at build time
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
  [Frontend] Axios/HttpClient interceptor runs:
    ① Attach Authorization: Bearer {token}
    ② Generate X-Timestamp = Date.now()
    ③ Compute X-Signature = HMAC-SHA256(secret, timestamp+method+path+body)
    ④ Set Content-Type: application/json
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
    ⑭ RequestSigningMiddleware →
         - timestamp present? not expired (< 5 min)?
         - recompute HMAC, compare_digest → reject 401 if no match
    ⑮ RateLimitMiddleware   → per-IP sliding window
    ⑯ IPBlocklistMiddleware → blocked IP?
    ⑰ SecurityHeadersMiddleware → add response headers
    ⑱ RequestSizeLimitMiddleware → body size check
    ⑲ CORSMiddleware        → allowed origin?
    ⑳ Route Handler         → process request
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
  [ ] Every request is signed with HMAC-SHA256 (X-Timestamp + X-Signature)
  [ ] Backend verifies signature on every non-exempt endpoint
  [ ] Timestamp check prevents replay attacks (> 5 min = reject)
  [ ] No sensitive fields (password, hashed_password, keys) in any API response
  [ ] No stack traces in production error responses

Frontend:
  [ ] API URL is proxy domain — never raw IP or port
  [ ] NEXT_PUBLIC_API_URL / REACT_APP_API_URL / environment.apiUrl = proxy URL
  [ ] Tokens stored in httpOnly cookies (Next.js) or in-memory (React/Angular)
  [ ] No tokens in localStorage
  [ ] All security headers set in next.config.ts / index.html meta

Backend:
  [ ] CORS allow_origins = explicit list — never ["*"] in production
  [ ] Rate limiting active (nginx + backend)
  [ ] Input validation on every endpoint (Pydantic / Data Annotations / Bean Validation)
  [ ] REQUEST_SIGNING_SECRET set and matches frontend signing secret
  [ ] PRODUCTION=true disables /docs and /openapi.json (FastAPI)

Secrets:
  [ ] .env never committed to git
  [ ] .env.example committed with empty values
  [ ] All secrets generated with: openssl rand -hex 32
  [ ] REQUEST_SIGNING_SECRET is same value in backend .env and frontend .env
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
✗  Same signing secret across dev/staging/production environments
✗  HTTP allowed in production — HTTPS only, redirect HTTP to HTTPS
✗  TLS 1.0 or 1.1 — TLS 1.2+ only
✗  Skipping signature verification on any authenticated endpoint
✗  X-Timestamp older than 5 minutes accepted — always check expiry
✗  password / hashed_password in any Pydantic Read schema or API response
✗  server_tokens on in Nginx — always off
✗  /docs or /openapi.json enabled in production (FastAPI)
```

---

*Applies to: Next.js · React · Angular (any frontend)*
*Applies to: FastAPI · ASP.NET Core · Spring Boot (any backend)*
*Security Stack: TLS 1.3 · HMAC-SHA256 signing · httpOnly cookies · Nginx reverse proxy · HSTS · CSP*

---

## Copyright

© 2026 **Udhayaboopathi V**. All rights reserved.

- Author:  Udhayaboopathi V
- Website: [udhayaboopathi.tech](https://udhayaboopathi.tech)
- GitHub:  [github.com/Udhayaboopathi](https://github.com/Udhayaboopathi)
