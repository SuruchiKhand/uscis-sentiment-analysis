from src.data_collector import RedditDataCollector
from src.analyzer import USCISAnalyzer
import os
import sys


def main():
    print("Starting Reddit USCIS Sentiment Analysis...")
    print("=" * 50)

    # Collect data if not already collected
    data_file = "data/uscis_posts.csv"

    if not os.path.exists(data_file):
        print("No existing data found. Starting data collection...")
        try:
            collector = RedditDataCollector()
            posts_df = collector.collect_posts()
            collector.save_data(posts_df)
        except Exception as e:
            print(f"Error during data collection: {e}")
            sys.exit(1)
    else:
        print("Using existing data file.")

    # Step 2: Analyze the data

    try:
        analyzer = USCISAnalyzer(data_file)
        print("\n Running comprehensive analysis...")

        # Get all analysis results
        queries = analyzer.analyze_commom_queries()
        topics = analyzer.analyze_topics()
        sentiment = analyzer.analyze_sentiment()
        categories, category_posts = analyzer.analyze_uscis_categories()

        # Generate report
        generate_report(analyzer, queries, topics, sentiment, categories)

    except Exception as e:
        print(f"Analysis failed: {e}")
        sys.exit(1)

    def generate_report(analyzer, queries, topics, sentiment, categories):
        """Generate comprehensive analysis report."""

        if not os.path.exists("results"):
            os.makedirs("results")

        report = f"""# Reddit r/USCIS Sentiment Analysis Report Generated: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}

    ## Dataset Overview
    - **Total Posts Analyzed**: {len(analyzer.df):,}
    - **Date Range**: {analyzer.df['created_date'].min()} to {analyzer.df['created_date'].max()}
    - **Subreddit**: r/USCIS
    - **Questions Identified**: {queries['total_questions']:,}

    ## 1. Most Common Queries & Terms

    ###Top 15 Keywords:
    """
        for i, (word, count) in enumerate(queries["common_words"][:15], 1):
            report += f"{i:2d}. **{word}**: {count:,} mentions\n"

        report += f"\n### Question Posts: {queries['total_questions']:,} out of {len(analyzer.df):,} total posts ({queries['total_questions'] / len(analyzer.df) * 100:.1f}%)\n"

        report += "\n## 2. Topic Analysis\n\n"
        for topic in topics:
            report += f"### {topic['description']}\n"
            report += f"Keywords: {', '.join(topic['keywords'])}\n"

        report += "\n## 3. Sentiment Analysis\n\n"
        report += f"### Overall Sentiment Distribution:\n"
        total_posts = sum(sentiment["sentiment_distribution"])
        for sent, count in sentiment["sentiment_distribution"].items():
            percentage = count / total_posts * 100
            report += (
                f"- **{sent}**: {count:,} posts ({count / total_posts * 100:.1f}%)\n"
            )

        report += f"\n**Average Sentiment Polarity**: {sentiment['average_polarity']:.3f} (Range: -1.0 to 1.0)\n"
        report += "\n## 4. USCIS Categories Analysis\n\n"
        for category, count in sorted(
            categories.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = count / len(analyzer.df) * 100
            report += f"- **{category.replace('_', ' ').title()}**: {count:,} posts ({percentage:.1f}%)\n"

        report += "\n## Key Insights\n\n"

        # Generate insights
        most_common_word = (
            queries["common_words"][0][0] if queries["common_words"] else "N/A"
        )
        dominant_sentiment = sentiment["sentiment_distribution"].idxmax()
        top_category = max(categories.items(), key=lambda x: x[1])[0].replace("_", " ")

        report += (
            f"1. **Most Discussed Term**: {most_common_word}' appears most frequently\n"
        )
        report += f"2. **Overall Mood**:'{dominant_sentiment}' sentiment dominates the discussions\n"
        report += f"3. **Primary Concern**: '{top_category.title()}' related posts are most common\n"
        report += f"4. **User Engagement**: Average of {analyzer.df['num_comments'].mean():.1f}comments per post\n"

        # Save report
        with open("results/analysis_report.md", "w", encoding="utf-8") as f:
            f.write(report)

        print("COMPHREHENSIVE ANALYSIS REPORT")
        print("=" * 50)
        print(report)
        print("\nFull report saved to results/analysis_report.md")


if __name__ == "__main__":
    import pandas as pd

    main()
