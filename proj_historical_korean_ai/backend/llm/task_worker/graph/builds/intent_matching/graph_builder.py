
from task_worker.graph.builds.base.graph_builder import BaseBuilder

from task_worker.graph.llm.my_llm import MyLLM
from task_worker.graph.nodes.rule_node import RuleNode
from task_worker.graph.nodes.llm_request_node import LLMRequestNode

from task_worker.graph.builds.base.rules import BaseRules
from task_worker.graph.builds.intent_matching.prompts import IntentMatchingPrompts

from langgraph.graph import END

class IntentMatchingBuilder(BaseBuilder):
    """_summary_
    의도 분류
    """
    
    def __init__(self, llm=MyLLM()):
        super().__init__(llm=llm)
    
    def build_graph(self):
        
        self.builder.add_node("initialize_graph", RuleNode(rule=BaseRules.initialize_graph, llm=self.llm))
        self.builder.add_node("llm_prompt_for_intent_matching", LLMRequestNode(IntentMatchingPrompts.prompt_for_intent_matching))
        
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