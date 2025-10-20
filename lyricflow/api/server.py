"""FastAPI service for LyricFlow."""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from pathlib import Path
import tempfile
import os

from lyricflow.core.lyrics_sync import LyricsSync
from lyricflow.core.romanizer import Romanizer
from lyricflow.utils.config import Config
from lyricflow.utils.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="LyricFlow API",
    description="Automated processing and embedding of song lyrics",
    version="0.1.0"
)

# Task storage (in production, use Redis or database)
tasks: Dict[str, Dict[str, Any]] = {}

# Initialize services
config = Config.load()
lyrics_sync = LyricsSync(config)
romanizer = Romanizer(config)


class ProcessResponse(BaseModel):
    """Response for process endpoint."""
    task_id: str
    status: str
    message: str


class StatusResponse(BaseModel):
    """Response for status endpoint."""
    status: str
    progress: float
    result: Optional[dict] = None
    error: Optional[str] = None


class RomanizeRequest(BaseModel):
    """Request for romanize endpoint."""
    text: str
    language: str = "ja"
    use_ai: bool = False


class RomanizeResponse(BaseModel):
    """Response for romanize endpoint."""
    original: str
    romanized: str
    language: str


class FetchRequest(BaseModel):
    """Request for fetch endpoint."""
    title: str
    artist: Optional[str] = None
    album: Optional[str] = None
    fetch_translation: bool = False
    fetch_romanization: bool = False


class LyricResultModel(BaseModel):
    """Model for a single lyric result."""
    track_id: int
    title: str
    artist: str
    album: str
    duration: int
    has_lyrics: bool
    has_subtitles: bool
    rating: int
    match_score: Optional[float] = None
    lyrics: Optional[str] = None
    synced_lyrics: Optional[str] = None
    translation: Optional[str] = None
    romanization: Optional[str] = None


class FetchResponse(BaseModel):
    """Response for fetch endpoint."""
    query: Dict[str, str]
    results_count: int
    results: list[LyricResultModel]


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "LyricFlow API",
        "version": "0.1.0",
        "endpoints": {
            "POST /process": "Upload audio file for processing",
            "GET /status/{task_id}": "Get processing status",
            "POST /romanize": "Romanize text",
            "POST /fetch/search": "Search for lyrics on Musixmatch",
            "GET /fetch/{track_id}": "Get lyrics for specific track",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/process", response_model=ProcessResponse)
async def process_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    use_ai: bool = False,
    overwrite: bool = False
):
    """
    Upload an audio file for lyrics processing.
    
    Returns a task_id to track progress.
    """
    # Validate file type
    valid_extensions = {'.mp3', '.m4a', '.flac', '.ogg', '.opus', '.wma'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Supported: {', '.join(valid_extensions)}"
        )
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Initialize task
    tasks[task_id] = {
        "status": "pending",
        "progress": 0.0,
        "filename": file.filename,
        "result": None,
        "error": None
    }
    
    # Save uploaded file temporarily
    temp_dir = Path(tempfile.gettempdir()) / "lyricflow"
    temp_dir.mkdir(exist_ok=True)
    temp_file = temp_dir / f"{task_id}_{file.filename}"
    
    try:
        content = await file.read()
        temp_file.write_bytes(content)
        
        # Schedule background processing
        background_tasks.add_task(
            process_audio_task,
            task_id,
            temp_file,
            use_ai,
            overwrite
        )
        
        return ProcessResponse(
            task_id=task_id,
            status="pending",
            message=f"Processing started for {file.filename}"
        )
    
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_audio_task(
    task_id: str,
    file_path: Path,
    use_ai: bool,
    overwrite: bool
):
    """Background task for processing audio file."""
    try:
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 0.1
        
        # Process the file
        result = lyrics_sync.process_audio_file(
            file_path,
            use_ai=use_ai,
            overwrite=overwrite,
            no_embed=False
        )
        
        tasks[task_id]["status"] = "complete"
        tasks[task_id]["progress"] = 1.0
        tasks[task_id]["result"] = result
    
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
    
    finally:
        # Clean up temporary file
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete temp file: {e}")


