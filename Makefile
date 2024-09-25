# Description: Makefile for the project
.PHONY: be


be:
	@echo "Starting backend"
	poetry run uvicorn backend.main:app --reload

db:
	@echo "Starting database"
	docker compose -f dockerfiles/postgre-docker-compose.yaml up -d