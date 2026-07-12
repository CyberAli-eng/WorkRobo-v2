● Tech Stack

  Frontend (frontend/)

  - Next.js 15 (App Router) + React 18 + TypeScript
  - Tailwind CSS v4 (with PostCSS + Autoprefixer)
  - framer-motion — animations
  - @xyflow/react — node-based / graph UIs (React Flow)
  - lucide-react — icons

  Backend (backend/)

  - Django 5 + Django REST Framework
  - Channels — WebSockets / ASGI
  - Celery + redis — background jobs and scheduling
  - Flower — Celery monitoring dashboard
  - PostgreSQL (psycopg[binary]) — primary database
  - gunicorn + uvicorn[standard] — WSGI / ASGI servers
  - django-cors-headers — CORS for the Next.js frontend

  Infra

  - Docker Compose — orchestrates django, postgres, redis, celery, celery-beat, flower
  - Node.js (npm) — frontend package management
  - Python — backend package management

  The shape (React Flow + Celery + Channels + async tasks) is consistent with a visual workflow / AI agent automation platform — a node-based  editor on the front end that dispatches jobs through Celery workers and streams updates back over Channels.


  ● Project Structure

  WorkRobo.ai/
  ├── backend/                    # Django + async stack
  │   ├── backend_project/        # Main Django project config
  │   │   ├── __init__.py
  │   │   ├── asgi.py             # ASGI entry (for Channels/WebSockets)
  │   │   ├── wsgi.py             # WSGI entry (for gunicorn)
  │   │   ├── celery.py           # Celery app definition
  │   │   ├── settings.py         # Django settings (env-driven)
  │   │   └── urls.py             # Root URL routing
  │   │
  │   ├── hello/                  # Demo Django app
  │   │   ├── __init__.py
  │   │   ├── apps.py
  │   │   └── views.py            # One view: "Hello World I Love You ALI"
  │   │
  │   ├── manage.py               # Django management CLI
  │   ├── requirements.txt        # Python deps
  │   ├── Dockerfile              # Backend container image
  │   ├── docker-compose.yml      # Multi-service orchestration
  │   ├── celerybeat-schedule     # Celery beat state file
  │   └── README.md
  │
  └── frontend/                   # Next.js + React Flow UI
      ├── app/                    # Next.js App Router
      │   └── page.tsx            # Home page — fetches /api/hello/
      ├── styles/                 # Global CSS
      ├── node_modules/           # Installed JS deps
      ├── next.config.mjs         # Next.js config
      ├── next-env.d.ts           # Next.js TS ambient types
      ├── package.json            # JS deps + scripts
      ├── package-lock.json
      ├── postcss.config.js       # PostCSS config (for Tailwind v4)
      ├── tailwind.config.ts      # Tailwind config
      └── tsconfig.json           # TypeScript config

  What's going on where

  backend_project/ — the "config" layer. Nothing business-related lives here; it's wiring:
  - settings.py reads env vars (e.g. DJANGO_SECRET_KEY, DJANGO_DEBUG), registers apps (hello, rest_framework, channels, corsheaders), and    
  configures middleware.
  - celery.py boots the Celery app so tasks can be discovered.
  - asgi.py / wsgi.py give the server two entry points: ASGI for WebSocket/realtime via Channels, WSGI for plain HTTP via gunicorn.

  hello/ — a placeholder Django app. One view returns a JSON greeting. It exists to prove the frontend ↔ backend bridge works and to give you  a copy-paste template for real apps (e.g. workflows/, agents/, runs/).

  docker-compose.yml — runs six services:
  - django — the API
  - postgres — database
  - redis — broker + Channels layer
  - celery — task worker
  - celery-beat — scheduled tasks
  - flower — Celery dashboard on :5555

  frontend/app/ — Next.js App Router. The whole UI is one file: page.tsx calls http://localhost:8000/api/hello/ on mount and renders the     
  response inside a framer-motion card. React Flow is installed but not yet wired up.

  frontend/*.{json,ts,js,mjs} — config files. Tailwind v4 uses the new PostCSS plugin (@tailwindcss/postcss), and the tsconfig.json is the   
  standard Next.js preset.

  The big picture

  Right now the structure is a vertical slice of plumbing, not features. Each side has the minimum needed to prove the connection (Django →  
  Next.js), but the real product — whatever React-Flow-based workflow editor the name "WorkRobo.ai" implies — hasn't been built yet. New work  would likely add backend/workflows/, backend/runs/, etc., and frontend/app/editor/, frontend/app/workflows/, etc.