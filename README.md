# RidgeRest — Leave Management System

A full-stack leave management web application where **employees** apply for leave and **employers** approve or reject requests, with real-time notifications, analytics, and team visibility.

## Features

### Core
- Employee leave application (sick, casual, annual)
- Employer approve/reject with rejection reasons
- Leave history with status filtering
- Role-based access control (RBAC)

### Bonus
- **JWT + Google OAuth 2.0** authentication (httpOnly cookies)
- **Leave Balance Tracker** — visual progress bars per leave type
- **Team Availability Calendar** — FullCalendar with approved leaves
- **Leave Analytics Dashboard** — charts (status, type, monthly trend, top employees)
- **Real-time Notifications** — Socket.IO push on approval/rejection
- **Dark Mode** toggle with localStorage persistence
- **PWA** — installable, offline-capable via Workbox
- **Datadog Observability** — APM, RUM, Continuous Profiler, custom metrics

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3, Vite, Tailwind CSS, Pinia, Vue Router |
| Backend | Python, FastAPI, Motor (async MongoDB) |
| Database | MongoDB Atlas (free M0 tier) |
| Auth | JWT (HS256, httpOnly cookies), Google OAuth 2.0 |
| Real-time | Socket.IO (python-socketio) |
| Charts | Chart.js + vue-chartjs, FullCalendar |
| Monitoring | Datadog (APM, RUM, Continuous Profiler) |
| Deployment | Render (backend), Vercel (frontend) |

## Project Structure

```
RidgeRest/
├── backend/
│   ├── app/
│   │   ├── core/           # security, cors, oauth
│   │   ├── routers/        # auth, leaves, balance, analytics
│   │   ├── schemas/        # Pydantic models
│   │   ├── config.py       # Settings from env
│   │   ├── database.py     # MongoDB connection + indexes
│   │   ├── socket_manager.py
│   │   └── main.py         # App entrypoint
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/     # Navbar, Toast, BalanceBadge
│   │   ├── views/          # auth/, employee/, employer/
│   │   ├── stores/         # Pinia stores
│   │   ├── router/         # Vue Router with guards
│   │   └── api/            # Axios instance
│   ├── package.json
│   └── vite.config.js
├── docs/                   # requirements, design, tasks, devlog
└── .github/workflows/      # Auto-devlog GitHub Action
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB Atlas account (free M0 cluster)
- Google Cloud Console project (for OAuth)

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux

pip install -r requirements.txt

# Copy and fill environment variables
cp .env.example .env
# Edit .env with your MongoDB URL, secret key, Google OAuth creds
```

### Frontend Setup

```bash
cd frontend
npm install

# Create .env file
echo VITE_API_URL=http://localhost:8000/api > .env
```

### Run Locally

```bash
# Terminal 1 — Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open http://localhost:5173

## Environment Variables

### Backend (.env)
| Variable | Description |
|----------|-------------|
| `MONGODB_URL` | MongoDB connection string |
| `SECRET_KEY` | JWT signing secret (generate with `openssl rand -hex 32`) |
| `FRONTEND_URL` | Frontend origin for CORS (e.g., `https://ridgerest.vercel.app`) |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `EXTRA_CORS_ORIGINS` | Comma-separated additional CORS origins |

### Frontend (.env)
| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API base URL |
| `VITE_DD_APPLICATION_ID` | Datadog RUM application ID (optional) |
| `VITE_DD_CLIENT_TOKEN` | Datadog RUM client token (optional) |

## Deployment

### Backend → Render
1. Create a new **Web Service** on Render
2. Set root directory to `backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `ddtrace-run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add all environment variables from `.env.example`

### Frontend → Vercel
1. Import repo on Vercel
2. Set root directory to `frontend`
3. Framework preset: Vite
4. Add `VITE_API_URL` pointing to your Render backend URL

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/signup` | — | Register |
| POST | `/api/auth/login` | — | Login |
| GET | `/api/auth/google` | — | Start Google OAuth |
| GET | `/api/auth/google/callback` | — | Google OAuth callback |
| GET | `/api/auth/me` | Any | Current user |
| POST | `/api/auth/logout` | Any | Logout |
| POST | `/api/leaves/` | Employee | Apply for leave |
| GET | `/api/leaves/my` | Employee | Own leave history |
| DELETE | `/api/leaves/{id}` | Employee | Cancel pending leave |
| GET | `/api/leaves/` | Employer | All leave requests |
| PATCH | `/api/leaves/{id}/approve` | Employer | Approve leave |
| PATCH | `/api/leaves/{id}/reject` | Employer | Reject leave |
| GET | `/api/balance/` | Employee | Own balance |
| GET | `/api/balance/{id}` | Employer | Employee's balance |
| GET | `/api/analytics/overview` | Employer | Dashboard analytics |

## License

MIT
