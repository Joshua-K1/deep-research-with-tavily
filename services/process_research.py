from pydantic import BaseModel
from agent.graph import graph
from services.s3 import S3UploadService
import logging

logger = logging.getLogger(__name__)


class ResearchRequest(BaseModel):
    user_id: str
    research_id: str
    research_topic: str


class ResearchResponse(BaseModel):
    research_id: str
    research_topic: str
    research_content: str


class ProcessResearchService:
    """Service for processing research requests"""

    def __init__(self, request: ResearchRequest, s3: S3UploadService):
        self.request = request
        self.s3 = s3


    async def process_research(self) -> ResearchResponse:
        try: 
            response = graph.invoke({"messages": [self.request.research_topic]})
            response_content = response["messages"][-1].content

            if (response_content is None or response_content.strip() == ""):
                raise ValueError("No response content received from graph")
            
            upload_result = await self.s3.uploadFile(
                content=response_content,
                s3_key=f"{self.request.research_id}/{self.request.user_id}-research.md",
                content_type="text/markdown"
            )

            if not upload_result:
                raise Exception("Failed to upload research content to S3")
            
            logger.info(f"Processed and uploaded research for ID: {self.request.research_id}")

            return ResearchResponse(
                research_id=self.request.research_id,
                research_topic=self.request.research_topic,
                research_content=response_content
            )
            
        except Exception as e:
            logger.error(f"Error processing research: {e}")
