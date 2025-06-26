import os
import random


REDDIT_USERNAME = os.environ["REDDIT_USERNAME"]
REDDIT_PASSWORD = os.environ["REDDIT_PASSWORD"]
REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
REDDIT_CLIENT_SECRET = os.environ["REDDIT_SECRET"]
REDDIT_USER_AGENT = os.environ["REDDIT_USER_AGENT"]

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

TARGET_SUBREDDITS = [
    "WeAreTheMusicMakers",
    "MakingHipHop",
    "TrapProduction",
    "ShareYourMusic",
    "ThisIsOurMusic",
    "BedroomBands",
    "LoFiHipHop",
    "PluggNB",
    "FutureBeatProducers",
    "NewMusic",
    "LetsHearYourMusic",
    "musicpromotion",
    "indieheads",         # be careful, only on “Self-Promo Saturday”
    "musicians",
    "MusicCritique",      # only with feedback requests
    "Songwriters",
    "MusicInTheMaking",   # for works-in-progress
]

PROMO_THREADS = {
      "MakingHipHop": ["showcase sunday"],
    "WeAreTheMusicMakers": ["feedback friday", "screenshot saturday"],
    "ShareYourMusic": ["daily share thread"],
    "indieheads": ["self-promo saturday"],
    "MusicCritique": ["weekly critique thread"],
}

TRIGGER_WORDS = [
    "looking for beats",
    "i need beats",
    "any beatmakers?"
    "type beat?",
    "instrumental recommendations",
    "pluggnb",
    "jerk beats",
    "hoodtrap beats",
    "who wants to collab?",
    "any producers here",
    "share your beats",
    "feedback",
    "new music friday",
    "can i get some feedback",
    "need new instrumentals",
    "any new tracks",
    "drop your music",
    "let's hear your music",
    "showcase your work",

]

REPLY_TEMPLATES = [
    "Hey! If you're into {genre}, check out my latest on Traktrain: {link} — always appreciate feedback!",
    "Just dropped some new {genre} beats here: {link} — let me know what you think!",
    "Producer here! If you want {artist} style beats, check my page: {link}",
    "Looking for feedback on my recent {genre} project: {link}",
    "Need new type beats? My Traktrain stays updated: {link}",
]
# Your main genres/styles and artist names
GENRES = ["pluggnb", "trap", "lofi", "jerk", "ambient jerk", "rnb jerk", "new jazz"]
ARTISTS = ["Playboi Carti", "Lawsy", "2hollis", "bibi trickz", "skaiwater", "lunchbox", "amir.pr0d",]
TRAKTRAIN_LINK = "https://traktrain.com/nixie_yung"

LLM_PROMPT_TEMPLATE = (
    "You're a helpful automation expert on Reddit. "
    "Someone just posted this comment: \"{comment_body}\"\n\n"
    "Reply with a friendly, concise suggestion about workflow automation, "
    "and mention this resource: https://cutt.ly/promptkitmini. "
    "Be informal but not spammy, and avoid repeating yourself."
    "avoid using the em dash (—) at all times. not negotiable."
    "use casual tone as if it were a good friend over the internet"
)
# Set a range for sleep duration (in seconds)
SLEEP_DURATION_MAX = 900  
SLEEP_DURATION_MIN = 300 
