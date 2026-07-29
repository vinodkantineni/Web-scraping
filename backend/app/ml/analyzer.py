import os
import json
import requests
from typing import Optional
from newspaper import Article
import nltk

nltk.download("punkt", quiet=True)

# Try to import torch and transformers, but allow fallback if they aren't loaded yet
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification, pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

# Global variables to cache local models once loaded
_local_models = {}

def get_local_models():
    """Lazy load local HF models to save memory if Gemini is used instead."""
    global _local_models
    if not HAS_TRANSFORMERS:
        raise ImportError("Transformers and torch must be installed to run local models.")
        
    if not _local_models:
        print("Loading local BART models on CPU/GPU (this can take some time)...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Summarizer
        summ_name = "facebook/bart-large-cnn"
        summ_tokenizer = AutoTokenizer.from_pretrained(summ_name)
        summ_model = AutoModelForSeq2SeqLM.from_pretrained(summ_name).to(device)
        
        # Bias Classifier
        bias_name = "facebook/bart-large-mnli"
        bias_tokenizer = AutoTokenizer.from_pretrained(bias_name)
        bias_model = AutoModelForSequenceClassification.from_pretrained(bias_name).to(device)
        
        bias_classifier = pipeline(
            "zero-shot-classification",
            model=bias_model,
            tokenizer=bias_tokenizer,
            device=0 if device == "cuda" else -1
        )
        
        _local_models = {
            "device": device,
            "summ_tokenizer": summ_tokenizer,
            "summ_model": summ_model,
            "bias_classifier": bias_classifier
        }
    return _local_models


def extract_article(url: str) -> tuple:
    """Download and extract title and text from URL."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.title, article.text
    except Exception as e:
        raise ValueError(f"Failed to extract article from URL: {str(e)}")


def analyze_with_gemini(text: str, api_key: str) -> dict:
    """Analyze text using Gemini API with structured JSON output."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = (
        "You are an objective media analyst and neutral editor. Analyze the news article provided below. "
        "Perform these steps:\n"
        "1. Extract/determine a factual, unbiased title.\n"
        "2. Generate a concise, objective summary of the facts (100-150 words).\n"
        "3. Evaluate the original text's political bias on 'Left Wing', 'Center', and 'Right Wing' "
        "as probabilities between 0.0 and 1.0 (they must sum approximately to 1.0).\n"
        "4. Rewrite the article text to be completely neutral, factual, and unbiased (debiased_text), "
        "removing all sensationalism, loaded words, opinion slants, and spin.\n"
        "5. Evaluate the newly rewritten debiased_text's political bias on 'Left Wing', 'Center', "
        "and 'Right Wing' (probabilities between 0.0 and 1.0).\n\n"
        f"ARTICLE CONTENT:\n{text}"
    )

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING"},
                    "summary": {"type": "STRING"},
                    "original_left": {"type": "NUMBER"},
                    "original_center": {"type": "NUMBER"},
                    "original_right": {"type": "NUMBER"},
                    "debiased_text": {"type": "STRING"},
                    "debiased_left": {"type": "NUMBER"},
                    "debiased_center": {"type": "NUMBER"},
                    "debiased_right": {"type": "NUMBER"}
                },
                "required": [
                    "title", "summary", 
                    "original_left", "original_center", "original_right",
                    "debiased_text",
                    "debiased_left", "debiased_center", "debiased_right"
                ]
            }
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Gemini API request failed ({response.status_code}): {response.text}")
        
    response_json = response.json()
    try:
        content_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
        result = json.loads(content_text)
        return result
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to parse structured JSON from Gemini response: {str(e)}")


