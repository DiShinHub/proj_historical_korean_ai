import os
import re


class PathTool:

    @staticmethod
    def get_relative_path_from_project(path: str) -> str:
        pattern = re.compile(f"^([\/])")
        return pattern.sub("", os.path.abspath(path).replace(os.path.abspath(os.getcwd()), ""))
