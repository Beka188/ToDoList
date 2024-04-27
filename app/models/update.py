from datetime import date
from typing import Optional, Union

from pydantic import BaseModel
from app.models.Task import TaskCategory, TaskStatus


class UpdateUserInfo(BaseModel):
    phone: Optional[str] = None
    name: Optional[str] = None
    city: Optional[str] = None


class createTask(BaseModel):
    title: str = "Title"
    description: Optional[str] = "Description of the task"
    status: Optional[TaskStatus] = "Status of the task: done, in_progress, to_do(default), missing"
    due_date: Union[int, date] = "deadline of the task: Provide in timestamp"
    category: Optional[TaskCategory] = "The category of the task: work, personal, education, social, other(default)"


class UpdateTask(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[TaskCategory] = None
    due_date: Optional[int] = None
    status: Optional[TaskStatus] = None
