import praw
import pandas as pd
from datetime import datetime, timezone
from config import REDDIT_CONFIG


def collect_sample_data():
    """Collect a small sample of posts from r/USCIS for testing."""
    try:

        reddit = praw.Reddit(
            client_id=REDDIT_CONFIG["client_id"],
            client_secret=REDDIT_CONFIG["client_secret"],
            user_agent=REDDIT_CONFIG["user_agent"],
            username=REDDIT_CONFIG["username"],
            password=REDDIT_CONFIG["password"],
        )
        print("Collecting sample data from r/USCIS...")
        subreddit = reddit.subreddit("USCIS")
        posts_data = []

        for submission in subreddit.hot(limit=5):
            post_date = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)

            posts_data.append(
                {
                    "id": submission.id,
                    "title": submission.title,
                    "text": submission.selftext,
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                    "created_date": post_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "author": (
                        str(submission.author) if submission.author else "deleted"
                    ),
                    "url": submission.url,
                }
            )

        # Create DataFrame and save
        df = pd.DataFrame(posts_data)

        # Ensure the data directory exists
        import os

        if not os.path.exists("data"):
            os.makedirs("data")

        # Save to CSV
        df.to_csv("data/uscis_posts.csv", index=False)
        print(f"Saved {len(df)} posts to data/uscis_posts.csv")
        print(f"Columns: {list(df.columns)}")

        return df

    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    collect_sample_data()
    print("Sample data collection completed.")
