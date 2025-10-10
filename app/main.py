from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
import logging

from contextlib import asynccontextmanager
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session
from typing import List, Optional

from . import models, schemas
from .dependencies import pagination_params, sorting_params, filtering_params
from .database import engine, get_db, Base
from .security import hash_password, verify_password
from jose import jwt, JWTError
from .auth import (
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    get_current_user,
    get_current_admin,
    SECRET_KEY,
    ALGORITHM,
)

logger = logging.getLogger(__name__)


# Define the lifespan async context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        redis_connection = redis.from_url(
            "redis://localhost", encoding="utf-8", decode_responses=True
        )
        await FastAPILimiter.init(redis_connection)
        logger.info("✅ Redis rate limiter initialized successfully.")
    except Exception as e:
        logger.warning(f"⚠️ Skipping Redis initialization: {e}")
        redis_connection = None
    yield
    if redis_connection:
        await redis_connection.aclose()
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
@app.post("/login", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
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
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id: int = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = (
        db.execute(select(models.User).where(models.User.id == user_id))
        .scalars()
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": new_access_token, "token_type": "bearer"}


@app.get("/admin/users", response_model=List[schemas.UserOut])
def list_users(
    current_admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return db.execute(select(models.User)).unique().scalars().all()


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


@app.get("/tasks", response_model=schemas.PaginatedResponse[schemas.Task])
def list_tasks(
    filters: dict = Depends(filtering_params),
    sorting: dict = Depends(sorting_params),
    pagination: dict = Depends(pagination_params),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skip, limit = pagination["skip"], pagination["limit"]

    # Base query (only user’s tasks)
    query = select(models.Task).where(models.Task.owner_id == current_user.id)

    # ✅ Apply filters
    if "completed" in filters:
        query = query.where(models.Task.completed == filters["completed"])
    if "priority" in filters:
        query = query.where(models.Task.priority == filters["priority"])
    if "title" in filters:
        query = query.where(models.Task.title.ilike(f"%{filters['title']}%"))

    # ✅ Count total (for pagination metadata)
    total = db.scalar(select(func.count()).select_from(query.subquery()))

    # ✅ Apply sorting
    sort_column = getattr(models.Task, sorting["sort_by"])
    if sorting["order"] == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # ✅ Apply pagination
    tasks = db.execute(query.offset(skip).limit(limit)).scalars().all()

    return schemas.PaginatedResponse(
        total=total,
        skip=skip,
        limit=limit,
        data=tasks,
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


@app.post(
    "/password-reset/request", dependencies=[Depends(RateLimiter(times=3, seconds=600))]
)
def request_password_reset(email: str, db: Session = Depends(get_db)):
    user = (
        db.execute(select(models.User).where(models.User.email == email))
        .scalars()
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reset_token = create_password_reset_token({"sub": str(user.id)})
    reset_link = f"http://localhost:8000/reset-password?token={reset_token}"
    print(f"Password reset link: {reset_link}")
    return {"message": "Password reset link sent"}


@app.post("/password-reset/confirm")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = (
        db.execute(select(models.User).where(models.User.id == user_id))
        .scalars()
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = hash_password(new_password)
    db.commit()
    return {"message": "Password has been reset successfully"}
