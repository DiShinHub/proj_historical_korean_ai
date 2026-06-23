from task_worker.graph.template_schema.prompt_template_schema import PromptTemplateSchema

class BasePrompts:
    """
    베이스 프롬프트 정의 클래스
    """
    
    @staticmethod
    def prompt() -> PromptTemplateSchema:
        
        prompt_template = """{prompt_core}"""
        
        prompt_template_schema: PromptTemplateSchema = {
            "prompt_mode" : "text",
            "prompt_template_system" : None,
            "prompt_template_user" : None,
            "prompt_template" : prompt_template
        }
        return prompt_template_schema
    