import os
import json
import re
from typing import Optional
from newspaper import Article
import google.generativeai as genai
from dotenv import load_dotenv

# Automatically load environment variables from .env files
load_dotenv()
backend_env = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
if os.path.exists(backend_env):
    load_dotenv(backend_env)

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

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it in your .env or deployment console.")

    genai.configure(api_key=api_key)
    
    # Preferred Gemini models in fallback order
    candidate_models = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-2.0-flash',
        'gemini-2.5-flash',
        'gemini-1.5-pro',
        'gemini-pro'
    ]

    # Query supported generation models to prioritize models available for this API key
    try:
        supported = [
            m.name.replace("models/", "")
            for m in genai.list_models()
            if "generateContent" in getattr(m, "supported_generation_methods", [])
        ]
        if supported:
            candidate_models = [m for m in candidate_models if m in supported] + [m for m in supported if m not in candidate_models]
    except Exception as list_err:
        print(f"Note: Could not retrieve dynamic model list ({list_err}), using default candidate list.")

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
    response_text = None
    last_error = None

    for model_name in candidate_models:
        try:
            print(f"Analyzing with Gemini API model '{model_name}'...")
            model = genai.GenerativeModel(model_name)
            # Try with JSON response_mime_type first
            try:
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
            except Exception:
                # Fallback to default generate_content
                response = model.generate_content(prompt)

            if response and hasattr(response, "text") and response.text:
                response_text = response.text.strip()
                print(f"Successfully generated analysis using model '{model_name}'.")
                break
        except Exception as err:
            last_error = err
            print(f"Model '{model_name}' failed: {err}")
            continue

    if not response_text:
        raise ValueError(f"Failed to process analysis with Gemini: {str(last_error)}")

    # Extract and parse JSON safely
    def parse_json_from_gemini(raw_text: str) -> dict:
        if not raw_text:
            raise ValueError("Received empty response text from Gemini API.")
        
        t = raw_text.strip()
        # 1. Try direct parse
        try:
            return json.loads(t)
        except Exception:
            pass

        # 2. Extract substring between first '{' and last '}'
        start_idx = t.find('{')
        end_idx = t.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            try:
                return json.loads(t[start_idx:end_idx + 1])
            except Exception:
                pass

        # 3. Strip codeblock markers ```json ... ```
        cleaned = t
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        if cleaned.endswith("```"):
            cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            return json.loads(cleaned.strip())
        except Exception as parse_err:
            raise ValueError(f"Failed to parse JSON output from Gemini API: {str(parse_err)}")

    data = parse_json_from_gemini(response_text)


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
