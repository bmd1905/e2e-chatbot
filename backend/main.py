from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
