import os
import torch
import nltk
from typing import Optional
from newspaper import Article
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    AutoModelForSequenceClassification,
    pipeline,
)

nltk.download("punkt", quiet=True)

# Global variables to cache local models once loaded
_local_models = {}


def get_local_models():
    """Lazy load local HuggingFace BART models. Models are cached after first load."""
    global _local_models

    if not _local_models:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading local BART models on {device} (this may take a moment on first run)...")

        # Summarizer
        summ_name = "facebook/bart-large-cnn"
        summ_tokenizer = AutoTokenizer.from_pretrained(summ_name)
        summ_model = AutoModelForSeq2SeqLM.from_pretrained(summ_name).to(device)

        # Bias Classifier (zero-shot via NLI)
        bias_name = "facebook/bart-large-mnli"
        bias_tokenizer = AutoTokenizer.from_pretrained(bias_name)
        bias_model = AutoModelForSequenceClassification.from_pretrained(bias_name).to(device)

        bias_classifier = pipeline(
            "zero-shot-classification",
            model=bias_model,
            tokenizer=bias_tokenizer,
            device=0 if device == "cuda" else -1,
        )

        _local_models = {
            "device": device,
            "summ_tokenizer": summ_tokenizer,
            "summ_model": summ_model,
            "bias_classifier": bias_classifier,
        }
        print("Models loaded successfully.")
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


def summarize(text: str, max_len: int = 130) -> str:
    """Generate a concise summary using BART-large-CNN."""
    models = get_local_models()
    device = models["device"]

    inputs = models["summ_tokenizer"](
        text,
        max_length=1024,
        truncation=True,
        return_tensors="pt",
    ).to(device)

    summary_ids = models["summ_model"].generate(
        inputs["input_ids"],
        max_length=max_len,
        min_length=40,
        num_beams=4,
        length_penalty=2.0,
        early_stopping=True,
    )

    return models["summ_tokenizer"].decode(summary_ids[0], skip_special_tokens=True)


def classify_bias(text: str) -> dict:
    """Run zero-shot bias classification on text, returning scores dict."""
    models = get_local_models()
    labels = ["Left Wing", "Center", "Right Wing"]
    result = models["bias_classifier"](text[:2000], labels)
    return dict(zip(result["labels"], result["scores"]))


def debias_text(text: str) -> str:
    """Rewrite text in a neutral tone using BART summarizer."""
    models = get_local_models()
    device = models["device"]

    prompt = (
        "Rewrite the following news article in a completely neutral, factual, "
        "and unbiased tone. Remove emotional language, opinions, and political framing.\n\n"
        + text
    )

    inputs = models["summ_tokenizer"](
        prompt,
        max_length=1024,
        truncation=True,
        return_tensors="pt",
    ).to(device)

    output_ids = models["summ_model"].generate(
        inputs["input_ids"],
        max_length=300,
        min_length=100,
        num_beams=5,
        length_penalty=2.5,
    )

    return models["summ_tokenizer"].decode(output_ids[0], skip_special_tokens=True)


def analyze_article(url: Optional[str] = None, raw_text: Optional[str] = None) -> dict:
    """Core analysis orchestrator using local HuggingFace BART models only.

    Steps:
      1. Extract article text (from URL or raw text).
      2. Summarize using facebook/bart-large-cnn.
      3. Detect original bias using facebook/bart-large-mnli (zero-shot).
      4. Generate a debiased rewrite.
      5. Detect bias on the debiased version.
      6. Calculate bias reduction percentage.
    """
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

    print("Analyzing with local HuggingFace BART models...")

    # 2. Summary
    summary = summarize(text)

    # 3. Original bias scores
    orig_scores = classify_bias(text)
    original_left = orig_scores.get("Left Wing", 0.0)
    original_center = orig_scores.get("Center", 0.0)
    original_right = orig_scores.get("Right Wing", 0.0)

    # 4. Debiased text
    debiased = debias_text(text)

    # 5. Debiased bias scores
    deb_scores = classify_bias(debiased)
    debiased_left = deb_scores.get("Left Wing", 0.0)
    debiased_center = deb_scores.get("Center", 0.0)
    debiased_right = deb_scores.get("Right Wing", 0.0)

    # 6. Bias reduction calculation
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
        "summary": summary,
        "original_left": original_left,
        "original_center": original_center,
        "original_right": original_right,
        "debiased_text": debiased,
        "debiased_left": debiased_left,
        "debiased_center": debiased_center,
        "debiased_right": debiased_right,
        "bias_reduction": bias_reduction,
    }
