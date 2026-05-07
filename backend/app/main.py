"""Codetta API 入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, questions, progress, judge, export

app = FastAPI(title="Codetta API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(progress.router)
app.include_router(judge.router)
app.include_router(export.router)


@app.get("/api/health")
def health():
    return {"ok": True}
