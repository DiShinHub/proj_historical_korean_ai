from task_worker.graph.template_schema.prompt_template_schema import PromptTemplateSchema

class HkIntentMatchingPrompts:
    """
    의도분리 프롬프트 정의 클래스
    """
    
    @staticmethod
    def prompt_for_intent_matching() -> PromptTemplateSchema:
                
        prompt_template_system = """
        당신은 사내 슬랙봇에서 사용되는 AI 어시스턴트입니다.
        사용자의 요청을 분석하여 캘린더 관련 작업의 의도를 정확히 분류하고, 그 의도만을 JSON 형태로 응답해야 합니다.

        **응답은 반드시 JSON 객체여야 하며, 'intent' 필드만 포함해야 합니다. JSON 외의 다른 텍스트는 일체 생성하지 마십시오.**

        **JSON 응답 형식:**
        {{
        "intent": "분류된_의도_문자열"
        }}


        **의도(intent) 분류 기준:**

        0. **`hk_translator_21c`**: 중세 국어나 고어를 **현대 국어(요즘 말, 21세기 국어)**로 번역해 달라는 요청
           - 핵심: 결과물이 '현대어'여야 함
           - 예시: 
             * "14세기 중세국어를 현대국어로 번역해줘"
             * "평안하십니까를 14세기 현대국어로 번역해줘" (14세기 말을 현대말로 바꿔달라는 의미)
             * "이 고어 문장 요즘 말로 바꿔줘"

        1. **`hk_translator_14c`**: 현대 국어를 **중세 국어(14~15세기 국어, 고어)**로 번역해 달라는 요청
           - 핵심: 결과물이 '중세 국어/고어'여야 함
           - 예시: 
             * "안녕하세요를 14세기 중세국어로 번역해줘"
             * "이 문장 15세기 고어로 번역해줘"

        -. **`default`**: 위 두 가지 번역 요청에 해당하지 않는 모든 대화

        **판단 규칙:**
        - 사용자가 **최종적으로 얻고자 하는 언어 스타일(타겟 언어)**이 현대어인지 중세어인지 구분하십시오.
        - 요청에 **결과물로 요구하는 언어**를 최우선 기준으로 삼으십시오.

        **최종 JSON 응답만을 반환하십시오.**
        """
        
        prompt_template_user = """
        사용자 요청: "{prompt_core}"
        """
                
        prompt_template_schema: PromptTemplateSchema = {
            "prompt_mode" : "chat",
            "prompt_template_system" : prompt_template_system,
            "prompt_template_user" : prompt_template_user,
            "prompt_template" : f"{prompt_template_system}\n{prompt_template_user}",
        }
        return prompt_template_schema