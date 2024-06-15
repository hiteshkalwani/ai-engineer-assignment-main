from pydantic import BaseModel


class CodeRequest(BaseModel):
    description: str
    language: str
