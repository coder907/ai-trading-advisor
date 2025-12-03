"""
Chart Analysis Tool

This tool enables agents to perform visual analysis of trading chart screenshots
using Google's Gemini vision model to identify technical patterns, trends, and trade setups.
"""

from crewai.tools import tool
import google.generativeai as genai
import os
import logging
from io import BytesIO

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

        google_api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=google_api_key)
        
        with open(chart_image_path, "rb") as f:
            image_bytes = BytesIO(f.read())
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        file_extension = os.path.splitext(chart_image_path)[1].lower()
        if file_extension not in [".png", ".jpg", ".jpeg"]:
            raise ValueError("Unsupported image format. Please use PNG or JPG images.")
        
        mime_type = "image/png" if file_extension == ".png" else "image/jpeg"

        response = model.generate_content([
            analysis_prompt,
            {"mime_type": mime_type, "data": image_bytes.read()}
        ])
        
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
