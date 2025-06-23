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
    OPENAI_API_KEY, TARGET_SUBREDDITS, TRIGGER_WORDS, LLM_PROMPT_TEMPLATE, SLEEP_DURATION
)

HISTORY_FILE = "used_subreddits.json"

# Logging setup
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

def generate_llm_reply(comment_body):
    prompt = LLM_PROMPT_TEMPLATE.format(comment_body=comment_body.strip())
    response = openai.ChatCompletion.create(
        api_key=OPENAI_API_KEY,
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=90,
        temperature=0.9,
    )
    return response.choices[0].message["content"].strip()

def process_comments_in_subreddit(reddit_instance, subreddit_name, comments_replied_to):
    logger.info(f"Searching last 1,000 comments in r/{subreddit_name}")
    subreddit = reddit_instance.subreddit(subreddit_name)
    for comment in subreddit.comments(limit=1000):
        try:
            if (
                matches_trigger(comment.body)
                and comment.id not in comments_replied_to
                and comment.author != reddit_instance.user.me()
            ):
                logger.info(f"Trigger word found in comment {comment.id}")
                llm_reply = generate_llm_reply(comment.body)
                comment.reply(llm_reply)
                logger.info(f"Replied to comment {comment.id}")
                comments_replied_to.append(comment.id)
                with open("comments_replied_to.txt", "a") as f:
                    f.write(comment.id + "\n")
                return True  # Replied, so stop for this run
        except praw.exceptions.APIException as api_exception:
            if hasattr(api_exception, "items") and api_exception.items and api_exception.items[0][0] == "ratelimit":
                msg = api_exception.items[0][1]
                minutes = re.search(r"(\d+) minutes?", msg)
                seconds = re.search(r"(\d+) seconds?", msg)
                sleep_time = 60  # Default to 1 minute
                if minutes:
                    sleep_time = int(minutes.group(1)) * 60 + 10
                elif seconds:
                    sleep_time = int(seconds.group(1)) + 10
                logger.warning(f"RATELIMIT: Sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)
                return False
            else:
                logger.exception(f"API error while replying: {api_exception}")
        except prawcore.exceptions.Forbidden as forbidden_error:
            logger.warning(f"Permission error for comment {comment.id}: {forbidden_error}. Skipping.")
        except Exception as error:
            logger.exception(f"Error processing comment {comment.id}: {error}")
    return False  # No reply made

if __name__ == "__main__":
    reddit_instance = bot_login()
    comments_replied_to = get_saved_comments()
    logger.info(f"Number of comments replied to: {len(comments_replied_to)}")

    while True:
        try:
            sub_name = get_next_subreddit()
            logger.info(f"Processing subreddit: r/{sub_name}")
            replied = process_comments_in_subreddit(reddit_instance, sub_name, comments_replied_to)
            logger.info(f"Sleeping for {SLEEP_DURATION} seconds...")
            time.sleep(int(SLEEP_DURATION))
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            time.sleep(int(SLEEP_DURATION))
        except KeyboardInterrupt:
            logger.info("Bot terminated by user.")
            break
