import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from core.model_manager import ModelManager
from agent.configuration import Configuration

from botocore.config import Config

logger = logging.getLogger(__name__)

import boto3
import re
import os


SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


# Mark schemas
class BoldMark(BaseModel):
    type: str = Field(default="bold", pattern="^bold$")


class ItalicMark(BaseModel):
    type: str = Field(default="italic", pattern="^italic$")


class CodeMark(BaseModel):
    type: str = Field(default="code", pattern="^code$")


class LinkMark(BaseModel):
    type: str = Field(default="link", pattern="^link$")
    attrs: Dict[str, Any] = Field(...)

    @field_validator("attrs")
    @classmethod
    def validate_attrs(cls, v):
        if "href" not in v:
            raise ValueError("Link mark must have href in attrs")
        return v


# Inline nodes
class TextNode(BaseModel):
    type: str = Field(default="text", pattern="^text$")
    text: str = Field(..., min_length=1)
    marks: Optional[List[Dict[str, Any]]] = None


class HardBreakNode(BaseModel):
    type: str = Field(default="hardBreak", pattern="^hardBreak$")


# Block nodes
class HeadingNode(BaseModel):
    type: str = Field(default="heading", pattern="^heading$")
    attrs: Dict[str, int] = Field(...)
    content: Optional[List[Dict[str, Any]]] = None

    @field_validator("attrs")
    @classmethod
    def validate_level(cls, v):
        if "level" not in v or not (1 <= v["level"] <= 6):
            raise ValueError("Heading level must be between 1 and 6")
        return v


class ParagraphNode(BaseModel):
    type: str = Field(default="paragraph", pattern="^paragraph$")
    content: Optional[List[Dict[str, Any]]] = None


class HorizontalRuleNode(BaseModel):
    type: str = Field(default="horizontalRule", pattern="^horizontalRule$")


class CodeBlockNode(BaseModel):
    type: str = Field(default="codeBlock", pattern="^codeBlock$")
    attrs: Optional[Dict[str, Any]] = None
    content: Optional[List[Dict[str, Any]]] = None


class BlockquoteNode(BaseModel):
    type: str = Field(default="blockquote", pattern="^blockquote$")
    content: List[Dict[str, Any]] = Field(..., min_length=1)


class ListItemNode(BaseModel):
    type: str = Field(default="listItem", pattern="^listItem$")
    content: List[Dict[str, Any]] = Field(..., min_length=1)


class BulletListNode(BaseModel):
    type: str = Field(default="bulletList", pattern="^bulletList$")
    content: List[Dict[str, Any]] = Field(..., min_length=1)


class OrderedListNode(BaseModel):
    type: str = Field(default="orderedList", pattern="^orderedList$")
    attrs: Optional[Dict[str, Any]] = None
    content: List[Dict[str, Any]] = Field(..., min_length=1)


# Tiptap document schema
class TiptapDoc(BaseModel):
    type: str = Field(default="doc", pattern="^doc$")
    content: List[Dict[str, Any]] = Field(default_factory=list)


