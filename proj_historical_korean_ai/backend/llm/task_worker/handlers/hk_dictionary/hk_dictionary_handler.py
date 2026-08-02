from task_worker.handlers.hk_dictionary.hk_dictionary_service import HKDictionaryService

class PromptsHandler():

    def __init__(self):
        self.hk_dictionary_service = HKDictionaryService()
        
    def handle_hk_dictionary_dump_raw(self, task):
        return self.hk_dictionary_service.handle_hk_dictionary_dump_raw(task)