from app.exception.bad_request_exception import BadRequestException
import re


class BaseValidation():
    
    def __init__(self):
        pass

    def valid_id(self, value):

        # 아이디 길이가 6자 이상, 12자 이하인지 확인
        if len(value) < 6 or len(value) > 12:
            raise BadRequestException('아이디는 최소 6자 이상, 12자 이하여야 합니다')
        
        # 아이디는 영문과 숫자로만 이루어져야 함
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise BadRequestException('아이디는 영문자와 숫자로만 이루어져야 합니다')

        return value

    def valid_password(self, value):
        
        # 비밀번호는 8자 이상, 20자 이하인지 확인
        if len(value) < 8 or len(value) > 20:
            raise BadRequestException('비밀번호는 8자 이상, 20자 이하여야 합니다.')
        
        # 공란 확인
        if " " in value:
            raise BadRequestException('비밀번호는 공란을 포함할 수 없습니다.')
        
        # 특수문자 확인
        if re.search(r'[@_!#$%^&*()<>?/\|}{~:]', value):
            raise BadRequestException('비밀번호는 특수문자를 포함할 수 없습니다.')

        # 비밀번호는 영문자, 숫자를 각각 1개 이상 포함해야 함
        if not re.search(r'[A-Za-z]', value) and \
           not re.search(r'\d', value):
            raise BadRequestException('비밀번호는 영문자, 숫자, 특수문자를 각각 1개 이상 포함해야 합니다')
        
        return value
    
    def valid_email(self, value):
        
        # 이메일 형식 검사
        if not re.match(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", value):
            raise BadRequestException('이메일 포멧이 일차하지 않습니다.')

        # . 뒤에 문자가 1개 이상 와야 함
        if not re.search(r'\.[a-zA-Z]{1,}', value.split('@')[1]):
            raise BadRequestException('이메일 포멧이 일차하지 않습니다.')
        
        return value
