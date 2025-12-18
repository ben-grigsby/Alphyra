from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import softmax

import torch
import pandas as pd

from scripts.transcriptions.text_chunking_functions import split_into_sentences


labels = ['neutral', 'positive', 'negative']

def analyze_sentiment(tokenizer, model, text):
    """
    Accepts:
      - A single string
      - A list of strings
    
    Returns:
      - A dict for a single string
      - A list of dicts for multiple strings
    """

    # Normalize input → always a list
    is_single = False
    if isinstance(text, str):
        text = [text]
        is_single = True

    # Tokenize batch
    inputs = tokenizer(
        text,
        return_tensors='pt',
        truncation=True,
        padding=True,
        max_length=512
    )

    # Run through model
    outputs = model(**inputs)

    # Softmax across sentiment dimension
    probs = softmax(outputs.logits, dim=1).detach().numpy()
    # shape: (batch, 3)

    results = []
    for row in probs:
        results.append({label: float(score) for label, score in zip(labels, row)})

    # Return single dictionary OR list of dictionaries depending on input
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