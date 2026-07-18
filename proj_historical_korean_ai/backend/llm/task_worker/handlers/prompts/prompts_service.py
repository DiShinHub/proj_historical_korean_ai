
from task_worker.tool.log_tool import LogTool
from task_worker.graph.builds.old_korean_translator_14c.graph_builder import OldkoreanTranslator14CBuilder
from task_worker.graph.llm.chat_gpt import ChatGPT

from task_worker.dao.chat_dao import chat_dao
from task_worker.module.websocket_module import web_socket_module

from task_worker.graph.builds.base.rules import BaseRules
from task_worker.exception.llm_exception import LlmException

class PromptsService():
    __logger = LogTool.get_logger(__qualname__)
    
    def __init__(self):
        self.old_korean_translator_14c_graph = OldkoreanTranslator14CBuilder(llm=ChatGPT()).build_graph()

        self.chat_dao = chat_dao
        self.web_socket_module = web_socket_module
        
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
        
        # LLM 처리 
        result = None
        try:
            llm_pipe_result = self.handle_llm_pipe(input_message)
            
            result = "success"
            llm_msg = f"{llm_pipe_result.get('llm_node_response_text_prev')}"
        
        except Exception as e:
            result = "fail"
            llm_msg = "관리자에게 문의 주세요."
            self.__logger.info(f"PromptsService.handle_prompts.handle_llm_pipe, error : {str(e)}")

        # LLM 결과 가공
        llm_response = {
            "result": result,
            "llm_msg": llm_msg,
        }

        # 결과 DB 저장
        self.chat_dao.add_chat_message(
            chat_session_seq=chat_session_seq,
            model_name="",
            role="SYSTEM",
            content=llm_msg,
            response_time_ms=0,
        )

        # 결과 소켓 전송
        data = {
            "command": "emit_room_connectionless", 
            "room_name": room_name, 
            "llm_response": llm_response
        }

        self.web_socket_module.send(
            room_name=room_name,
            data=data
        )
        
        # TODO : 첫 번째 대화라면 타이틀을 변경시킴
        
        task["task_status"] = "success"
        return llm_response    

    def handle_llm_pipe(
            self,
            input_message
        ):
        """
        llm_pipe 처리

        Parameters
        ----------
        input_message : 사용자 입력 메세지 (str)

        Returns
        ----------
        llm_pipe_result: llm_pipe 처리 결과
        """
        llm_pipe_result = self.old_korean_translator_14c_graph.invoke({"input_message": input_message})

        # TODO : 의도 분류 llm
        # TODO : 의도 분류에 따른 graph 실행

        return llm_pipe_result

    
        
        # # 의도 분류 
        # result = self.im_graph.invoke({"input_message": input_message})
        # if result.get('llm_node_response_dict_prev') == None or\
        #     result.get('llm_node_response_dict_prev').get("intent") == None:
        #     raise LlmException("im_graph fail, no llm_node_response_dict_prev")
        
        # intent = result.get('llm_node_response_dict_prev').get("intent")
        
        # # 의도에 따른 graph 실행
        # llm_response = None 
        # if intent == "create":
        #     result = self.gcm_graph.invoke({"input_message": input_message})
        #     llm_response = f"일정이 생성되었습니다. 확인해 주세요. {result.get('llm_node_response_text_prev')}"
        
        # else:
        #     result = self.base_graph.invoke({"input_message": input_message})
        #     llm_response = f"요청에 답변드립니다. {result.get('llm_node_response_text_prev')}"
        