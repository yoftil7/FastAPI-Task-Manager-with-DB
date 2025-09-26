from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# for creating a task, (request)
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=128)
    completed: bool = Field(default=False)
    priority: Optional[int] = None


# for returning a task, -including id
class Task(TaskCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
