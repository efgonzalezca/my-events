# My Events — Frontend

SPA built with **React 19 + TypeScript + Vite + Tailwind CSS v4** that consumes
the API in [`backend/`](../backend). Designed to be simple to read and demo: no
Redux, no TanStack Query — just `Context` for auth and `useState` for the rest.

## Stack

- Vite + React 19 + TypeScript
- React Router v7 (`BrowserRouter`)
- Axios (with interceptors for JWT and 401 → logout)
- Tailwind CSS v4 (`@tailwindcss/vite`)

## Environment variables

`VITE_API_URL` points to the backend. The Docker flow injects it from the root
`docker-compose.yml`. To run Vite directly outside the container, create a
`.env` file (there is a `.env.example`):

```env
VITE_API_URL=http://localhost:8000/api
```

## Running (Docker, recommended)

From the repository root:

```bash
make dev
```

Brings up `db` + `backend` + `frontend`:

- Frontend (Vite with hot reload): <http://localhost:5173>
- Backend: <http://localhost:8000>
- API docs: <http://localhost:8000/api/docs>

The `frontend` service uses the `development` target of the `Dockerfile` and
mounts `./frontend` so changes are reflected instantly.

## Scripts (inside the container or locally)

```bash
npm install
npm run dev       # starts Vite at http://localhost:5173
npm run build     # type-checks and produces a prod bundle in dist/
npm run preview   # serves dist/ locally
npm run lint
```

## Layout

```
src/
├── api/              # axios client + per-module functions
│   ├── client.ts        # axios + interceptors (auth, 401)
│   ├── auth.ts          # register, login, me
│   ├── events.ts        # list, get, create, update, publish, cancel, delete
│   ├── sessions.ts      # CRUD + link/unlink speakers
│   └── registrations.ts # register, cancel, my registrations
├── auth/
│   ├── AuthContext.tsx  # provider + useAuth hook
│   └── ProtectedRoute.tsx
├── components/       # reusable building blocks (Button, Input, EventCard, Pager, …)
├── pages/            # one screen per file
├── lib/
│   ├── errors.ts        # backend code → Spanish message map
│   └── datetime.ts      # ISO ↔ datetime-local + es-CO formatting
├── types.ts          # interfaces mirroring the backend
├── App.tsx           # routes and layout
└── main.tsx
```

## Routes

| Path | Auth | Screen |
|---|---|---|
| `/login` | public | sign in |
| `/register` | public | create account (role `attendee`) |
| `/events` | public | paginated list with search |
| `/events/:id` | public | event detail + sessions; register / cancel registration |
| `/profile` | required | current user details + my registrations |
