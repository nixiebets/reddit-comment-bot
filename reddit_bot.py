import praw
import prawcore
import time
import os
import logging
import json
import random
import re
import openai
from config import (
    REDDIT_USERNAME, REDDIT_PASSWORD, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT,
    OPENAI_API_KEY, TARGET_SUBREDDITS, TRIGGER_WORDS, LLM_PROMPT_TEMPLATE, SLEEP_DURATION_MIN, SLEEP_DURATION_MAX,
REPLY_TEMPLATES, GENRES, ARTISTS, TRAKTRAIN_LINK
)

HISTORY_FILE = "used_subreddits.json"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def bot_login():
    logger.info("Logging in...")
    reddit_instance = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        user_agent=REDDIT_USER_AGENT,
        check_for_async=False
    )
    logger.info(f"Logged in as: {reddit_instance.user.me()}")
    return reddit_instance

def get_saved_comments():
    if not os.path.isfile("comments_replied_to.txt"):
        return []
    with open("comments_replied_to.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def get_next_subreddit():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            used = set(json.load(f))
    else:
        used = set()
    unused = [s for s in TARGET_SUBREDDITS if s not in used]
    if not unused:
        used = set()
        unused = list(TARGET_SUBREDDITS)
    sub_name = random.choice(unused)
    used.add(sub_name)
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(used), f)
    return sub_name

def matches_trigger(comment_body):
    body = comment_body.lower()
    return any(word in body for word in TRIGGER_WORDS)

def generate_reply(comment_body):
    # Try to match genre or artist from comment
    genre = next((g for g in GENRES if g in comment_body.lower()), random.choice(GENRES))
    artist = next((a for a in ARTISTS if a.lower() in comment_body.lower()), random.choice(ARTISTS))
    template = random.choice(REPLY_TEMPLATES)
    reply = template.format(
        genre=genre,
        artist=artist,
        link=TRAKTRAIN_LINK
    )
    return reply

def process_comments_in_subreddit(reddit_instance, subreddit_name, comments_replied_to):
    logger.info(f"Searching last 1,000 comments in r/{subreddit_name}")
    subreddit = reddit_instance.subreddit(subreddit_name)
    print("About to iterate comments")
    try:
        for comment in subreddit.comments(limit=1000):
            # Skip bots and deleted users
            if (
                comment.author is None
                or str(comment.author).lower() == "automoderator"
                or str(comment.author).lower() == str(reddit_instance.user.me()).lower()
                
            ):
                continue  # Skip to next comment

            if matches_trigger(comment.body) and comment.id not in comments_replied_to:
                reply_text = generate_reply(comment.body)
                print(f"Replied to comment {comment.id} (by {comment.author}) with: {reply_text}")
                comment.reply(reply_text)
                comments_replied_to.append(comment.id)
                with open("comments_replied_to.txt", "a") as f:
                    f.write(comment.id + "\n")
                return True  # Only reply once per run
    except Exception as e:
        print(f"Error in process_comments_in_subreddit: {e}")
    return False

# ---- MAIN BLOCK (AT THE BOTTOM!!) ----
if __name__ == "__main__":
    print("Reddit bot script is starting...")
    try:
        reddit_instance = bot_login()
        comments_replied_to = get_saved_comments()
        logger.info(f"Number of comments replied to: {len(comments_replied_to)}")

        while True:
            sub_name = get_next_subreddit()
            logger.info(f"Processing subreddit: r/{sub_name}")
            replied = process_comments_in_subreddit(reddit_instance, sub_name, comments_replied_to)
            sleep_time = random.randint(SLEEP_DURATION_MIN, SLEEP_DURATION_MAX)
            logger.info(f"Selected subreddit: {sub_name}")
            logger.info(f"Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback; traceback.print_exc()
