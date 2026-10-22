"""LLM client for the Agents SDK, routed through OpenRouter.

Pick a model with solid tool-calling support (check the model's page on
OpenRouter) -- the agent relies on function calling to reach the knowledge base.
"""
from agents import OpenAIChatCompletionsModel, set_tracing_disabled
from openai import AsyncOpenAI

from app.core.config import settings

# The SDK's default trace exporter uploads to OpenAI and needs an OpenAI key.
# With OpenRouter that just produces 401 noise, so tracing is off. To keep
# tracing, remove this and call set_tracing_export_api_key(<openai key>).
set_tracing_disabled(True)

_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
    timeout=60.0,       # per LLM call; bounds a hung provider
    max_retries=2,
    default_headers={"X-Title": "SupportBot"},
)

chat_model = OpenAIChatCompletionsModel(model=settings.llm_model, openai_client=_client)