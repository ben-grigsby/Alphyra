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



def get_inputted_source(query):
    df = get_db_info(query)

    source_lst = df['source_url'].unqiue().tolist()

    return source_lst



def get_sentiment_dataframe(news_search_query, existing_articles_query):
    source_lst = get_inputted_source(existing_articles_query)
    df = search_news_db(news_search_query)

    sentence_info = []
    lst_sentences = []

    for _, row in df.iterrows():
        if row['url'] in source_lst:
            continue

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

            sentence_info.append(tmp_dict)
            lst_sentences.append(sent)
    
    sentence_sentiment = analyze_sentiment(lst_sentences)

    for i in range(len(sentence_sentiment)):
            sentence_info[i]['positive_score'] = sentence_sentiment[i]['positive']
            sentence_info[i]['neutral_score'] = sentence_sentiment[i]['neutral']
            sentence_info[i]['negative_score'] = sentence_sentiment[i]['negative']


    df = pd.DataFrame(sentence_info)

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
    news_query = """
        SELECT
            *
        FROM raw.news
        """
    
    dupe_query = """
        SELECT
            DISTINCT url
        FROM staging_staging.stg_sentiment
        WHERE source_type != 'Youtube'
        """

    insert_news_sentimnet_to_db(get_sentiment_dataframe(news_query, dupe_query))



# Add in logic to avoid inserting duplicate columns