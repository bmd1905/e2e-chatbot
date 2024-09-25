from fastapi import FastAPI

from .core.database import init_db

app = FastAPI(
    title="E2E Chatbot Platform",
    description="A fully-featured chatbot platform with authentication, subscriptions, and more.",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/health", tags=["Health"])
async def read_root():
    """
    Health check endpoint.

    - **Returns**: Status of the application.
    """
    return {"status": "OK"}
