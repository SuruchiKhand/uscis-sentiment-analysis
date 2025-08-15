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
            print(f"Failed to connect to Reddit API: {e}")
            raise

    def collect_posts(self, subreddit_name="USCIS", limit=1000):
        """Collects posts from a specified subreddit within a date range."""
        print(f"Collecting posts from r/{subreddit_name}...")

        subreddit = self.reddit.subreddit(subreddit_name)
        posts_data = []
        collected_ids = set()  # Prevent duplicates

        try:
            # Parse date range - Fix the datetime parsing
            start_date = ANALYSIS_CONFIG["start_date"]
            end_date = ANALYSIS_CONFIG["end_date"]

            # Convert to datetime objects if they're strings
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
            elif not start_date.tzinfo:
                start_date = start_date.replace(tzinfo=timezone.utc)

            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
            elif not end_date.tzinfo:
                end_date = end_date.replace(tzinfo=timezone.utc)

            print(f"Collecting posts from {start_date.date()} to {end_date.date()}")

            collected = 0

            # Collect from different sorting methods
            for sort_method in ["new", "hot", "top"]:
                print(f"Collecting from {sort_method} posts...")
                method_collected = 0

                try:
                    if sort_method == "new":
                        submissions = subreddit.new(limit=limit // 3)
                    elif sort_method == "hot":
                        submissions = subreddit.hot(limit=limit // 3)
                    else:
                        submissions = subreddit.top(
                            time_filter="year", limit=limit // 3
                        )

                    for submission in submissions:
                        # Skip if we already have this post
                        if submission.id in collected_ids:
                            continue

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
                            collected_ids.add(submission.id)
                            collected += 1
                            method_collected += 1

                            if collected % 50 == 0:
                                print(f"Collected {collected} posts so far...")

                        # Add delay to respect Reddit's rate limits
                        time.sleep(0.1)

                except Exception as method_error:
                    print(f"Error collecting from {sort_method}: {method_error}")
                    continue

                print(f"Collected {method_collected} posts from {sort_method}")

            print(f"Finished collecting posts. Total collected: {collected}")

            # If we got very few posts, let's try without date filtering
            if collected < 20:
                print(
                    f"Warning: Only collected {collected} posts. This might be due to:"
                )
                print(
                    f"1. Date range too restrictive: {start_date.date()} to {end_date.date()}"
                )
                print(f"2. Low activity in r/{subreddit_name}")
                print(f"3. API limits or permissions")

                # Try collecting without date filter as fallback
                print("Attempting to collect recent posts without date filtering...")
                fallback_posts = self.collect_recent_posts(subreddit, limit=200)
                if fallback_posts:
                    print(f"Collected additional {len(fallback_posts)} recent posts")
                    posts_data.extend(fallback_posts)

        except Exception as e:
            print(f"An error occurred while collecting posts: {e}")
            print(f"Returning {len(posts_data)} posts collected so far")

        # Create DataFrame and remove duplicates
        df = pd.DataFrame(posts_data)
        if not df.empty:
            df = df.drop_duplicates(subset=["id"], keep="first")
            print(f"Final dataset: {len(df)} unique posts")

        return df

    def collect_recent_posts(self, subreddit, limit=200):
        """Fallback method to collect recent posts without date filtering."""
        posts_data = []
        try:
            # Just get recent posts
            for submission in subreddit.new(limit=limit):
                post_date = datetime.fromtimestamp(submission.created_utc, timezone.utc)
                posts_data.append(
                    {
                        "id": submission.id,
                        "title": submission.title,
                        "text": submission.selftext,
                        "score": submission.score,
                        "num_comments": submission.num_comments,
                        "created_date": post_date,
                        "author": (
                            str(submission.author) if submission.author else "deleted"
                        ),
                        "url": submission.url,
                        "sort_method": "new_fallback",
                    }
                )
                time.sleep(0.05)  # Shorter delay for fallback
        except Exception as e:
            print(f"Fallback collection failed: {e}")

        return posts_data

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
