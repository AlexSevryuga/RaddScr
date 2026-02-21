"""
Minimal FastAPI for testing Render deployment
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RaddScr Test API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "RaddScr API is running!", "version": "0.1.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}
