# RidgeRest — Requirements

## Objective
Build a web application where **employees** can apply for leave and **employers** can approve or reject those requests.

---

## Functional Requirements

### Employee Features
- Sign up with email/password (role: employee)
- Sign in via email/password or Google OAuth 2.0
- Apply for leave: select leave type, start date, end date, reason
- View own leave applications with status (Pending / Approved / Rejected)
- Cancel a pending leave request
- View remaining leave balance (Sick / Casual / Annual)

### Employer Features
- Sign up with email/password (role: employer)
- Sign in via email/password or Google OAuth 2.0
- View all employee leave requests (filterable by status, employee, date range)
- Approve a leave request
- Reject a leave request (must provide a reason)
- View team availability calendar (who is on leave)
- View analytics dashboard (leave trends, breakdowns)

---

## Non-Functional Requirements

### Security
- JWT-based authentication (httpOnly cookie, HS256, 8h expiry)
- Google OAuth 2.0 as alternative login
- Role-based access control (RBAC): employee vs employer enforced server-side
- Strict CORS: only allow configured frontend origin, credentials enabled
- Passwords hashed with bcrypt (passlib)
- Input validation on both frontend and backend (Pydantic v2)

### Tech Stack (Mandatory)
- **Frontend:** Vue.js + Tailwind CSS
- **Backend:** Python (FastAPI) with REST APIs
- **Database:** MongoDB Atlas

### Deployment
- Frontend hosted on Vercel
- Backend hosted on Render
- Application accessible via public URLs

### Monitoring (Production-Grade)
- Datadog APM with continuous profiler (flame graphs)
- Datadog RUM for frontend performance (Core Web Vitals, session replay)
- Log-trace correlation via ddtrace
- Custom business metrics (leave applied/approved/rejected rates)
- Alerting monitors (latency, error rate, anomalies)

### Code Quality
- Clean, readable code with proper folder structure
- Environment variables for all secrets
- Basic error handling throughout

---

## Bonus Requirements (All Implemented)
- [x] JWT-based authentication
- [x] Role-based access control (Employee vs Employer)
- [x] Basic input validation (required fields, date validation)
- [x] Well-written README with setup, API docs, deployment instructions

## Extra Features Beyond Requirements
- Google OAuth 2.0 login
- Leave balance tracker (Sick: 10, Casual: 10, Annual: 15 days/year)
- Team availability calendar
- Analytics dashboard with charts
- Real-time notifications via Socket.io
- Dark mode + PWA
- Datadog full-stack observability (APM, Profiling, RUM, Logs, Monitors)
- Auto-generated devlog via GitHub Actions
