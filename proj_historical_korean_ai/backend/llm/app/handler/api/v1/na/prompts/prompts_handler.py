from fastapi import APIRouter, Depends
from app.handler.api.v1.na.prompts.dto.req_prompt_post_index import ReqPromptPostIndex
from app.handler.api.v1.na.prompts.prompts_service import LlmBridgesService
from app.model.vo.result_vo import ResultVo
from app.tool.log_tool import LogTool

from app.config.redis_config.redis_config_repository import redis_config_repository

logger = LogTool.get_logger()
router: APIRouter = APIRouter(prefix="/prompts", tags=["/api/v1/au/prompts"])
service = LlmBridgesService(
    redis_config_repository=redis_config_repository
)


@router.post("/")
async def index(
    params: ReqPromptPostIndex,
) -> ResultVo:
    return await service.index(params)
