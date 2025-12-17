from fastapi import APIRouter
from . import provas

router = APIRouter()
router.include_router(provas.router, prefix="/provas", tags=["provas"])

