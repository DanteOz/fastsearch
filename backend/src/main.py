import os
from datetime import datetime

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sqlalchemy import URL, create_engine, text

from model import ONNXRanker, ONNXRetriever

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION")
NUM_CANDIDATES = int(os.getenv("NUM_CANDIDATES"))
NUM_RESULTS = int(os.getenv("NUM_RESULTS"))

PG_HOST = os.getenv("PGHOST")
PG_DATABASE = os.getenv("PGDATABASE")
PG_USER = os.getenv("PGUSER")
PG_PASSWORD = os.getenv("PGPASSWORD")


retriever = ONNXRetriever(model_id=os.getenv("RETRIEVER_MODEL"))
ranker = ONNXRanker(model_id=os.getenv("RANKING_MODEL"))
engine = create_engine(
    url=URL.create(
        drivername="postgresql+psycopg",
        host=PG_HOST,
        database=PG_DATABASE,
        username=PG_USER,
        password=PG_PASSWORD,
        query={"sslmode": "require"},
    )
)

app = FastAPI(title="FastSearch", description="Semantic search for fast.ai lectures.")


@app.get("/")
def index() -> dict:
    return {"msg": "success"}


class Feedback(BaseModel):
    feedback: int
    query: str
    result_id: str


@app.post("/api/feedback", status_code=204)
def feedback(req: Feedback):
    """Insert search result feedback into feedback db."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with engine.connect() as conn:
        sql = text(
            """
            INSERT INTO 
                fastsearch.feedback (query, result_id, feedback, timestamp) 
            VALUES (
                :query, 
                :result_id, 
                :feedback, 
                :timestamp
            );
            """
        )
        conn.execute(
            sql,
            {
                "query": req.query,
                "result_id": req.result_id,
                "feedback": req.feedback,
                "timestamp": timestamp,
            },
        )
        conn.commit()


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
            text(
                "INSERT INTO fastsearch.queries (query, timestamp) VALUES (:query, :timestamp);"
            ),
            {"query": query, "timestamp": timestamp},
        )
        conn.commit()


@app.get("/api/search")
def search(query: str, tasks: BackgroundTasks) -> list[Result]:
    """Find lecture segments relevant to user query."""
    tasks.add_task(insert_query, query=query)

    client = QdrantClient(
        host=QDRANT_HOST,
        api_key=QDRANT_API_KEY,
        prefer_grpc=True,
        https=(QDRANT_API_KEY is not None and QDRANT_API_KEY != ""),
    )
    # Stage: Retrival
    sentence_embed = retriever(query)
    candidates = client.search(
        collection_name=QDRANT_COLLECTION,
        search_params=models.SearchParams(hnsw_ef=len(sentence_embed), exact=False),
        query_vector=sentence_embed,
        limit=NUM_CANDIDATES,
    )

    # Stage: Rerank
    documents = [c.payload["text"] for c in candidates]
    ranked_idxs = ranker(query=query, candidates=documents, num_results=NUM_RESULTS)
    ranked_candidates = (candidates[i] for i in ranked_idxs)

    results = []
    for candidate in ranked_candidates:
        candidate.payload["start"] = int(candidate.payload["start"])
        results.append(Result(id=candidate.id, **candidate.payload))

    return results
