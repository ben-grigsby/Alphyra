import pandas as pd

from scripts.sentiment.finbert_sentiment import analyze_sentiment 

from scripts.analyze_db.database_functions import (
    get_db_info,
    insert_sentiment_into_db
)

from scripts.transcriptions.text_chunking_functions import split_into_sentences



def search_news_db(query):
    df = get_db_info(query)
    return df



def get_sentence_sentiment(text):
    sentences = split_into_sentences(chunk=text)
    
    lst_dicts = []

    for sent in sentences:
        sentiment_dict = analyze_sentiment(sent)
        lst_dicts.append(sentiment_dict)
    
    return lst_dicts



def get_sentiment_dataframe(query):
    df = search_news_db(query)

    sentiment_records = []

    for _, row in df.iterrows():
        print(f"[INFO] Analyzing sentiment for {row['symbol']} article summary.")
        sentences = split_into_sentences(chunk=row['summary'])
        for sent in sentences:
            tmp_dict = {
                'sentence': sent,
                'stock_symbol': row['symbol'],
                'model_name': 'FinBERT',
                'source_type': row['source'],
                'source_url': row['url'],
                'published_at': row['published_at'],
            }

            sentiment_dict = analyze_sentiment(sent)

            tmp_dict['positive_score'] = sentiment_dict['positive']
            tmp_dict['neutral_score'] = sentiment_dict['neutral']
            tmp_dict['negative_score'] = sentiment_dict['negative']

            sentiment_records.append(tmp_dict)

    df = pd.DataFrame(sentiment_records)

    return df



def insert_news_sentimnet_to_db(df):
    print(f"Inserting news article sentiment DataFrame into raw.sentiment")

    status, error = insert_sentiment_into_db(df)

    if status:
        print(f"[INFO] Successfully inserted news article sentiment into raw.sentiment.")
    else:
        print(f"[ERROR] Failed to insert news article sentiment into raw.sentiment.")
        print(f"[ERROR] Error: {error}")



if __name__ == "__main__":
    query = """
        SELECT
            *
        FROM raw.news
        """
    insert_news_sentimnet_to_db(get_sentiment_dataframe(query))



# Add in logic to avoid inserting duplicate columns