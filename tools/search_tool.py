"""
Internet Search Tool

This tool enables agents to search the internet for technical, fundamental,
and macroeconomic data to support trading analysis using Serper API.
"""

from crewai.tools import tool
import requests
import json
import os
import logging

logging.basicConfig(level=logging.INFO)

@tool("Internet Search Tool")
def search_internet(query: str) -> str:
    """
    Search the internet for technical, fundamental, and macroeconomic data
    to support trading analysis. Use this tool to gather real-time market
    information, news, company fundamentals, sector trends, or economic indicators.
    
    Args:
        query: The search query string containing keywords for financial,
               technical, or fundamental data.
    
    Returns:
        A string containing search results with relevant market information.
    """
    try:
        logging.info(f"Search Internet Tool: Starting search for query: {query}")

        serper_api_key = os.getenv("SERPER_API_KEY")
        url = "https://google.serper.dev/news"
        
        payload = json.dumps({
            "q": query,
            "tbs": "qdr:m" # Results from the last month
        })
        
        headers = {
            'X-API-KEY': serper_api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant information
        results = []
        
        if data.get("news"):
            results.append("Recent News & Market Information:")
            results.append("=" * 50)
            for item in data["news"][:5]:
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                source = item.get("source", "")
                date = item.get("date", "")
                link = item.get("link", "")
                
                result_text = f"\n• {title}"
                if snippet:
                    result_text += f"\n  {snippet}"
                if source:
                    result_text += f"\n  Source: {source}"
                if date:
                    result_text += f"\n  Date: {date}"
                if link:
                    result_text += f"\n  Link: {link}"
                
                results.append(result_text)
        
        logging.info(f"Search Internet Tool: Found {len(data.get('news', []))} results for query '{query}'")
        
        if results:
            return "\n".join(results)
        else:
            return f"Search completed for '{query}' but no specific results found. Consider refining the search query or using alternative keywords."
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Search Internet Tool: Request ERROR - {str(e)}")
        return f"Error performing internet search: {str(e)}. Please check your SERPER_API_KEY and internet connection."
    except Exception as e:
        logging.error(f"Search Internet Tool: Unexpected ERROR - {str(e)}")
        return f"Unexpected error during search: {str(e)}"
