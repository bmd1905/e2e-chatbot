# Description: Makefile for the project
.PHONY: be, test


be:
	@echo "Starting backend"
	poetry run uvicorn backend.main:app --reload

db:
	@echo "Starting database"
	docker compose -f dockerfiles/postgre-docker-compose.yaml up -d

test:
	@echo "Running tests"
	poetry run pytest