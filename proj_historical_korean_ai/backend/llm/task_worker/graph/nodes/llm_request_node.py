from task_worker.tool.log_tool import LogTool
from task_worker.tool.json_tool import JsonTool

from task_worker.graph.states.langgraph_state import LanggraphState
from task_worker.graph.builds.base.rules import BaseRules
from task_worker.graph.template_schema.prompt_template_schema import PromptTemplateSchema

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.runnables import Runnable, RunnableConfig
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
# from langchain.prompts.few_shot import FewShotPromptTemplate
# from langchain.output_parsers import StructuredOutputParser

from typing import Optional
    
class LLMRequestNode(Runnable):
    """
    LangGraph 실행 중 LLM을 호출
    
    Parameters
    ----------
        prompt_template (func): 프롬프트 탬플릿
        
    Returns 
    ----------
        response_bool (bool): 응답 결과
        llm_node_response_text_prev (text): 응답 텍스트
        llm_node_response_dict_prev (dict): 응답 텍스트에서 파싱한 json (파싱 불가면 None) 
    """
    
    def __init__(self, prompt_template):
        self.__logger = LogTool.get_logger(self.__class__.__name__) 
        self.prompt_template = prompt_template
        
    def invoke(self, state: dict, config: Optional[RunnableConfig] = None) -> LanggraphState:
        
        # 탬플릿 스키마 로드
        prompt_template_schema:PromptTemplateSchema = self.prompt_template()
        prompt_mode = prompt_template_schema.get("prompt_mode")
        prompt_template = prompt_template_schema.get("prompt_template")
        prompt_template_system = prompt_template_schema.get("prompt_template_system")
        prompt_template_user = prompt_template_schema.get("prompt_template_user")
        
        # 일반형 프롬프트
        if prompt_mode == "text":
            prompt_obj = PromptTemplate.from_template(prompt_template)
        
        # 대화형 프롬프트
        elif prompt_mode == "chat":
            prompt_obj = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(prompt_template_system),
                HumanMessagePromptTemplate.from_template(prompt_template_user)
            ])
        
        # TODO : 예시 기반 프롬프트
        elif prompt_mode == "fewshot":
            pass 
        
        # TODO : 구조화 응답을 유도하는 프롬프트
        elif prompt_mode  == "json_structured":
            pass
        
        # default, 일반형
        else:
            prompt_obj = PromptTemplate.from_template(self.prompt_template())
            
        # --- llm & chain 실행
        llm = state.get("llm")
        prompt_core = state.get("prompt_core") 

        llm_chain = LLMChain(llm=llm, prompt=prompt_obj)
        result = llm_chain.invoke({"prompt_core": prompt_core})
        
        # --- 결과 처리
        prompt_template_name = self.prompt_template.__qualname__
        llm_node_response_text_prev = result["text"]
        llm_node_response_dict_prev = JsonTool().parse_json_data_from_fulltext(result["text"])

        llm_node_responses = state.get("llm_node_responses")
        llm_node_responses.update(
            {
                prompt_template_name : {
                    "llm_node_response_text" : llm_node_response_text_prev,
                    "llm_node_response_dict" : llm_node_response_dict_prev
                }
            }
        )
        
        # --- history
        BaseRules.insert_prompt_history(
            state, 
            prompt_core=prompt_core, 
            prompt_template_name=self.prompt_template.__qualname__, 
            llm_node_response_text_prev=llm_node_response_text_prev
        )
        
        return {
            **state, 
            "llm_node_response_text_prev": llm_node_response_text_prev,
            "llm_node_response_dict_prev": llm_node_response_dict_prev,
            "llm_node_responses" : llm_node_responses
        }