"""
Documentation Support Agent - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import routes
from database.connection import init_db

app = FastAPI(
    title="Documentation Support Agent",
    description="AI-powered documentation quality improvement system",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(routes.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()

@app.get("/")
async def root():
    return {"message": "Documentation Support Agent API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

