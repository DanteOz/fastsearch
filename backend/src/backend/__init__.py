from fastapi import APIRouter, FastAPI

from backend.routes import feedback, search

app = FastAPI(
    title="FastSearch",
    description="Semantic search for fast.ai lectures.",
)


# Declare API routes
api = APIRouter(prefix="/api", tags=["api"])
api.include_router(search.router)
api.include_router(feedback.router)
app.include_router(api)


@app.get("/")
def root() -> dict:
    return {"msg": "success"}
