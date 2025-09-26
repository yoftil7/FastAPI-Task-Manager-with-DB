from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./tasks.db"

# create engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)  # sqlite only

# session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class for out models.
Base = declarative_base()


# dependency for fastapi
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
