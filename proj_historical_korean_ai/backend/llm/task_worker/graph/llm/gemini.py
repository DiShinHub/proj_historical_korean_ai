from langchain.llms.base import LLM
from typing import Optional, List, Dict, Any
import requests

class Gemini(LLM):
    model: str = ""
    base_url: str = ""
    max_tokens: int = 200

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": self.max_tokens
        }
        response = requests.post(self.base_url, headers=headers, json=data)
        if response.status_code != 200:
            raise ValueError(f"Request failed: {response.status_code}, {response.text}")
        return response.json()['choices'][0]['text']

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model": self.model}

    @property
    def _llm_type(self) -> str:
        return "custom_vllm"