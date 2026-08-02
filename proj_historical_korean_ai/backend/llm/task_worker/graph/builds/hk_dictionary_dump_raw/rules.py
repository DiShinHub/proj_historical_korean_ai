from task_worker.graph.states.langgraph_state import LanggraphState
from task_worker.graph.builds.base.rules import BaseRules

class HKDictionaryDumpRawCRules(BaseRules):
    """_summary_ 
    rule 정의
    """
    
    @staticmethod
    def update_prompt_core(state: LanggraphState):

        updated_state = {**state}
        
        kwargs = {}
        kwargs["prompt_core"] = state.get("llm_node_response_text_prev")
        res_set_state = BaseRules.set_state(state, **kwargs)

        updated_state |= res_set_state
        return updated_state