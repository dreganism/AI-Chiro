from fastapi import APIRouter
from backend.api.auth import router as auth_router
from backend.api.upload import router as upload_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(upload_router)
