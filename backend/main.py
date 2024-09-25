from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.database import init_db
from .routers import auth_router, chatbot_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        yield
    finally:
        pass


app = FastAPI(
    title="E2E Chatbot Platform",
    description="A fully-featured chatbot platform with authentication, subscriptions, and more.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(chatbot_router)


@app.get("/health", tags=["Health"])
async def read_root():
    """
    Health check endpoint.

    - **Returns**: Status of the application.
    """
    return {"status": "OK"}
