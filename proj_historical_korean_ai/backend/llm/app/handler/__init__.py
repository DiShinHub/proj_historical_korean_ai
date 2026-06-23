from fastapi import APIRouter

from .api import router as api_router
from .root.root_handler import router as root_router

router: APIRouter = APIRouter(prefix="")
router.include_router(api_router)
router.include_router(root_router)
