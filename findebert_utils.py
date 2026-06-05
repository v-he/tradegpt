from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

device = "cuda:0" if torch.cuda.is_available() else "cpu"

MODEL_NAME = "mrm8488/deberta-v3-ft-financial-news-sentiment-analysis"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).to(device)

# According to the model card, labels are:
# 0 -> negative, 1 -> neutral, 2 -> positive
labels = ["negative", "neutral", "positive"]


def estimate_sentiment(news):
    """Estimate (probability, sentiment) from a list of news headlines."""
    if not news:
        return 0.0, "neutral"

    # Tokenize and move to device
    tokens = tokenizer(
        news,
        return_tensors="pt",
        padding=True,
        truncation=True,
    ).to(device)

    # Forward pass
    outputs = model(**tokens)
    logits = outputs.logits

    # Aggregate across headlines, then softmax
    logits_sum = torch.sum(logits, dim=0)
    probs = torch.nn.functional.softmax(logits_sum, dim=-1)

    idx = torch.argmax(probs)
    probability = float(probs[idx].item())
    sentiment = labels[int(idx)]

    return probability, sentiment


if __name__ == "__main__":
    tensor, sentiment = estimate_sentiment(
        ["markets responded negatively to the news!", "traders were displeased!"]
    )
    print(tensor, sentiment)
    print(torch.cuda.is_available())
