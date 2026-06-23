from fastapi import APIRouter

from app.handler.api.v1.na.health.health_service import HealthService
from app.model.vo.result_vo import ResultVo
from app.tool.log_tool import LogTool

logger = LogTool.get_logger()
router: APIRouter = APIRouter(prefix="/health", tags=["/api/v1/na/health"])
service = HealthService()


@router.get("")
async def get_index() -> ResultVo:
    return await service.get_index()
