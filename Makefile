# Description: Makefile for the project
.PHONY: be


be:
	@echo "Starting backend"
	poetry run uvicorn backend.main:app --reload