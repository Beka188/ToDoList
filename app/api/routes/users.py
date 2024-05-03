from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer

from app.core.auth import AuthHandler
from app.models.User import find_user, find_user_id, all_users, delete_user

app = FastAPI()
auth_handler = AuthHandler()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
base = "http://127.0.0.1:8000"

router = APIRouter()


@router.get("/")
def read_users():
    return all_users()


@router.get("/{user_id}")
def read_user_by_id(user_id: int):
    user = find_user_id(user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{user_id}")
def delete_user_by_id(user_id: int, token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user and user.id == user_id:
        delete_user(email)
        return {"message": "Successfully deleted"}
    raise HTTPException(status_code=403, detail="You can delete this user!")
