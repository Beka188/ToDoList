from fastapi import FastAPI, Request
from database import init_db
app = FastAPI()


@app.get("/")
def home():
    return "Hello World!"

@app.post("/token")
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return login_jwt(form_data)@app.post("/")


def create_task(request: Request):

    return "Hi"


if __name__ == "__main__":
    init_db()
    # uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("PORT", default=8000), log_level="info")
