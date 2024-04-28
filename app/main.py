from datetime import date
from typing import Annotated, Union

from fastapi import FastAPI, Depends, Form, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi_mail import FastMail, MessageSchema, MessageType
from starlette.responses import JSONResponse

from app.auth import login_jwt, AuthHandler
from app.emailVerification import conf
from app.models.Group import add_to_group, create_new_group, find_group, all_groups, delete_group
from app.models.GroupTask import GroupTask, find_group_id
from app.models.Task import Task, find_task, update, delete_user_task, TaskStatus, TaskCategory
from app.models.User import User, find_user, update_user, delete_user
from app.models.invitations import generate_unique_token, Invitation, is_invitation
from app.models.update import UpdateTask
from app.database import init_db
from app.models.email import find_user_by_token, Email, is_valid_email, delete_verification_token

app = FastAPI()
auth_handler = AuthHandler()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
base = "http://127.0.0.1:8000"


@app.get("/")
def home():
    return "Hello World!!"


@app.post("/auth/login")
def user_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return login_jwt(form_data)


@app.post("/auth/signup")
def sign_up(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if not is_valid_email(email):
        raise HTTPException(status_code=422, detail="The email format is incorrect!")
    if find_user(email) is None:
        new_user = User(username, email, password)
        return new_user.add()
    else:
        raise HTTPException(status_code=409, detail="User already exists")


@app.post("/auth/send_verify_email/")
async def send_email_verification(token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    token = generate_unique_token()
    em = Email(email, token)
    em.add()
    a = base + f"/auth/verify/{token}"
    html = f"<p>Hi, please click the following link to verify your email:</p><a href=\"{a}\">Verify Email</a>"
    message = MessageSchema(
        subject="ToDoAPP-verification",
        recipients=[email],
        body=f"Verification: {html}",
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})


@app.get("/auth/verify/{token}")
async def verify_email(token: str):
    email = find_user_by_token(token)
    if email is None:
        raise HTTPException(status_code=404, detail="User not found")
    update_user(email, {"is_email_verified": True})
    return {"message": "Email verified successfully"}


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
    group_id = find_group_id(task_id)
    #  only the admin should change group tasks, and others only status
    if user and task and user.id == task["user_id"]:
        data = update_data.dict(exclude_unset=True)
        if "category" in data and task["category"] != data["category"] and (
                task["category"] == TaskCategory.GROUP or data["category"] == TaskCategory.GROUP):
            raise HTTPException(status_code=403, detail="Can't change category to/from Group")
        update(task_id, data)
        return find_task(task_id)
    elif task and task["category"] == TaskCategory.GROUP and group_id:
        found = False
        for group in user.user_member_groups():
            if group.id == group_id:
                found = True
                break
        if found:
            update(task_id, {"status": update_data.status or task["status"]})
            return find_task(task_id)
        else:
            raise HTTPException(status_code=403, detail="You can not change this task!")
    elif task:
        raise HTTPException(status_code=403, detail="You can not change this task!")
    else:
        raise HTTPException(status_code=404, detail="Not Found!")


@app.delete("/users/me/delete_task/{task_id}")
async def delete_task(task_id: int, token: str = Depends(oauth2_scheme)):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    task = find_task(task_id)
    if user and task and "user_id" in task and user.id == task["user_id"]:
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
        return new_task.add()
    else:
        raise HTTPException(status_code=404, detail="User not found!")


@app.post("/users/me/group/new_group")
def create_group(name: str, description: str, token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user:
        created = create_new_group(user.id, name, description)
        if created is None:
            raise HTTPException(status_code=409, detail="Group with such name already exist!")
        else:
            return created
    else:
        raise HTTPException(status_code=404, detail="User not found!")


@app.get("/users/me/ownGroups")
def user_admin_groups(token: Annotated[str, Depends(oauth2_scheme)]):
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
def user_member_groups(token: Annotated[str, Depends(oauth2_scheme)]):
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
    found = False
    for group in all_groups(user.id):
        if group["id"] == group_id:
            found = True
            break
    if found:
        invitation_token = generate_unique_token()
        group_invitation = Invitation(sender_id=user.id, group_id=group_id, token=invitation_token)
        group_invitation.add()
        return {"token": invitation_token}
    elif user:
        raise HTTPException(status_code=403, detail="This is not your group!")
    else:
        raise HTTPException(status_code=404, detail="User not found!")


@app.post("/users/me/group/invitations/accept/{token}")
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


@app.post("/users/me/group/invitations/decline/{token}")
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


@app.post("/users/me/group/{group_id}/new_task")
def new_group_task(group_id: int, title: str, description: str, status: TaskStatus, due_date: Union[int, date],
                   token: Annotated[str, Depends(oauth2_scheme)]):
    if not isinstance(due_date, int):
        raise HTTPException(status_code=422, detail="The date format is incorrect!")
    email = auth_handler.decode_token(token)
    user = find_user(email)
    found = False
    for group in all_groups(user.id):
        if group["id"] == group_id:
            found = True
            break
    if found:
        new_task = create_task(title, description, status, due_date, TaskCategory.GROUP, token)
        if new_task:
            group_task = GroupTask(group_id, new_task["id"])
            return group_task.add()
    else:
        raise HTTPException(status_code=403,
                            detail="You are not the owner of the group! Only the owner can create tasks!")


@app.delete("/users/me/delete_group/{group_id}")
async def deleteGroup(group_id: int, token: str = Depends(oauth2_scheme)):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    group = find_group(group_id)
    if user and group and user.id == group["creator_id"]:
        delete_group(group_id)
        raise HTTPException(status_code=200, detail="Successfully deleted group")
    elif group and user:
        raise HTTPException(status_code=403, detail="You can not delete this group¬¬¬!")
    else:
        raise HTTPException(status_code=404, detail="Not Found!")


# check if that group still exist?
if __name__ == "__main__":
    print()
    # delete_user("esil.seitkalyk@gmail.com")
    delete_verification_token("madikphone222@gmail.com")
    # uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("PORT", default=8000), log_level="info")
