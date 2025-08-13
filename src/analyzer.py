import pandas as pd
import nltk
import re
from textblob import TextBlob
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np

# Download required NLTK data
try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("corpora/stopwords")
except LookupError:
    print("Downloading NLTK data...")
    nltk.download("punkt")
    nltk.download("stopwords")


class USCISAnalyzer:
    def __init__(self, data_file="data/uscis_posts.csv"):
        """Initialize the analyzer with data file."""
        try:
            self.df = pd.read_csv(data_file)
            print(f"Loaded {len(self.df)} posts from analysis")
            self.preprocess_data()
        except FileNotFoundError:
            print(f"Data file not found: {data_file}")
            raise

    def preprocess_data(self):
        """Clean and preprocess text data."""
        print("Preprocessing data...")

        # Convert date column
        self.df["created_date"] = pd.to_datetime(self.df["created_date"])

        # Convert title and text
        self.df["full_text"] = (
            self.df["title"].fillna("") + " " + self.df["text"].fillna("")
        )

        # Clean text
        self.df["clean_text"] = self.df["full_text"].apply(self.clean_text)

        # Remove empty posts
        self.df = self.df[self.df["clean_text"].str.len() > 10]

        print("Preprocessing complete! {len(self.df)} posts ready for analysis.")

    def clean_text(self, text):
        """Clean individual text entries."""
        if pd.isna(text):
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)

        # Remove special characters but keep spaces
        text = re.sub(r"[^a-zA-Z\s]", "", text)

        # Remove extra whitespace
        text = " ".join(text.split())

        return text

    def analyze_common_queries(self, top_n=20):
        """Find most common queries and keywords."""
        print("Analyzing common queries...")

        # Find question posts
        question_patterns = [
            "how",
            "what",
            "when",
            "where",
            "why",
            "can I",
            "should I",
            "is it",
            "do I",
        ]
        question_posts = self.df[
            self.df["clean_text"].str.contains("|".join(question_patterns), na=False)
        ]

        # Get word frequency
        all_text = " ".join(self.df["clean_text"])
        words = all_text.split()

        # Remove common stopwords
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "a",
            "an",
            "this",
            "that",
            "these",
            "those",
            "i",
            "me",
            "my",
            "we",
            "us",
            "our",
            "you",
            "your",
            "he",
            "him",
            "his",
            "she",
            "her",
            "it",
            "its",
            "they",
            "them",
            "their",
        }
        filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
        common_words = Counter(filtered_words).most_common(top_n)

        return {
            "question_posts": question_posts,
            "common_words": common_words,
            "total_questions": len(question_posts),
        }

    def analyze_topics(self, n_topics=5):
        """Perform topic modeling"""
        print("Performing topic analysis...")

        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            max_features=100, stop_words="english", ngram_range=(1, 2), min_df=5
        )
        tfidf_matrix = vectorizer.fit_transform(self.df["clean_text"])

        # Perform LDA
        lda = LatentDirichletAllocation(
            n_components=n_topics, random_state=42, max_iter=10
        )
        lda.fit(tfidf_matrix)

        # Extract topics
        feature_names = vectorizer.get_feature_names_out()
        topics = []

        for topic_idx, topic in enumerate(lda.components_):
            top_words = [feature_names[i] for i in topic.argsort()[-8:]][::-1]
            topics.append(
                {
                    "topic_id": topic_idx + 1,
                    "keywords": top_words,
                    "description": f"Topic[topic_idx + 1]: {', '.join(top_words[:5])}",
                }
            )
        return topics

    def analyze_sentiments(self):
        """Perform sentiment analysis."""
        print("Performing sentiment analysis...")

        def get_sentiment(text):
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity

            if polarity > 0.1:
                return "positive"
            elif polarity < -0.1:
                return "negative"
            else:
                return "neutral"

        self.df["sentiment"] = self.df["clean_text"].apply(get_sentiment)
        self.df["polarity_score"] = self.df["clean_text"].apply(
            lambda x: TextBlob(x).sentiment.polarity
        )

        # Get sentiment distribution
        sentiment_counts = self.df["sentiment"].value_counts()

        # Monthly sentiment trends
        self.df["month"] = self.df["created_date"].dt.to_period("M")
        monthly_sentiment = (
            self.df.groupby(["month", "sentiment"]).size().unstack(fill_value=0)
        )

        return {
            "sentiment_counts": sentiment_counts,
            "monthly_trends": monthly_sentiment,
            "average_polarity": self.df["polarity_score"].mean(),
        }

        def analyze_uscis_categories(self):
            """Analyze USCIS specific categories."""
            print("Analyzing USCIS categories...")

            categories = {
                "green_card": [
                    "green card",
                    "i485",
                    "adjustment of status",
                    "aos",
                    "permanent resident",
                ],
                "citizenship": [
                    "n400",
                    "citizenship",
                    "naturalization",
                    "oath ceremony",
                    "citizen",
                ],
                "work_visa": [
                    "h1b",
                    "h-1b",
                    "i94",
                    "work authorization",
                    "ead",
                    "work permit",
                ],
                "family_visa": [
                    "i130",
                    "family petition",
                    "spouse visa",
                    "fiance",
                    "k1",
                    "marriage",
                ],
                "processing_issues": [
                    "delay",
                    "waiting",
                    "processing time",
                    "stuck",
                    "slow",
                    "expedite",
                ],
            }

            category_counts = {}
            category_posts = {}

            for category, keywords in categories.items():
                pattern = "|".join(keywords)
                mask = self.df["clean_text"].str.contains(pattern, case=False)
                count = mask.sum()
                category_counts[category] = count
                category_posts[category] = self.df[mask]
            return category_counts, category_posts


if __name__ == "__main__":
    analyzer = USCISAnalyzer()

    # Run analyses
    queries = analyzer.analyze_common_queries()
    topics = analyzer.analyze_topics()
    sentiment = analyzer.analyze_sentiment()
    categories, _ = analyzer.analyze_uscis_categories()

    print("\n" + "=" * 50)
    print("Analysis Results")
    print("=" * 50)

    print(f"\n TOP 10 COMMON WORDS:")
    for word, count in queries["common_words"][:10]:
        print(f"{word}: {count}")

    print(f"\n TOPICS DISCOVERED:")
    for topic in topics:
        print(f" {topic['description']}")

    print(f"\n SENTIMENT DISTRIBUTION:")
    for sentiment, count in sentiment["sentiment_distribution"].items():
        percentage = (count / len(analyzer.df)) * 100
        print(f"{sentiment}: {count} ({percentage:.1f}%)")

    print(f"\n USCIS CATEGORIES:")
    for category, count in categories.items():
        print(f" {category.replace('_', ' ').title()}: {count} posts")
