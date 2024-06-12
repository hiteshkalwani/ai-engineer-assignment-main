from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.api import code_generator
import openai
import os

app = FastAPI()

# Load environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up templates directory
templates = Jinja2Templates(directory="app/templates")

# Serve static files (like JavaScript and CSS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Include the code_generator router
app.include_router(code_generator.router)

# Additional endpoints for generating tests, improving tests, and running tests
