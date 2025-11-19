from sqlalchemy import Column, Integer, String
from app.database import Base

class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    categories = Column(String, nullable=False)   # comma-separated
