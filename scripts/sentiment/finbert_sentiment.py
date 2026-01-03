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
    """
    Run sentence-level sentiment analysis using a pretrained FinBERT model.

    This function accepts either a single sentence or a list of sentences,
    filters invalid/empty inputs, and returns sentiment scores for each
    valid sentence. Inference is performed in batch for efficiency.

    Parameters
    ----------
    text : str or list[str]
        A single sentence or a list of sentences to analyze.
    tokenizer : transformers.PreTrainedTokenizer
        Tokenizer associated with the FinBERT model.
    model : transformers.PreTrainedModel
        FinBERT sentiment classification model.

    Returns
    -------
    list[dict] or dict
        If `text` is a list:
            A list of dictionaries, one per sentence, each containing:
                {
                    "positive": float,
                    "neutral": float,
                    "negative": float
                }

        If `text` is a single string:
            A single dictionary with the same structure.

        Returns an empty list if no valid sentences are provided or
        if an error occurs during inference.
    """
    
    print("STARTING SENTIMENT ANALYSIS FUNCTION.")

    is_single = False
    if isinstance(text, str):
        text = [text]
        is_single = True
    

    text = [s for s in text if s and s.strip()]
    if not text:
        return []

    try:
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

    except Exception as e:
        print(f"[ERROR] An error occurred when analyzing the sentiment of the chunk of sentences...")
        print(f"[ERROR] {e}")


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