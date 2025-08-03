
from llama_index.core import Settings
from llama_index.embeddings.gemini import GeminiEmbedding
from fastapi import FastAPI, HTTPException

import os
import uvicorn
from contextlib import asynccontextmanager
import dotenv
from utils.ContentReviewApp import ContentReviewApp
from consts.consts import AppError, ModelConfig
from models.submission_models import  SubmissionRequest
from fastapi.middleware.cors import CORSMiddleware
from consts.consts import CorsConfig


dotenv.load_dotenv()

Settings.embed_model = GeminiEmbedding(model_name=ModelConfig.EMBEDDING_MODEL, api_key=os.environ["GOOGLE_API_KEY"])

app_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global app_instance
    app_instance = ContentReviewApp(csv_path="data.csv")
    yield
    app_instance = None

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CorsConfig.CORSMIDDLEWARE_ALLOW_ORIGINS,
    allow_credentials=CorsConfig.CORSMIDDLEWARE_ALLOW_CREDENTIALS,
    allow_methods=CorsConfig.CORSMIDDLEWARE_ALLOW_METHODS,
    allow_headers=CorsConfig.CORSMIDDLEWARE_ALLOW_HEADERS,
)

@app.post("/review_submission")
async def review_submission_endpoint(request: SubmissionRequest):
    """API endpoint to review a single submission"""
    if app_instance is None:
        raise HTTPException(status_code=500, detail=AppError.APP_START_FAIL)
    result = app_instance.review_submission(request.campaign_id, request.submission)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/list_campaigns")
async def list_campaigns_endpoint():
    if app_instance is None:
        raise HTTPException(status_code=500, detail=AppError.APP_START_FAIL)
    campaign_ids = app_instance.get_campaign_ids()
    return {"campaign_ids": campaign_ids}

@app.get("/random_brief")
async def random_brief_endpoint():
    """API endpoint to generate a random brand brief"""
    if app_instance is None:
        raise HTTPException(status_code=500, detail=AppError.APP_START_FAIL)
    brief = app_instance.generate_random_brief()
    return {"brief": brief}

@app.get("/random_submission")
async def random_submission_endpoint():
    """API endpoint to generate a random influencer submission"""
    if app_instance is None:
        raise HTTPException(status_code=500, detail=AppError.APP_START_FAIL)
    submission = app_instance.generate_random_submission()
    return {"submission": submission}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)