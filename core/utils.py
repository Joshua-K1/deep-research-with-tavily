import logging

logger = logging.getLogger(__name__)


def write_to_markdown(content: str, filename: str ):
    """Writes research reports and sources to a markdown file."""
    try:
        with open(filename, 'w') as file:
            file.write(content)

    except IOError as e:
        logger.error(f"Failed to write to {filename}: {e}")



def generate_citations_from_tavily(search_results, query):
    """Generate citations from Tavily search results"""
    citations = []
    
    for idx, result in enumerate(search_results):
        if isinstance(result, dict):
            citation = {
                "short_url": f"[{idx+1}]",
                "url": result.get("url", ""),
                "title": result.get("title", ""),
                "segments": [{
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "short_url": f"[{idx+1}]",
                }]
            }
            citations.append(citation)
    
    return citations


def create_cited_text(search_results, query):
    """Create a cited summary from search results"""
    # Use Tavily's answer if available
    if search_results and isinstance(search_results[0], dict) and "answer" in search_results[0]:
        base_text = search_results[0]["answer"]
    else:
        # Generate summary from results
        base_text = f"Research findings for: {query}\n\n"
        for idx, result in enumerate(search_results):
            if isinstance(result, dict):
                base_text += f"{result.get('content', '')} [{idx+1}]\n\n"
    
    return base_text