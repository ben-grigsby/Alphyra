-- Create schema 
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS mart;

-- Create raw news tables
CREATE TABLE IF NOT EXISTS raw.news(
    id SERIAL PRIMARY KEY,
    content_id CHAR(32) NOT NULL UNIQUE,
    company_name VARCHAR(500),
    sector VARCHAR(100),
    symbol VARCHAR(10),
    headline TEXT,
    summary TEXT,
    source VARCHAR(255),
    category VARCHAR(100),
    published_at TIMESTAMP,
    url TEXT,
    raw_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Create raw videos tables
CREATE TABLE IF NOT EXISTS raw.videos (
    id SERIAL PRIMARY KEY,
    content_id CHAR(32) NOT NULL UNIQUE,
    symbol VARCHAR(10) NOT NULL,
    video_id VARCHAR(100) NOT NULL,
    title TEXT,
    url TEXT,
    transcript_path TEXT,
    is_copy BOOLEAN NOT NULL,
    publish_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create raw sentiment table (sentence-level)
CREATE TABLE IF NOT EXISTS raw.sentiment (
    id SERIAL PRIMARY KEY,
    content_id CHAR(32) NOT NULL,
    sentence TEXT,
    positive_score FLOAT,
    neutral_score FLOAT,
    negative_score FLOAT,
    model_name VARCHAR(100),
    source_type VARCHAR(50),
    source_url TEXT,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create raw stock prices table
CREATE TABLE IF NOT EXISTS raw.stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10),
    date DATE,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create raw company financials table
CREATE TABLE IF NOT EXISTS raw.company_financials (
    symbol TEXT,
    source TEXT,
    metric_type TEXT,
    metric_name TEXT,
    metric_period TEXT,
    metric_value DOUBLE PRECISION,
    snapshot_date DATE NULL,
    financial_period_end DATE NULL,
    retrieved_at TIMESTAMP,
    raw_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sentiment index
CREATE INDEX IF NOT EXISTS idx_sentiment_content_id
ON raw.sentiment(content_id);