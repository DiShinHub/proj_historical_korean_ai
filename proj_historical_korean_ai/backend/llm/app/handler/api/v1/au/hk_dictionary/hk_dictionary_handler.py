from fastapi import APIRouter, Depends, Body, Query
from typing import Dict, Any

from app.config.authentication_config.jwt_authentication_provider import UserDetailsDto
from app.handler.api.v1.au.hk_dictionary.hk_dictionary_service import HkDictionaryService
from app.model.vo.result_vo import ResultVo
from app.repository.context_repository import context_repository
from app.tool.log_tool import LogTool

logger = LogTool.get_logger()
router: APIRouter = APIRouter(prefix="/hk_dictionary", tags=["hk_dictionary"])
service = HkDictionaryService()


@router.post("")
async def post_hk_dictionary(
    request_dto: Dict[str, Any] = Body(...),
    user_details: UserDetailsDto = Depends(context_repository.get_user_details)
) -> ResultVo:
    """고어 사전 항목 등록"""
    return await service.post_hk_dictionary(request_dto, user_details)


@router.get("/{seq}")
async def get_hk_dictionary(
    seq: int
) -> ResultVo:
    """고어 사전 항목 단건 조회"""
    return await service.get_hk_dictionary(seq)


@router.get("")
async def get_hk_dictionary_list(
    modern_korean: str | None = Query(None, description="현대어 검색어"),
    historical_period_start_dt: str | None = Query(None, description="시대 시작일시 (ISO format)"),
    historical_period_end_dt: str | None = Query(None, description="시대 종료일시 (ISO format)"),
    order_by: str = Query("seq", description="정렬 컬럼 (기본값: seq)"),
    order_direction: str = Query("desc", description="정렬 방향 (asc / desc)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지당 개수"),
) -> ResultVo:
    
    """고어 사전 항목 목록 조회 (검색 및 페이징)"""
    return await service.get_hk_dictionary_list(
        modern_korean=modern_korean,
        historical_period_start_dt=historical_period_start_dt,
        historical_period_end_dt=historical_period_end_dt,
        order_by=order_by,
        order_direction=order_direction,
        page=page,
        page_size=page_size
    )


@router.put("/{seq}")
async def put_hk_dictionary(
    seq: int,
    request_dto: Dict[str, Any] = Body(...),
    user_details: UserDetailsDto = Depends(context_repository.get_user_details)
) -> ResultVo:
    """고어 사전 항목 수정"""
    return await service.put_hk_dictionary(seq, request_dto, user_details)


@router.delete("/{seq}")
async def delete_hk_dictionary(
    seq: int,
    user_details: UserDetailsDto = Depends(context_repository.get_user_details)
) -> ResultVo:
    """고어 사전 항목 삭제 (Soft Delete)"""
    return await service.delete_hk_dictionary(seq, user_details)

@router.post("/dump")
async def dump_raw_hk_dictionary(
    request_dto: Dict[str, Any] = Body(...),
    user_details: UserDetailsDto = Depends(context_repository.get_user_details)
) -> ResultVo:
    """고어 사전 항목 등록"""
    return await service.dump_raw_hk_dictionary(request_dto, user_details)