import os
from typing import Optional, List, Dict, Any

from pydantic import PrivateAttr
from langchain.llms.base import LLM
from openai import OpenAI


class ChatGPT(LLM):
    model: str = "gpt-5-mini"
    max_tokens: int = 1000

    _client: OpenAI = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = OpenAI(
            api_key=os.environ["CHAT_GPT_SECRET_KEY"]
        )

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
    ) -> str:

        response = self._client.responses.create(
            model=self.model,
            input=prompt,
            max_output_tokens=self.max_tokens,
            reasoning={
                "effort": "minimal"
            }
        )

        return response.output_text

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
        }

    @property
    def _llm_type(self) -> str:
        return "chatgpt"