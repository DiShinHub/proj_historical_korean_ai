import traceback

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import Response

from app.config.authentication_config.jwt_authentication_provider import AuthenticationException, AuthorizationException

from app.exception.no_content_exception import NoContentException 
from app.exception.bad_request_exception import BadRequestException 
from app.exception.not_found_exception import NotFoundException
from app.exception.devlab_exception import DevlabException 
from app.exception.no_access_exception import NoAccessException 

from app.model.vo.result_vo import ResultExceptionVo
from app.tool.log_tool import LogTool

logger = LogTool.get_logger("exception_handler_provider")


async def default_exception_handler(request: Request, e: Exception) -> Response:
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Internal Server Error"
    media_type = "application/json"
    if isinstance(e, StarletteHTTPException) or isinstance(e, HTTPException):
        if hasattr(e, "status_code"):
            status_code = e.status_code
        if hasattr(e, "detail"):
            message = e.detail
    elif isinstance(e, RequestValidationError) or isinstance(e, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        message = "Unprocessable Entity"
    if type(e) == NoContentException: # A 특별한 케이스 204는 "컨텐츠 없음" 이 응답은 클라이언트에 반환할 내용이 없을 때 사용되며, 따라서 응답에는 본문이 없어야 함
        status_code = status.HTTP_204_NO_CONTENT
        return Response(status_code=status_code)
    elif type(e) == BadRequestException:
        status_code = status.HTTP_400_BAD_REQUEST
        message = f"{e}"
    elif isinstance(e, AuthenticationException):
        status_code = status.HTTP_401_UNAUTHORIZED
        message = "Unauthorized"
    elif isinstance(e, AuthorizationException):
        status_code = status.HTTP_403_FORBIDDEN
        message = "Forbidden"
    elif type(e) == NoAccessException:
        status_code = status.HTTP_403_FORBIDDEN
        message = f"{e}"
    elif type(e) == NotFoundException:
        status_code = status.HTTP_404_NOT_FOUND
        message = f"{e}"
    elif type(e) == DevlabException:
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        message = f"{e}"
        
    if status_code >= 400:
        logger.error(f"Exception Handler Catch url       = [{request.url}]")
        logger.error(f"Exception Handler Catch type      = [{type(e)}]")
        logger.error(f"Exception Handler Catch exception = [{e}]")
        logger.error(f"Exception Handler Catch traceback = [{traceback.format_exc()}]")
        
    return Response(
        media_type=media_type,
        status_code=status_code,
        content=jsonable_encoder(ResultExceptionVo(success=False, message=message).json())
    )
