from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logger import logger

app = FastAPI(title="EduChat Pro API", version="2.1")

# CORS Middleware
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")] if settings.ALLOWED_ORIGINS else []
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.error(f"AppException: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "code": exc.code,
            "message": exc.message,
            "status_code": exc.status_code
        }
    )

# Include Routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "EduChat Pro API is running."}
