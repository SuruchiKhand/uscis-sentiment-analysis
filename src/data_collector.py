import praw
import pandas as pd
import time
from datetime import datetime, timezone
import os
from config import REDDIT_CONFIG, ANALYSIS_CONFIG


class RedditDataCollector:
    def __init__(self):
        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CONFIG["client_id"],
                client_secret=REDDIT_CONFIG["client_secret"],
                user_agent=REDDIT_CONFIG["user_agent"],
                username=REDDIT_CONFIG["username"],
                password=REDDIT_CONFIG["password"],
            )
            print("Successfully connected to Reddit API.")
        except Exception as e:
            print(f"Failed to connect to Reddit API:, {e}")
            raise

    def collect_posts(self, subreddit_name="USCIS", limit=1000):
        """Collects posts from a specified subreddit within a date range."""
        print(f"Collecting posts from r/{subreddit_name}...")

        subreddit = self.reddit.subreddit(subreddit_name)
        posts_data = []

        try:
            # Parse data range
            start_date = datetime.strftime(ANALYSIS_CONFIG["start_date"], "%Y-%m-%d")
            end_date = datetime.strftime(ANALYSIS_CONFIG["end_date"], "%Y-%m-%d")
            start_date = start_date.replace(tzinfo=timezone.utc)
            end_date = end_date.replace(tzinfo=timezone.utc)

            collected = 0

            # Collect from different sorting methods
            for sort_method in ["new", "hot", "top"]:
                print(f"Collecting from {sort_method} posts...")

                if sort_method == "new":
                    submissions = subreddit.new(limit=limit // 3)
                elif sort_method == "hot":
                    submissions = subreddit.hot(limit=limit // 3)
                else:
                    submissions = subreddit.top(time_filter="year", limit=limit // 3)

                for submission in submissions:
                    # Convert timestamp to datetime
                    post_date = datetime.fromtimestamp(
                        submission.created_utc, timezone.utc
                    )
                    # Check if the post is within the specified date range
                    if start_date <= post_date <= end_date:
                        posts_data.append(
                            {
                                "id": submission.id,
                                "title": submission.title,
                                "text": submission.selftext,
                                "score": submission.score,
                                "num_comments": submission.num_comments,
                                "created_date": post_date,
                                "author": (
                                    str(submission.author)
                                    if submission.author
                                    else "deleted"
                                ),
                                "url": submission.url,
                                "sort_method": sort_method,
                            }
                        )
                        collected += 1

                        if collected % 50 == 0:
                            print(f"Collected {collected} posts so far...")

                    # Add delay to respect Reddit's rate limits
                    time.sleep(0.1)
            print(f"Finished collecting posts. Total collected: {collected}")

        except Exception as e:
            print(f"An error occurred while collecting posts: {e}")
            return pd.DataFrame(posts_data)  # Return what we have so far

    def save_data(self, df, filename="uscis_posts.csv"):
        """Save collected data to CSV file."""
        if not os.path.exists("data"):
            os.makedirs("data")

        filepath = f"data/{filename}"
        df.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")
        return filepath


if __name__ == "__main__":
    collector = RedditDataCollector()
    posts_df = collector.collect_posts()
    collector.save_data(posts_df)
