
from task_worker.tool.log_tool import LogTool

from task_worker.graph.builds.base.graph_builder import BaseBuilder
from task_worker.graph.builds.hk_intent_matching.graph_builder import HkIntentMatchingBuilder
from task_worker.graph.builds.hk_audio_creator.graph_builder import HkAudioCreatorBuilder
from task_worker.graph.builds.hk_translator_21c.graph_builder import HKTranslator21CBuilder
from task_worker.graph.builds.hk_translator_14c.graph_builder import HKTranslator14CBuilder
from task_worker.graph.builds.hk_ipa_14c.graph_builder import HKIpa14CBuilder
from task_worker.graph.llm.chat_gpt import ChatGPT
from task_worker.graph.llm.chat_gpt_tts import ChatGPTTTS

from task_worker.dao.chat_dao import chat_dao
from task_worker.module.websocket_module import WebSocketModule

from task_worker.graph.builds.base.rules import BaseRules
from task_worker.exception.llm_exception import LlmException

import datetime
import os 

class PromptsService():
    __logger = LogTool.get_logger(__qualname__)
    
    def __init__(self):
        
        self.base_graph = BaseBuilder(llm=ChatGPT()).build_graph()
        self.hk_intent_matching_graph = HkIntentMatchingBuilder(llm=ChatGPT()).build_graph()
        self.hk_audio_creator_graph = HkAudioCreatorBuilder(llm=ChatGPTTTS()).build_graph()

        self.hk_translator_21c_graph = HKTranslator21CBuilder(llm=ChatGPT()).build_graph()
        self.hk_translator_14c_graph = HKTranslator14CBuilder(llm=ChatGPT()).build_graph()
        self.hk_ipa_14c_graph = HKIpa14CBuilder(llm=ChatGPT()).build_graph()
        self.hk_ipa_14c_graph = HKIpa14CBuilder(llm=ChatGPT()).build_graph()

        self.chat_dao = chat_dao
        self.web_socket_module = WebSocketModule()
        self.web_socket_module.start()
        
    def handle_prompts(self, task):
        """
        프롬프트 처리 워커

        Parameters
        ----------
        task : 테스크 데이터 (dict)
        """
        
        params = task.get("params")
        room_name = params.get("room_name")
        input_message = params.get("input_message")
        chat_session_seq = params.get("chat_session_seq")

        #
        llm_msg = ""

        # 의도 분류 
        res_hk_intent_matching_graph = self.hk_intent_matching_graph.invoke({"input_message": input_message})
        intent = res_hk_intent_matching_graph.get("llm_node_response_json_prev").get("intent")

        result = "fail"
        try:
            # case, 현대국어
            if intent == "hk_translator_21c":
                res_hk_translator_21c_graph = self.hk_translator_21c_graph.invoke({"input_message": input_message})
                llm_msg = res_hk_translator_21c_graph.get('llm_node_response_text_prev')

                # 결과 DB 저장
                self.chat_dao.add_chat_message(
                    chat_session_seq=chat_session_seq,
                    model_name="",
                    role="SYSTEM",
                    content=[llm_msg],
                    ipa=[],
                    audio_path="",
                    audio_expire_yn="N",
                    response_time_ms=0,
                )

            # case, 14세기 중세국어
            elif intent == "hk_translator_14c":

                # 번역요청 
                hk_translator_14c_result = self.hk_translator_14c_graph.invoke({"input_message": input_message})
                hk_translator_14c_response_json = hk_translator_14c_result.get('llm_node_response_json_prev')
                hk_translations = hk_translator_14c_response_json.get("translations")
                if hk_translations == None:
                    raise Exception("번역 실패")

                # 번역결과 -> ipa 변환
                hk_ipa_translations = []
                for hk_translation in hk_translations:
                    hk_ipa_14c_result = self.hk_ipa_14c_graph.invoke({"input_message": hk_translation})
                    hk_ipa_14c_response_json = hk_ipa_14c_result.get('llm_node_response_json_prev')
                    hk_ipa_translation = hk_ipa_14c_response_json.get('translation')
                    if hk_ipa_translation == None:
                        raise Exception("ipa 변환 실패")

                    hk_ipa_translations.append(hk_ipa_translation)
                
                # ipa -> 음성변환
                hk_audio_translations_path = []
                for i in range(0, len(hk_ipa_translations)):

                    hk_translator_14c_translation = hk_translations[i]

                    input_message = f"text : {hk_translator_14c_translation} "
                    input_message += f"ipa : {hk_ipa_translations[i]} "

                    hk_audio_creator_result = self.hk_audio_creator_graph.invoke({"input_message": input_message})
                    hk_audio_creator_response_text = hk_audio_creator_result.get('llm_node_response_text_prev')
                    hk_audio_translations_path.append(hk_audio_creator_response_text)

                # 결과 DB 저장
                self.chat_dao.add_chat_message(
                    chat_session_seq=chat_session_seq,
                    model_name="",
                    role="SYSTEM",
                    content=hk_translations,
                    ipa=hk_ipa_translations,
                    audio_path=hk_audio_translations_path,
                    audio_expire_yn="N",
                    response_time_ms=0,
                )

                llm_msg = ""
                if len(hk_translations) == 0:
                    llm_msg = f"관리자에게 문의 주세요."

                elif len(hk_translations) == 1:
                    llm_msg = f"{hk_translations[0]}^T|A^{hk_audio_translations_path[0]}"

                else:
                    for i in range(0, len(hk_translations)):
                        llm_msg += f"{hk_translations[i]}^T|A^{hk_audio_translations_path[i]}\n\n"
                
            # default
            else:
                res_base_graph = self.base_graph.invoke({"input_message": input_message})
                llm_msg = res_base_graph.get('llm_node_response_text_prev')

                # 결과 DB 저장
                self.chat_dao.add_chat_message(
                    chat_session_seq=chat_session_seq,
                    model_name="",
                    role="SYSTEM",
                    content=[llm_msg],
                    ipa=[],
                    audio_path="",
                    audio_expire_yn="N",
                    response_time_ms=0,
                )
            
            result = "success"
        
        except Exception as e:
            llm_msg = "관리자에게 문의 주세요."
            self.__logger.info(f"PromptsService.handle_prompts.handle_llm_pipe, error : {str(e)}")

        finally:
            
            # 결과 소켓 전송
            data = {
                "command": "emit_room_connectionless", 
                "room_name": room_name, 
                "llm_response": {
                    "result": result,
                    "llm_msg": llm_msg,
                }
            }

            self.web_socket_module.send(
                room_name=room_name,
                data=data
            )