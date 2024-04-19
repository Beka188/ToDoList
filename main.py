from sqlalchemy import DateTime
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from database import init_db
from typing import Annotated

from models.User import User, find_user
from auth import login_jwt, AuthHandler

app = FastAPI()
auth_handler = AuthHandler()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
def home():
    return "Hello World!"


@app.post("/auth/login")
def user_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return login_jwt(form_data)


@app.post("/auth/signup")
def sign_up(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if find_user(email) is None:
        new_user = User(username, email, password)
        new_user.add()
    else:
        raise HTTPException(status_code=409, detail="User already exists")


@app.post("/token")
def access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return login_jwt(form_data)


@app.get("/users/me")
def get_info_about_user(token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user:
        return user.__repr__()

@app.get("/tasks/new")
def create_task(title: str, description: str, status: str, due_date: DateTime, token: Annotated[str, Depends(oauth2_scheme)]):
    return "Hi"


if __name__ == "__main__":
    init_db()
    # uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("PORT", default=8000), log_level="info")
