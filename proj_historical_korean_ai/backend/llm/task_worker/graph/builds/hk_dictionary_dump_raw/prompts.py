from task_worker.graph.builds.base.prompts import BasePrompts
from task_worker.graph.template_schema.prompt_template_schema import (
    PromptTemplateSchema,
)


class HKDictionaryDumpRawCPrompts(BasePrompts):
    """
    중세국어-현대국어 단어 대 단어(1:1 대응) 매핑 프롬프트 정의 클래스
    """
    @staticmethod
    def prompt_remove_useless() -> PromptTemplateSchema:

        prompt_template_system = """
            당신은 고전 문헌 및 중세국어 데이터 전처리 전문 에이전트입니다.
            제공된 입력 데이터에는 중세국어 원문, 각주 번호(예: 주001), 한자/서지 제목(예: 복식분축(...)), 현대어 번역문 등이 섞여 있습니다.
            당신의 목표는 2차 단어 매핑 작업이 수월하도록 불필요한 노이즈를 완전 제거하고 정제된 데이터만 추출하는 것입니다.

            **정제 규칙:**
            1. **각주 제거**: '주001)', '주002)' 같은 모든 각주 번호 및 단어 끝에 붙은 각주용 숫자를 완전히 제거하세요. (예: '복식근주001)' -> '복식근')
            2. **메타데이터/제목 제거**: '복식분축(卜式分畜 : ...)'과 같은 한자 제목, 설명, 서지 정보는 모두 제거하세요.
            3. **공백 정제**: 각주나 메타데이터가 지워지면서 생긴 불필요한 이중 공백, 양끝 공백을 깔끔히 정리하세요.

        """

        prompt_template_user = """
            다음 raw 입력 데이터를 정제하세요.

            [입력 데이터]
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

    @staticmethod
    def prompt_hk_dictionary_dump_raw() -> PromptTemplateSchema:

        prompt_template_system = """
            당신은 중세국어 전문 역사언어학자입니다.
            당신의 목표는 제공된 현대 한국어 텍스트를 중세국어로 번역한 후, **동일한 순서와 의미로 대응하는 [중세국어 어휘, 현대국어 어휘] 1:1 쌍(Pair)**을 어절/단어 단위로 완벽히 분리하여 추출하는 것입니다.

            **엄격한 작업 규칙:**
            1. **1:1 대응 원칙**: 중세국어 어휘 하나에 반드시 그에 정확히 대응하는 현대국어 어휘 하나만 매핑하세요. 문장 전체나 구(Phrase) 단위로 뭉쳐서 넣지 마세요.
            2. **노이즈 및 주석 제거**: '복ᄉᆞᆨ근주', '하람주'처럼 단어 뒤에 붙는 주석이나 오탈자 표기를 배제하고, 깔끔한 중세국어 표기 형태만 추출하세요.
            3. **순서 유지**: 문장의 흐름(어순)에 맞춰 어휘 쌍을 순서대로 배열하세요.
            4. **누락 최소화**: 문장을 구성하는 주요 체언, 용언, 부사, 조사 조합을 가능한 한 빠짐없이 단어 단위로 다 잘라내어 추출하세요.

            **응답 형식 규칙:**- 
            **반드시 RFC 8259 표준을 준수하는 Valid JSON만 출력하세요.**
            - **모든 JSON Key와 String Value에는 반드시 큰따옴표(Double Quote, ")만 사용해야 합니다. 홑따옴표(Single Quote, ')나 Smart Quote(“, ”)는 절대 사용 금지입니다.**
            - 텍스트 값 내부에 큰따옴표가 포함될 경우 반드시 `\\"` 형태로 이스케이프 처리하세요.
            - **오직 JSON 객체만 반환합니다.** 마크다운 코드 블록(```json)이나 앞뒤 설명 문장을 절대 출력하지 마세요.

            **JSON 응답 스키마:**
            {{
                "word_pairs": [
                    ["중세국어 어휘1", "현대국어 어휘1"],
                    ["중세국어 어휘2", "현대국어 어휘2"]
                ]
            }}
        """

        prompt_template_user = """
            다음은 단어 매핑 예시이다.

            ### 예시 1 (단문)
            현대 한국어:
            나는 집에 간다.

            반환:
            {{
                "word_pairs": [
                    ["나ᄂᆞᆫ", "나는"],
                    ["집의", "집에"],
                    ["가노라", "간다"]
                ],
                "reason": "주어, 부사어(목적지), 종결사식을 1:1 어절 단위로 매핑함."
            }}

            ---

            ### 예시 2 (복합문 / 서술문)
            현대 한국어:
            복식은 한나라 사람이다. 농사짓는 일과 가축 기르는 일을 하였다.

            반환:
            {{
                "word_pairs": [
                    ["복ᄉᆞᆨᄋᆞᆫ", "복식은"],
                    ["한나라", "한나라"],
                    ["사ᄅᆞᆷ이로다", "사람이다"],
                    ["농사짓ᄂᆞᆫ", "농사짓는"],
                    ["일과", "일과"],
                    ["ᄀᆞᄎᆞᆨ", "가축"],
                    ["기ᄅᆞᄂᆞᆫ", "기르는"],
                    ["일을", "일을"],
                    ["ᄒᆞ였ᄂᆞ니라", "하였다"]
                ],
                "reason": "고유명사, 체언+조사, 용언 활용형을 문맥 순서에 맞춰 1:1 단어 단위로 매핑함."
            }}

            ---

            이제 다음 현대 한국어 문장을 분석하여 중세국어 단어 매핑 2차원 배열(word_pairs)을 생성하라.

            현대 한국어:
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