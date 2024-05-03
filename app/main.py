from fastapi import FastAPI
from fastapi.routing import APIRoute
from app.api.main import api_router


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    generate_unique_id_function=custom_generate_unique_id,
)

app.include_router(api_router)

from app.models.User import delete_user
from app.models.email import delete_verification_token

if __name__ == "__main__":
    delete_verification_token("esil.seitkalyk@gmail.com")
    # dele
