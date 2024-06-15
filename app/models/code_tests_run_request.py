from pydantic import BaseModel


class CodeTestsRunRequest(BaseModel):
    code: str
    test_cases: str
    language: str
