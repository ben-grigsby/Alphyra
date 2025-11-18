# Alphyra



# Ideas

- Start off with text article downloads
    - Reasoning:
        1. I can do a wide sweep rather quickly 
        2. I can later utilize keywords that appear in headlines or summaries to hone in on the Youtube search videos which speeds up that process
        3. I need to match the company's that have news and are being stored in my database to the ones that have videos


- Setting up data for modeling
    - Treat the video sentiment analysis as sparse, if it is there then that's a great addition and if it's not my model can still handle it 
    - Each row will represent a company on a specific day and the average sentiment of news on that day and videos if possible along with some other things like a moving average or something 

- Think about how embeddings can work its way into this project


# Problem

- Currently figuring out a way to determine historic shares outstanding so the model wil be better at determining the output price without being too heavily influenced by how large the daily sell price is or buy price
    - Solution
        - Find the quarterly shares outstanding from SEC filings or something and then determine the market cap by multiplying shares outstanding with closing_price 

