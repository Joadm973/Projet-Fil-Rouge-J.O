"""FastAPI backend — YPerf JO 2028."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import home, exploration, athletes, predictions, annotations, generations, multisource

app = FastAPI(title="YPerf API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(home.router, prefix="/api/home", tags=["home"])
app.include_router(exploration.router, prefix="/api/exploration", tags=["exploration"])
app.include_router(athletes.router, prefix="/api/athletes", tags=["athletes"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(annotations.router, prefix="/api/annotations", tags=["annotations"])
app.include_router(generations.router, prefix="/api/generations", tags=["generations"])
app.include_router(multisource.router, prefix="/api/multisource", tags=["multisource"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
