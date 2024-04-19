from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from database import init_db
from typing import Annotated

from models.User import User, find_user
from auth import login_jwt

app = FastAPI()


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

@app.get("/token")
def access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return login_jwt(form_data)


def create_task(request: Request):
    return "Hi"


if __name__ == "__main__":
    init_db()
    # uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("PORT", default=8000), log_level="info")
