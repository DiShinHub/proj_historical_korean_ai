from task_worker.graph.template_schema.prompt_template_schema import PromptTemplateSchema
from task_worker.graph.builds.base.prompts import BasePrompts

class HKTranslator21CPrompts(BasePrompts):
    """
    프롬프트 정의 클래스
    """

    @staticmethod
    def prompt_21c() -> PromptTemplateSchema:

        prompt_template_system = """
            당신은 중세국어(고려 말~조선 초기) 전문 역사언어학자이다.
            목표는 중세국어 문장을 현대 한국어로 가능한 한 자연스럽고 정확하게 번역하는 것이다.
            최종 결과를 **JSON 객체 형태로만 반환**해야 합니다.

            **JSON 응답 형식:**
            {{
            "translations": [],
            "reason": ""
            }}

            **필수 항목 상세 정의 및 엄격한 규칙:**
            - **translations (번역 결과 후보)**: 현대 한국어 번역 결과 후보를 배열의 형태로 저장합니다. 역사적 어휘와 어법을 고려하여 최대 3개까지 신뢰도 순으로 저장하며, 첫 번째 요소가 가장 추천하는 번역입니다.
            - **reason (번역 사유)**: 중세국어 어휘/어미 분석 및 현대어 해석 사유를 문자열 형태로 저장합니다.

            **응답 형식 규칙 (매우 중요):**
            - **오직 JSON 객체만 반환합니다.** 형식: `{{\"translations\": [str], \"reason\": str}}`
            - **JSON 객체 이외에 응답 전후에 어떤 추가적인 설명, 인사말, 문장, 또는 불필요한 공백도 절대 포함하지 마세요.**
        """

        prompt_template_user = """
            다음은 번역 예시이다.

            ### 예시 1

            중세국어:
            안녕ᄒᆞ신가

            반환:
            {{
                "translations": [
                    "안녕하세요.",
                    "안녕하신가요?"
                ],
                "reason": "중세국어 의문형/인사 표현 '안녕ᄒᆞ신가'를 현대의 일상적인 안부 인사로 번역하였다."
            }}

            ---

            ### 예시 2

            중세국어:
            나ᄂᆞᆫ 집으로 가노라

            반환:
            {{
                "translations": [
                    "나는 집에 간다.",
                    "나는 집으로 갑니다."
                ],
                "reason": "1인칭 주어 '나ᄂᆞᆫ'과 화자의 동작을 나타내는 종결어미 '-노라'를 현대 평서문 형태로 변환하였다."
            }}

            ---

            ### 예시 3

            중세국어:
            므스ᄉᆞᆯ ᄒᆞᄂᆞ냐

            반환:
            {{
                "translations": [
                    "무엇을 하고 있는가?",
                    "무엇을 하느냐?"
                ],
                "reason": "의문사 '므스'(무엇)와 목적격 조사, 의문형 어미 '-ᄂᆞ냐'를 현대 의문문으로 재구성하였다."
            }}

            ---

            ### 예시 4

            중세국어:
            나ᄂᆞᆫ 그 사ᄅᆞᆷᄋᆞᆯ 보앗노라

            반환:
            {{
                "translations": [
                    "나는 그 사람을 만났다.",
                    "나는 그 사람을 보았다."
                ],
                "reason": "중세국어 '보다'가 대면 및 만남을 뜻함을 고려하여 현대 한국어로 자연스럽게 번역하였다."
            }}

            ---

            ### 예시 5

            중세국어:
            오ᄂᆞᆯ ᄂᆞᆯ히 됴타

            반환:
            {{
                "translations": [
                    "오늘 날씨가 좋다."
                ],
                "reason": "명사 'ᄂᆞᆯ'(날씨)과 형용사 '됴타'(좋다)의 어휘 변화를 반영하여 변환하였다."
            }}

            ---

            ### 예시 6

            중세국어:
            밥을 먹엇ᄂᆞ냐

            반환:
            {{
                "translations": [
                    "밥을 먹었는가?",
                    "밥을 먹었느냐?"
                ],
                "reason": "과거 시제 선어말어미와 의문형 어미의 현대화 작업을 거쳐 번역하였다."
            }}

            ---

            ### 예시 7

            중세국어:
            나ᄂᆞᆫ 너를 기드리ᄂᆞ니라

            반환:
            {{
                "translations": [
                    "나는 너를 기다리고 있다.",
                    "나는 너를 기다린다."
                ],
                "reason": "동사 '기드리다'와 현재 진행/확정 의미를 나타내는 어미 '-ᄂᆞ니라'를 현대 진행형 표현으로 매핑하였다."
            }}

            ---

            ### 예시 8

            중세국어:
            비옵건대 강녕ᄒᆞ기를 바라노라

            반환:
            {{
                "translations": [
                    "부디 건강하기를 바란다.",
                    "비옵건대 편안하시기를 바랍니다."
                ],
                "reason": "겸양 표현 '비옵건대'와 한자어 '강녕(康寧)'을 현대에 익숙한 '건강' 문맥으로 다듬어 번역하였다."
            }}

            ---

            이제 다음 문장을 번역하라.

            중세국어:
            {prompt_core}

            반환:
            """

        prompt_template_schema: PromptTemplateSchema = {
            "prompt_mode": "chat",
            "prompt_template_system": prompt_template_system,
            "prompt_template_user": prompt_template_user,
            "prompt_template": f"{prompt_template_system}\n{prompt_template_user}",
        }
        return prompt_template_schema