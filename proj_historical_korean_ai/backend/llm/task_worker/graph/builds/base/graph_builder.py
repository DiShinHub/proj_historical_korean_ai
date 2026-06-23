from task_worker.graph.llm.my_llm import MyLLM
from task_worker.graph.states.langgraph_state import LanggraphState

from task_worker.graph.nodes.llm_request_node import LLMRequestNode
from task_worker.graph.nodes.rule_node import RuleNode

from task_worker.graph.builds.base.prompts import BasePrompts
from task_worker.graph.builds.base.rules import BaseRules

from langgraph.graph import StateGraph, END

class BaseBuilder():
    """_summary_
    프롬프트 튜닝 없이 llm 요청
    """
    
    def __init__(
        self, 
        llm=MyLLM()
    ):
        self.graph = None
        self.builder = None
        self.llm = llm
        self.builder = StateGraph(LanggraphState)
        
    def build_graph(self):
        
        # 노드 셋팅
        self.builder.add_node("initialize_graph", RuleNode(rule=BaseRules.initialize_graph, llm=self.llm))
        self.builder.add_node(f"prompt", LLMRequestNode(BasePrompts.prompt))
        
        # 노드 연결
        self.builder.set_entry_point("initialize_graph")
        node_sequence = [
            "initialize_graph",
            "prompt",
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