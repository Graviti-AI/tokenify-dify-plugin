from collections.abc import Generator
from typing import Optional, Union

from dify_plugin import OAICompatLargeLanguageModel
from dify_plugin.entities.model import AIModelEntity
from dify_plugin.entities.model.llm import LLMResult
from dify_plugin.entities.model.message import PromptMessage, PromptMessageTool

# Fixed endpoint. Users cannot set another URL.
ENDPOINT_URL = "https://api.tokenify.dev/v1"


class TokenifyLargeLanguageModel(OAICompatLargeLanguageModel):
    def _update_credential(self, credentials: dict) -> None:
        credentials["endpoint_url"] = ENDPOINT_URL
        credentials["mode"] = "chat"
        credentials["openai_api_key"] = credentials.get("api_key")
        credentials.setdefault("function_calling_type", "tool_call")
        credentials.setdefault("stream_function_calling", "supported")

    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: Optional[list[PromptMessageTool]] = None,
        stop: Optional[list[str]] = None,
        stream: bool = True,
        user: Optional[str] = None,
    ) -> Union[LLMResult, Generator]:
        self._update_credential(credentials)
        return super()._invoke(
            model, credentials, prompt_messages, model_parameters, tools, stop, stream, user
        )

    def validate_credentials(self, model: str, credentials: dict) -> None:
        self._update_credential(credentials)
        super().validate_credentials(model, credentials)

    def get_customizable_model_schema(
        self, model: str, credentials: dict
    ) -> AIModelEntity:
        self._update_credential(credentials)
        return super().get_customizable_model_schema(model, credentials)

    def get_num_tokens(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        tools: Optional[list[PromptMessageTool]] = None,
    ) -> int:
        self._update_credential(credentials)
        return super().get_num_tokens(model, credentials, prompt_messages, tools)
