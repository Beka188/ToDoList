import os

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return "Hello World!"


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("PORT", default=8000), log_level="info")
