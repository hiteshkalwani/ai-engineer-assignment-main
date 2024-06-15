from pydantic import BaseModel


class CodeTestsImproveRequest(BaseModel):
    code: str
    language: str
    test_cases: str
    test_feedback: str