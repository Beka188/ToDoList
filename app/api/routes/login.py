from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi_mail import MessageSchema, MessageType, FastMail
from starlette.responses import JSONResponse

from app.core.security import login_jwt, AuthHandler
from app.core.emailVerification import conf
from app.models.User import find_user, User, update_user
from app.models.email import is_valid_email, Email, find_user_by_token
from app.models.invitations import generate_unique_token

router = APIRouter()
auth_handler = AuthHandler()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
base = "http://127.0.0.1:8000"


@router.get("/")
def home():
    return {"message": "Welcome to the my project!"}


@router.post("/token")
def access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return login_jwt(form_data)


@router.post("/signup")
def sign_up(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if not is_valid_email(email):
        raise HTTPException(status_code=422, detail="The email format is incorrect!")
    if find_user(email) is None:
        new_user = User(username, email, password)
        return new_user.add()
    else:
        raise HTTPException(status_code=409, detail="User already exists")


@router.post("/login/send_verify_email/")
async def send_email_verification(token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    token = generate_unique_token()
    em = Email(email, token)
    em.add()
    a = base + f"/auth/verify/{token}"
    html = f"<p>Hi, please click the following link to verify your email:</p><a href=\"{a}\">Verify Email</a>"
    message = MessageSchema(
        subject="ToDoAPP-verification",
        recipients=[email, ],
        body=f"Verification: {html}",
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})


@router.get("/login/verify/{token}")
async def verify_email(token: str):
    email = find_user_by_token(token)
    if email is None:
        raise HTTPException(status_code=404, detail="User not found")
    update_user(email, {"is_email_verified": True})
    return {"message": "Email verified successfully"}
