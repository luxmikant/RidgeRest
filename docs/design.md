# RidgeRest — Design Document

## Deployment Topology

```
┌─────────────┐     HTTPS     ┌──────────────────┐     HTTPS     ┌─────────────────┐
│   Browser    │──────────────▶│  Vercel (CDN)    │               │  Datadog Cloud  │
│   (Vue SPA)  │               │  Vue 3 + Vite    │               │  APM · RUM ·    │
│   + DD RUM   │               │  Static Assets   │               │  Logs · Profiler│
└──────┬───────┘               └──────────────────┘               └────────▲────────┘
       │                                                                   │
       │  REST API (httpOnly cookie)                              ddtrace HTTP intake
       │  + Socket.io (WebSocket)                                          │
       │                                                                   │
       ▼                                                                   │
┌──────────────────────────────────────────────────────────────────────────┤
│                        Render (Web Service)                              │
│  ┌─────────────────────────────────────────────────────────┐             │
│  │  ddtrace-run uvicorn app.main:app                       │─────────────┘
│  │  FastAPI + python-socketio (ASGI)                       │
│  │  ├── core/security.py    (JWT + RBAC)                   │
│  │  ├── core/cors.py        (strict CORS)                  │
│  │  ├── core/oauth.py       (Google OAuth via authlib)     │
│  │  ├── routers/auth.py     (signup, login, google, me)    │
│  │  ├── routers/leaves.py   (CRUD + approve/reject)        │
│  │  ├── routers/balance.py  (leave balance)                │
│  │  └── routers/analytics.py (aggregations)                │
│  └──────────────────────────┬──────────────────────────────┘
│                              │
└──────────────────────────────┼──────────────────────────────
                               │  Motor (async MongoDB driver)
                               ▼
                ┌──────────────────────────┐
                │  MongoDB Atlas (M0 Free) │
                │  Collections:            │
                │  · users                 │
                │  · leaves                │
                │  · leave_balances        │
                │  · revoked_tokens (TTL)  │
                │  · oauth_states (TTL)    │
                └──────────────────────────┘
```

---

## Data Models

### users
| Field | Type | Notes |
|-------|------|-------|
| _id | ObjectId | auto |
| name | string | required |
| email | string | unique index |
| hashed_password | string | null for Google-only users |
| role | string | "employee" \| "employer" |
| department | string | optional, default "" |
| auth_provider | string | "local" \| "google" |
| google_id | string | optional, for Google OAuth users |
| created_at | datetime | auto |

### leaves
| Field | Type | Notes |
|-------|------|-------|
| _id | ObjectId | auto |
| employee_id | string | ref: users._id |
| employee_name | string | denormalized for display |
| leave_type | string | "sick" \| "casual" \| "annual" |
| start_date | date | must be >= today |
| end_date | date | must be >= start_date |
| reason | string | min 10 chars |
| status | string | "pending" \| "approved" \| "rejected" |
| rejection_reason | string | required when status = rejected |
| created_at | datetime | auto |
| updated_at | datetime | auto on status change |

### leave_balances
| Field | Type | Notes |
|-------|------|-------|
| _id | ObjectId | auto |
| employee_id | string | ref: users._id, indexed |
| year | int | e.g. 2026 |
| sick | { total: 10, used: 0 } | object |
| casual | { total: 10, used: 0 } | object |
| annual | { total: 15, used: 0 } | object |

### revoked_tokens
| Field | Type | Notes |
|-------|------|-------|
| _id | ObjectId | auto |
| jti | string | unique index |
| revoked_at | datetime | TTL index: expires after 8h (matching token exp) |

### oauth_states
| Field | Type | Notes |
|-------|------|-------|
| _id | ObjectId | auto |
| nonce | string | unique index |
| role | string | "employee" \| "employer" |
| created_at | datetime | TTL index: expires after 10 min |

---

## Authentication Flows

