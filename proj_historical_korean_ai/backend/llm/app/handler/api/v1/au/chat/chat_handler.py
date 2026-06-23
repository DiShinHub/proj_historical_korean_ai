from fastapi import APIRouter, Depends

from app.config.authentication_config.jwt_authentication_provider import UserDetailsDto
from app.handler.api.v1.au.chat.chat_service import ChatService
from app.model.vo.result_vo import ResultVo
from app.repository.context_repository import context_repository
from app.tool.log_tool import LogTool

from fastapi import Body, Depends, Query
from typing import Dict, Any

logger = LogTool.get_logger()
router: APIRouter = APIRouter(prefix="/chat", tags=["chat"])
service = ChatService()

@router.post("/chat_session")
async def post_chat_session(
        request_dto: Dict[str, Any] = Body(...),
        user_details: UserDetailsDto = Depends(context_repository.get_user_details)
) -> ResultVo:
    return await service.post_chat_session(request_dto, user_details)

@router.get("/chat_session/my-list")
async def get_my_chat_session_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_details: UserDetailsDto = Depends(context_repository.get_user_details),
) -> ResultVo:
    return await service.get_my_chat_session_list(
        user_details=user_details,
        page=page,
        page_size=page_size,
    )

@router.put("/chat_session/chat_session_seq/{chat_session_seq}")
async def put_chat_session(
        chat_session_seq: int, 
        request_dto: Dict[str, Any] = Body(...)
) -> ResultVo:
    return await service.put_chat_session(chat_session_seq, request_dto)

@router.delete("/chat_session/chat_session_seq/{chat_session_seq}")
async def delete_chat_session(
        chat_session_seq: int
) -> ResultVo:
    return await service.delete_chat_session(chat_session_seq)


@router.post("/chat_message")
async def post_chat_message(
    request_dto: Dict[str, Any] = Body(...),
    user_details: UserDetailsDto = Depends(context_repository.get_user_details)
) -> ResultVo:
    return await service.post_chat_message(request_dto, user_details)

@router.get("/chat_message/list")
async def get_chat_message_list_by_session(
    chat_session_seq: int = Query(1, ge=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> ResultVo:
    
    return await service.get_chat_message_list_by_session(
        chat_session_seq=chat_session_seq,
        page=page,
        page_size=page_size,
    )

@router.put("/chat_message/chat_message_seq/{chat_message_seq}")
async def put_chat_message(
    chat_message_seq: int, 
    request_dto: Dict[str, Any] = Body(...)
) -> ResultVo:
    return await service.put_chat_message(chat_message_seq, request_dto)

