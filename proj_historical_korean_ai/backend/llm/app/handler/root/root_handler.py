from fastapi import Request, APIRouter

from app.handler.root.root_service import RootService
from app.model.vo.result_vo import ResultVo
from app.tool.log_tool import LogTool

logger = LogTool.get_logger()
router: APIRouter = APIRouter(prefix="", tags=["/root"])
service = RootService()


@router.get("/")
async def get_index(request: Request) -> ResultVo:
    return service.get_index(request)
