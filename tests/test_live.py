"""Live checks against https://api.tokenify.dev — skipped unless TOKENIFY_API_KEY is set.

Run: TOKENIFY_API_KEY=tk-... .venv/bin/python -m pytest tests/test_live.py -q
"""
import os

import pytest
from dify_plugin.entities.model.message import UserPromptMessage, PromptMessageTool

from models.llm.llm import TokenifyLargeLanguageModel

KEY = os.environ.get("TOKENIFY_API_KEY")
pytestmark = pytest.mark.skipif(not KEY, reason="TOKENIFY_API_KEY not set")
MODEL = "deepseek/deepseek-v4.1-flash"


def creds():
    return {"api_key": KEY, "context_size": "1048576", "max_tokens_to_sample": "32768"}


def test_validate_credentials():
    TokenifyLargeLanguageModel([]).validate_credentials(MODEL, creds())


def test_blocking_completion():
    result = TokenifyLargeLanguageModel([])._invoke(
        MODEL, creds(), [UserPromptMessage(content="Reply with the single word: pong")],
        {"max_tokens": 400}, stream=False)
    assert "pong" in result.message.content.lower()
    assert result.usage.total_tokens > 0


def test_streaming_completion():
    chunks = list(TokenifyLargeLanguageModel([])._invoke(
        MODEL, creds(), [UserPromptMessage(content="Count from 1 to 3, digits only, comma separated.")],
        {"max_tokens": 400}, stream=True))
    text = "".join(c.delta.message.content or "" for c in chunks if isinstance(c.delta.message.content, str))
    assert "1" in text and "3" in text


def test_tool_call():
    tool = PromptMessageTool(name="get_weather", description="Get the weather for a city",
                             parameters={"type": "object", "properties": {"city": {"type": "string"}},
                                         "required": ["city"]})
    result = TokenifyLargeLanguageModel([])._invoke(
        MODEL, creds(), [UserPromptMessage(content="What is the weather in Paris? Use the tool.")],
        {"max_tokens": 600}, tools=[tool], stream=False)
    assert result.message.tool_calls
    assert result.message.tool_calls[0].function.name == "get_weather"
