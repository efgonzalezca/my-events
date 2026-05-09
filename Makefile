COMPOSE_DEV := docker compose -f docker-compose.yml -f docker-compose.dev.yml
SVC         := backend

.PHONY: help dev down logs shell lock build test migrate upgrade downgrade

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
	@echo ""
	@echo "Migrations (Alembic):"
	@echo "  make migrate m=\"...\"    - new revision (autogenerate) + upgrade head"
	@echo "  make upgrade            - alembic upgrade head"
	@echo "  make downgrade          - alembic downgrade -1"

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

test:
	$(COMPOSE_DEV) exec $(SVC) pytest -v

migrate:
ifndef m
	$(error usage: make migrate m="message")
endif
	$(COMPOSE_DEV) exec $(SVC) alembic revision --autogenerate -m "$(m)"
	$(COMPOSE_DEV) exec $(SVC) alembic upgrade head

upgrade:
	$(COMPOSE_DEV) exec $(SVC) alembic upgrade head

downgrade:
	$(COMPOSE_DEV) exec $(SVC) alembic downgrade -1
