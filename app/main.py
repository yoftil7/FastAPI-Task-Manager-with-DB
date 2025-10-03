from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .database import engine, get_db, Base
from .security import hash_password, verify_password
from .auth import create_access_token, get_current_user


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
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# login route
@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # query the user from the db
    user = (
        db.execute(
            select(models.User).where(
                or_(
                    models.User.username == form_data.username,
                    models.User.email == form_data.username,
                )
            )
        )
        .scalars()
        .first()
    )
    # check if user exists
    if not user:
        raise HTTPException(status_code=404, detail="User not found, login First!")

    # check if password matches
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    # create the token
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/tasks", response_model=schemas.Task, status_code=201)
def create_task(
    task: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_task = models.Task(**task.model_dump(), owner_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)  # get auto-generated ID
    return db_task


@app.get("/tasks", response_model=List[schemas.Task])
def list_tasks(
    current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return (
        db.execute(select(models.Task).where(models.Task.owner_id == current_user.id))
        .scalars()
        .all()
    )


@app.get("/tasks/{task_id}", response_model=schemas.Task)
def get_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = (
        db.execute(
            select(models.Task).where(
                models.Task.owner_id == current_user.id, models.Task.id == task_id
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
    updated: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = (
        db.execute(
            select(models.Task).where(
                models.Task.owner_id == current_user.id, models.Task.id == task_id
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
def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = (
        db.execute(
            select(models.Task).where(
                models.Task.owner_id == current_user.id, models.Task.id == task_id
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
