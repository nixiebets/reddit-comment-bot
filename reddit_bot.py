import praw
import prawcore
import time
import os
import logging
import json
import random
from config import (
    REDDIT_USERNAME,
    REDDIT_PASSWORD,
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    TARGET_SUBREDDITS,
    TARGET_STRING,
    REPLY_MESSAGE,
    SLEEP_DURATION,
)

HISTORY_FILE = "used_subreddits.json"

# Configuring logging
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

def handle_rate_limit(api_exception, retry_attempts=3):
    for attempt in range(retry_attempts):
        retry_after = api_exception.response.headers.get('retry-after')
        if retry_after:
            logger.warning(f"Rate limited. Retrying after {retry_after} seconds. Attempt {attempt + 1}/{retry_attempts}")
            time.sleep(int(retry_after) + 1)
        else:
            logger.error(f"API Exception: {api_exception}")
            break
    else:
        logger.error("Exceeded retry attempts. Aborting.")
        raise

def process_single_comment(comment, comments_replied_to, reddit_instance):
    if (
        TARGET_STRING in comment.body
        and comment.id not in comments_replied_to
        and comment.author != reddit_instance.user.me()
    ):
        logger.info(f"String with '{TARGET_STRING}' found in comment {comment.id}")
        try:
            comment.reply(REPLY_MESSAGE)
            logger.info(f"Replied to comment {comment.id}")
            comments_replied_to.append(comment.id)
            with open("comments_replied_to.txt", "a") as f:
                f.write(comment.id + "\n")
        except prawcore.exceptions.Forbidden as forbidden_error:
            logger.warning(f"Permission error for comment {comment.id}: {forbidden_error}. Skipping.")
        except Exception as reply_error:
            logger.exception(f"Error while replying to comment {comment.id}: {reply_error}")

def process_comments_in_subreddit(reddit_instance, subreddit_name, comments_replied_to):
    logger.info(f"Searching last 1,000 comments in r/{subreddit_name}")
    subreddit = reddit_instance.subreddit(subreddit_name)
    for comment in subreddit.comments(limit=1000):
        try:
            process_single_comment(comment, comments_replied_to, reddit_instance)
        except prawcore.exceptions.Forbidden as forbidden_error:
            logger.warning(f"Permission error for comment {comment.id}: {forbidden_error}. Skipping.")
        except Exception as error:
            logger.exception(f"Error processing comment {comment.id}: {error}")

def get_next_subreddit():
    # Load used subreddit history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            used = set(json.load(f))
    else:
        used = set()
    # Find unused subreddits
    unused = [s for s in TARGET_SUBREDDITS if s not in used]
    if not unused:
        used = set()
        unused = list(TARGET_SUBREDDITS)
    sub_name = random.choice(unused)
    used.add(sub_name)
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(used), f)
    return sub_name

if __name__ == "__main__":
    reddit_instance = bot_login()
    comments_replied_to = get_saved_comments()
    logger.info(f"Number of comments replied to: {len(comments_replied_to)}")

    while True:
        try:
            sub_name = get_next_subreddit()
            logger.info(f"Processing subreddit: r/{sub_name}")
            process_comments_in_subreddit(reddit_instance, sub_name, comments_replied_to)
            logger.info(f"Sleeping for {SLEEP_DURATION} seconds...")
            time.sleep(int(SLEEP_DURATION))
        except praw.exceptions.APIException as api_exception:
            handle_rate_limit(api_exception)
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            time.sleep(int(SLEEP_DURATION))
        except KeyboardInterrupt:
            logger.info("Bot terminated by user.")
            break
