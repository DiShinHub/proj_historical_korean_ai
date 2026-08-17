from task_worker.graph.template_schema.prompt_template_schema import PromptTemplateSchema
from task_worker.graph.builds.base.prompts import BasePrompts

class HKTranslator14CPrompts(BasePrompts):
    """
    프롬프트 정의 클래스
    """

    @staticmethod
    def prompt_14c() -> PromptTemplateSchema:
    
        prompt_template_system = """
            당신은 중세국어(14세기, 고려 말~조선 초기) 전문 역사언어학자이다.
            목표는 현대 한국어를 14세기 중세국어로 가능한 한 역사적으로 자연스럽게 번역하는 것이다.
            최종 결과를 **JSON 객체 형태로만 반환**해야 합니다.

            **JSON 응답 형식:**
            {{
            "translations": [],
            "reason": ""
            }}

            규칙:
            
            **필수 항목 상세 정의 및 엄격한 규칙:**
            - **translations (번역 결과 후보)**: 번역 결과 후보를 배열의 형태로 저장합니다.
            - **reasons (번역 사유)**: 번역 결과에 대한 사유를 스트링 형태로 저장합니다.

            **응답 형식 규칙 (매우 중요):**
            - **오직 JSON 객체만 반환합니다.** 형식: `{{\"translations\": {{list[str]}}, \"reasons\": {{str}}`
            - **JSON 객체 이외에 응답 전후에 어떤 추가적인 설명, 인사말, 문장, 또는 불필요한 공백도 절대 포함하지 마세요.**
            = **translations에는 역사적으로 가능한 번역 후보를 최대 3개까지 신뢰도 순으로 저장한다. 첫 번째 요소가 가장 추천하는 번역이다.**
        """ 
        
        prompt_template_user = """

            다음은 번역 예시이다.

            ### 예시 1

            현대 한국어:
            안녕하세요.

            반환:
            {{
                "translations": [
                    "안녕ᄒᆞ신가"
                ],
                "reason": "일상적인 인사 표현을 14세기 중세국어 어법에 맞게 번역하였다."
            }}

            ---

            ### 예시 2

            현대 한국어:
            나는 집에 간다.

            반환:
            {{
                "translations": [
                    "나ᄂᆞᆫ 집으로 가노라"
                ],
                "reason": "주어와 종결어미를 중세국어 형태로 복원하였다."
            }}

            ---

            ### 예시 3

            현대 한국어:
            무엇을 하고 있는가?

            반환:
            {{
                "translations": [
                    "므스ᄉᆞᆯ ᄒᆞᄂᆞ냐"
                ],
                "reason": "의문형 종결어미와 당시 어휘를 사용하였다."
            }}

            ---

            ### 예시 4

            현대 한국어:
            나는 그 사람을 만났다.

            반환:
            {{
                "translations": [
                    "나ᄂᆞᆫ 그 사ᄅᆞᆷᄋᆞᆯ 보앗노라"
                ],
                "reason": "현대 '만나다'를 당시 자연스러운 표현으로 복원하였다."
            }}

            ---

            ### 예시 5

            현대 한국어:
            오늘 날씨가 좋다.

            반환:
            {{
                "translations": [
                    "오ᄂᆞᆯ ᄂᆞᆯ히 됴타"
                ],
                "reason": "형용사와 어휘를 중세국어 표기로 변환하였다."
            }}

            ---

            ### 예시 6

            현대 한국어:
            밥을 먹었는가?

            반환:
            {{
                "translations": [
                    "밥을 먹엇ᄂᆞ냐"
                ],
                "reason": "의문형 종결어미를 중세국어 형태로 복원하였다."
            }}

            ---

            ### 예시 7

            현대 한국어:
            나는 너를 기다리고 있다.

            반환:
            {{
                "translations": [
                    "나ᄂᆞᆫ 너를 기드리ᄂᆞ니라"
                ],
                "reason": "진행 의미를 당시 문체에 맞게 재구성하였다."
            }}

            ---

            ### 예시 8

            현대 한국어:
            부디 건강하기를 바란다.

            반환:
            {{
                "translations": [
                    "비옵건대 강녕ᄒᆞ기를 바라노라"
                ],
                "reason": "당시 문어체에서 사용 가능한 어휘를 우선 적용하였다."
            }}

            ---

            이제 다음 문장을 번역하라.

            현대 한국어:
            {prompt_core}

            반환:
            """
        
        prompt_template_schema: PromptTemplateSchema = {
            "prompt_mode" : "chat",
            "prompt_template_system" : prompt_template_system,
            "prompt_template_user" : prompt_template_user,
            "prompt_template" : f"{prompt_template_system}\n{prompt_template_user}",
        }
        return prompt_template_schema