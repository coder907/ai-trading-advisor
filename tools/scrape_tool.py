"""
Web Scraping Tool

This tool enables agents to scrape and extract content from web pages
for detailed analysis of news articles, company reports, and market information.
"""

from crewai.tools import tool
import requests
import json
import os
import logging

logging.basicConfig(level=logging.INFO)

@tool("Scrape Website Tool")
def scrape_website(url: str) -> str:
    """
    Scrape and extract content from a specific web page URL.
    Use this tool to get detailed information from news articles, financial reports,
    company announcements, or any web page that requires in-depth content extraction.
    
    Args:
        url: The full URL of the webpage to scrape (e.g., https://finance.yahoo.com/news/...)
    
    Returns:
        A string containing the extracted text content, title, description, and metadata from the page.
    """
    try:
        logging.info(f"Scrape Website Tool: Starting scrape for URL: {url}")

        serper_api_key = os.getenv("SERPER_API_KEY")
        scrape_url = "https://scrape.serper.dev"
        
        payload = json.dumps({
            "url": url
        })
        
        headers = {
            'X-API-KEY': serper_api_key,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(scrape_url, headers=headers, data=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract and format the content
        results = []
        
        if data.get("text"):
            results.append("ARTICLE CONTENT:")
            results.append("=" * 70)
            results.append(data["text"])
            results.append("")
        
        metadata = data.get("metadata", {})
        if metadata:
            results.append("METADATA:")
            results.append("-" * 70)
            
            if metadata.get("title"):
                results.append(f"Title: {metadata['title']}")
            
            if metadata.get("description"):
                results.append(f"Description: {metadata['description']}")
            
            if metadata.get("keywords"):
                results.append(f"Keywords: {metadata['keywords']}")
            
            jsonld = data.get("jsonld", {})

            if jsonld.get("datePublished"):
                results.append(f"Published: {jsonld['datePublished']}")
            
            if jsonld.get("author", {}).get("name"):
                results.append(f"Author: {jsonld['author']['name']}")
        
        logging.info(f"Scrape Website Tool: Successfully scraped content from {url}")
        
        if results:
            return "\n".join(results)
        else:
            return f"Successfully accessed {url} but no content could be extracted. The page might be protected or have no readable content."
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Scrape Website Tool: Request ERROR - {str(e)}")
        return f"Error scraping website: {str(e)}. Please check the URL and your internet connection."
    except Exception as e:
        logging.error(f"Scrape Website Tool: Unexpected ERROR - {str(e)}")
        return f"Unexpected error while scraping: {str(e)}"
