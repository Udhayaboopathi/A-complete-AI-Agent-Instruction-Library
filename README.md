<div align="center">

<!-- ANIMATED TYPING HEADER -->
<a href="https://github.com/Udhayaboopathi">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=32&duration=2800&pause=800&color=00F5FF&center=true&vCenter=true&width=900&height=80&lines=AI+Agent+Prompt+Library;Make+Your+AI+Follow+YOUR+Architecture;Enterprise+Code.+Every+Time.+No+Drift." alt="Typing SVG" />
</a>

<br/>

<!-- SUBTITLE -->
### 🧠 A strict instruction library that forces any AI agent to build production-grade code - your way, every time.

<br/>

<!-- BADGES -->
![Files](https://img.shields.io/badge/Instruction_Files-11-00F5FF?style=for-the-badge&logo=markdown&logoColor=white)
![Backends](https://img.shields.io/badge/Backends-4-39FF14?style=for-the-badge&logo=serverless&logoColor=white)
![Frontends](https://img.shields.io/badge/Frontends-4-FF00FF?style=for-the-badge&logo=react&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

<!-- TECH SHIELDS -->
<p>
<img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/Django-092E20?style=flat-square&logo=django&logoColor=white"/>
<img src="https://img.shields.io/badge/.NET-512BD4?style=flat-square&logo=dotnet&logoColor=white"/>
<img src="https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white"/>
<img src="https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=nextdotjs&logoColor=white"/>
<img src="https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black"/>
<img src="https://img.shields.io/badge/Angular-DD0031?style=flat-square&logo=angular&logoColor=white"/>
<img src="https://img.shields.io/badge/Flutter-02569B?style=flat-square&logo=flutter&logoColor=white"/>
<img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white"/>
<img src="https://img.shields.io/badge/Traefik-24A1C1?style=flat-square&logo=traefikproxy&logoColor=white"/>
</p>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>

</div>

## 🎯 The Problem

You ask your AI agent to *"build a user feature"*…

- 🤡 It invents its own folder structure
- 🌀 Next feature = completely different pattern
- 🔓 Security becomes an afterthought
- 🍝 Your codebase turns into spaghetti

**AI agents have no memory of *your* architecture. So every response drifts.**

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>
</div>

## ✨ The Solution

**11 battle-tested `.md` instruction files** that act as a strict rulebook for any AI coding agent (Cursor · GitHub Copilot · Claude · Windsurf).

Drop the files into your project, reference them in your prompt, and the AI builds **consistent, secure, enterprise-grade code - every single time.**

```txt
"Read database.md, backend.md, frontend.md, security.md
 and STRICTLY follow every instruction in them."
```

That's it. No drift. Same structure for every feature. 🔥

### Version policy

The baselines in this repository were verified on **2026-10-14**. For a new project, use the listed supported major/minor and resolve the latest stable security patch that is mutually compatible with the framework, runtime, plugins, and deployment platform. Commit lockfiles and use immutable container digests in production. Do not silently upgrade an existing project across a major version: read the official migration guide, run codemods where provided, and pass build, typecheck, lint, unit, integration, and end-to-end tests first.

“Latest” never means beta, RC, nightly, `latest` container tags, or an unverified dependency mix. For long-lived products, a currently supported LTS may be better than the newest feature line; record that decision in the project.

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>
</div>

## 📦 What's Inside

<table>
<tr>
<td width="50%" valign="top">

### ⚡ Backends (4)
| Stack | Language |
|-------|----------|
| 🐍 FastAPI + SQLAlchemy | Python |
| 🐍 Django + DRF | Python |
| 🟣 ASP.NET Core | C# |
| ☕ Spring Boot | Java |

</td>
<td width="50%" valign="top">

### 🎨 Frontends (4)
| Stack | Platform |
|-------|----------|
| ▲ Next.js 16.4 | Web (SSR) |
| ⚛️ React + Vite | Web (SPA) |
| 🔺 Angular 22 | Web |
| 💙 Flutter | Mobile · Desktop · Web |

Every frontend instruction supports both **new builds** and **total migration from another frontend stack**. Migration changes the framework and architecture while preserving the existing design, colors, branding, text, fonts, theme, responsive behavior, and animations.

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🗄️ Database (1)
| File | Purpose |
|------|---------|
| 🐘 PostgreSQL | Standalone DB project + reconcile engine (`db_deploy.py`) |

</td>
<td width="50%" valign="top">

### 🔐 Security (1)
| Feature | Protection |
|---------|-----------|
| 🛡️ Traefik + secure auth | TLS, HttpOnly/BFF or PKCE auth, CSRF, HSTS/CSP |

</td>
</tr>
</table>

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>
</div>

## 🗂️ Repository Structure

```txt
A-complete-AI-Agent-Instruction-Library/
│
├── 📁 Backend/
│   ├── FASTAPI_ORM_STRUCTURE.md      # Python · FastAPI + SQLAlchemy async
│   ├── DJANGO_STRUCTURE.md           # Python · Django + DRF
│   ├── ASPNET_STRUCTURE.md           # C# · ASP.NET Core 10 LTS + EF Core
│   └── SPRINGBOOT_STRUCTURE.md       # Java · Spring Boot 4.1 + JPA
│
├── 📁 Frontend/
│   ├── NEXTJS_FRONTEND_STRUCTURE.md  # Next.js 16.4 App Router
│   ├── REACTJS_FRONTEND_STRUCTURE.md # React 19.3 + Vite 8 SPA
│   ├── ANGULARJS_FRONTEND_STRUCTURE.md # Angular 22 standalone
│   └── FLUTTER_STRUCTURE.md          # Flutter multi-platform
│
├── 📁 Database/
│   └── DATABASE_STRUCTURE.md         # PostgreSQL project + inspect/diff/deploy engine
│
├── 📁 Security/
│   └── SECURITY_LAYER.md             # Traefik · TLS · auth · CSRF · headers
│
├── 📁 Skill/
│   └── FASTAPI_NEXTJS_STACK.md       # This stack: FastAPI + Next.js + DB + Security
│
├── 📁 scripts/
│   └── validate_library.py            # Deterministic library checks
│
├── 📄 HOW_TO_USE.md                  # Complete usage guide
└── 📄 README.md                      # You are here
```

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>
</div>

## 🚀 Quick Start

<details open>
<summary><b>▶️ 3 steps to get started</b></summary>

<br/>

**1️⃣ Copy the files you need into your project root**

```bash
# Example: FastAPI + Next.js stack
your-project/
├── FASTAPI_ORM_STRUCTURE.md
├── NEXTJS_FRONTEND_STRUCTURE.md
├── DATABASE_STRUCTURE.md
└── SECURITY_LAYER.md
```

**2️⃣ Start your AI chat with the master prompt**

```txt
Read these files in my project root and STRICTLY follow every
instruction in all of them for all code you generate:
- FASTAPI_ORM_STRUCTURE.md
- NEXTJS_FRONTEND_STRUCTURE.md
- DATABASE_STRUCTURE.md
- SECURITY_LAYER.md

Confirm by summarizing each, then wait for my first task.
```

**3️⃣ Describe your idea — the AI builds it your way**

```txt
IDEA: Build an inventory system with products, stock tracking,
and low-stock alerts. Admins manage users, staff only view stock.

Follow all the instruction files strictly.
Build in order: database → backend → frontend.
```

</details>

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>
</div>

## 🧩 What Every File Contains

<div align="center">

| Section | What It Gives You |
|:-------:|:------------------|
| 🏗️ **Folder Structure** | The exact, mandatory layout - no guessing |
| 📐 **Layer Rules** | What each layer owns and what it must never do |
| 💻 **Code Blueprints** | Copy-paste production-ready examples |
| 🏷️ **Naming Conventions** | One consistent style across the whole codebase |
| ➕ **Add-a-Feature Steps** | Numbered checklist for every new resource |
| 🔄 **Full Frontend Migration** | Convert any existing frontend without redesigning it |
| 🎨 **Visual Preservation Contract** | Keep UI, colors, branding, copy, fonts, theme, layout, and motion unchanged |
| 🚫 **Absolute Prohibitions** | Hard rules the AI can never break |
| ✅ **Pre-Completion Checklist** | Quality gate before the AI says "done" |

</div>

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>
</div>

## 🔐 Security-First by Default

<details>
<summary><b>🛡️ Every stack ships with enterprise security built in</b></summary>

<br/>

- ✅ **Backend IP hidden** — Traefik reverse proxy; browser only ever sees `api.yourdomain.com`
- ✅ **Secret-safe clients** — no shared HMAC key in browser/mobile builds; optional signing is server-to-server with nonce replay protection
- ✅ **No plain-text data** — HTTPS/TLS 1.3 everywhere, HSTS enforced
- ✅ **Secure tokens** — httpOnly cookies / in-memory / encrypted storage — never `localStorage`
- ✅ **Rate limiting** — global + stricter limits on auth endpoints
- ✅ **Security headers** — CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy
- ✅ **No secret leaks** — no stack traces, no server identity in production responses

</details>

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>
</div>

## 🎬 How It Works

```mermaid
flowchart LR
    A[💡 Your Idea] --> B[📄 Reference .md files]
    B --> C{🤖 AI Agent}
    C -->|reads rules| D[🗄️ Database Layer]
    C -->|reads rules| E[⚡ Backend Layer]
    C -->|reads rules| F[🎨 Frontend Layer]
    C -->|reads rules| G[🔐 Security Layer]
    D --> H[✅ Consistent<br/>Production Code]
    E --> H
    F --> H
    G --> H

    style A fill:#0a0a0f,stroke:#00f5ff,color:#00f5ff
    style C fill:#0a0a0f,stroke:#ff00ff,color:#ff00ff
    style H fill:#0a0a0f,stroke:#39ff14,color:#39ff14
```

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>
</div>

## 💡 Why Use This?

<div align="center">

| ❌ Without | ✅ With This Library |
|-----------|--------------------|
| AI invents random structures | One strict, enforced architecture |
| Inconsistent code per feature | Identical patterns every time |
| Security added later (if ever) | Security-first by default |
| Constant back-and-forth fixing | AI gets it right the first time |
| Different rules per framework | Same philosophy across 8 stacks |

</div>

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>
</div>

## 📖 Full Usage Guide

Everything — setup order, environment variables, daily workflow, production checklist, and prompt templates - is in **[`HOW_TO_USE.md`](./HOW_TO_USE.md)**.

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>
</div>

## 🤝 Contributing

Got a rule that improves consistency or security? PRs welcome!

1. 🍴 Fork the repo
2. 🌿 Create a branch (`git checkout -b feature/new-rule`)
3. 💾 Commit your change
4. 🚀 Open a Pull Request

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>

<br/>

## 👨‍💻 Author

**Udhayaboopathi V** - Full Stack & DevOps Engineer

[![Portfolio](https://img.shields.io/badge/Portfolio-udhayaboopathi.tech-00F5FF?style=for-the-badge&logo=google-chrome&logoColor=white)](https://udhayaboopathi.tech)
[![GitHub](https://img.shields.io/badge/GitHub-Udhayaboopathi-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Udhayaboopathi)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-udhayaboopathi-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/udhayaboopathi)

<br/>

### ⭐ If this saves you time, drop a star - it helps more than you think!

![Star History](https://img.shields.io/github/stars/Udhayaboopathi?style=social)

<br/>

<sub>© 2026 Udhayaboopathi V · Built with 💚 in Chennai, Tamil Nadu, India</sub>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>

</div>
