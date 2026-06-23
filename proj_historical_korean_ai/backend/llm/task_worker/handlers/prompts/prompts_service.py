
from task_worker.tool.log_tool import LogTool
from task_worker.graph.builds.base.graph_builder import BaseBuilder
from task_worker.graph.builds.intent_matching.graph_builder import IntentMatchingBuilder

from task_worker.module.socket_client_module import SocketClientModule

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
        self.socket_client_module = SocketClientModule(username=f"llm_task_worker_{worker_id}")
        
    def handle_prompts(self, task):
        """
        프롬프트 처리 워커

        Parameters
        ----------
        task : 테스크 데이터 (dict)
        """
        
        params = task.get("params")
        room_name = params.get("room_name")
        prompt = params.get("prompt")
        
        # 
        response = {
            "result": "",
            "llm_msg": "",
        }
        
        #
        self.__logger.info("here1")
        self.socket_client_module.connect()
        self.__logger.info("here2")

        request = {"command": "emit_to_room_connectionless", "room_name": room_name, "llm_response": params}
        self.__logger.info(f"request1 : {request}")
        self.socket_client_module.send_data(json.dumps(request).encode())
        self.__logger.info(f"request2 : {request}")
        
        time.sleep(0.01)
        self.socket_client_module.disconnect()
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
        