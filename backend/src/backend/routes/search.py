import os
from datetime import datetime

import onnxruntime as ort
import transformers
from fastapi import APIRouter, BackgroundTasks
from huggingface_hub import hf_hub_download
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sqlalchemy import text
from transformers import AutoTokenizer

from backend.database import engine

transformers.logging.set_verbosity_error()

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION")
NUM_CANDIDATES = int(os.getenv("NUM_CANDIDATES"))
NUM_RESULTS = int(os.getenv("NUM_RESULTS"))


class ONNXRetriever:
    def __init__(self, model_id: str) -> None:
        session_opts = ort.SessionOptions()
        session_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        model_path = hf_hub_download(model_id, "model.onnx", local_files_only=True)
        self.encoder = ort.InferenceSession(model_path, session_opts)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)

    def __call__(self, query: str) -> list[float]:
        """Create embedding for user query."""
        tokens = self.tokenizer(query, return_tensors="np", truncation=True)
        embedding = self.encoder.run(None, dict(**tokens))
        return embedding[0].tolist()


class ONNXRanker:
    def __init__(self, model_id: str) -> None:
        session_opts = ort.SessionOptions()
        session_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        model_path = hf_hub_download(model_id, "model.onnx", local_files_only=True)
        self.ranker = ort.InferenceSession(model_path, session_opts)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)

    def __call__(self, query: str, candidates: list[str], num_results: int) -> list[int]:
        """Reranks candidate documents against query. Returns list of ranked indicies."""
        tokens = self.tokenizer(
            [query for _ in range(len(candidates))],
            candidates,
            return_tensors="np",
            padding=True,
            truncation=True,
        )
        scores = self.ranker.run(None, dict(**tokens))
        return scores[0].argsort().tolist()[:num_results]


retriever = ONNXRetriever(model_id=os.getenv("RETRIEVER_MODEL"))
ranker = ONNXRanker(model_id=os.getenv("RANKING_MODEL"))


router = APIRouter()


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


def log_search(query: str) -> None:
    """Insert user query into feedback db."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with engine.connect() as conn:
        conn.execute(
            "INSERT INTO fastsearch.queries (query, timestamp) VALUES (:query, :timestamp);",
            {"query": query, "timestamp": timestamp},
        )
        conn.commit()


@router.get("/search")
def search(query: str, tasks: BackgroundTasks) -> list[Result]:
    """Find lecture segments relevant to user query."""
    tasks.add_task(log_search, query=query)

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
