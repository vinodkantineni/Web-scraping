# !pip install transformers torch nltk newspaper3k gradio lxml_html_clean --quiet

import nltk
import gradio as gr
import torch
import matplotlib.pyplot as plt
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    AutoModelForSequenceClassification,
    pipeline
)
from newspaper import Article

nltk.download("punkt", quiet=True)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading models on {device}...")

summ_name = "facebook/bart-large-cnn"
summ_tokenizer = AutoTokenizer.from_pretrained(summ_name)
summ_model = AutoModelForSeq2SeqLM.from_pretrained(summ_name).to(device)

bias_name = "facebook/bart-large-mnli"
bias_tokenizer = AutoTokenizer.from_pretrained(bias_name)
bias_model = AutoModelForSequenceClassification.from_pretrained(bias_name).to(device)

bias_classifier = pipeline(
    "zero-shot-classification",
    model=bias_model,
    tokenizer=bias_tokenizer,
    device=0 if device == "cuda" else -1
)

LABELS = ["Left Wing", "Center", "Right Wing"]

def summarize(text, max_len=130):
    inputs = summ_tokenizer(
        text,
        max_length=1024,
        truncation=True,
        return_tensors="pt"
    ).to(device)

    summary_ids = summ_model.generate(
        inputs["input_ids"],
        max_length=max_len,
        min_length=40,
        num_beams=4,
        length_penalty=2.0,
        early_stopping=True
    )

    return summ_tokenizer.decode(summary_ids[0], skip_special_tokens=True)


def debias_text(text):
    prompt = (
        "Rewrite the following news article in a completely neutral, factual, "
        "and unbiased tone. Remove emotional language, opinions, and political framing.\n\n"
        + text
    )

    inputs = summ_tokenizer(
        prompt,
        max_length=1024,
        truncation=True,
        return_tensors="pt"
    ).to(device)

    output_ids = summ_model.generate(
        inputs["input_ids"],
        max_length=300,
        min_length=100,
        num_beams=5,
        length_penalty=2.5
    )

    return summ_tokenizer.decode(output_ids[0], skip_special_tokens=True)

def analyze_news(input_text_or_url):
    try:
        # Load article
        if input_text_or_url.strip().startswith("http"):
            article = Article(input_text_or_url)
            article.download()
            article.parse()
            text = article.text
        else:
            text = input_text_or_url

        if len(text.strip()) < 150:
            return "Text too short", "-", "-", "-", None, "-"

        # Summary
        summary = summarize(text)

        # Bias
        bias_result = bias_classifier(text[:2000], LABELS)
        labels = bias_result["labels"]
        original_scores = bias_result["scores"]

        bias_scores = "\n".join([
            f"{label}: {round(score * 100, 2)}%"
            for label, score in zip(labels, original_scores)
        ])

        # Debiased
        debiased = debias_text(text)

        # Bias
        debiased_result = bias_classifier(debiased[:2000], LABELS)
        debiased_scores = debiased_result["scores"]

        fig = plt.figure()
        plt.plot(labels, original_scores, marker='o', label="Original Article")
        plt.plot(labels, debiased_scores, marker='o', label="Debiased Article")
        plt.title("Bias Comparison: Original vs Debiased")
        plt.xlabel("Bias Category")
        plt.ylabel("Confidence Score")
        plt.xticks(rotation=45)
        plt.legend()

        original_dominant_score = max(original_scores)
        debiased_dominant_score = max(debiased_scores)

        bias_reduction = (
            (original_dominant_score - debiased_dominant_score)
            / original_dominant_score
        ) * 100

        reduction_text = f"Bias Reduction: {round(bias_reduction, 2)}%"

        return (
            summary,
            bias_scores,
            debiased,
            text,
            fig,
            reduction_text
        )

    except Exception as e:
        return f"Error: {str(e)}", "-", "-", "-", None, "-"

interface = gr.Interface(
    fn=analyze_news,
    inputs=gr.Textbox(label="URL or Article Text", lines=8),
    outputs=[
        gr.Textbox(label="Summary", lines=6),
        gr.Textbox(label="Exact Bias Scores", lines=5),
        gr.Textbox(label="Debiased / Neutral Article", lines=25, max_lines=None),
        gr.Textbox(label="Original Snippet", lines=20, max_lines=None),
        gr.Plot(label="Bias Comparison Graph"),
        gr.Textbox(label="Bias Reduction Percentage")
    ],
    title="📰 AI News Bias Detection & Debiasing System",
    description="Detects political bias, shows exact scores, compares bias graph, and calculates Bias Reduction %"
)

interface.launch(debug=True)
