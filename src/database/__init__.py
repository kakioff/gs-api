from sqlmodel import create_engine, Session
from config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url)


def get_db():
    db = Session(engine)
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()