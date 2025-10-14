from fastapi import FastAPI
import os
import logging

# Basic logging configuration
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)
logger.info("Logging initialized with level %s", log_level)

app = FastAPI(title="Redcrawl OSINT API", version="1.0.0")

@app.lifespan("startup")
async def startup_event():
    logger.info("Starting up...")

@app.lifespan("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")

@app.get("/")
async def root():
    return {"message": "Hello World"}