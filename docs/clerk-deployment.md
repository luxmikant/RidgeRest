# Deployment: Clerk Auth Setup

## 1. Clerk Dashboard

1. Go to [clerk.com](https://clerk.com) → create application (or use existing)
2. **Allowed redirect URLs** — add:
   - `https://ridge-rest.vercel.app/dashboard-redirect`
   - `https://ridge-rest.vercel.app/setup-role`
   - `http://localhost:5173/dashboard-redirect` (dev)
   - `http://localhost:5173/setup-role` (dev)
3. **Allowed origins** — add:
   - `https://ridgerest.onrender.com`
   - `https://ridge-rest.vercel.app`
4. Copy **Publishable key** (`pk_live_...`) and **Secret key** (`sk_live_...`)

---

## 2. Render (backend)

Go to your Render service → **Environment** tab.

**Remove** these old vars (if present):
- `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_HOURS`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`

**Add / update**:
| Key | Value |
|-----|-------|
| `CLERK_SECRET_KEY` | `sk_live_...` |
| `CLERK_PUBLISHABLE_KEY` | `pk_live_...` |
| `FRONTEND_URL` | `https://ridge-rest.vercel.app` *(single value, no trailing slash)* |
| `MONGODB_TLS_ALLOW_INVALID_CERTIFICATES` | `false` |

---

## 3. Vercel (frontend)

Go to your Vercel project → **Settings → Environment Variables**.

**Add**:
| Key | Value |
|-----|-------|
| `VITE_CLERK_PUBLISHABLE_KEY` | `pk_live_...` |
| `VITE_API_URL` | `https://ridgerest.onrender.com` |

Redeploy the frontend after saving these.

---

## 4. Migrate existing users (optional)

If you have users in MongoDB created before Clerk:

```bash
cd backend
# Set env vars (or create .env file)
export CLERK_SECRET_KEY=sk_live_...
export MONGODB_URL=mongodb+srv://...
python -m scripts.migrate_users_to_clerk
```

The script will:
- Find MongoDB users without a `clerk_id`
- Create them in Clerk with their email/name/role
- Update MongoDB with the new Clerk IDs
- Re-link their leaves and leave_balances records

---

## 5. Verify deployment

1. Open `https://ridge-rest.vercel.app/login` → click **Sign In** → Clerk hosted sign-in opens
2. Sign up as employee → role picker appears → Clerk hosted sign-up opens → redirects to `/setup-role` → MongoDB profile created → redirects to `/employee/dashboard`
3. Employer flow: same but lands on `/employer/dashboard`
4. Check `/api/auth/me` returns user JSON with Bearer token in Authorization header
