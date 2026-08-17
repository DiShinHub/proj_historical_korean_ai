
from task_worker.graph.states.langgraph_state import LanggraphState

from task_worker.graph.nodes.rule_node import RuleNode
from task_worker.graph.nodes.llm_request_node import LLMRequestNode

from task_worker.graph.builds.hk_intent_matching.rules import HkIntentMatchingRules
from task_worker.graph.builds.hk_intent_matching.prompts import HkIntentMatchingPrompts

from langgraph.graph import StateGraph, END

class HkIntentMatchingBuilder():
    """_summary_
    의도 분류
    """
    
    def __init__(
        self, 
        llm
    ):
        self.graph = None
        self.builder = None
        self.llm = llm
        self.builder = StateGraph(LanggraphState)
    
    def build_graph(self):
        
        self.builder.add_node("initialize_graph", RuleNode(rule=HkIntentMatchingRules.initialize_graph, llm=self.llm))
        self.builder.add_node("llm_prompt_for_intent_matching", LLMRequestNode(HkIntentMatchingPrompts.prompt_for_intent_matching))
        
        # 노드 연결
        self.builder.set_entry_point("initialize_graph")
        node_sequence = [
            "initialize_graph",
            "llm_prompt_for_intent_matching",
            END
        ]
        self.add_linear_edges(node_sequence)
        
        # 컴파일
        self.graph = self.builder.compile()
        return self.graph
    
    def add_linear_edges(self, node_names: list[str]):
        
        # 노드를 정의 순서대로 연결할 때 씀
        for i in range(len(node_names) - 1):
            self.builder.add_edge(node_names[i], node_names[i + 1])
    
    def add_edges(self):
        return
    
    def get_graph(self):
        return self.graph