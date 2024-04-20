from typing import Optional

from pydantic import BaseModel
from models.Task import CategoryType, TaskStatus


class UpdateUserInfo(BaseModel):
    phone: Optional[str] = None
    name: Optional[str] = None
    city: Optional[str] = None


class UpdateTask(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[CategoryType] = None
    due_date: Optional[int] = None
    status: Optional[TaskStatus] = None
