import os
from pydantic import BaseModel, Field
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig


class Configuration(BaseModel):
    """The configuration for the agent."""
    llm_provider: str = Field(
        default="bedrock",
        metadata={
            "description": "The LLM provider to use. Options are 'anthropic', 'openai', 'azure', 'bedrock'."
        },
    )

    aws_region: str = Field(
        default="eu-west-2",
        metadata={
            "description": "The AWS region to use for Bedrock and other AWS services."
        }
    )

    temperature: float = Field(
        default=1.0,
        metadata={
            "description": "The temperature to use for the language model."
        }
    )

    openai_native_model: str = Field(
        default="gpt-5",
        metadata={
            "description": "The name of the OpenAI model to use when llm_provider is set to 'openai'."
        }
    )

    default_thinking_model: str = Field(
        default="eu.anthropic.claude-3-5-sonnet-20240620-v1:0",
        metadata={
            "description": "The name of the language model to use for the agent's default thinking."
        },
    )

    query_generator_model: str = Field(
        default="eu.anthropic.claude-3-5-sonnet-20240620-v1:0",
        metadata={
            "description": "The name of the language model to use for the agent's query generation."
        },
    )

    reflection_model: str = Field(
        default="eu.anthropic.claude-3-5-sonnet-20240620-v1:0",
        metadata={
            "description": "The name of the language model to use for the agent's reflection."
        },
    )

    answer_model: str = Field(
        default="eu.anthropic.claude-3-5-sonnet-20240620-v1:0",
        metadata={
            "description": "The name of the language model to use for the agent's answer."
        },
    )

    number_of_initial_queries: int = Field(
        default=1,
        metadata={"description": "The number of initial search queries to generate."},
    )

    max_research_loops: int = Field(
        default=1,
        metadata={"description": "The maximum number of research loops to perform."},
    )

    max_search_results: int = Field(
        default=2,
        metadata={"description": "The maximum number of search results returned from the Tavily Search API."}
    )

    tavily_api_key: str = Field(
        default="",
        metadata={"description": "The API key for the Tavily Search API."}
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
