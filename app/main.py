from fastapi import FastAPI
from fastapi.routing import APIRoute
from app.api.main import api_router


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    generate_unique_id_function=custom_generate_unique_id,
)

app.include_router(api_router)

from app.models.User import delete_user, drop_users_table
from app.models.email import delete_verification_token
from app.core.database import init_db
from app.models.Task import delete_user_task

if __name__ == "__main__":
    # delete_user_task()
    # init_db()
    # drop_users_table()
    delete_user("esil.seitkalyk@gmail.com")
    delete_verification_token("esil.seitkalyk@gmail.com")
    # dele
