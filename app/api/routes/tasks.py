from datetime import date
from typing import Annotated, Union

from fastapi import Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer

from app.core.security import AuthHandler
from app.models.GroupTask import find_group_id, delete_group_task
from app.models.Task import Task, find_task, update, delete_user_task, TaskStatus, TaskCategory, get_all_tasks
from app.models.User import find_user
from app.models.update import UpdateTask
from fastapi import APIRouter

router = APIRouter()
auth_handler = AuthHandler()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/")
def read_tasks(token: Annotated[str, Depends(oauth2_scheme)], status: str = Query(None), category: str = Query(None),
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

@router.get("/{id}")
def read_task(task_id: int, token: Annotated[str, Depends(oauth2_scheme)]):
    user = find_user(auth_handler.decode_token(token))
    if user and find_task(task_id) and find_task(task_id)["user_id"] == user.id:
        return find_task(task_id)
    elif find_task(task_id):
        raise HTTPException(status_code=403, detail="You can not see this task!")
    elif user:
        raise HTTPException(status_code=404, detail="Task not found!")
    raise HTTPException(status_code=404, detail="User not found!")


@router.post("/")
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


@router.patch("/{task_id}")
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


@router.delete("/{task_id}")
async def delete_task(task_id: int, token: str = Depends(oauth2_scheme)):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    task = find_task(task_id)
    if user and task and "user_id" in task and user.id == task["user_id"]:
        delete_user_task(task_id)
        if task["category"] == TaskCategory.GROUP:
            delete_group_task(task_id == task_id)
        raise HTTPException(status_code=200, detail="Successfully deleted task")
    elif task:
        raise HTTPException(status_code=403, detail="You can not delete this task!")
    else:
        raise HTTPException(status_code=404, detail="Not Found!")

