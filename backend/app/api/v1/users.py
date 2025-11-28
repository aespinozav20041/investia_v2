from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def list_users_stub():
    return {"detail": "User endpoints to be implemented"}
