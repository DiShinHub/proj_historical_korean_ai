
from task_worker.tool.log_tool import LogTool
from task_worker.graph.builds.base.graph_builder import BaseBuilder
from task_worker.graph.builds.intent_matching.graph_builder import IntentMatchingBuilder

from task_worker.module.websocket_module import web_socket_module

from task_worker.graph.builds.base.rules import BaseRules
from task_worker.exception.llm_exception import LlmException

import uuid
import json
import time

class PromptsService():
    __logger = LogTool.get_logger(__qualname__)
    
    def __init__(self):
        self.base_graph = BaseBuilder().build_graph()
        self.im_graph = IntentMatchingBuilder().build_graph()
        
        worker_id = str(uuid.uuid4())[0:10]
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
        content = params.get("content")
        
        # 
        response = {
            "result": "test",
            "llm_msg": "test",
        }
        
        #
        data = {
            "command": "emit_room_connectionless", 
            "room_name": room_name, 
            "llm_response": response
        }

        self.web_socket_module.send(
            room_name=room_name,
            data=data
        )
        
        #
        # TODO 테스크 완료/실패 처리 
        task["task_status"] = "success"

        return response        
    
        # # input_message 생성
        # input_message = BaseRules.generate_input_message(text)
        
        # direct request
        # TODO : 의도 분류 llm
        # TODO : 의도 분류에 따른 graph 실행
        result = self.base_graph.invoke({"input_message": input_message})
        llm_response = f"요청에 답변드립니다. {result.get('llm_node_response_text_prev')}"
        
        return llm_response
    
        
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
        