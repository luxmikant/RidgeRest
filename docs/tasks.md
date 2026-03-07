# RidgeRest — Task Tracker

> This file is updated as development progresses. Check off tasks as they are completed.

---

## Phase 0 — Docs Bootstrap
- [x] Create docs/requirements.md
- [x] Create docs/design.md
- [x] Create docs/tasks.md
- [x] Create docs/devlog.md
- [x] Create .github/workflows/devlog.yml

## Phase 1 — Project Setup
- [x] Init backend/ (FastAPI project structure)
- [x] Create requirements.txt with all dependencies
- [x] Create .env.example
- [x] Create backend/app/config.py (settings from env)
- [x] Create backend/app/database.py (Motor client + indexes)
- [x] Init frontend/ (Vue 3 + Vite)
- [x] Add Tailwind CSS
- [x] Add Vue Router + Pinia
- [x] Configure vite-plugin-pwa
- [x] Create frontend API axios instance

## Phase 2 — Authentication + CORS + RBAC
- [x] Backend: core/security.py (JWT create/verify, RBAC deps)
- [x] Backend: core/cors.py (strict CORS middleware)
- [x] Backend: core/oauth.py (Google OAuth via authlib)
- [x] Backend: schemas/user.py (Pydantic models)
- [x] Backend: routers/auth.py (signup, login, google, me, logout)
- [x] Frontend: Login.vue (email/password + Google OAuth buttons)
- [x] Frontend: Signup.vue (email/password + role selector)
- [x] Frontend: OAuthCallback.vue
- [x] Frontend: Pinia auth store (token, user, hydrate)
- [x] Frontend: Router guards (auth + role)
- [x] Frontend: axios interceptor (withCredentials, 401 handling)

## Phase 3 — Core Leave CRUD + Balance
- [x] Backend: schemas/leave.py (Pydantic models)
- [x] Backend: routers/leaves.py (apply, my, cancel, list, approve, reject)
- [x] Backend: routers/balance.py (get own, get by id)
- [x] Backend: leave balance init-on-signup logic
- [x] Backend: balance decrement on approve, increment on reject/cancel
- [x] Backend: overlap conflict check
- [x] Frontend: ApplyLeave.vue (form + live balance preview)
- [x] Frontend: LeaveHistory.vue (table + status badges + cancel)
- [x] Frontend: Requests.vue (employer table + approve/reject + rejection modal)

## Phase 4 — Bonus Features
- [x] Backend: socket_manager.py (python-socketio ASGI)
- [x] Backend: emit leave_status_changed on approve/reject
- [x] Frontend: socket.js store (connect, listen, toast)
- [x] Backend: routers/analytics.py (MongoDB aggregation pipeline)
- [x] Frontend: Analytics.vue (vue-chartjs doughnut + bar + stat cards)
- [x] Frontend: TeamCalendar.vue (FullCalendar/vue-cal)
- [x] Frontend: BalanceBadge.vue (3 progress bars)
- [x] Frontend: Dark mode toggle (Tailwind dark class)
- [x] Frontend: PWA manifest + service worker

## Phase 5 — Polish + Validation
- [x] Backend: Pydantic validators (dates, enums, required fields)
- [x] Frontend: form validation (dates, min chars, required)
- [x] Frontend: Toast.vue component
- [x] Frontend: Axios error interceptor → toast
- [ ] End-to-end flow testing (manual)

## Phase 6 — Deployment
- [ ] MongoDB Atlas: whitelist 0.0.0.0/0, create TTL indexes
- [ ] Render: deploy backend with ddtrace-run
- [ ] Vercel: deploy frontend
- [ ] Configure all env vars (backend + frontend)
- [ ] Verify live URLs working

## Phase 7 — Datadog Monitoring
- [x] Backend: ddtrace patch_all() + structured logging
- [ ] Backend: custom metrics (leave.applied/approved/rejected)
- [x] Frontend: @datadog/browser-rum init + setUser
- [ ] Datadog: create dashboard (flame graphs, latency, logs, RUM)
- [ ] Datadog: configure monitors/alerts
- [ ] Verify: flame graphs visible in APM Profiling
- [ ] Verify: log-trace correlation working

## README
- [ ] Project overview
- [ ] Tech stack
- [ ] Local setup instructions
- [ ] API endpoint documentation
- [ ] Deployment instructions + topology
- [ ] Screenshots / demo
