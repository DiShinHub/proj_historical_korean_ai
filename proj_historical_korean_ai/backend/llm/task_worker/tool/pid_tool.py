import os


class PidTool:
    @staticmethod
    def get_pid():
        return os.getpid()

    @staticmethod
    def create_pid_file(file_name: str):
        with open(file_name, mode="w", encoding="utf-8") as pid_file:
            pid_file.write(f"{PidTool.get_pid()}")

    @staticmethod
    def remove_pid_file(file_name: str):
        if os.path.exists(file_name):
            os.remove(file_name)
