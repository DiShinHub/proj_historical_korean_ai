
from task_worker.tool.log_tool import LogTool
from task_worker.graph.builds.hk_dictionary_dump_raw.graph_builder import HKDictionaryDumpRawCBuilder
from task_worker.graph.llm.chat_gpt import ChatGPT

from task_worker.dao.chat_dao import chat_dao
from task_worker.dao.hk_dictionary_service_dao import hk_dictionary_dao
from task_worker.module.websocket_module import web_socket_module

from task_worker.graph.builds.base.rules import BaseRules
from task_worker.exception.llm_exception import LlmException

class HKDictionaryService():
    __logger = LogTool.get_logger(__qualname__)
    
    def __init__(self):
        self.hk_dictionary_dump_raw_graph = HKDictionaryDumpRawCBuilder(llm=ChatGPT()).build_graph()

        self.chat_dao = chat_dao
        self.hk_dictionary_dao = hk_dictionary_dao
        self.web_socket_module = web_socket_module
        
    def handle_hk_dictionary_dump_raw(self, task):
        """
        프롬프트 처리 워커

        Parameters
        ----------
        task : 테스크 데이터 (dict)
        """
        
        params = task.get("params")
        input_message = params.get("input_message")
        reg_member_seq = params.get("reg_member_seq", 1)
        historical_period_start_dt = params.get("historical_period_start_dt")
        historical_period_end_dt = params.get("historical_period_end_dt")
        room_name = params.get("room_name")

        # LLM 처리 
        try:
            llm_pipe_result = self.handle_llm_pipe(input_message)
        
        except Exception as e:
            self.handle_response(
                result = "fail", 
                llm_msg = "관리자에게 문의 주세요."
            )
            self.__logger.info(f"HKDictionaryService.handle_hk_dictionary.handle_llm_pipe, error : {str(e)}")
            return
        
        # DB 처리 
        try:
            items_cnt = self.handle_word_pairs(
                word_pairs=llm_pipe_result['llm_node_response_json_prev']['word_pairs'],
                historical_period_start_dt=historical_period_start_dt,
                historical_period_end_dt=historical_period_end_dt,
                reg_member_seq=reg_member_seq
            )
        
        except Exception as e:
            self.handle_response(
                result = "fail", 
                llm_msg = "관리자에게 문의 주세요."
            )
            self.__logger.info(f"HKDictionaryService.handle_hk_dictionary.handle_word_pairs, error : {str(e)}")
            return

        self.handle_response(
            result = "success", 
            llm_msg = "처리성공",
            items_cnt = items_cnt
        )
    
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
        llm_pipe_result = self.hk_dictionary_dump_raw_graph.invoke({"input_message": input_message})

        return llm_pipe_result

    def handle_word_pairs(self,
            word_pairs, 
            historical_period_start_dt,
            historical_period_end_dt,
            reg_member_seq
        ):

        items = [
            {
                "historical_korean": pair[0],  # 고어 (예: 사\ue46c미라)
                "modern_korean": pair[1],      # 현대어 (예: 사람이라)
                "historical_period_start_dt": historical_period_start_dt,
                "historical_period_end_dt": historical_period_end_dt
            }
            for pair in word_pairs
        ]
        
        hk_dictionary_dao.bulk_add_hk_dictionary(
            items=items,
            reg_member_seq=reg_member_seq
        )
        return len(items)
    
    def handle_response(self, room_name=None, result=None, llm_msg=None, items_cnt=None):

        llm_response = {
            "result" : result,
            "llm_msg" : llm_msg,
            "items_cnt" : items_cnt
        }

        if room_name:
            data = {
                "command": "emit_room_connectionless", 
                "room_name": room_name, 
                "llm_response": llm_response
            }

            self.web_socket_module.send(
                room_name=room_name,
                data=data
            )