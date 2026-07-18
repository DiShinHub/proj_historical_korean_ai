from task_worker.tool.log_tool import LogTool
from task_worker.graph.states.langgraph_state import LanggraphState
from task_worker.dao.prompt_history_dao import prompt_history_dao

from typing import get_type_hints, get_origin, Any

class BaseRules:
    """_summary_ 
    공통적으로 쓰이는 rule 정의

    """
    
    @staticmethod
    def initialize_graph(state: LanggraphState, **kwargs):
        """
        그래프 초기화
        
        Parameters
        ----------
            state (LanggraphState): state 객체
            kwargs (kwargs): kwargs
            
        Returns 
        ----------
            updated_state (LanggraphState): 업데이트 된 state 객체
        """
        
        res_init_state = BaseRules.init_state(state, **kwargs)
        res_split_prompt_rule_and_core = BaseRules.split_prompt_rule_and_core(state)
        
        updated_state = {**state}
        updated_state |= res_init_state
        updated_state |= res_split_prompt_rule_and_core
        
        return updated_state
        
    @staticmethod
    def init_state(state: LanggraphState, **kwargs):
        """
        state 초기화
        
        Parameters
        ----------
            state (LanggraphState): state 객체
            
        Returns 
        ----------
            updated_state (LanggraphState): 업데이트 된 state 객체
        """
        
        def get_default_value(type_hint):
            origin = get_origin(type_hint)

            # 일반 타입이면
            if origin is None:
                if type_hint == str:
                    return ""
                elif type_hint == int:
                    return 0
                elif type_hint == float:
                    return 0.0
                elif type_hint == bool:
                    return False
                elif type_hint == list:
                    return []
                elif type_hint == dict:
                    return {}
                elif type_hint == type(None):
                    return None
                else:
                    return None

            # Generic 타입 처리
            if origin == list:
                return []
            elif origin == dict:
                return {}
            elif origin == tuple:
                return ()
            elif origin == set:
                return set()

            return None 
        
        _params = {}
        type_hints = get_type_hints(LanggraphState)
        for key, hint in type_hints.items():
            _params[key] = get_default_value(hint)
            
        updated_state = {**state, **_params}
        if kwargs:
            updated_state |= BaseRules.set_state(state, **kwargs)

        return updated_state
    
    @staticmethod
    def set_state(state: LanggraphState, **kwargs):
        """
        state 설정
        
        Parameters
        ----------
            state (LanggraphState): state 객체
            
        Returns 
        ----------
            update (kwargs): 업데이트 할 값
        """

        if kwargs:
            _params = {}
            valid_keys = get_type_hints(LanggraphState).keys()
            _params = {
                key: kwargs[key]
                for key in valid_keys
                if key in kwargs and kwargs[key] is not None
            }
            
        update = {k: v for k, v in _params.items() if v is not None}
        return {
            **state,
            **update
        }
    
    @staticmethod
    def generate_input_message(text, member_seq):
        """
        input_message 생성
        
        Parameters
        ----------
            text (str): 메세지
            member_seq (int): 요청자 시퀀스
            
        Returns 
        ----------
            input_message (str): 그래프에 삽입할 메세지 
            
            e.g.) 
            input_message : <!rule^.^member_seq=0>2025년 7월21일 오후 8시에 1시간 동안 캡스톤 프로젝트 중간보고 미팅할 예정이야. Meeting Room으로 예약해.
            prompt_rule : <!rule^.^member_seq=0>
            prompt_core : 2025년 7월21일 오후 8시에 1시간 동안 캡스톤 프로젝트 중간보고 미팅할 예정이야. Meeting Room으로 예약해.
        """
        
        rule_text = "<!rule^"
        
        # employ info
        rule_text += f'.^member_seq={member_seq}'
        rule_text += f'!>'
        
        input_message = f"{rule_text}{text}"
        return input_message
            
    @staticmethod
    def split_prompt_rule_and_core(state: LanggraphState):
        """
        룰파트와 코어 파트를 분리
        
        Parameters
        ----------
            state (LanggraphState): state 객체
            
        Returns 
        ----------
            prompt_rule (str): 프롬프트 룰파트, 그래프 내에서 룰파트에 사용함 
            prompt_core (str): 프롬프트 코어파트, 그래프 내에서 LLM파트에 사용함 
        """
        input_message = state.get("input_message")
        
        if "<!rule^" in input_message:
            input_message_split = input_message.split("!>")
            prompt_rule = input_message_split[0].replace("<!rule^", "")
            prompt_core = input_message_split[1]
        
        else:
            prompt_rule = None
            prompt_core = input_message.strip()
     
        return {
            **state, 
            "prompt_rule": prompt_rule,
            "prompt_core": prompt_core
        }
    
    @staticmethod
    def parse_prompt_rule(state: LanggraphState):
        """
        룰파트에서 값을 파싱
        
        Parameters
        ----------
            state (LanggraphState): state 객체
            
        Returns 
        ----------
            member_seq (int): 요청자 시퀀스
        """
        member_seq = None
        prompt_rule = state.get("prompt_rule")
        if prompt_rule:
            prompt_rule_dict = {}
            for item in prompt_rule.split('.^'):
                if '=' in item:
                    key, value = item.split('=', 1)
                    prompt_rule_dict[key] = value
            
            member_seq = prompt_rule_dict.get("member_seq")
        
        return {
            "member_seq": member_seq,
        }
        
    @staticmethod
    def insert_prompt_history(
            state: LanggraphState, 
            prompt_core, 
            prompt_template_name, 
            llm_node_response_text_prev
        ):
        """
        프롬프트 처리 결과 저장
        
        Parameters
        ----------
            state (LanggraphState): state 객체
            prompt_core (str): 프롬프트 코어 
            prompt_template_name (str) : 프롬프트 탬플릿(객체) 이름
            llm_node_response_text_prev (str) : 노드 처리 결과
        """
        member_seq = BaseRules.parse_prompt_rule(state).get("member_seq")
        
        llm_model_name = None
        llm = state.get("llm")
        if llm:
            if hasattr(llm, 'model'):
                llm_model_name = llm.model
        
        prompt_history_dao.insert_prompt_history(
            llm_model_name=llm_model_name,
            prompt_template_name=prompt_template_name,
            prompt_core=prompt_core,
            response=llm_node_response_text_prev,
            member_seq=member_seq
        )
        return {
            **state
        }