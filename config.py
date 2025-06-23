import os

REDDIT_USERNAME = os.environ["REDDIT_USERNAME"]
REDDIT_PASSWORD = os.environ["REDDIT_PASSWORD"]
REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
REDDIT_CLIENT_SECRET = os.environ["REDDIT_SECRET"]
REDDIT_USER_AGENT = os.environ["REDDIT_USER_AGENT"]

# config.py
TARGET_SUBREDDITS = ["ChatGPT",
   "ArtificialIntelligence",
    "PromptEngineering",
    "Automation",
    "Notion",
    "Productivity",
    "ObsidianMD",
    "SideProject",
    "Entrepreneur",
    "SideHustle",
    "Gumroad",
    "Passive_Income",
    "SaaS",
    "InternetIsBeautiful",
    "Copywriting",
    "ContentCreators",
    "SocialMedia",
    "NoCode",
    "TechSupport",
    "Freelance",
    "SmallBusiness",
    "LifeProTips",
    "GetDisciplined",
    "SelfImprovement",
    "Workspaces"]

# reddit_bot.py
subreddit = reddit.subreddit("+".join("ChatGPT",
    "ArtificialIntelligence",
    "PromptEngineering",
    "Automation",
    "Notion",
    "Productivity",
    "ObsidianMD",
    "SideProject",
    "Entrepreneur",
    "SideHustle",
    "Gumroad",
    "Passive_Income",
    "SaaS",
    "InternetIsBeautiful",
    "Copywriting",
    "ContentCreators",
    "SocialMedia",
    "NoCode",
    "TechSupport",
    "Freelance",
    "SmallBusiness",
    "LifeProTips",
    "GetDisciplined",
    "SelfImprovement",
    "Workspaces"))

TARGET_STRING = "workflow"
REPLY_MESSAGE = "here's a solid resource for automating tasks with AI: https://cutt.ly/promptkitmini"
SLEEP_DURATION = 10
