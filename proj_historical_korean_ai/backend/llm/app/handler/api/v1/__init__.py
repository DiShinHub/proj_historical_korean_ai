from fastapi import APIRouter

from .au import router as au_router
from .na import router as na_router

router: APIRouter = APIRouter(prefix="/v1")
router.include_router(au_router)
router.include_router(na_router)
