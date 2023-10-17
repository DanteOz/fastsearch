from datetime import datetime

from sqlalchemy import text
from database import engine
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Feedback(BaseModel):
    feedback: int
    query: str
    result_id: str


@router.put("/feedback")
def feedback(req: Feedback):
    """Insert search result feedback into feedback db."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with engine.connect() as conn:
        sql = text(
            """
            INSERT INTO 
                feedback (query, result_id, feedback, timestamp) 
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
