# Frontend (React)

This is a minimal React frontend (Vite) that talks to the API endpoint `POST /chat`.

Run locally:

```bash
cd frontend
npm install
npm run dev
```

By default the app will call `http://localhost:8000/chat`. You can change the backend URL with the Vite env variable `VITE_API_URL`.

Example:

```bash
VITE_API_URL="http://localhost:8000" npm run dev
```
