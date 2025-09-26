from .database import Base


def init_db(engine):
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
