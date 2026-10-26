# Fixes to Neha's docker-compose.yml (DEV-220)

Neha's compose file had five mistakes. Each one was found by running the stack and reading the output, then fixed one at a time.

| # | Mistake | Symptom | How it was found | Fix |
|---|---|---|---|---|
| 1 | `depends_on: mongo`, but the service is named `db` | Compose refuses to start: `service "api" depends on undefined service "mongo": invalid compose project` | `docker compose config --quiet` | `depends_on: db` |
| 2 | `MONGO_URL` pointed at `localhost:27017` | API returns `503` with `"db":"down"` | `curl -i localhost:5050/health`, then `docker compose exec api printenv MONGO_URL` | Use the service name: `@db:27017`. Inside a container, `localhost` is that container itself. |
| 3 | Volume mounted at `/data/database` | Orders disappear after `docker compose down` and `up` | Placed an order, restarted, `GET /orders` returned `[]`; `ls /data/database` was empty | Mount at `/data/db`, where MongoDB actually stores data |
| 4 | Database published to the host (`27017:27017`) with a password in the file | MongoDB reachable from outside the stack | `docker compose port db 27017` → `0.0.0.0:27017` | Removed `ports` from `db`; the API reaches it over the internal network. Credentials moved to `.env` (see README). |
| 5 | `image: mongo:latest` | Different developers can get different database versions | `docker compose exec db mongod --version` → `v8.3.11` | Pinned to `mongo:8.3`, the version the data was created with |

Also removed `version: "3.8"`: Compose ignores it and warns that it is obsolete.

## Not one of Neha's mistakes: port 5000 on macOS

On macOS, port 5000 is used by AirPlay Receiver, so the API is published on host port **5050** (`5050:8000`). The left number is the port on the host; the right number is the port inside the container. Containers talk to each other on the right-hand number.
