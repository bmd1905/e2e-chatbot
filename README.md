# End-to-end Chatbot


### Backend

#### Start PostgreSQL

```bash
make db
```

#### FastAPI

```bash
make be
```

```bash
poetry run alembic revision --autogenerate -m "initial migration"
poetry run alembic upgrade head
```