def analyze_with_local_models(title: str, text: str) -> dict:
    """Analyze and debias text using locally loaded BART models."""
    models = get_local_models()
    device = models["device"]
    
    # 1. Summarization
    inputs = models["summ_tokenizer"](
        text,
        max_length=1024,
        truncation=True,
        return_tensors="pt"
    ).to(device)
    
    summary_ids = models["summ_model"].generate(
        inputs["input_ids"],
        max_length=130,
        min_length=40,
        num_beams=4,
        length_penalty=2.0,
        early_stopping=True
    )
    summary = models["summ_tokenizer"].decode(summary_ids[0], skip_special_tokens=True)
    
    # 2. Original Bias Detection
    labels = ["Left Wing", "Center", "Right Wing"]
    original_result = models["bias_classifier"](text[:2000], labels)
    
    # Map predictions back to key names
    orig_scores = dict(zip(original_result["labels"], original_result["scores"]))
    original_left = orig_scores.get("Left Wing", 0.0)
    original_center = orig_scores.get("Center", 0.0)
    original_right = orig_scores.get("Right Wing", 0.0)
    
    # 3. Debiasing (neutral rewriting)
    prompt = (
        "Rewrite the following news article in a completely neutral, factual, "
        "and unbiased tone. Remove emotional language, opinions, and political framing.\n\n"
        + text
    )
    
    inputs_debias = models["summ_tokenizer"](
        prompt,
        max_length=1024,
        truncation=True,
        return_tensors="pt"
    ).to(device)
    
    output_ids = models["summ_model"].generate(
        inputs_debias["input_ids"],
        max_length=300,
        min_length=100,
        num_beams=5,
        length_penalty=2.5
    )
    debiased_text = models["summ_tokenizer"].decode(output_ids[0], skip_special_tokens=True)
    
    # 4. Debiased Bias Detection
    debiased_result = models["bias_classifier"](debiased_text[:2000], labels)
    deb_scores = dict(zip(debiased_result["labels"], debiased_result["scores"]))
    debiased_left = deb_scores.get("Left Wing", 0.0)
    debiased_center = deb_scores.get("Center", 0.0)
    debiased_right = deb_scores.get("Right Wing", 0.0)
    
    return {
        "title": title or "Analyzed Article",
        "summary": summary,
        "original_left": original_left,
        "original_center": original_center,
        "original_right": original_right,
        "debiased_text": debiased_text,
        "debiased_left": debiased_left,
        "debiased_center": debiased_center,
        "debiased_right": debiased_right
    }


def analyze_article(url: Optional[str] = None, raw_text: Optional[str] = None) -> dict:
    """Core analysis orchestrator selecting between Gemini API and Local HF Models."""
    # 1. Fetch text if URL is provided
    title = ""
    text = ""
    if url:
        title, text = extract_article(url)
    elif raw_text:
        text = raw_text
        title = "Pasted Text Analysis"
        
    if not text or len(text.strip()) < 150:
        raise ValueError("Article content must be at least 150 characters long.")

    # 2. Check if Gemini API Key is available
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        print("Using Gemini API for analysis...")
        result = analyze_with_gemini(text, api_key)
        # Preserve original URL if applicable
        result["url"] = url
        result["text"] = text
    else:
        print("GEMINI_API_KEY not found. Falling back to local Hugging Face models...")
        if not HAS_TRANSFORMERS:
            raise RuntimeError(
                "Local fallback failed: transformers/torch not installed and GEMINI_API_KEY is missing."
            )
        result = analyze_with_local_models(title, text)
        result["url"] = url
        result["text"] = text

    # 3. Calculate Bias Reduction
    # Formula compares maximum non-center score reduction
    orig_max_bias = max(result["original_left"], result["original_right"])
    deb_max_bias = max(result["debiased_left"], result["debiased_right"])
    
    if orig_max_bias > 0:
        bias_reduction = ((orig_max_bias - deb_max_bias) / orig_max_bias) * 100
        # If bias actually went down, reduction is positive. Cap between -100% and 100%
        result["bias_reduction"] = round(max(-100.0, min(100.0, bias_reduction)), 2)
    else:
        result["bias_reduction"] = 0.0

    return result
