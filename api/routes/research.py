import os
import asyncio
import logging

from services.s3 import S3UploadService
from services.process_research import (
    ResearchRequest, 
    ProcessResearchService
)

from fastapi import (
    APIRouter,
)

RESEARCH_BUCKET = os.getenv("RESEARCH_BUCKET")
AWS_REGION = os.getenv("AWS_REGION")

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create")
async def create_research(req_data: ResearchRequest): 
    logger.info("Received research request")

    s3 = S3UploadService(RESEARCH_BUCKET, AWS_REGION)

    research_service = ProcessResearchService(req_data, s3)

    asyncio.create_task(research_service.process_research())

    return {
        "message": f"Research started for investigation: {req_data.research_id}"
    }
