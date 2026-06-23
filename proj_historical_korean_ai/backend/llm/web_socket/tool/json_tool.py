
import json
import re 


class JsonTool:
    @staticmethod
    def parse_json_data_from_fulltext(text):
        """
       json으로 변환할 수 있는 구절이 있으면 변환

        Parameters
        ----------
        text (str): 풀텍스트
        
        returns
        ----------
        json_data (dict): 파싱 된 dict, 없으면 빈 딕셔너리
        """
        
        json_data = {}
        start_idx = None
        stack = []
        for i, char in enumerate(text):
            if char == '{':
                if start_idx is None:
                    start_idx = i
                stack.append('{')
                
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack:
                        # JSON 객체 문자열 추출
                        json_str = text[start_idx:i+1]
                        try:
                            json_data = json.loads(json_str)
                            return json_data
                        except json.JSONDecodeError:
                            return json_data
        return json_data
