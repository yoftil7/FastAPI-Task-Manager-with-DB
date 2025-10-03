from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List


# for creating a task, (request)
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=128)
    completed: bool = Field(default=False)
    priority: Optional[int] = None


# for returning a task, -including id
class Task(TaskCreate):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


# user base
class UserBase(BaseModel):
    username: str
    email: EmailStr


# Create user
class UserCreate(UserBase):
    password: str = Field(..., max_length=72)
    role: str = "user"


# returning a user
class UserOut(UserBase):
    id: int
    username: str
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)


# returning user with tasks
class UserWithTasks(UserOut):
    tasks: List[Task] = Field(default_factory=list)
