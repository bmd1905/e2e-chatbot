from fastapi import FastAPI

app = FastAPI(
    title="E2E Chatbot Platform",
    description="A fully-featured chatbot platform with authentication, subscriptions, and more.",
    version="1.0.0",
)


@app.get("/health", tags=["Health"])
async def read_root():
    """
    Health check endpoint.

    - **Returns**: Status of the application.
    """
    return {"status": "OK"}
