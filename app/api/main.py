from fastapi import APIRouter

from app.api.routes import users, login, group, tasks

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(group.router, prefix="/group", tags=["group"])






