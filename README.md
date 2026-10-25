# BrewCart

Online coffee ordering.

- `frontend/`: Express frontend, http://localhost:3000
- `api/`: Flask API backed by MongoDB, http://localhost:5000 (`/health`, `/menu`, `/orders`)
- `db`: MongoDB

## Run locally

```
docker compose up -d --build
```

(Doesn't fully work yet, see DEV-220.)
