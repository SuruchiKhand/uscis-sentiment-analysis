import praw
from config import REDDIT_CONFIG

try:
    reddit = praw.Reddit(
        client_id=REDDIT_CONFIG["client_id"],
        client_secret=REDDIT_CONFIG["client_secret"],
        user_agent=REDDIT_CONFIG["user_agent"],
        username=REDDIT_CONFIG["username"],
        password=REDDIT_CONFIG["password"],
    )
    print(f"Aunthenticated as: {reddit.user.me()}")
    print("Credentials are working.")

except Exception as e:
    print(f"Authentication failed: {e}")
    print("\nCheck these:")
    print("1. Client ID is correct.")
    print("2. Cient Secret is correct.")
    print("3. Username and password are correct.")
    print("4. Reddit app is set to 'script' type.")
