from config import REDDIT_CONFIG
import praw


def test_auth():
    print("Testing Reddit authetication...")
    print(f"Client ID length: {len(REDDIT_CONFIG['client_id'])}")
    print(f"Clients Secret length: {len(REDDIT_CONFIG['client_secret'])}")

    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CONFIG["client_id"],
            client_secret=REDDIT_CONFIG["client_secret"],
            user_agent=REDDIT_CONFIG["user_agent"],
            username=REDDIT_CONFIG["username"],
            password=REDDIT_CONFIG["password"],
        )
        # Test basic authentication
        user = reddit.user.me()
        print(f"Successfully authenticated as: {user}")

        # Test subreddit access
        subreddit = reddit.subreddit("USCIS")
        print(f"Can access r/USCIS")

        # Try to get one post
        for post in subreddit.hot(limit=1):
            print(f"Can read posts: Sample: {post.title[:50]}...")
            break

    except Exception as e:
        print(f"Authentication failed: {e}")
        return False


if __name__ == "__main__":
    test_auth()
    print("Reddit authentication test completed.")
