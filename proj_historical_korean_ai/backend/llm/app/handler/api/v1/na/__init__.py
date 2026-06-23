from fastapi import APIRouter

from .auth.auth_handler import router as auth_router
from .health.health_handler import router as health_router
from .test.test_handler import router as test_router
from .prompts.prompts_handler import router as prompt_router

router: APIRouter = APIRouter(prefix="/na")
router.include_router(auth_router)
router.include_router(health_router)
router.include_router(test_router)
router.include_router(prompt_router)