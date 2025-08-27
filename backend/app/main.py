from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import ask, drive_router

app = FastAPI(title="Notes Assistant API")

# CORS Middleware (for later frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all domains
    allow_credentials=True,
    allow_methods=["*"], # Allow all HTTP methods (GET, POST, PUT, DELETE...)
    allow_headers=["*"], # Allow all headers
)

# Health check route
@app.get("/")
def health_check():
    return {"status": "ok"}

# Include API routes
app.include_router(ask.router, prefix="/api")
app.include_router(drive_router.router, prefix="/api")
