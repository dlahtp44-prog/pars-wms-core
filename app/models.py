from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Inbound(Base):
    __tablename__ = "inbounds"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String, index=True)
    item_name = Column(String)
    quantity = Column(Integer)
    location = Column(String, index=True)
