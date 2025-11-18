import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from bson import ObjectId
from datetime import datetime, timezone

from database import db, create_document, get_documents
from schemas import VideoJob, VideoJobOut, ClipRequest, ClipResult, DetectedMoment

app = FastAPI(title="AI Clipper Backend", description="Analyze YouTube links, find key moments, and generate clip overlays.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AI Clipper Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Utility
class AnalyzeRequest(BaseModel):
    youtube_url: str

@app.post("/api/analyze", response_model=VideoJobOut)
def analyze_youtube(req: AnalyzeRequest):
    """Simulate analysis of a YouTube link and store a job in DB.
    In a real system, you would fetch transcript/audio, run ML to detect highlights.
    Here, we'll create heuristic moments and save.
    """
    if not req.youtube_url or "youtube" not in req.youtube_url:
        raise HTTPException(status_code=400, detail="URL harus berupa link YouTube yang valid")

    # Heuristic demo moments
    moments = [
        DetectedMoment(start_sec=5, end_sec=12, label="Intro punch", confidence=0.91),
        DetectedMoment(start_sec=35, end_sec=48, label="Key point", confidence=0.88),
        DetectedMoment(start_sec=120, end_sec=136, label="Best moment", confidence=0.93),
    ]

    job = VideoJob(
        youtube_url=req.youtube_url,
        title=None,
        author=None,
        thumbnail_url=None,
        status="analyzed",
        detected_moments=moments,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    job_id = create_document("videojob", job)

    # Return with id field that matches response model
    return {**job.model_dump(), "id": job_id}

@app.get("/api/jobs", response_model=List[VideoJobOut])
def list_jobs(limit: int = 20):
    docs = get_documents("videojob", {}, limit)
    norm: List[dict] = []
    for d in docs:
        # Convert ObjectId to string and expose as id
        _id = d.get("_id")
        if isinstance(_id, ObjectId):
            d["id"] = str(_id)
        elif _id is not None:
            d["id"] = str(_id)
        # Remove raw _id to keep output clean (response_model filters anyway)
        d.pop("_id", None)
        norm.append(d)
    return norm

@app.get("/api/jobs/{job_id}", response_model=VideoJobOut)
def get_job(job_id: str):
    try:
        doc = db["videojob"].find_one({"_id": ObjectId(job_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Job tidak ditemukan")
        doc["id"] = str(doc.pop("_id"))
        return doc
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="ID tidak valid")

@app.post("/api/clip", response_model=ClipResult)
def create_clip(req: ClipRequest):
    # Validate job exists
    try:
        _ = db["videojob"].find_one({"_id": ObjectId(req.job_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Job ID tidak valid")

    if req.end_sec <= req.start_sec:
        raise HTTPException(status_code=400, detail="end_sec harus lebih besar dari start_sec")

    # Fake render: produce a mock preview URL and return overlays configuration
    preview_url = f"https://placehold.co/1280x720?text=Clip+{req.start_sec:.0f}-{req.end_sec:.0f}s"
    result = ClipResult(
        job_id=req.job_id,
        preview_url=preview_url,
        start_sec=req.start_sec,
        end_sec=req.end_sec,
        overlays=req.overlays,
        animation=req.animation,
        emoji=req.emoji,
        created_at=datetime.now(timezone.utc)
    )
    return result

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
