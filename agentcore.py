from bedrock_agentcore.runtime import BedrockAgentCoreApp
from services.process_research import ResearchRequest, ProcessResearchService
from services.s3 import S3UploadService

import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = BedrockAgentCoreApp()

RESEARCH_BUCKET = os.getenv("RESEARCH_BUCKET", "legislation-agent-outputs")
AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")

@app.entrypoint
async def agent_invocation(payload, context):
    try: 
        logger.info(f"Received payload: {payload}")

        required_fields = ["user_id", "research_id", "research_topic"]

        for field in required_fields:
            if not payload.get(field):
                raise ValueError(f"Missing required field: {field}")

        research_request = ResearchRequest(
            user_id=payload.get("user_id"),
            research_id=payload.get("research_id"),
            research_topic=payload.get("research_topic")
        )

        s3 = S3UploadService(RESEARCH_BUCKET, AWS_REGION)

        research_service = ProcessResearchService(research_request, s3)
        result = await research_service.process_research()

        if not result:
            raise Exception("Failed to process research request")


        logger.info(f"Research processing initiated for ID: {research_request.research_id}")

        return {
            "statusCode": 200, 
            "body": {
                "message": f"Research completed for investigation: {result.research_id}",
            }
        }

    except Exception as e:
        logger.error(f"Error in agent invocation: {e}")
        return {
            "statusCode": 500,
            "body": {
                "error": str(e)
            }
        }

if __name__ == "__main__":
    app.run()

