from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict

from langgraph.graph import add_messages
from typing_extensions import Annotated


import operator


class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[list, operator.add]
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: int
    reasoning_model: str

class DetailedFindingsState(TypedDict):
    findings: Annotated[list[dict], operator.add]  
    finding_categories: Annotated[dict, operator.add]  
    evidence_quality_scores: Annotated[dict, operator.add]  
    contradictions: Annotated[list[dict], operator.add]  
    data_points: Annotated[list[dict], operator.add]  

class AnalysisImplicationsState(TypedDict):
    analysis: str  
    key_insights: Annotated[list[str], operator.add]  
    implications: Annotated[dict, operator.add]  
    stakeholder_impact: Annotated[dict, operator.add]  
    risk_assessment: Annotated[list[dict], operator.add]  
    confidence_level: float  

class FutureOutlookState(TypedDict):
    future_outlook: str 
    predictions: Annotated[list[dict], operator.add]  
    scenarios: Annotated[list[dict], operator.add]  
    trend_analysis: Annotated[dict, operator.add] 
    recommendations: Annotated[list[str], operator.add]  
    monitoring_indicators: Annotated[list[str], operator.add]  

class ConclusionState(TypedDict):
    conclusion: str  # Main conclusion text
    key_takeaways: Annotated[list[str], operator.add] 
    answered_questions: Annotated[list[str], operator.add]  
    unanswered_questions: Annotated[list[str], operator.add] 
    limitations: Annotated[list[str], operator.add] 
    further_research_needed: Annotated[list[str], operator.add]  

class ReflectionState(TypedDict):
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: Annotated[list, operator.add]
    research_loop_count: int
    number_of_ran_queries: int


class Query(TypedDict):
    query: str
    rationale: str


class QueryGenerationState(TypedDict):
    search_query: list[Query]


class WebSearchState(TypedDict):
    search_query: str
    id: str


@dataclass(kw_only=True)
class SearchStateOutput:
    running_summary: str = field(default=None)  # Final report
