.PHONY: help up down logs ps test

PORT ?= 80

help:  ## list the targets
	@grep -E '^[a-z]+:.*## ' Makefile | awk -F':.*## ' '{printf "  make %-6s %s\n", $$1, $$2}'

up: .env  ## build, start and wait until everything is healthy
	docker compose up -d --build --wait

down:  ## stop and remove containers (data is kept)
	docker compose down

logs:  ## follow logs of all services
	docker compose logs -f --tail 50

ps:  ## status and health of each service
	docker compose ps

test:  ## smoke test through the proxy
	@curl -fsS localhost:$(PORT)/healthz > /dev/null && echo "ok   proxy     /healthz"
	@curl -fsS localhost:$(PORT)/ | grep -q "BrewCart Menu" && echo "ok   frontend  /"
	@curl -fsS localhost:$(PORT)/api/health | grep -q '"db":"up"' && echo "ok   api + db  /api/health"
	@curl -fsS localhost:$(PORT)/api/menu | grep -q Espresso && echo "ok   api       /api/menu"
	@echo "all checks passed"

.env:
	cp .env.example .env
	@echo "Created .env from .env.example - set MONGO_PASSWORD before the first start"