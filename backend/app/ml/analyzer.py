import os
import json
from typing import Optional
from newspaper import Article
import google.generativeai as genai

def extract_article(url: str) -> tuple:
    """Download and extract title and text from URL."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.title, article.text
    except Exception as e:
        raise ValueError(f"Failed to extract article from URL: {str(e)}")

def analyze_article(url: Optional[str] = None, raw_text: Optional[str] = None) -> dict:
    """Core analysis orchestrator using Google Gemini API."""
    # 1. Fetch text
    title = ""
    text = ""
    if url:
        title, text = extract_article(url)
    elif raw_text:
        text = raw_text
        title = "Pasted Text Analysis"

    if not text or len(text.strip()) < 150:
        raise ValueError("Article content must be at least 150 characters long.")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it in your .env or deployment console.")

    genai.configure(api_key=api_key)
    
    # Use flash for fast text tasks
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
You are an expert, objective political analyst and editor.
Read the following news article text and perform three tasks:
1. Provide a concise, fact-based summary (around 100-130 words).
2. Rewrite the article text in a completely neutral, factual, and unbiased tone. Remove all emotional language, opinions, and political framing.
3. Analyze the political bias of BOTH the original text and your debiased text. 
   Provide a confidence score (between 0.0 and 1.0) for three categories: Left Wing, Center, Right Wing. The three scores must sum to 1.0.

Return the response STRICTLY as a valid JSON object with the following schema:
{{
  "summary": "String",
  "original_bias": {{
    "left": 0.0,
    "center": 0.0,
    "right": 0.0
  }},
  "debiased_text": "String",
  "debiased_bias": {{
    "left": 0.0,
    "center": 0.0,
    "right": 0.0
  }}
}}

Article text:
{text[:4000]}
"""
    print("Analyzing with Gemini API...")
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean markdown formatting if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        data = json.loads(response_text)
    except Exception as e:
        raise ValueError(f"Failed to process analysis with Gemini: {str(e)}")

    original_left = data["original_bias"]["left"]
    original_center = data["original_bias"]["center"]
    original_right = data["original_bias"]["right"]
    
    debiased_left = data["debiased_bias"]["left"]
    debiased_center = data["debiased_bias"]["center"]
    debiased_right = data["debiased_bias"]["right"]

    # Calculate bias reduction
    orig_max_bias = max(original_left, original_right)
    deb_max_bias = max(debiased_left, debiased_right)

    if orig_max_bias > 0:
        bias_reduction = ((orig_max_bias - deb_max_bias) / orig_max_bias) * 100
        bias_reduction = round(max(-100.0, min(100.0, bias_reduction)), 2)
    else:
        bias_reduction = 0.0

    return {
        "title": title or "Analyzed Article",
        "url": url,
        "text": text,
        "summary": data["summary"],
        "original_left": original_left,
        "original_center": original_center,
        "original_right": original_right,
        "debiased_text": data["debiased_text"],
        "debiased_left": debiased_left,
        "debiased_center": debiased_center,
        "debiased_right": debiased_right,
        "bias_reduction": bias_reduction,
    }
