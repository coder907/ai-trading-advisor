"""
Chart Analysis Tool

This tool enables agents to perform visual analysis of trading chart screenshots
using Google's Gemini vision model to identify technical patterns, trends, and trade setups.
"""

from crewai.tools import tool
from google import genai
from PIL import Image
import os
import logging

logging.basicConfig(level=logging.INFO)

@tool("Analyze Chart")
def analyze_chart(chart_image_path: str, analysis_prompt: str) -> str:
    """
    Perform visual analysis of a trading chart screenshot using AI vision.
    This tool can identify technical patterns, trends, support/resistance levels,
    chart structures, and potential trade setups from the chart image.
    
    Args:
        chart_image_path: Path to the chart image file (PNG, JPG, etc.)
        analysis_prompt: Specific question or instruction for the chart analysis
                        (e.g., "Identify the trend and key support/resistance levels")
    
    Returns:
        A detailed textual description of the chart analysis including patterns,
        trends, and technical observations.
    """
    try:
        logging.info(f"Chart Analysis Tool: Starting analysis for chart at {chart_image_path}")

        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                analysis_prompt,
                Image.open(chart_image_path)
            ]
        )

        analysis_text = response.text
        
        logging.info(f"Chart Analysis Tool: Successfully analyzed chart from {chart_image_path}")
        
        if analysis_text:
            return f"CHART VISUAL ANALYSIS:\n{'=' * 70}\n\n{analysis_text}"
        else:
            return "Chart analysis completed but no text output was generated. The image may not contain recognizable chart patterns."
    
    except FileNotFoundError:
        logging.error(f"Chart Analysis Tool: File not found - {chart_image_path}")
        return f"Error: Chart image file not found at path: {chart_image_path}"
    except Exception as e:
        logging.error(f"Chart Analysis Tool: Unexpected ERROR - {str(e)}")
        return f"Error analyzing chart: {str(e)}. Please ensure the image file is valid and accessible."
