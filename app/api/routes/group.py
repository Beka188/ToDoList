from datetime import date
from typing import Annotated, Union

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer

from app.api.routes.tasks import create_task
from app.core.auth import AuthHandler
from app.models.Group import add_to_group, create_new_group, find_group, all_groups, delete_group
from app.models.GroupTask import GroupTask
from app.models.Task import TaskStatus, TaskCategory
from app.models.User import find_user
from app.models.invitations import generate_unique_token, Invitation, is_invitation
from app.models.email import delete_verification_token

router = APIRouter()
auth_handler = AuthHandler()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
base = "http://127.0.0.1:8000"


@router.post("/")
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


@router.get("/admin")
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

@router.get("/member")
def user_member_groups(token: Annotated[str, Depends(oauth2_scheme)]):
    # return {"Hello"}
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user:
        groups = user.user_member_groups()
        return {"groups": groups}
    elif not user:
        raise HTTPException(status_code=404, detail="User not found!")
    else:
        raise HTTPException(status_code=500)

@router.get("/{group_id}")
def group_info(group_id: int, token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    group = find_group(group_id)
    if user and group and user.id == group["creator_id"]:
        return find_group(group_id)
    elif not user:
        raise HTTPException(status_code=404, detail="User not found!")
    else:
        raise HTTPException(status_code=500)





@router.post("/invitation")
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


@router.post("/accept_invitation/{token}")
def accept_invitation(invitation_token: str, token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user:
        group_invitation = is_invitation(invitation_token)
        if group_invitation:
            add_to_group(group_invitation.group_id, user.id)
            delete_verification_token(email)
            return {"message": "Invitation accepted"}
        else:
            raise HTTPException(status_code=404, detail="Invitation not found")
    else:
        raise HTTPException(status_code=404, detail="User not found!")


@router.post("/decline_invitation/{token}")
def decline_invitation(invitation_token: str, token: Annotated[str, Depends(oauth2_scheme)]):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    if user:
        group_invitation = is_invitation(invitation_token)
        delete_verification_token(email)
        if group_invitation:
            return {"message": "Invitation declined"}
        else:
            raise HTTPException(status_code=404, detail="Invitation not found")
    else:
        raise HTTPException(status_code=404, detail="User not found!")


@router.post("/{group_id}")
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


@router.delete("/{group_id}")
async def delete_group_by_id(group_id: int, token: str = Depends(oauth2_scheme)):
    email = auth_handler.decode_token(token)
    user = find_user(email)
    group = find_group(group_id)
    if user and isinstance(group, dict) and user.id == group.get("creator_id"):
        delete_group(group_id)
        raise HTTPException(status_code=200, detail="Successfully deleted group")
    elif group and user:
        raise HTTPException(status_code=403, detail="You can not delete this group¬¬¬!")
    else:
        raise HTTPException(status_code=404, detail="Not Found!")
