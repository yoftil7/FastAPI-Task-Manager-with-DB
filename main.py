from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .database import engine, Base, get_db

# create the db tables.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager with DB")


@app.post("/tasks", response_model=schemas.Task, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)  # get auto-generated ID
    return db_task


@app.get("/tasks", response_model=List[schemas.Task])
def list_task(db: Session = Depends(get_db)):
    return db.query(models.Task).all()
