import os

REDDIT_USERNAME = os.environ["REDDIT_USERNAME"]
REDDIT_PASSWORD = os.environ["REDDIT_PASSWORD"]
REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
REDDIT_CLIENT_SECRET = os.environ["REDDIT_SECRET"]
REDDIT_USER_AGENT = os.environ["REDDIT_USER_AGENT"]

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

TARGET_SUBREDDITS = [
    "ChatGPT", "ArtificialIntelligence", "PromptEngineering", "Automation",
    "Notion", "Productivity", "ObsidianMD", "SideProject", "Entrepreneur", "SideHustle",
    "Gumroad", "Passive_Income", "SaaS", "InternetIsBeautiful", "Copywriting", "ContentCreators",
    "SocialMedia", "NoCode", "TechSupport", "Freelance", "SmallBusiness", "LifeProTips",
    "GetDisciplined", "SelfImprovement", "Workspaces"
]

TRIGGER_WORDS = [
    "workflow", "automation", "template", "prompt", "system", "ai", "streamline", "optimize"
]

LLM_PROMPT_TEMPLATE = (
    "You're a helpful automation expert on Reddit. "
    "Someone just posted this comment: \"{comment_body}\"\n\n"
    "Reply with a friendly, concise suggestion about workflow automation, "
    "and mention this resource: https://cutt.ly/promptkitmini. "
    "Be informal but not spammy, and avoid repeating yourself."
)

SLEEP_DURATION = 10
