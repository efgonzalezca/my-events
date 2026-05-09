COMPOSE_DEV := docker compose -f docker-compose.yml -f docker-compose.dev.yml
SVC         := backend

.PHONY: help dev down logs shell lock build

help:
	@echo ""
	@echo "Stack:"
	@echo "  make dev                - up --build"
	@echo "  make down               - down"
	@echo "  make status             - ps"
	@echo "  make logs               - logs -f"
	@echo "  make build              - rebuild"
	@echo ""
	@echo "Backend (Python):"
	@echo "  make test               - pytest -v"
	@echo "  make lock               - regenerate poetry.lock"

dev:
	$(COMPOSE_DEV) up --build

down:
	$(COMPOSE_DEV) down

status:
	$(COMPOSE_DEV) ps

logs:
	$(COMPOSE_DEV) logs -f

lock:
	$(COMPOSE_DEV) run --rm $(SVC) poetry lock

build:
	$(COMPOSE_DEV) build $(SVC)
