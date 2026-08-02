
from task_worker.tool.log_tool import LogTool
from task_worker.graph.states.langgraph_state import LanggraphState
from task_worker.exception.llm_exception import LlmException

from langchain_core.runnables import Runnable, RunnableConfig
from typing import Optional
    
class EventNode(Runnable):
    """
    LangGraph 실행 중 이벤트를 실행 (AI Agent)
    
    Parameters
    ----------
        event_tool (obj): 이벤트 툴
        
    Returns 
    ----------
        response_bool (bool): 처리 결과
        llm_node_response_text_prev (text): 응답 텍스트
        event_params (dict): 이벤트에 사용 된 파라메터
    """
    
    def __init__(self, event_tool):
        self.logger = LogTool.get_logger(self.__class__.__name__) 
        self.event_tool = event_tool

    def invoke(self, state: dict, config: Optional[RunnableConfig] = None) -> LanggraphState:

        try:
            event_params = state.get("event_params") 
            if not event_params: 
                event_params = state.get("llm_node_response_json_prev") # state에 event_params이 없으면 이전 노드의 dict type 결과물을 사용
            
            result = self.event_tool.invoke(event_params)
            
            return {
                **state, 
                "llm_node_response_text_prev": result,
                "event_params": event_params
            }
            
        except Exception as e:
            raise LlmException(f"EventNode fail, {str(e)}")