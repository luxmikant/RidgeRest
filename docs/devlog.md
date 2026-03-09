# RidgeRest — Development Log

> Auto-updated by GitHub Actions on every push to `main`. Manual entries welcome.

---
## 2026-03-07 15:18 UTC — e2ecae3
**Author:** shree
**Commit:** feat: Implement employee leave management system with signup, leave application, and employer approval features
**Changed files:**
```

```

---

## 2026-03-07 15:59 UTC — e337ca0
**Author:** shree
**Commit:** pin python 3.12 for render deployment
**Changed files:**
```
backend/runtime.txt
```

---

## 2026-03-08 03:39 UTC — f238760
**Author:** shree
**Commit:** Merge branch 'main' of https://github.com/luxmikant/RidgeRest
**Changed files:**
```
docs/devlog.md
```

---

## 2026-03-08 03:46 UTC — ed05d20
**Author:** shree
**Commit:** fix: add runtime.txt to repo root so Render picks up Python 3.12.3
**Changed files:**
```
runtime.txt
```

---

## 2026-03-09 06:53 UTC — 9903ee2
**Author:** shree
**Commit:** feat: migrate auth to Clerk (hosted pages + Bearer token)
**Changed files:**
```
backend/.env.example
backend/app/config.py
backend/app/core/oauth.py
backend/app/core/security.py
backend/app/database.py
backend/app/routers/auth.py
backend/requirements.txt
backend/scripts/__init__.py
backend/scripts/migrate_users_to_clerk.py
frontend/.env.example
frontend/package-lock.json
frontend/package.json
frontend/public/icon-192.png
frontend/public/icon-512.png
frontend/src/App.vue
frontend/src/api/index.js
frontend/src/components/Navbar.vue
frontend/src/main.js
frontend/src/router/index.js
frontend/src/stores/auth.js
```

---

## 2026-03-09 06:54 UTC — 9e3c97c
**Author:** shree
**Commit:** docs: Clerk deployment guide
**Changed files:**
```
docs/clerk-deployment.md
```

---

## 2026-03-09 07:09 UTC — cc93e17
**Author:** shree
**Commit:** fix: use window.Clerk in auth store to avoid inject() outside component context
**Changed files:**
```
frontend/src/App.vue
frontend/src/stores/auth.js
```

---

## 2026-03-09 07:18 UTC — 3e6b22e
**Author:** shree
**Commit:** fix: make Clerk keys optional so server starts without them (returns 503 on auth routes)
**Changed files:**
```
backend/app/config.py
backend/app/core/security.py
```

---

## 2026-03-09 07:26 UTC — 8a502b3
**Author:** shree
**Commit:** fix: remove dead legacy auth code causing NameError on startup
**Changed files:**
```
backend/app/routers/auth.py
```

---

## 2026-03-09 07:52 UTC — 2a0a9d7
**Author:** shree
**Commit:** fix: add /api prefix to axios baseURL
**Changed files:**
```
frontend/src/api/index.js
```

---

