# Description: Makefile for the project
.PHONY: fe, be, test


fe:
	@echo "Starting frontend"
	poetry run python3 -m frontend.gradio_app

be:
	@echo "Starting backend"
	poetry run uvicorn backend.main:app --reload

db:
	@echo "Starting database"
	docker compose -f dockerfiles/postgre-docker-compose.yaml up -d

test:
	@echo "Running tests"
	poetry run pytest