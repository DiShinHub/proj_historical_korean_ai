import os
import time
from multiprocessing import Process
from task_worker.config.logging_config.logging_config_runner import LoggingConfigRunner
from task_worker.handlers.task_handler import TaskHandler

class TaskWorker:

    def __init__(self):
        self.config_logger()
        self.task_handler = TaskHandler()
            
    def config_logger(self):
        logging_config_runner = LoggingConfigRunner(_is_singleton=False)
        logging_config_runner.run()
    
    def run(self):
        self.task_handler.run()


def start_worker(worker_id: int):
    print(f"[Worker-{worker_id}] 시작 (PID: {os.getpid()})")
    try:
        worker = TaskWorker()
        worker.run()

    except Exception as e:
        print(f"[Worker-{worker_id}] 예외 발생으로 프로세스 종료 (PID: {os.getpid()}): {e}")
        raise e


def create_process(worker_id: int) -> Process:
    p = Process(target=start_worker, args=(worker_id,), name=f"Worker-{worker_id}")
    p.start()
    return p


if __name__ == "__main__":
    worker_count = int(os.getenv("WORKER_COUNT", 1))
    print(f"[Main] 총 {worker_count}개의 TaskWorker 프로세스를 로딩합니다.")

    # 1. 초기 프로세스 딕셔너리 생성 {worker_id: Process}
    workers = {}
    for i in range(1, worker_count + 1):
        workers[i] = create_process(i)

    # 2. 메인 프로세스 헬스체크 루프 
    while True:
        time.sleep(5)  # 5초마다 프로세스 상태 감시

        for worker_id, p in list(workers.items()):
            if not p.is_alive():
                print(f"[Main] Worker-{worker_id} (PID: {p.pid}) 가 비정상 종료되었습니다. (ExitCode: {p.exitcode})")
                print(f"[Main] Worker-{worker_id} 를 다시 생성하여 살려냅니다...")
                
                # 완전히 자원 해제 후 해당 worker_id로 새 프로세스 시작
                p.join()
                workers[worker_id] = create_process(worker_id)