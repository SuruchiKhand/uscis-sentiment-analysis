# USCIS Sentiment Analysis

Analyze sentiment and trends in r/USCIS Reddit discussions to understand community concerns around U.S. immigration processes.

## Features

- **Data Collection**: Automated Reddit post collection via PRAW API
- **Sentiment Analysis**: Classify posts as positive, negative, or neutral using TextBlob
- **Topic Modeling**: Identify key themes with TF-IDF and LDA
- **Category Classification**: Group posts by USCIS service areas (Green Card, Citizenship, Work Visa, etc.)
- **Automated Reports**: Generate comprehensive analysis in Markdown format

## Quick Start

1. **Install dependencies**

   ```bash
   pip install praw pandas nltk textblob scikit-learn numpy
   ```

2. **Configure Reddit API**

   ```python
   # config.py
   REDDIT_CONFIG = {
       "client_id": "your_client_id",
       "client_secret": "your_client_secret",
       "user_agent": "your_app_name/1.0",
       "username": "your_username",
       "password": "your_password"
   }
   ```

3. **Run analysis**

   python main.py

## Sample Results

- **240 posts analyzed** (Jan-Aug 2025)
- **Sentiment**: 62.9% neutral, 31.7% positive, 5.4% negative
- **Top concern**: Interview processes (252 mentions)
- **Main categories**: Green Card (28.3%), Work Visa (28.3%), Citizenship (21.7%)

## Project Structure

```
├── src/
│   ├── data_collector.py    # Reddit API collection
│   └── analyzer.py          # NLP analysis
├── main.py                  # Run complete pipeline
├── config.py               # Settings
└── results/analysis_report.md
```

## Tech Stack

Python • PRAW • pandas • NLTK • TextBlob • scikit-learn
