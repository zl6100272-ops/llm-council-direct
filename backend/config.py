"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# Provider registry - keyed by model prefix (e.g., "openai" in "openai/gpt-4o")
PROVIDERS = {
    "openai": {
        "base_url": "https://api.openai.com/v1/chat/completions",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "format": "openai",
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "api_key": os.getenv("GOOGLE_API_KEY"),
        "format": "openai",
    },
    "xai": {
        "base_url": "https://api.x.ai/v1/chat/completions",
        "api_key": os.getenv("XAI_API_KEY"),
        "format": "openai",
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1/messages",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "format": "anthropic",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1/chat/completions",
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "format": "openai",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "api_key": os.getenv("QWEN_API_KEY"),
        "format": "openai",
    },
    "glm": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "api_key": os.getenv("GLM_API_KEY"),
        "format": "openai",
    },
    "moonshot": {
        "base_url": "https://api.moonshot.cn/v1/chat/completions",
        "api_key": os.getenv("MOONSHOT_API_KEY"),
        "format": "openai",
    },
    "stepfun": {
        "base_url": "https://api.stepfun.com/v1/chat/completions",
        "api_key": os.getenv("STEPFUN_API_KEY"),
        "format": "openai",
    },
}

# Council members - list of model identifiers (provider/model)
COUNCIL_MODELS = [
    "deepseek/deepseek-chat",
    "openai/gpt-4o",
    "google/gemini-2.5-flash",
    "qwen/qwen-plus",
    "glm/glm-4-flash",
]

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = "deepseek/deepseek-reasoner"

# Data directory for conversation storage
DATA_DIR = "data/conversations"
