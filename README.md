# WorkRobo.ai — Project State
### Phase 0 Scaffold — Last Updated: July 2026

---

## Current Status

Phase 0 is in progress. The monorepo skeleton is live — Django, Next.js, Docker Compose, and all supporting services are running. Auth, credential vault, and model scoping are being built now (Steps 0.3 → 0.5).

---

## Tech Stack

### Frontend (`frontend/`)
| Package | Purpose |
|---|---|
| Next.js 15 (App Router) + React 18 + TypeScript | Core UI framework |
| Tailwind CSS v4 (PostCSS + Autoprefixer) | Utility-first styling |
| framer-motion | Animations and transitions |
| @xyflow/react | Node-based canvas / graph editor (React Flow) |
| lucide-react | Icon library |

### Backend (`backend/`)
| Package | Purpose |
|---|---|
| Django 5 + Django REST Framework | API framework |
| Django Channels | WebSockets / ASGI real-time layer |
| Celery + Redis | Background job queue and scheduling |
| Flower | Celery monitoring dashboard |
| PostgreSQL (psycopg[binary]) | Primary database |
| gunicorn + uvicorn[standard] | WSGI / ASGI servers |
| django-cors-headers | CORS for the Next.js frontend |

### Infrastructure
| Tool | Purpose |
|---|---|
| Docker Compose | Orchestrates all services (django, postgres, redis, celery, celery-beat, flower) |
| Node.js (npm) | Frontend package management |
| Python (pip) | Backend package management |

---

## Project Structure

```
WorkRobo.ai/
├── backend/                        # Django + async stack
│   ├── backend_project/            # Main Django project config (wiring only, no business logic)
│   │   ├── __init__.py
│   │   ├── asgi.py                 # ASGI entry — Channels / WebSockets
│   │   ├── wsgi.py                 # WSGI entry — gunicorn
│   │   ├── celery.py               # Celery app definition + autodiscovery
│   │   ├── settings.py             # All settings, env-driven (no hardcoded secrets)
│   │   └── urls.py                 # Root URL routing
│   │
│   ├── hello/                      # ✅ Demo app — proves frontend ↔ backend bridge
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   └── views.py                # GET /api/hello/ → JSON greeting
│   │
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml          # Six services: django, postgres, redis, celery, celery-beat, flower
│   ├── celerybeat-schedule
│   └── README.md
│
└── frontend/                       # Next.js + React Flow UI
    ├── app/                        # Next.js App Router
    │   └── page.tsx                # Home page — fetches /api/hello/, renders with framer-motion card
    ├── styles/                     # Global CSS
    ├── node_modules/
    ├── next.config.mjs
    ├── next-env.d.ts
    ├── package.json
    ├── package-lock.json
    ├── postcss.config.js           # PostCSS config for Tailwind v4
    ├── tailwind.config.ts
    └── tsconfig.json
```

### Apps to be added (planned)
```
backend/
├── accounts/       # Custom User model (email as USERNAME_FIELD) — Phase 0.3
├── core/           # UserScopedModel base + Credential vault — Phase 0.5  ← IN PROGRESS
├── workflows/      # Workflow, Node, Edge, WorkflowRun, WorkflowVersion — Phase 0.3 + 1.1
└── ...

frontend/app/
├── auth/           # Login / signup pages — Phase 0.3
├── editor/         # React Flow canvas workspace — Phase 2
└── workflows/      # Dashboard, template picker — Phase 2+
```

---

## What Each Layer Does

### `backend_project/` — Config layer
Pure wiring. Nothing business-related lives here.
- `settings.py` reads env vars (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DATABASE_URL`, `REDIS_URL`, `FERNET_KEY`), registers apps, configures middleware
- `celery.py` boots the Celery app so tasks are auto-discovered across all apps
- `asgi.py` / `wsgi.py` provide two entry points: ASGI for WebSocket/realtime via Channels, WSGI for plain HTTP via gunicorn

### `hello/` — Demo app (placeholder)
One view: `GET /api/hello/` returns a JSON greeting. Exists to prove the bridge works and serves as a copy-paste template for real apps (`workflows/`, `core/`, etc.). Will be removed or repurposed before production.

### `docker-compose.yml` — Six services
| Service | Port | Notes |
|---|---|---|
| `django` | 8000 | API + ASGI server |
| `postgres` | 5432 | Primary database |
| `redis` | 6379 | Celery broker + Channels layer |
| `celery` | — | Task worker |
| `celery-beat` | — | Scheduled tasks |
| `flower` | 5555 | Celery monitoring dashboard |

### `frontend/app/page.tsx` — Current UI
Calls `http://localhost:8000/api/hello/` on mount, renders the response inside a framer-motion card. `@xyflow/react` is installed but not yet wired — canvas work begins Phase 2.

---

## Architectural Decisions Locked So Far

| Decision | Choice | Rationale |
|---|---|---|
| User model | Custom `User` in `accounts/`, email as `USERNAME_FIELD`, no username field | Cleanest SaaS identity long-term; free to change only at Phase 0 |
| DRF auth default | `IsAuthenticated` globally | Safe default — anonymous = 401, no endpoint accidentally open |
| Token storage | `localStorage` now, HttpOnly cookies in Phase 4 | Unblocks Phase 1 engine work; hardening is already on Phase 4 checklist |
| Model scoping | All four models defined with user FKs from Phase 0 | PRD schema locked; scoping pattern proven on real models not stubs |
| Credential location | `core/` app alongside `UserScopedModel` | Security primitive referenced by all domains — no cross-app import issues |
| Credential encryption | Symmetric Fernet, key from env var | Simple, reversible, sufficient; key rotation added in Phase 4+ when needed |
| API exposure of credential value | Never — API returns `{id, name, provider, created_at}` only | Raw keys never leave the server; frontend only needs ID for picker dropdown |
| Encryption test | Single focused pytest: plaintext-not-in-DB + round-trip recovery | Proves the two invariants that matter; more coverage added when needed |

---

## Phase 0 Checklist

- [x] **0.1** — Monorepo + Docker skeleton (`docker-compose up` runs all six services)
- [x] **0.2** — Verified: Next.js fetches Django hello endpoint successfully
- [ ] **0.3** — Auth: custom User model, JWT (simplejwt), login/signup, `IsAuthenticated` global default
- [ ] **0.4** — Verified: two users cannot access each other's data by ID guessing
- [ ] **0.5** — Credential vault: `Credential` model in `core/`, Fernet encryption, CRUD API, test ← **IN PROGRESS**
- [ ] **0.6** — Verified: raw Postgres row shows ciphertext, not plaintext

---

## What Doesn't Exist Yet

The structure right now is **vertical plumbing, not features**. Each side has the minimum to prove the connection. The actual product — the React Flow workflow editor, agent execution engine, and six vertical suites — hasn't been built yet.

Real work begins:
- **Phase 1** — Celery + LangGraph + WebSocket engine
- **Phase 2** — Canvas UI wired to live engine
- **Phase 3–5** — Six agent suites as loadable templates
- **Phase 6** — Approval nodes, replay, marketplace, cross-suite triggers, POLICY routing
