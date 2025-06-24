import streamlit as st
import praw
import config

from config import (
    REDDIT_USERNAME, REDDIT_PASSWORD, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT,
    TARGET_SUBREDDITS, TRIGGER_WORDS
)

st.title("Reddit Bot Control Panel")

st.write("Configure your Reddit bot and test it here.")

with st.form("config_form"):
    subreddit = st.selectbox("Pick a subreddit to test", TARGET_SUBREDDITS)
    trigger_word = st.text_input("Trigger word to search", TRIGGER_WORDS[0])
    run_test = st.form_submit_button("Test Bot")

if run_test:
    st.write(f"Running bot on r/{subreddit} for trigger '{trigger_word}' ...")
    # Example: Test connection only
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        user_agent=REDDIT_USER_AGENT,
        check_for_async=False
    )
    st.success(f"Logged in as: {reddit.user.me()}")
    st.info("You can extend this to trigger bot functions, show logs, etc.")
