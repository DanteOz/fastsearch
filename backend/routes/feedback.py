from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from database import engine

router = APIRouter()


class Feedback(BaseModel):
    feedback: int
    query: str
    result_id: str


@router.post("/feedback", status_code=204)
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