### Flow A: Email/Password
```
1. POST /api/auth/signup  { name, email, password, role }
   → bcrypt hash password → insert user (auth_provider: "local")
   → init leave_balance if role=employee
   → create JWT { sub: user_id, email, role, jti, exp }
   → Set-Cookie: access_token=<jwt>; HttpOnly; SameSite=Lax; Secure; Path=/

2. POST /api/auth/login  { email, password }
   → verify bcrypt → issue JWT → Set-Cookie (same as above)

3. GET /api/auth/me  (cookie auto-sent)
   → decode JWT → check jti not in revoked_tokens → return user profile

4. POST /api/auth/logout  (cookie auto-sent)
   → decode JWT → insert jti into revoked_tokens → clear cookie
```

### Flow B: Google OAuth 2.0
```
1. Frontend: user clicks "Sign in with Google as Employee"
   → browser navigates to GET /api/auth/google?role=employee

2. Backend: generate nonce → store { nonce, role } in oauth_states (TTL 10 min)
   → build Google authorization URL with state=base64({ nonce })
   → redirect browser to Google

3. Google authenticates user → redirects to GET /api/auth/google/callback?code=...&state=...

4. Backend: decode state → verify nonce exists in oauth_states → delete nonce
   → exchange code for tokens via authlib
   → fetch Google userinfo (email, name, google_id)
   → upsert user: find by google_id or email
     - if new: create user (auth_provider: "google", role from state)
     - if exists: update google_id if missing
   → issue JWT → Set-Cookie → redirect to FRONTEND_URL/oauth-callback

5. Frontend OAuthCallback.vue: GET /api/auth/me → hydrate Pinia → redirect to dashboard
```

---

## CORS Policy

| Setting | Value | Reason |
|---------|-------|--------|
| allow_origins | [FRONTEND_URL] | strict — no wildcards |
| allow_credentials | True | httpOnly cookie requires this |
| allow_methods | GET, POST, PATCH, DELETE, OPTIONS | all used methods |
| allow_headers | Content-Type, X-Request-ID | no Authorization needed (cookie-based) |
| expose_headers | X-Request-ID | for client-side tracing |
| max_age | 600 | cache preflight for 10 min |

Dev mode: `EXTRA_CORS_ORIGINS=http://localhost:5173` adds local dev server.

---

## RBAC Matrix

| Endpoint | Employee | Employer |
|----------|----------|----------|
| POST /api/auth/signup | yes | yes |
| POST /api/auth/login | yes | yes |
| GET /api/auth/me | yes | yes |
| POST /api/auth/logout | yes | yes |
| POST /api/leaves/ | **yes** | no (403) |
| GET /api/leaves/my | **yes** | no (403) |
| DELETE /api/leaves/{id} | **yes** (own pending only) | no (403) |
| GET /api/leaves/ | no (403) | **yes** |
| PATCH /api/leaves/{id}/approve | no (403) | **yes** |
| PATCH /api/leaves/{id}/reject | no (403) | **yes** |
| GET /api/balance/ | **yes** | no (403) |
| GET /api/balance/{id} | no (403) | **yes** |
| GET /api/analytics/overview | no (403) | **yes** |

---

## Datadog Instrumentation Map

| Layer | Instrumentation | What It Captures |
|-------|----------------|-------------------|
| FastAPI routes | ddtrace auto-patch | request spans, status codes, latency per endpoint |
| MongoDB (Motor) | ddtrace auto-patch | query spans, collection, operation, duration |
| HTTP calls (authlib) | ddtrace auto-patch | Google OAuth HTTP call spans |
| Python runtime | DD_RUNTIME_METRICS | GC pauses, heap, thread count |
| CPU profiling | DD_PROFILING_ENABLED | continuous flame graphs per function |
| Logs | ddtrace.contrib.logging | trace_id/span_id injected for correlation |
| Custom metrics | datadog SDK | leave.applied/approved/rejected, auth events |
| Frontend | @datadog/browser-rum | page loads, Web Vitals, JS errors, API waterfall |
| User sessions | RUM setUser() | user id, role, name tagged to sessions |