@app.get("/status/{task_id}", response_model=StatusResponse)
async def get_status(task_id: str):
    """
    Get the status of a processing task.
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    return StatusResponse(
        status=task["status"],
        progress=task["progress"],
        result=task.get("result"),
        error=task.get("error")
    )


@app.post("/romanize", response_model=RomanizeResponse)
async def romanize_text(request: RomanizeRequest):
    """
    Romanize text.
    
    Accepts JSON with text and returns romanized version.
    """
    try:
        romanized = romanizer.romanize(
            request.text,
            language=request.language,
            use_ai=request.use_ai
        )
        
        return RomanizeResponse(
            original=request.text,
            romanized=romanized,
            language=request.language
        )
    except Exception as e:
        logger.error(f"Romanization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fetch/search", response_model=FetchResponse)
async def fetch_lyrics_search(request: FetchRequest):
    """
    Search for lyrics on Musixmatch.
    
    Returns a list of matching tracks with lyrics.
    """
    try:
        from lyricflow.core.musixmatch import MusixmatchFetcher
        
        fetcher = MusixmatchFetcher()
        results = fetcher.search(
            title=request.title,
            artist=request.artist,
            album=request.album,
            fetch_lyrics=True,
            fetch_translation=request.fetch_translation,
            fetch_romanization=request.fetch_romanization
        )
        
        # Convert to Pydantic models and add match scores
        result_models = []
        for result in results:
            match_score = result.match_score(request.title, request.artist or "")
            
            result_models.append(LyricResultModel(
                track_id=result.track_id,
                title=result.title,
                artist=result.artist,
                album=result.album,
                duration=result.duration,
                has_lyrics=result.has_lyrics,
                has_subtitles=result.has_subtitles,
                rating=result.rating,
                match_score=match_score,
                lyrics=result.lyrics,
                synced_lyrics=result.synced_lyrics,
                translation=result.translation,
                romanization=result.romanization
            ))
        
        # Sort by match score
        result_models.sort(key=lambda r: r.match_score or 0, reverse=True)
        
        return FetchResponse(
            query={
                "title": request.title,
                "artist": request.artist or "",
                "album": request.album or ""
            },
            results_count=len(result_models),
            results=result_models
        )
    
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Musixmatch fetcher not available. Install with: pip install requests"
        )
    except Exception as e:
        logger.error(f"Fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/fetch/{track_id}")
async def fetch_lyrics_by_id(
    track_id: int,
    synced: bool = True,
    translation: bool = False,
    romanization: bool = False
):
    """
    Get lyrics for a specific Musixmatch track ID.
    
    Args:
        track_id: Musixmatch common track ID
        synced: Get synced lyrics (LRC format)
        translation: Get translation
        romanization: Get romanization
    """
    try:
        from lyricflow.core.musixmatch import MusixmatchAPI
        
        api = MusixmatchAPI()
        
        result = {
            "track_id": track_id,
            "lyrics": None,
            "synced_lyrics": None,
            "translation": None,
            "romanization": None
        }
        
        # Fetch lyrics
        if synced:
            result["synced_lyrics"] = api.get_lyrics(track_id, synced=True)
        else:
            result["lyrics"] = api.get_lyrics(track_id, synced=False)
        
        # Fetch translation (requires track_id, not commontrack_id)
        # This is a limitation - we'd need to store both IDs
        if translation:
            result["translation"] = "Translation requires track_id from search results"
        
        # Romanization
        if romanization:
            lyrics_to_romanize = result["synced_lyrics"] or result["lyrics"]
            if lyrics_to_romanize:
                result["romanization"] = romanizer.romanize(lyrics_to_romanize)
        
        return result
    
    
    except Exception as e:
        logger.error(f"Romanization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task from memory."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del tasks[task_id]
    return {"message": "Task deleted"}


@app.get("/tasks")
async def list_tasks():
    """List all tasks."""
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": task["status"],
                "filename": task.get("filename"),
                "progress": task["progress"]
            }
            for task_id, task in tasks.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
