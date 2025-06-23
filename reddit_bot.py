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
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=90,
            temperature=0.9,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"OpenAI error or quota reached: {e}; using static fallback reply.")
        return "here's a solid resource for automating tasks with AI: https://cutt.ly/promptkitmini"

def process_comments_in_subreddit(reddit, subreddit_name, comments_replied_to):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        for comment in subreddit.comments(limit=1000):
            try:
                if (
                    matches_trigger(comment.body)
                    and comment.id not in comments_replied_to
                    and comment.author != reddit.user.me()
                ):
                    llm_reply = generate_llm_reply(comment.body)
                    comment.reply(llm_reply)
                    print(f"Replied to comment {comment.id}")
                    comments_replied_to.append(comment.id)
                    with open("comments_replied_to.txt", "a") as f:
                        f.write(comment.id + "\n")
                    return True  # Only reply once per run
            except praw.exceptions.RedditAPIException as api_exception:
                for error in api_exception.items:
                    if error.error_type == "RATELIMIT":
                        m = re.search(r"(\d+) (minutes|minute|seconds|second)", error.message)
                        if m:
                            num = int(m.group(1))
                            if "minute" in m.group(2):
                                sleep_time = num * 60
                            else:
                                sleep_time = num
                        else:
                            sleep_time = 600  # default 10 minutes
                        print(f"Hit rate limit, sleeping for {sleep_time} seconds.")
                        time.sleep(sleep_time)
                        break
                    else:
                        print(f"Reddit error: {error.message}")
            except Exception as e:
                print(f"Error replying: {e}")
    except prawcore.exceptions.NotFound:
        print(f"Subreddit {subreddit_name} not found or is private/banned.")
    except Exception as e:
        print(f"General error: {e}")
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
            logger.info(f"Sleeping for {SLEEP_DURATION} seconds...")
            time.sleep(int(SLEEP_DURATION))
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback; traceback.print_exc()
