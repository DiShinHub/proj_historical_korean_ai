from typing import TypedDict, Annotated, Any

# 상태 정의
class LanggraphState(TypedDict):
    llm: Annotated[object, "llm"]
    input_message:Annotated[str, "입력 메세지"]
    prompt_rule: Annotated[str, "프롬프트 룰파트"]
    prompt_core: Annotated[str, "프롬프트 LLM 코어파트"]
    llm_node_response_text_prev: Annotated[dict, "직전 LLM 노드 처리 결과 text"]
    llm_node_response_dict_prev: Annotated[dict, "직전 LLM 노드 처리 결과 dict"]
    llm_node_responses: Annotated[dict, "llm 노드 처리 결과들"]
    event_params: Annotated[dict, "이벤트 파라메터"]
    params: Annotated[dict, "기타 파라메터"]