from task_worker.graph.template_schema.prompt_template_schema import PromptTemplateSchema
from task_worker.graph.builds.base.prompts import BasePrompts

class HKIpa14CPrompts(BasePrompts):
    """
    프롬프트 정의 클래스
    """

    @staticmethod
    def prompt_14c() -> PromptTemplateSchema:
        """
        중세국어(14세기) 텍스트를 IPA(국제음성기호)로 변환하는 프롬프트
        """
        
        # JSON 예시가 포함된 부분의 중괄호를 {{ }} 로 이스케이프 처리합니다.
        prompt_template_system = """
            당신은 14세기 중세국어(고려 말~조선 초기) 음운론을 전공한 역사음성학 전문가이다.
            목표는 제공된 14세기 중세국어 문장을 당시의 학술적 음성 발음에 맞추어 **IPA(국제음성기호)**로 정확하게 변환하는 것이다.
            최종 결과를 **JSON 객체 형태로만 반환**해야 합니다.

            **음운 표기 지침 (14세기 국어 기준):**
            - 아래아(ㆍ): /ʌ/ 또는 /ɒ/
            - 반치음(ㅿ): /z/ 또는 /β/ (환경에 따른 유성 마찰음)
            - 옛응(ㆁ): 음목(초성)일 경우 /ŋ/, 종성일 경우 /ŋ/
            - 여린히읗(ㆆ): 성문 파열음 /ʔ/
            - 어두 자음군(ㅸ, ㅼ, ㅽ 등): 당시의 병서 표기를 음성학적으로 반영 (예: ㅸ -> /β/)
            - 성조(방점): 필요한 경우 평성, 거성, 상성(장음/복합조)의 음성적 특성을 고려하여 표기

            **필수 항목 상세 정의 및 엄격한 규칙:**
            - **translation (IPA 변환 결과)**: 입력된 중세국어 문장의 IPA 기호 변환 결과를 스트링 형태로 저장합니다.
            - **reason (변환 사유)**: 음운론적 규칙 적용 배경 및 특이 음소 변환 사유를 설명합니다.

            **응답 형식 규칙 (매우 중요):**
            - **오직 JSON 객체만 반환합니다.** 형식: {{"translation": "...", "reason": "..."}}
            - **JSON 객체 이외에 응답 전후에 어떤 추가적인 설명, 인사말, 문장, 또는 불필요한 공백도 절대 포함하지 마세요.**
            - **translation에는 학술적으로 가장 타당한 IPA 표기를 저장합니다.**
        """ 
        
        prompt_template_user = """
            다음은 중세국어 IPA 변환 예시이다.

            ### 예시 1

            중세국어:
            안녕ᄒᆞ신가

            반환:
            {{
                "translation": "an.njəŋ.hʌ.ɕin.ɡa",
                "reason": "아래아(ㆍ)를 14세기 음가인 /ʌ/로 반영하고, 자음 간 음성 변화를 기호화함."
            }}

            ---

            ### 예시 2

            중세국어:
            나ᄂᆞᆫ 집으로 가노라

            반환:
            {{
                "translation": "na.nʌn tɕi.pɯ.ɾo ka.no.ɾa",
                "reason": "조사 'ᄂᆞᆫ'의 아래아(/ʌ/) 및 유음 /ɾ/의 연음 현상을 반영함."
            }}

            ---

            ### 예시 3

            중세국어:
            오ᄂᆞᆯ ᄂᆞᆯ히 됴타

            반환:
            {{
                "translation": "o.nʌl nʌl.çi tjo.tʰa",
                "reason": "14세기 구개음화 이전의 '됴'(/tjo/) 발음과 ㅎ 종성 체념 현상을 반영함."
            }}

            ---

            이제 다음 중세국어 문장을 IPA로 변환하라.

            중세국어:
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