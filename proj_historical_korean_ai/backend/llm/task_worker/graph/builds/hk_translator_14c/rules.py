from task_worker.graph.states.langgraph_state import LanggraphState
from task_worker.graph.builds.base.rules import BaseRules

from typing import get_type_hints, get_origin, Any

class HKTranslator14CRules(BaseRules):
    """_summary_ 
    rule 정의
    """

    @staticmethod
    def regen_llm_node_response_json_prev(state: LanggraphState):
        """
        state 설정
        
        Parameters
        ----------
            state (LanggraphState): state 객체
            
        Returns 
        ----------
            update (kwargs): 업데이트 할 값
        """

        # 예외처리, 변환할 수 없는 경우 state 그대로 리턴
        updated_state = {**state}
        if state.get("llm_node_response_json_prev") == None:
            return updated_state
        
        if len(state.get("llm_node_response_json_prev")) == 0:
            return updated_state
        
        if state.get("llm_node_response_json_prev").get("translations") == None:
            return updated_state

        # 형식 변경
        llm_node_response_text_prev_new = ""
        translations = state.get("llm_node_response_json_prev").get("translations", [])
        llm_node_response_text_prev_new = "\n\n".join(translations)

        # 상태 갱신 
        kwargs = {}
        kwargs["llm_node_response_text_prev"] = llm_node_response_text_prev_new
        res_set_state = BaseRules.set_state(state, **kwargs)
        
        updated_state |= res_set_state
        return updated_state
    