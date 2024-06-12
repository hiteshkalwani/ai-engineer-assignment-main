from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    code: str
    feedback: str
    language: str