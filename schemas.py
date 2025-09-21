from pydantic import BaseModel, Field
from typing import Optional


# for creating a task, (request)
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=128)
    completed: bool = Field(default=False)
    priority: Optional[int] = None


# for returning a task, -including id
class Task(TaskCreate):
    id: int

    class Config:
        orm_mode = True  # allows returning SQLAlchemy objects directly
