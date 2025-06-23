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

import openai

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
    
    except openai.RateLimitError:
        print("Quota exceeded. Using static fallback reply.")
        return "here's a great resource for automating tasks with AI: https://cutt.ly/promptkitmini"
    except Exception as e:
        print(f"Unexpected error from OpenAI: {e}")
        return "found a great resource for automating tasks with AI: https://cutt.ly/promptkitmini"
        

import time
import praw

def process_comments_in_subreddit(reddit, subreddit_name, comments_replied_to):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        for comment in subreddit.comments(limit=1000):
            # your code...
            try:
                comment.reply("Your reply here!")
                print(f"Replied to comment {comment.id}")
            except praw.exceptions.RedditAPIException as api_exception:
                for error in api_exception.items:
                    if error.error_type == "RATELIMIT":
                        # Usually message looks like:
                        # "Looks like you've been doing that a lot. Take a break for 9 minutes before trying again."
                        import re
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
                        break  # Important to break or return to avoid retrying instantly!
                    else:
                        print(f"Reddit error: {error.message}")
            except Exception as e:
                print(f"Error replying: {e}")

    except prawcore.exceptions.NotFound:
        print(f"Subreddit {subreddit_name} not found or is private/banned.")
    except Exception as e:
        print(f"General error: {e}")
