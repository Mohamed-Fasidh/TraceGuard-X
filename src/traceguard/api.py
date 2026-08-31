from fastapi import FastAPI
from pydantic import BaseModel
from src.traceguard.pipeline import evaluate_one

app = FastAPI(
    title="TraceGuard X API",
    version="2.0.0",
    description="Evidence-first, adversarial evaluation for coding-agent trajectories."
)

class Request(BaseModel):
    trace: dict

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}

@app.post("/evaluate")
def evaluate(req: Request):
    return evaluate_one(req.trace)
