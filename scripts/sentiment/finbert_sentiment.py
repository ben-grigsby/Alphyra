from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import softmax

import torch
import pandas as pd

from scripts.transcriptions.text_chunking_functions import split_into_sentences

# Load FinBERT modle & tokenizer
tokenizer = AutoTokenizer.from_pretrained('yiyanghkust/finbert-tone')
model = AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')

labels = ['neutral', 'positive', 'negative']

def analyze_sentiment(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    probs = softmax(outputs.logits, dim=1).detach().numpy()[0]

    return {label: float(score) for label, score in zip(labels, probs)}



if __name__ == '__main__':
    sentences = split_into_sentences('downloads/transcriptions/nvidia_test.txt')

    text_sentiment_df = {
        'Sentence': [],
        'Positive': [],
        'Neutral': [],
        'Negative': []
    }

    for sentence in sentences:
        sentiment = analyze_sentiment(sentence)

        text_sentiment_df['Sentence'].append(sentence)
        text_sentiment_df['Positive'].append(sentiment['positive'])
        text_sentiment_df['Neutral'].append(sentiment['neutral'])
        text_sentiment_df['Negative'].append(sentiment['negative'])

    text_sentiment_df = pd.DataFrame(text_sentiment_df)

    print(text_sentiment_df.sort_values('Positive', ascending=False).head(10))
    text_sentiment_df.to_csv("data/sample_sentiment_df.txt")