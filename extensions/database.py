from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
import socket
import time
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy import Integer, Column, Boolean, Text, String

DATABASE_URL = "mysql+pymysql://nginxadminui:cuzw2pKMsEjmeuLb@db/main_db"
LOCAL_DATABASE_URL = "mysql+pymysql://nginxadminui:cuzw2pKMsEjmeuLb@localhost/main_db"


# Test the database connection using socket
def test_db_connection():
    try:
        with socket.create_connection(("db", 3306), timeout=5):
            return True
    except socket.gaierror:
        return False


engine = create_engine(DATABASE_URL if test_db_connection() else LOCAL_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base: DeclarativeMeta = declarative_base()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Data(Base):
    __tablename__ = "data"

    id = Column(String(30), primary_key=True, index=True)
    is_active = Column(Boolean)
    text = Column(Text)


class Logs(Base):
    __tablename__ = "logs"

    id = Column(
        String(20),
        primary_key=True,
        index=True,
        default=lambda: int(time.time() * 1000),
    )
    importance = Column(Integer, index=True)
    value = Column(Text)


Base.metadata.create_all(engine)  # type: ignore
