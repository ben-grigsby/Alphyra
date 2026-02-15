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
    """
    Search YouTube for videos matching a query within a specified date range.

    Parameters
    ----------
    text : list
        A list of sentences that will be inserted into the NLP sentiment analysis function

    Returns
    -------
    list of dict
        A list of dictionaries with the index corresponding to each 
    """
    sentences = split_into_sentences(chunk=text)
    
    lst_dicts = []

    for sent in sentences:
        sentiment_dict = analyze_sentiment(sent)
        lst_dicts.append(sentiment_dict)
    
    return lst_dicts



def get_inputted_source(query):
    df = get_db_info(query)

    source_lst = df['source_url'].unique().tolist()

    return source_lst



def get_sentiment_dataframe(news_search_query, existing_articles_query):
    source_set = set(get_inputted_source(existing_articles_query))
    df = search_news_db(news_search_query)

    if df.empty:
        print(f"[INFO] No news to run sentiment analysis on")
        return df

    if source_set:
        print(f"[INFO] Separating new articles from articles that have already been processed")
        processed_articles_mask = df['url'].apply(lambda x: x in source_set)
        processed_articles_df = df[processed_articles_mask]
        new_articles_df = df[~processed_articles_mask]
    else:
        print(f"[INFO] Ingesting into raw.sentiment for the first time")
        new_articles_df = df
        processed_articles_df = df.iloc[0:0]

    sentence_info = []
    lst_sentences = []

    if not processed_articles_df.empty:
        print(f"[INFO] {processed_articles_df.shape[0]} duplicate articles")


    print(f"[INFO] Starting sentiment analysis on {new_articles_df.shape[0]} articles")

    if not new_articles_df.empty:
        for _, row in new_articles_df.iterrows():

            print(f"[INFO] Analyzing sentiment for {row['url']} article summary.")
            sentences = split_into_sentences(chunk=row['summary'])
            for sent in sentences:
                tmp_dict = {
                    'sentence': sent,
                    'model_name': 'FinBERT',
                    'source_type': row['source'],
                    'source_url': row['url'],
                    'published_at': row['published_at'],
                }

                sentence_info.append(tmp_dict)
                lst_sentences.append(sent)
        
        sentence_sentiment = analyze_sentiment(lst_sentences)
        
        for info, sentiment in zip(sentence_info, sentence_sentiment):
            info['positive_score'] = sentiment['positive']
            info['neutral_score'] = sentiment['neutral']
            info['negative_score'] = sentiment['negative']
        

    df = pd.DataFrame(sentence_info)

    return df



def insert_news_sentiment_to_db(df):
    if df.empty:
        print(f"[INFO] Empty news dataframe. Ending news sentiment analysis function")
        return

    print(f"[INFO] Inserting news article sentiment DataFrame into raw.sentiment")

    status, error = insert_sentiment_into_db(df)

    if status and error != 'Empty':
        print(f"[INFO] Successfully inserted news article sentiment into raw.sentiment.")
    elif status and error == 'Empty':
        print(f"[INFO] No news article sentiment inserted due to no news in raw.news.")
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
            DISTINCT source_url
        FROM raw.sentiment
        WHERE source_type != 'Video'
        """

    insert_news_sentiment_to_db(get_sentiment_dataframe(news_query, dupe_query))




# Add in logic to avoid inserting duplicate columns