import uvicorn, os

from fastapi import FastAPI, Depends, Form, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from database import init_db
from typing import Annotated, Union
from datetime import date

from models.update import UpdateTask
from models.User import User, find_user
from models.Task import Task, find_task, update, delete_user_task, TaskStatus, TaskCategory
from models.Group import add_to_group, create_new_group, all_members
from models.invitations import generate_unique_token, Invitation, is_invitation
from auth import login_jwt, AuthHandler

app = FastAPI()
auth_handler = AuthHandler()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
def home():
    return "Hello World!!"


@app.post("/auth/login")
def user_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return login_jwt(form_data)


@app.post("/auth/signup")
def sign_up(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if find_user(email) is None:
        new_user = User(username, email, password)
        new_user.add()
        raise HTTPException(status_code=200, detail="Successful sign up!")
    else:
        raise HTTPException(status_code=409, detail="User already exists")


@app.post("/token")
def access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return login_jwt(form_data)


@app.get("/users/me/info")
def get_info_about_user(token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user:
        return {"username": user.username,
                "email": user.email
                }


@app.get("/users/me/tasks")
def user_tasks(token: Annotated[str, Depends(oauth2_scheme)], status: str = Query(None), category: str = Query(None),
               sort_by: str = Query(None)):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user:
        tasks = user.all_tasks()
        if sort_by:
            reverse = False
            if sort_by.startswith("-"):
                reverse = True
                sort_by = sort_by[1:]
            tasks.sort(key=lambda x: x.get(sort_by), reverse=reverse)
        if status is not None:
            if status in TaskStatus:
                tasks = [task for task in tasks if task["status"] == status]
            else:
                raise HTTPException(status_code=400, detail="Provided status is not valid!")
        if category is not None:
            if category in TaskCategory:
                tasks = [task for task in tasks if task["category"] == category]
            else:
                raise HTTPException(status_code=400, detail="Provided category is not valid!")
        return {"tasks": tasks}
    elif not user:
        raise HTTPException(status_code=404, detail="User not found!")
    else:
        raise HTTPException(status_code=500)


@app.patch("/users/me/update_task/{task_id}")
async def update_task(task_id: int, update_data: UpdateTask, token: str = Depends(oauth2_scheme)):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    task = find_task(task_id)
    if user and task and user.id == task.user_id:
        data = update_data.dict(exclude_unset=True)
        update(task_id, data)
        return find_task(task_id).__repr__()
    elif task:
        raise HTTPException(status_code=403, detail="You can not change this task!")
    else:
        raise HTTPException(status_code=404, detail="Not Found!")


@app.delete("/users/me/delete_task/{task_id}")
async def delete_task(task_id: int, token: str = Depends(oauth2_scheme)):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    task = find_task(task_id)
    if user and task and user.id == task.user_id:
        delete_user_task(task_id)
        raise HTTPException(status_code=200, detail="Successfully deleted task")
    elif task:
        raise HTTPException(status_code=403, detail="You can not delete this task!")
    else:
        raise HTTPException(status_code=404, detail="Not Found!")


@app.post("/users/me/new_task")
def create_task(title: str, description: str, status: TaskStatus, due_date: Union[int, date], category: TaskCategory,
                token: Annotated[str, Depends(oauth2_scheme)]):
    if not isinstance(due_date, int):
        raise HTTPException(status_code=422, detail="The date format is incorrect!")
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user:
        new_task = Task(title, description, due_date, status, user.id, category)
        new_task.add()
        raise HTTPException(status_code=200, detail="Successfully added!")
    else:
        raise HTTPException(status_code=404, detail="User not found!")


@app.post("/users/me/group/new_group")
def create_group(name: str, description: str, token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user:
        created = create_new_group(user.id, name, description)
        if created == -1:
            raise HTTPException(status_code=400, detail="Incorrect format!")
        elif created == 0:
            raise HTTPException(status_code=409, detail="Group with such name already exist!")
        else:
            raise HTTPException(status_code=200, detail="Successfully added!")
    else:
        raise HTTPException(status_code=404, detail="User not found!")


@app.get("/users/me/ownGroups")
def user_tasks(token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user:
        groups = user.user_own_groups()
        return {"groups": groups}
    elif not user:
        raise HTTPException(status_code=404, detail="User not found!")
    else:
        raise HTTPException(status_code=500)


@app.get("/users/me/memberGroups")
def user_tasks(token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user:
        groups = user.user_member_groups()
        return {"groups": groups}
    elif not user:
        raise HTTPException(status_code=404, detail="User not found!")
    else:
        raise HTTPException(status_code=500)


@app.post("/users/me/group/invitations/create")
def create_invitation(group_id: int, token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user:
        invitation_token = generate_unique_token()
        group_invitation = Invitation(sender_id=user.id, group_id=group_id, token=invitation_token)
        group_invitation.add()
        return {"token": invitation_token}
    else:
        raise HTTPException(status_code=404, detail="User not found!")


@app.post("/invitations/accept/{token}")
def accept_invitation(invitation_token: str, token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user:
        group_invitation = is_invitation(invitation_token)
        if group_invitation:
            add_to_group(group_invitation.group_id, user.id)
            return {"message": "Invitation accepted"}
        else:
            raise HTTPException(status_code=404, detail="Invitation not found")
    else:
        raise HTTPException(status_code=404, detail="User not found!")


@app.post("/invitations/decline/{token}")
def decline_invitation(invitation_token: str, token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user:
        group_invitation = is_invitation(invitation_token)
        if group_invitation:
            return {"message": "Invitation declined"}
        else:
            raise HTTPException(status_code=404, detail="Invitation not found")
    else:
        raise HTTPException(status_code=404, detail="User not found!")


# check if that group still exist?
if __name__ == "__main__":
    print(accept_invitation("504d11b6-fb13-42ca-8478-7f96a1c6a91a"))
    # init_db()
    # token = generate_unique_token()
    # invitation = Invitation(sender_id=1, group_id=1, token=token)
    # invitation.add()
    # uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("PORT", default=8000), log_level="info")