# Investigation page schema
class InvestigationOutputPage(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(...)
    content: TiptapDoc
    children: List["InvestigationOutputPage"] = Field(default_factory=list)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        if not SLUG_PATTERN.match(v):
            raise ValueError("slug must be lowercase-kebab")
        return v


# Update forward reference
InvestigationOutputPage.model_rebuild()


class InvestigationOutputPages(BaseModel):
    pages: List[InvestigationOutputPage] = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_unique_slugs(self):
        seen_slugs = set()

        def walk(nodes: List[InvestigationOutputPage], path: str = ""):
            for i, node in enumerate(nodes):
                current_path = f"{path}.pages[{i}]" if path else f"pages[{i}]"
                if node.slug in seen_slugs:
                    raise ValueError(
                        f"Duplicate slug '{node.slug}' found at {current_path}"
                    )
                seen_slugs.add(node.slug)

                if node.children:
                    walk(node.children, f"{current_path}.children")

        walk(self.pages)
        return self


# Investigation DTO
class InvestigationDto(BaseModel):
    title: str


class WikiService:
    def __init__(self):
        self.name = "WikiService"

    def _create_investigation_output(self, model: type[BaseModel]) -> Dict[str, any]:
        """Convert Pydantic model to tool schema format"""
        json_schema = model.model_json_schema()

        return {"json": json_schema}

    def _convert_pydantic_to_bedrock_schema(
        self, model: type[BaseModel]
    ) -> Dict[str, Any]:
        """Convert Pydantic model to Bedrock tool schema format"""
        json_schema = model.model_json_schema()

        # Bedrock expects a specific format for tool input schema
        return {"json": json_schema}


    def generate_investigation_output(
        self, investigation: InvestigationDto, report_content: str
    ) -> InvestigationOutputPages:
        import json

        prompt = f"""
        You are transforming existing report content into a structured nested wiki JSON format.

        CONTEXT
        - Investigation title: {investigation.title}

        EXISTING REPORT CONTENT:
        {report_content}

        TASK
        Transform the above report content into a JSON object with a "pages" key containing an array of pages.
        - Analyze the existing content structure and organize it into logical pages and sub-pages
        - Preserve all the information from the original content
        - Convert the content into ProseMirror/Tiptap JSON format

        Each page object must be:
        {{
        "title": string,                 // human title derived from the content
        "slug": string,                  // lowercase-kebab; unique across the entire tree
        "content": {{ ... }},              // ProseMirror/Tiptap JSON document
        "children": [ ... ]              // array of child pages; order = nav order
        }}

        CONTENT (ProseMirror/Tiptap JSON)
        - Root of each page must be: {{ "type": "doc", "content": [...] }}.
        - Allowed block nodes: "heading", "paragraph", "bulletList", "orderedList", "listItem", "blockquote", "codeBlock", "horizontalRule", "hardBreak".
        - Inline: "text" nodes with optional marks: "bold", "italic", "code", "link" (attrs: {{ "href": URL }}).
        - Headings must include level 1..6 in attrs: {{ "level": n }}.
        - For EVERY heading, set a stable id in attrs: {{ "id": "kebab-case-anchor" }}.
        - Anchors must be lowercase-kebab and unique within the page.
        - If an anchor would duplicate, append "-2", "-3", etc.
        - Convert markdown or plain text formatting into proper ProseMirror JSON structure
        - NO Markdown or HTML strings in the output; only PM/Tiptap JSON.

        STRUCTURE
        - Analyze the content to determine logical page boundaries (e.g., major sections become pages)
        - The array order defines sibling order; children[] defines sub-pages.
        - Each page should contain a meaningful portion of the original content
        - Maintain the logical flow and hierarchy from the original report

        SLUG RULES
        - Generate slugs from the page titles: lowercase-kebab format
        - slug regex: ^[a-z0-9]+(?:-[a-z0-9]+)*$
        - Must be unique across the entire tree (not just per parent)
        - Do NOT include numeric prefixes (e.g., "1.2-"). Numbers are added at render time.

        ABSOLUTE OUTPUT RULES
        - Output ONLY valid JSON with a "pages" key.
        - Do NOT include any extra properties outside the schema.
        - No commentary, explanations, or markdown code blocks.
        - Start your response with {{ and end with }}
        - Preserve ALL information from the original content - do not summarize or omit details
        """

        # Define the tool for structured output
        tool_config = {
            "tools": [
                {
                    "toolSpec": {
                        "name": "transform_report_to_wiki",
                        "description": "Transform existing report content into structured wiki pages JSON",
                        "inputSchema": self._convert_pydantic_to_bedrock_schema(
                            InvestigationOutputPages
                        ),
                    }
                }
            ],
            "toolChoice": {"tool": {"name": "transform_report_to_wiki"}},
        }

        # create configurable object
        bedrock_config = Config(
            read_timeout=900, connect_timeout=60, retries={"max_attempts": 3}
        )

        boto3_client = boto3.client(
            "bedrock-runtime",
            region_name="eu-west-2",
            config=bedrock_config,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        logger.info("Sending schema request to Bedrock")

        response = boto3_client.converse(
            modelId="anthropic.claude-3-7-sonnet-20250219-v1:0",
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            toolConfig=tool_config,
            inferenceConfig={"temperature": 0.0, "maxTokens": 50000},
        )

        output_message = response["output"]["message"]

        # Find tool use in the response
        tool_use = None
        for content in output_message.get("content", []):
            if "toolUse" in content:
                tool_use = content["toolUse"]
                break

        if not tool_use:
            raise ValueError("No tool use found in Bedrock response")

        # Parse and validate the result
        result_data = tool_use.get("input", {})

        if not result_data or "pages" not in result_data:
            raise ValueError(f"Invalid tool response - missing pages. Got: {result_data}")

        return InvestigationOutputPages(**result_data)
