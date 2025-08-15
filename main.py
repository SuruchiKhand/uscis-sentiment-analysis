from src.data_collector import RedditDataCollector
from src.analyzer import USCISAnalyzer
import os
import sys
import pandas as pd


def generate_report(analyzer, queries, topics, sentiment, categories):
    """Generate comprehensive analysis report."""

    if not os.path.exists("results"):
        os.makedirs("results")

    report = f"""# Reddit r/USCIS Sentiment Analysis Report
Generated: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}

## Dataset Overview
- **Total Posts Analyzed**: {len(analyzer.df):,}
- **Date Range**: {analyzer.df['created_date'].min()} to {analyzer.df['created_date'].max()}
- **Subreddit**: r/USCIS
- **Questions Identified**: {queries.get('total_questions', 0):,}

## 1. Most Common Queries & Terms

### Top 15 Keywords:
"""
    common_words = queries.get("common_words", [])
    if common_words:
        for i, (word, count) in enumerate(common_words[:15], 1):
            report += f"{i:2d}. **{word}**: {count:,} mentions\n"
    else:
        report += "No common words found.\n"

    total_questions = queries.get("total_questions", 0)
    report += f"\n### Question Posts: {total_questions:,} out of {len(analyzer.df):,} total posts ({total_questions / len(analyzer.df) * 100:.1f}%)\n"

    report += "\n## 2. Topic Analysis\n\n"
    if topics and len(topics) > 0:
        for i, topic in enumerate(topics, 1):
            report += f"### Topic {i}: {topic.get('description', 'Topic ' + str(i))}\n"
            report += f"Keywords: {', '.join(topic.get('keywords', []))}\n\n"
    else:
        report += "No topics could be extracted from the dataset (likely due to small sample size).\n\n"

    report += "\n## 3. Sentiment Analysis\n\n"

    # Handle different sentiment return formats
    print(f"Debug - Sentiment object type: {type(sentiment)}")
    print(f"Debug - Sentiment content: {sentiment}")

    sentiment_dist = {}
    if isinstance(sentiment, dict):
        if "sentiment_distribution" in sentiment:
            sentiment_dist = sentiment["sentiment_distribution"]
        elif "sentiment_counts" in sentiment:
            # Convert pandas Series to dict
            sentiment_counts = sentiment["sentiment_counts"]
            if hasattr(sentiment_counts, "to_dict"):
                sentiment_dist = sentiment_counts.to_dict()
            else:
                sentiment_dist = dict(sentiment_counts)
    elif hasattr(sentiment, "value_counts"):  # pandas Series
        sentiment_dist = sentiment.value_counts().to_dict()
    elif isinstance(sentiment, (list, tuple)):
        # If it's just a list of sentiments, count them
        from collections import Counter

        sentiment_dist = dict(Counter(sentiment))

    if sentiment_dist:
        report += f"### Overall Sentiment Distribution:\n"
        total_posts = sum(sentiment_dist.values()) if sentiment_dist else 0

        for sent, count in sentiment_dist.items():
            percentage = count / total_posts * 100 if total_posts > 0 else 0
            report += f"- **{sent}**: {count:,} posts ({percentage:.1f}%)\n"

        # Try to get average polarity
        avg_polarity = 0
        if isinstance(sentiment, dict):
            avg_polarity = sentiment.get("average_polarity", 0)
        report += f"\n**Average Sentiment Polarity**: {avg_polarity:.3f} (Range: -1.0 to 1.0)\n"

    report += "\n## 4. USCIS Categories Analysis\n\n"
    if categories and isinstance(categories, dict):
        for category, count in sorted(
            categories.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = count / len(analyzer.df) * 100 if len(analyzer.df) > 0 else 0
            report += f"- **{category.replace('_', ' ').title()}**: {count:,} posts ({percentage:.1f}%)\n"
    else:
        report += "No category analysis available.\n"

    report += "\n## Key Insights\n\n"

    # Generate insights with error handling
    try:
        # Handle common words
        common_words = queries.get("common_words", [])
        most_common_word = common_words[0][0] if common_words else "N/A"

        # Handle sentiment
        dominant_sentiment = "N/A"
        if sentiment_dist:
            dominant_sentiment = max(sentiment_dist.items(), key=lambda x: x[1])[0]

        # Handle categories
        top_category = "N/A"
        if categories and isinstance(categories, dict):
            top_category = max(categories.items(), key=lambda x: x[1])[0].replace(
                "_", " "
            )

        # Handle comments
        avg_comments = 0
        if hasattr(analyzer, "df") and "num_comments" in analyzer.df.columns:
            avg_comments = analyzer.df["num_comments"].mean()

        report += f"1. **Most Discussed Term**: '{most_common_word}' appears most frequently\n"
        report += f"2. **Overall Mood**: '{dominant_sentiment}' sentiment dominates the discussions\n"
        report += f"3. **Primary Concern**: '{top_category.title()}' related posts are most common\n"
        report += (
            f"4. **User Engagement**: Average of {avg_comments:.1f} comments per post\n"
        )

        if len(analyzer.df) < 50:
            report += f"\n**Note**: This analysis is based on a small dataset ({len(analyzer.df)} posts). "
            report += "Results may not be representative. Consider collecting more data for more reliable insights.\n"

    except Exception as e:
        report += f"Error generating insights: {str(e)}\n"

    # Save report
    try:
        with open("results/analysis_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("Full report saved to results/analysis_report.md")
    except Exception as e:
        print(f"Error saving report: {e}")

    print("\nCOMPREHENSIVE ANALYSIS REPORT")
    print("=" * 50)
    print(report)


def main():
    print("Starting Reddit USCIS Sentiment Analysis...")
    print("=" * 50)

    # Collect data if not already collected
    data_file = "data/uscis_posts.csv"

    # Option to force fresh data collection
    force_new_collection = (
        input("Do you want to collect fresh data? (y/N): ").lower().strip() == "y"
    )

    if force_new_collection or not os.path.exists(data_file):
        if force_new_collection and os.path.exists(data_file):
            print("Removing existing data file to collect fresh data...")
            os.remove(data_file)

        print("Starting data collection...")
        try:
            collector = RedditDataCollector()
            posts_df = collector.collect_posts()
            collector.save_data(posts_df)
            print(f"Successfully collected {len(posts_df)} posts!")
        except Exception as e:
            print(f"Error during data collection: {e}")
            sys.exit(1)
    else:
        print("Using existing data file.")

    # Step 2: Analyze the data
    try:
        analyzer = USCISAnalyzer(data_file)
        print(f"\nLoaded {len(analyzer.df)} posts for analysis")

        # Check if we have enough data
        if len(analyzer.df) < 3:
            print("Warning: Very small dataset. Some analyses may not work properly.")
            print("Consider collecting more data for better results.")

        print("\nRunning comprehensive analysis...")

        # Get all analysis results with error handling
        try:
            print("Analyzing common queries...")
            queries = analyzer.analyze_common_queries()
        except Exception as e:
            print(f"Error in query analysis: {e}")
            queries = {"common_words": [], "total_questions": 0}

        try:
            print("Performing topic analysis...")
            topics = analyzer.analyze_topics()
        except Exception as e:
            print(f"Topic analysis failed (common with small datasets): {e}")
            topics = []

        try:
            print("Analyzing sentiment...")
            sentiment = analyzer.analyze_sentiment()
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            sentiment = {"sentiment_distribution": {}, "average_polarity": 0}

        try:
            print("Analyzing USCIS categories...")
            categories, category_posts = analyzer.analyze_uscis_categories()
        except Exception as e:
            print(f"Error in category analysis: {e}")
            categories = {}

        # Generate report
        generate_report(analyzer, queries, topics, sentiment, categories)

    except Exception as e:
        print(f"Analysis failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback

        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
