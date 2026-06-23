
from task_worker.config.logging_config.logging_config_runner import LoggingConfigRunner
from task_worker.handlers.task_handler import TaskHandler

class TaskWorker():

    def __init__(self):
        self.config_logger()
        self.task_handler = TaskHandler()
            
    def config_logger(self):
        logging_config_runner = LoggingConfigRunner(_is_singleton=False)
        logging_config_runner.run()
        
    def config_lang_graph(self):
        pass
    
    def run(self):
        self.task_handler.run()
    
if __name__ == "__main__":
    # 필요시 개수 증분
    task_worker = TaskWorker()
    task_worker.run()