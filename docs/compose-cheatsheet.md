# Docker Compose cheat sheet (Project 04)

Every command used in this project, with what each part does.

## Validate and run

| Command | What it does |
|---|---|
| `docker compose config --quiet` | Parse and validate the file (and `.env` substitutions). No output = valid. |
| `docker compose config` | Print the final file with variables filled in. **Shows secrets**, so don't paste it anywhere. |
| `docker compose up -d --build` | Build images if needed, create networks and volumes, start everything in the background |
| `docker compose up -d --wait` | Same, but return only when every service is running **and healthy** |
| `docker compose up -d` (after an edit) | Recreate only the services whose configuration changed |
| `docker compose down` | Remove containers and networks. **Named volumes are kept.** |
| `docker compose down -v` | Also delete named volumes: **wipes the database** |
| `docker compose stop db` / `start db` | Stop or start one service without removing it |

## Inspect

| Command | What it does |
|---|---|
| `docker compose ps` | Services, status, `(healthy)` / `(unhealthy)`, published ports |
| `docker compose logs proxy --tail 5` | Last 5 log lines of one service |
| `docker compose logs -f` | Follow all logs live (Ctrl+C to stop) |
| `docker compose exec api printenv MONGO_URL` | Run a command inside a running service |
| `docker compose exec db mongod --version` | Which MongoDB version is really running |
| `docker compose port db 27017` | Which host port, if any, a container port is published on |
| `docker network ls --filter name=devops-project-04` | The project's networks |
| `docker network inspect <net> --format '{{range .Containers}}{{.Name}} {{end}}'` | Which containers are on a network |
| `docker volume ls --filter name=mongo-data` | The named volume holding the data |

## Debug a 502 from inside the proxy

```bash
docker compose logs proxy --tail 5                               # connect() failed (111: Connection refused) ... upstream: "http://IP:PORT/..."
docker compose exec proxy wget -S -O- http://api:8000/health     # can the proxy reach the API on that port?
docker compose exec proxy nginx -t                               # test config syntax
docker compose exec proxy nginx -s reload                        # apply config without downtime
```

| Error from inside the proxy | Meaning |
|---|---|
| `bad address 'api'` | DNS failed: not on the same network, or a wrong service name |
| `Connection refused` | Name resolved, but nothing listens on that port: wrong port, or the app is down |
| Hangs, then times out | Firewall or routing, or the app is stuck |

## Test through the proxy

```bash
curl -i localhost/                       # frontend through Nginx
curl -i localhost/api/health             # API through Nginx (prefix /api stripped)
curl localhost/api/orders
curl -X POST localhost/api/orders -H "Content-Type: application/json" -d '{"item":"Latte","qty":2}'
curl -s -o /dev/null -w "%{http_code}\n" localhost:5050/health   # 000 = nothing listening
```

## Compose file building blocks

| Snippet | Purpose |
|---|---|
| `ports: ["80:80"]` | `HOST:CONTAINER`. Only the proxy publishes a port. |
| `./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro` | Bind mount: a host file inside the container, read-only |
| `mongo-data:/data/db` | Named volume, mounted where MongoDB writes |
| `networks: [edge, backend]` | The API is the only service on both networks |
| `backend: { internal: true }` | No route to the outside world |
| `depends_on: { db: { condition: service_healthy } }` | Wait until `db` is healthy, not just started |
| `healthcheck: { interval: 10s, start_interval: 2s }` | Override timing; `test` is inherited from the Dockerfile |
| `${MONGO_USER:?set MONGO_USER in .env}` | Required variable: a clear error if missing |
| `${PROXY_PORT:-80}` | Default value if not set |

## Nginx reverse proxy

```nginx
location /api/ {
    proxy_pass http://api:8000/;     # trailing / strips the /api prefix
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

## Git safety for `.env`

```bash
git check-ignore -v .env     # .gitignore:8:.env  .env  → it will never be committed
git status                   # .env must not appear
```
