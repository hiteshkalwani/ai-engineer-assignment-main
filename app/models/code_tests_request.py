from pydantic import BaseModel


class CodeTestsRequest(BaseModel):
    code: str
    language: str
