import os
from datetime import datetime

from database import engine
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sqlalchemy import text

from routes.search.model import ONNXRanker, ONNXRetriever

router = APIRouter()


QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION")
NUM_CANDIDATES = int(os.getenv("NUM_CANDIDATES"))
NUM_RESULTS = int(os.getenv("NUM_RESULTS"))

retriever = ONNXRetriever(model_id=os.getenv("RETRIEVER_MODEL"))
ranker = ONNXRanker(model_id=os.getenv("RANKING_MODEL"))


class Query(BaseModel):
    query: str


class Result(BaseModel):
    id: int
    video_id: str
    title: str
    text: str
    start: int
    thumbnail: str
    lesson: str | None
    forum: str | None
    course: str | None


def insert_query(query: str):
    """Insert user query into feedback db."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO fastsearch.queries (query, timestamp) VALUES (:query, :timestamp);"),
            {"query": query, "timestamp": timestamp},
        )
        conn.commit()


@router.post("/search")
def search(req: Query, tasks: BackgroundTasks) -> list[Result]:
    """Find lecture segments relevant to user query."""
    tasks.add_task(insert_query, query=req.query)

    client = QdrantClient(
        host=QDRANT_HOST,
        api_key=QDRANT_API_KEY,
        prefer_grpc=True,
        https=(QDRANT_API_KEY is not None and QDRANT_API_KEY != ""),
    )
    # Stage: Retrival
    sentence_embed = retriever(req.query)
    candidates = client.search(
        collection_name=QDRANT_COLLECTION,
        search_params=models.SearchParams(hnsw_ef=len(sentence_embed), exact=False),
        query_vector=sentence_embed,
        limit=NUM_CANDIDATES,
    )

    # Stage: Rerank
    documents = [c.payload["text"] for c in candidates]
    ranked_idxs = ranker(query=req.query, candidates=documents, num_results=NUM_RESULTS)
    ranked_candidates = (candidates[i] for i in ranked_idxs)

    results = []
    for candidate in ranked_candidates:
        candidate.payload["start"] = int(candidate.payload["start"])
        results.append(Result(id=candidate.id, **candidate.payload))

    return results
