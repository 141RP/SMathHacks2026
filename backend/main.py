from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, surveys, coverage

app = FastAPI(title="ReefSync API")

# CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(surveys.router, prefix="/surveys", tags=["Surveys"])
app.include_router(coverage.router, prefix="/coverage", tags=["Coverage"])
