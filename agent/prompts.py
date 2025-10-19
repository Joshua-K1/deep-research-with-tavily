from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


query_writer_instructions = """Your goal is to generate sophisticated and diverse web search queries. These queries are intended for an advanced automated web research tool capable of analyzing complex results, following links, and synthesizing information.

Instructions:
- Always prefer a single search query, only add another query if the original question requests multiple aspects or elements and one query is not enough.
- Each query should focus on one specific aspect of the original question.
- Don't produce more than {number_queries} queries.
- Queries should be diverse, if the topic is broad, generate more than 1 query.
- Don't generate multiple similar queries, 1 is enough.
- Query should ensure that the most current information is gathered. The current date is {current_date}.

Format: 
- Format your response as a JSON object with ALL two of these exact keys:
   - "rationale": Brief explanation of why these queries are relevant
   - "query": A list of search queries

Example:

Topic: What revenue grew more last year apple stock or the number of people buying an iphone
```json
{{
    "rationale": "To answer this comparative growth question accurately, we need specific data points on Apple's stock performance and iPhone sales metrics. These queries target the precise financial information needed: company revenue trends, product-specific unit sales figures, and stock price movement over the same fiscal period for direct comparison.",
    "query": ["Apple total revenue growth fiscal year 2024", "iPhone unit sales growth fiscal year 2024", "Apple stock price growth fiscal year 2024"],
}}
```

Context: {research_topic}"""


web_researcher_summariser_instructions = """
You will be presented with the results of web searches on "{research_topic}". Your task is to synthesise this information into a verbose, well-structured report summary that captures the key insights and findings in a verifiable text artifact.

Instructions:
 - Ensure that the most recent information is included. The current date is {current_date}.
 - Consolidate key findings while meticulously tracking the source(s) for each specific piece of information.
 - The output should be a well-written summary or report based on your search findings.
 - Only include the information found in the search results, don't make up any information.
 - Cite all sources used in the report in markdown format (e.g. [rand.org](https://www.rand.org/pubs/research_reports/RRA3243-3.html)). THIS IS A MUST.


 Research Results:
 {research_results}
"""


web_searcher_instructions = """Conduct targeted web searches to gather the most recent, credible information on "{research_topic}" and synthesize it into a verifiable text artifact.

Instructions:
- Query should ensure tha the most current information is gathered. The current date is {current_date}.
- Conduct multiple, diverse searches to gather comprehensive information.
- Consolidate key findings while meticulously tracking the source(s) for each specific piece of information.
- The output should be a well-written summary or report based on your search findings.
- Only include the information found in the search results, don't make up any information.

Research Topic:
{research_topic}
"""


reflection_instructions = """You are an expert research assistant analyzing summaries about "{research_topic}".

Instructions:
- Identify knowledge gaps or areas that need deeper exploration and generate a follow-up query. (1 or multiple).
- If provided summaries are sufficient to answer the user's question, don't generate a follow-up query.
- If there is a knowledge gap, generate a follow-up query that would help expand your understanding.
- Focus on technical details, implementation specifics, or emerging trends that weren't fully covered.

Requirements:
- Ensure the follow-up query is self-contained and includes necessary context for web search.

Output Format:
- Format your response as a JSON object with these exact keys:
   - "is_sufficient": true or false
   - "knowledge_gap": Describe what information is missing or needs clarification
   - "follow_up_queries": Write a specific question to address this gap

Example:
```json
{{
    "is_sufficient": true, // or false
    "knowledge_gap": "The summary lacks information about performance metrics and benchmarks", // "" if is_sufficient is true
    "follow_up_queries": ["What are typical performance benchmarks and metrics used to evaluate [specific technology]?"] // [] if is_sufficient is true
}}
```

Reflect carefully on the Summaries to identify knowledge gaps and produce a follow-up query. Then, produce your output following this JSON format:

Summaries:
{summaries}
"""


