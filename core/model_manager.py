import os
import boto3
from botocore.config import Config

from typing import Optional
from langchain_core.runnables import RunnableConfig

from agent.configuration import Configuration

from langchain_aws import ChatBedrockConverse
from langchain_openai import AzureChatOpenAI, ChatOpenAI


class ModelManager:
    def __init__(self, config: Optional[RunnableConfig] = None):
        self.config = Configuration.from_runnable_config(config)

    def configure_boto_client(self, model_id):
        bedrock_config = Config(
            read_timeout=300,
            connect_timeout=60,
            retries={'max_attempts': 3}
        )

        return boto3.client(
            'bedrock-runtime',
            region_name=self.config.aws_region,
            config=bedrock_config,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

    def configure_bedrock_client(self, model_id) -> ChatBedrockConverse:
        bedrock_config = Config(
            read_timeout=300,
            connect_timeout=60,
            retries={
                'max_attempts': 3,
            }
        )

        bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=self.config.aws_region,
            config=bedrock_config
        )

        return ChatBedrockConverse(
            model_id=model_id,
            client=bedrock_client,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.config.aws_region,
            temperature=self.config.temperature,
        )

    def configure_azure_client(self, deployment_name) -> AzureChatOpenAI:
        return AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            deployment_name=deployment_name,
        )
    
    def configure_openai_client(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self.config.openai_native_model,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=self.config.temperature,
        )