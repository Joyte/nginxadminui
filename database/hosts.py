from . import Base, get_db, Session, engine
from sqlalchemy import Integer, Date, Column, Boolean, Text, String, TIMESTAMP


class Data(Base):
    __tablename__ = "data"

    id = Column(String(30), primary_key=True, index=True)
    bool = Column(Boolean)
    text = Column(Text)


class Logs(Base):
    __tablename__ = "logs"

    id = Column(TIMESTAMP, primary_key=True, index=True)
    importance = Column(Integer, index=True)
    value = Column(Text)


Base.metadata.create_all(engine)  # type: ignore
