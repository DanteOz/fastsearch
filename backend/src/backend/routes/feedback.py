from datetime import datetime
from enum import IntEnum

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text

from backend.database import engine

router = APIRouter()


class Relevance(IntEnum):
    pos = 1
    neg = -1


class Feedback(BaseModel):
    feedback: Relevance
    query: str
    result_id: str


@router.post("/feedback", status_code=204)
def feedback(req: Feedback) -> None:
    """Insert search result feedback into feedback db."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with engine.connect() as conn:
        result = conn.execute(
            text("""\
            INSERT INTO fastsearch.feedback (query, result_id, feedback, timestamp)
            VALUES (:query, :result_id, :feedback, :timestamp);
            """),
            {
                "query": req.query,
                "result_id": req.result_id,
                "feedback": req.feedback.value,
                "timestamp": timestamp,
            },
        )
        conn.commit()
    if result.rowcount != 1:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="could not submit feedback.",
        )
