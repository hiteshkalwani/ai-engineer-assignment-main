from fastapi import APIRouter, HTTPException
from app.models import CodeRequest, FeedbackRequest
import openai
import os

# Load environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the router
router = APIRouter()

@router.post("/generate_code")
async def generate_code(request: CodeRequest):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Generate {request.language} code for: {request.description}",
            max_tokens=150
        )
        code = response.choices[0].text.strip()
        return {"code": code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Provide Feedback Endpoint
@router.post("/improve_code")
async def improve_code(request: FeedbackRequest):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Improve this {request.language} code based on the feedback: {request.feedback}\n\n{request.code}",
            max_tokens=150
        )
        improved_code = response.choices[0].text.strip()
        return {"code": improved_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))