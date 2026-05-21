# app/operations/llm_config.py
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()

def get_llm(max_tokens: int = 1024):
    return ChatAnthropic(
        model="claude-opus-4-7",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=max_tokens
    )

# One LLM per agent with appropriate token limits
llm_supervisor = get_llm(max_tokens=64)
llm_fetch      = get_llm(max_tokens=2048)
llm_create     = get_llm(max_tokens=1024)
llm_update     = get_llm(max_tokens=512)
llm_cancel     = get_llm(max_tokens=256)
llm_validate   = get_llm(max_tokens=512)
llm_invoice    = get_llm(max_tokens=1024)
llm_return     = get_llm(max_tokens=1024)