from typing import Annotated

from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from app.models.User import login
import jwt

# from User import *


class AuthHandler:
    security = HTTPBearer()
    secret = 'SECRET'

    def encode_token(self, user_username):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=5),
            'iat': datetime.utcnow(),
            'sub': user_username
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'

        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=['HS256']
            )
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Signature has expired")
        except jwt.InvalidTokenError:
            return unauthorized()

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)


auth_handler = AuthHandler()


def login_jwt(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = login(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    jwt_token = auth_handler.encode_token(form_data.username)
    return {"access_token": jwt_token}


async def unauthorized():
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
