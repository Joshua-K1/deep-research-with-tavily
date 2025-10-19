# Graph Engine Service

An AI-powered research automation service that generates comprehensive, well-structured research reports using LangGraph and AWS Bedrock. The service combines web search, multi-step reasoning, and large language models to produce detailed, cited research documents.

## Features

- **Multi-Stage Research Pipeline**: Orchestrates web search, content summarization, reflection, and report generation through a sophisticated LangGraph workflow
- **Iterative Refinement**: Automatically identifies knowledge gaps and performs follow-up research to ensure comprehensive coverage
- **Multi-LLM Support**: Flexible configuration supporting AWS Bedrock (Claude), Azure OpenAI, and OpenAI
- **Structured Output**: Generates both markdown reports and ProseMirror/Tiptap JSON for rich document formatting
- **Citation Management**: Automatic extraction and formatting of source citations from web search results
- **Async Processing**: Non-blocking research execution for improved throughput
- **AWS Integration**: Built-in support for S3 storage, Bedrock runtime, and CloudWatch observability
- **Dual Deployment Modes**: Run as REST API service or AWS Bedrock AgentCore runtime

## Architecture

The service implements a graph-based workflow with the following stages:

1. **Query Generation**: LLM generates optimized search queries based on the research topic
2. **Web Research**: Parallel execution of web searches using Tavily API
3. **Summarization**: LLM summarizes search results with proper citations
4. **Reflection**: Analyzes knowledge gaps and generates follow-up queries
5. **Loop Control**: Decides whether to continue researching or finalize the report
6. **Report Generation**: Creates comprehensive markdown report with 10-section structure
7. **Storage**: Uploads final report to S3

```
┌─────────────────┐
│ Research Request│
└────────┬────────┘
         │
         ▼
  ┌──────────────┐
  │Generate Query│
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Web Research │◄───┐
  │  (Parallel)  │    │
  └──────┬───────┘    │
         │            │
         ▼            │
  ┌──────────────┐    │
  │ Reflection   │    │
  └──────┬───────┘    │
         │            │
         ▼            │
    ┌────────┐        │
    │Continue?├────Yes┘
    └───┬────┘
        │No
        ▼
  ┌──────────────┐
  │   Finalize   │
  │    Answer    │
  └──────┬───────┘
         │
         ▼
    ┌────────┐
    │S3 Upload│
    └────────┘
```

## Prerequisites

- Python 3.13 or higher
- AWS Account with Bedrock access
- Tavily API Key (for web search)
- S3 bucket for report storage

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd graph-engine-service
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with required environment variables:
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=eu-west-1
RESEARCH_BUCKET=your-s3-bucket-name

# Tavily Search API
TAVILY_API_KEY=your_tavily_api_key

# Optional: Azure OpenAI (if using Azure)
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_api_key
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Optional: OpenAI (if using OpenAI directly)
OPENAI_API_KEY=your_openai_api_key
```

## Configuration

The agent can be configured via the `agent/configuration.py` file:

```python
class Configuration:
    # LLM Provider Selection
    llm_provider: str = "bedrock"  # Options: "bedrock", "azure", "openai"

    # AWS Configuration
    aws_region: str = "eu-west-2"

    # Model Configuration (per task)
    query_generator_model: str = "eu.anthropic.claude-3-5-sonnet-20241022-v2:0"
    reflection_model: str = "eu.anthropic.claude-3-5-sonnet-20241022-v2:0"
    answer_model: str = "eu.anthropic.claude-3-5-sonnet-20241022-v2:0"

    # Research Parameters
    number_of_initial_queries: int = 1    # Number of initial search queries
    max_research_loops: int = 1           # Maximum reflection/research loops
    max_search_results: int = 2           # Results per search query

    # LLM Parameters
    temperature: float = 1.0
    max_tokens: int = 4096
```

## Usage

### Option 1: REST API Server

Start the FastAPI server:
```bash
python main.py
```

The server will start on `http://0.0.0.0:8000`.

**Create a research request**:
```bash
curl -X POST http://localhost:8000/research/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "research_id": "research456",
    "research_topic": "Recent developments in renewable energy technologies"
  }'
```

**Response**:
```json
{
  "message": "Research has started for research_id: research456",
  "research_id": "research456"
}
```

The research report will be stored in S3 at: `s3://{RESEARCH_BUCKET}/research456/user123-research.md`


### Option 2: AWS Bedrock AgentCore

Deploy to AWS Bedrock using the configuration in `.bedrock_agentcore.yaml`:
```bash
# Configure the agent
agentcore configure -e agentcore.py

# Launch the agent
agentcore launch --env env=$env

```

## API Reference

### POST /research/create

Creates a new research request and processes it asynchronously.

**Request Body**:
```json
{
  "user_id": "string",         // User identifier
  "research_id": "string",     // Unique research identifier
  "research_topic": "string"   // Research topic or question
}
```



## Project Structure

```
graph-engine-service/
├── agent/                          # Core agent logic
│   ├── configuration.py            # Agent configuration
│   ├── graph.py                    # LangGraph workflow definition
│   ├── state.py                    # Graph state schemas
│   ├── prompts.py                  # System prompts for each node
│   ├── tools_and_schemas.py        # Pydantic models for structured output
│   ├── utils.py                    # Citation & message utilities
│   └── wiki.py                     # ProseMirror/Tiptap JSON conversion
├── api/                            # REST API layer
│   └── routes/
│       ├── research.py             # Research endpoints
│       └── health.py               # Health check routes
├── services/                       # Business logic services
│   ├── process_research.py        # Research orchestration
│   └── s3.py                       # S3 file upload service
├── core/                           # Shared utilities
│   ├── model_manager.py            # LLM client configuration
│   └── utils.py                    # Citation generation utilities
├── examples/                       # Example outputs
│   └── renewable_energy.md         # Sample research report
├── agentcore.py                    # Bedrock AgentCore entry point
├── main.py                         # FastAPI app entry point
├── Dockerfile                      # Docker build configuration
├── requirements.txt                # Python dependencies
├── .bedrock_agentcore.yaml        # Bedrock deployment config
└── README.md                       # This file
```



## Output Format

Research reports are generated with the following structure:

1. **Executive Summary**: Key findings overview
2. **Introduction**: Research context and methodology
3. **Background**: Historical context and current state
4. **Comprehensive Findings**: Detailed research results with citations
5. **Cross-Source Synthesis**: Integration of information across sources
6. **Critical Analysis**: Evaluation of findings and methodologies
7. **Implications**: Broader significance and recommendations
8. **Future Outlook**: Emerging trends and predictions
9. **Conclusion**: Summary and key takeaways
10. **References**: Formatted citations of all sources

See `examples/renewable_energy.md` for a sample output.



