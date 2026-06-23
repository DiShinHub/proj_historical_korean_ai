from task_worker.handlers.prompts.prompts_service import PromptsService

class PromptsHandler():

    def __init__(self):
        self.prompts_service = PromptsService()
        
    def handle_prompts(self, task):
        return self.prompts_service.handle_prompts(task)