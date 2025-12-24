from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import softmax

import torch
import pandas as pd

from scripts.transcriptions.text_chunking_functions import split_into_sentences


labels = ['neutral', 'positive', 'negative']
tokenizer = AutoTokenizer.from_pretrained('yiyanghkust/finbert-tone')
model = AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')

model.eval()



def analyze_sentiment(text, tokenizer=tokenizer, model=model):
    print("STARTING SENTIMENT ANALYSIS FUNCTION.")

    is_single = False
    if isinstance(text, str):
        text = [text]
        is_single = True

    print("Tokenizing input")

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    )

    inputs = {k: v.to("cpu") for k, v in inputs.items()}

    print("Running model (inference mode)")

    with torch.no_grad():                    # ← REQUIRED
        outputs = model(**inputs)

    print("Calculating softmax")

    probs = softmax(outputs.logits, dim=1).cpu().numpy()

    results = [
        {label: float(score) for label, score in zip(labels, row)}
        for row in probs
    ]

    if not text:
        return []

    return results[0] if is_single else results



if __name__ == '__main__':
        # Load FinBERT modle & tokenizer
    tokenizer = AutoTokenizer.from_pretrained('yiyanghkust/finbert-tone')
    model = AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')

    sentences = split_into_sentences('downloads/transcriptions/nvidia_test.txt')

    text_sentiment_df = {
        'Sentence': [],
        'Positive': [],
        'Neutral': [],
        'Negative': []
    }

    for sentence in sentences:
        sentiment = analyze_sentiment(tokenizer, model, sentence)

        text_sentiment_df['Sentence'].append(sentence)
        text_sentiment_df['Positive'].append(sentiment['positive'])
        text_sentiment_df['Neutral'].append(sentiment['neutral'])
        text_sentiment_df['Negative'].append(sentiment['negative'])

    text_sentiment_df = pd.DataFrame(text_sentiment_df)

    print(text_sentiment_df.sort_values('Positive', ascending=False).head(10))
    text_sentiment_df.to_csv("data/sample_sentiment_df.txt")