answer_instructions = """Generate a comprehensive, detailed and well structured research report based on the provided summaries and research topic.

Instructions:
- The current date is {current_date}.
- You are the final step of a multi-step research process, don't mention that you are the final step. 
- You have access to all the information gathered from the previous steps.
- You have access to the user's question.
- Create a structured, multi-section report that thoroughly analyses the research topic.
- Aim for a detailed, comprehensive analysis of at least 2 pages.
- Use clear section headers to organise your findings.
- Provide detailed explanations for each key point with supporting evidence.
- Cross-reference information between different sources the build stronger arguments.
- Synthesize insights from various sources to present a cohesive understanding and deeper insights.
- Include the sources you used from the Summaries in the answer correctly, use markdown format (e.g. [rand.org](https://www.rand.org/pubs/research_reports/RRA3243-3.html)). THIS IS A MUST.

- Rquired Report Structure:
1. Executive Summary

Strategic Overview: Synthesize the most critical insights and their strategic implications
Key Findings Snapshot: 3-5 bullet points highlighting transformative discoveries
Core Recommendations: Priority actions ranked by impact and feasibility
Bottom Line: Clear, direct answer to the research question with confidence level indicated

2. Introduction and Research Framework

Research Objectives: Specific questions the research aims to answer
Scope and Boundaries: What is and isn't covered, with explicit rationale
Methodology: Research approach, sources consulted, search strategies employed, and analytical frameworks used
Limitations and Caveats: Acknowledge gaps, potential biases, and areas requiring further investigation

3. Background and Context

Historical Evolution: Trace the development of the topic over relevant time periods
Current Landscape: Present state analysis with supporting data and statistics
Market/Industry Context: Ecosystem mapping, key players, and competitive dynamics (where applicable)
Regulatory and Policy Environment: Relevant laws, regulations, and policy considerations

4. Comprehensive Findings Analysis
Organize by major themes or research questions, with each section including:

Detailed Narrative: In-depth exploration with supporting evidence
Data and Statistics: Quantitative backing with proper context and interpretation
Expert Perspectives: Quotes, insights, and viewpoints from authoritative sources
Case Studies and Examples: Real-world applications and illustrations
Emerging Patterns: Trends and patterns identified across sources

5. Cross-Source Synthesis and Validation

Consensus Areas: Where multiple authoritative sources align
Divergent Viewpoints: Document disagreements with analysis of why perspectives differ
Source Quality Assessment: Evaluate credibility, recency, and potential biases of key sources
Evidence Strength Matrix: Map findings by level of supporting evidence and source agreement
Knowledge Gaps: Explicitly identify what remains unknown or contested

6. Critical Analysis and Interpretation

Significance Assessment: Why these findings matter and to whom
Causal Relationships: Identify cause-and-effect dynamics where supported by evidence
Risk Factors and Challenges: Obstacles, threats, and complicating factors
Opportunities and Advantages: Positive developments and leverage points
Comparative Analysis: Benchmarking against alternatives, competitors, or historical precedents

7. Implications and Strategic Recommendations

Stakeholder Impact Analysis: How findings affect different constituencies
Tiered Recommendations:

Immediate actions (0-3 months)
Short-term initiatives (3-12 months)
Long-term strategic moves (1+ years)


Implementation Considerations: Resources required, potential barriers, success factors
Risk-Benefit Analysis: Weigh potential outcomes of recommended actions

8. Future Outlook and Scenarios

Trend Projection: Extrapolate current trajectories with supporting rationale
Scenario Planning: Multiple potential future states (optimistic, pessimistic, most likely)
Catalysts and Inflection Points: Events or developments that could accelerate change
Watch List: Key indicators to monitor for early signals of change

9. Conclusion

Research Question Resolution: Definitive answer with appropriate nuance
Synthesis of Core Insights: Integrate findings into coherent narrative
Final Perspective: Overarching takeaway and its broader significance
Call to Action: What should readers do with this information

10. Appendices (where relevant)

Methodology Detail: Extended explanation of research approach
Source Bibliography: Comprehensive list of all sources with annotations
Data Tables: Supporting datasets and detailed statistics
Glossary: Technical terms and acronyms defined
Additional Context: Supplementary information that supports but doesn't fit main narrative


- Writing Guidelines:
- Use detailed explanations with specific examples and data points where available
- Include relevant statistics, quotes, and factual details from sources
- Explain technical concepts thoroughly for better understanding
- Connect related information across different sections
- Provide nuanced analysis rather than simple summaries
- When sources disagree, present multiple perspectives and analyze the differences
- Use transitional phrases to link ideas and create flow between sections
- Cite all sources used in the report in markdown format (e.g. [rand.org](https://www.rand.org/pubs/research_reports/RRA3243-3.html)). THIS IS A MUST.

User Context:
- {research_topic}


Summaries:
{summaries}"""