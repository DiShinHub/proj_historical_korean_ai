from task_worker.tool.log_tool import LogTool
from task_worker.graph.states.langgraph_state import LanggraphState

from langchain_core.runnables import Runnable, RunnableConfig
from typing import Optional
    
class RuleNode(Runnable):
    """
    룰 실행 노드 
    LangGraph 실행 중 서비스적으로 정의 된 룰을 실행
    
    static method나 일반 함수를 주입받아 실행
    
    Parameters
    ----------
        rule (func): 실행할 서비스 함수
        
    Returns 
    ----------
        state (LanggraphState): 사용자 정의
    """
    
    def __init__(self, rule, **kwargs):
        self.logger = LogTool.get_logger(self.__class__.__name__) 
        self.rule = rule
        self.kwargs = kwargs

    def invoke(self, state: dict, config: Optional[RunnableConfig] = None) -> LanggraphState:
        return self.rule(state, **self.kwargs)