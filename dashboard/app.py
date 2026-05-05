import streamlit as st
import pandas as pd
import os

from sqlalchemy import create_engine
from dotenv import load_dotenv

POSTGRES_URL = os.getenv("POSTGRES_URL")
engine = create_engine(POSTGRES_URL)

st.set_page_config(
    page_title="Alphyra",
    page_icon=":material/dataset:",
    layout="wide"
)

st.title("Alphyra Dashboard")

with st.expander("About Alphyra"):
    st.title("About Alphyra")
    st.write("""
                Alphyra is designed to reduce the time it takes to switch between different websites when learning about a company/stock.
                The goal is to aggregate all sorts of information deemed useful to learning more about a company and subsequently improving decision-making.
            """)
    

query = """
    SELECT *
    FROM staging_intermediate.int_video_sentiment
    LIMIT 10
"""

df = pd.read_sql(query, engine)

st.dataframe(df)