from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .database import engine, get_db, Base


# Define the lifespan async context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown logic (optional)
    # Add any cleanup code here


app = FastAPI(lifespan=lifespan, title="Task Manager with DB")


@app.post("/users", response_model=schemas.UserOut, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(
        username=user.username, email=user.email, hashed_password=user.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/tasks", response_model=schemas.Task, status_code=201)
def create_task(task: schemas.TaskCreate, user_id: int, db: Session = Depends(get_db)):
    db_task = models.Task(**task.model_dump(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)  # get auto-generated ID
    return db_task


@app.get("/tasks", response_model=List[schemas.Task])
def list_tasks(user_id: int, db: Session = Depends(get_db)):
    return (
        db.execute(select(models.Task).where(models.Task.owner_id == user_id))
        .scalars()
        .all()
    )


@app.get("/tasks/{task_id}", response_model=schemas.Task)
def get_task(task_id: int, user_id: int, db: Session = Depends(get_db)):
    task = (
        db.execute(
            select(models.Task).where(
                models.Task.owner_id == user_id, models.Task.id == task_id
            )
        )
        .scalars()
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    user_id: int,
    updated: schemas.TaskCreate,
    db: Session = Depends(get_db),
):
    task = (
        db.execute(
            select(models.Task).where(
                models.Task.owner_id == user_id, models.Task.id == task_id
            )
        )
        .scalars()
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in updated.model_dump().items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, user_id: int, db: Session = Depends(get_db)):
    task = (
        db.execute(
            select(models.Task).where(
                models.Task.owner_id == user_id, models.Task.id == task_id
            )
        )
        .scalars()
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return None
