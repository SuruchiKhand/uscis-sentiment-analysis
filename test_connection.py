import praw
import pandas as pd
from datetime import datetime, timezone
import time
from config import REDDIT_CONFIG, ANALYSIS_CONFIG


def test_reddit_connection():
    """Test if Reddit API connection works"""
    try:
        print(" Testing Reddit API connection...")

        # Initialize Reddit connection
        reddit = praw.Reddit(
            client_id=REDDIT_CONFIG["client_id"],
            client_secret=REDDIT_CONFIG["client_secret"],
            user_agent=REDDIT_CONFIG["user_agent"],
            username=REDDIT_CONFIG["username"],
            password=REDDIT_CONFIG["password"],
        )

        print(" Successfully connected to Reddit API")

        # Test data collection with a small sample
        print("🔍 Testing data collection from r/USCIS...")

        subreddit = reddit.subreddit("USCIS")
        posts_data = []

        # Collect just a few posts for testing
        count = 0
        for submission in subreddit.hot(limit=10):
            try:
                # Convert timestamp to datetime object
                post_date = datetime.fromtimestamp(
                    submission.created_utc, tz=timezone.utc
                )

                posts_data.append(
                    {
                        "id": submission.id,
                        "title": submission.title,
                        "text": submission.selftext,
                        "score": submission.score,
                        "num_comments": submission.num_comments,
                        "created_date": post_date,  # Keep as datetime object
                        "author": (
                            str(submission.author) if submission.author else "deleted"
                        ),
                        "url": submission.url,
                    }
                )
                count += 1

                if count >= 5:  # Just collect 5 posts for testing
                    break

                time.sleep(0.2)  # Small delay to be respectful

            except Exception as e:
                print(f"  Error processing post {submission.id}: {e}")
                continue

        # Create DataFrame
        test_df = pd.DataFrame(posts_data)

        print(f" Test successful! Collected {len(test_df)} posts")

        if len(test_df) > 0:
            print("\n Sample post information:")
            for i, row in enumerate(test_df.head(3).iterrows()):
                idx, data = row
                print(f"{i+1}. Title: {data['title'][:80]}...")
                print(f"   Date: {data['created_date'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Score: {data['score']}, Comments: {data['num_comments']}")
                print()

            # Test date filtering (this was causing the original error)
            print(" Testing date filtering...")
            try:
                start_date = datetime.strptime(
                    ANALYSIS_CONFIG["start_date"], "%Y-%m-%d"
                )
                end_date = datetime.strptime(ANALYSIS_CONFIG["end_date"], "%Y-%m-%d")
                start_date = start_date.replace(tzinfo=timezone.utc)
                end_date = end_date.replace(tzinfo=timezone.utc)

                # Filter posts by date range
                filtered_df = test_df[
                    (test_df["created_date"] >= start_date)
                    & (test_df["created_date"] <= end_date)
                ]

                print(f" Date filtering works! {len(filtered_df)} posts in date range")
                print(f" Date range: {start_date.date()} to {end_date.date()}")

            except Exception as e:
                print(f" Date filtering error: {e}")
        else:
            print(" No posts collected. This might be due to:")
            print("   - Network connectivity issues")
            print("   - Subreddit access restrictions")
            print("   - API rate limiting")

        return True

    except Exception as e:
        print(f" Test failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Check your credentials in config.py")
        print("   2. Make sure your Reddit app is set to 'script' type")
        print("   3. Verify your internet connection")
        print("   4. Check if r/USCIS subreddit is accessible")
        return False


if __name__ == "__main__":
    success = test_reddit_connection()

    if success:
        print("\n Connection test passed! You can now run the full data collection.")
    else:
        print(
            "\n Connection test failed. Please fix the issues above before proceeding."
        )
