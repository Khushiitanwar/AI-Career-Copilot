import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY", "")

# Default Models
# We'll use high-quality and fast models supported on OpenRouter
DEFAULT_MODEL = "google/gemini-2.5-flash"  # Highly capable, cheap, and very fast
CRITIC_MODEL = "anthropic/claude-3-haiku"  # Great for structured critique

def get_llm(model: str = DEFAULT_MODEL, temperature: float = 0.5, max_tokens: int = 2000) -> ChatOpenAI:
    """
    Returns an instance of ChatOpenAI configured to work with OpenRouter.
    """
    if not OPENROUTER_API_KEY:
        # If no key is set, we raise an error which we can catch to run in demo mode
        raise ValueError("OPENROUTER_API_KEY is not configured in .env file.")
        
    return ChatOpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        default_headers={
            "HTTP-Referer": "https://github.com/google/antigravity", # Required by OpenRouter
            "X-Title": "AI Career Copilot"
        }
    )
