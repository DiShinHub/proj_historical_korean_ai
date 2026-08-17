
from task_worker.module.minio_module import minio_module

from pydantic import PrivateAttr
from langchain.llms.base import LLM
from openai import OpenAI

from typing import Optional, List, Dict, Any

import datetime
import os

class ChatGPTTTS(LLM):
    model: str = "gpt-4o-mini-tts"
    voice: str = "alloy"
    response_format: str = "wav"

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

        response = self._client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=prompt,
            response_format=self.response_format,
        )
        
        # minio에 업로드
        minio_file_path = f"/audio/output_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}.wav"
        local_file_path = minio_module.generate_local_path("wav")

        try:
            response.write_to_file(local_file_path)

            minio_module.upload_file(
                minio_file_path=minio_file_path, 
                local_file_path=local_file_path
            )

        except Exception as e :
            raise Exception(f"HkAudioCreatorRules.create_audio_file : error, {str(e)}")

        finally:
            # 임시 파일 삭제
            os.remove(local_file_path)

        return minio_file_path

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "voice": self.voice,
            "response_format": self.response_format,
        }

    @property
    def _llm_type(self) -> str:
        return "chatgpt_tts"