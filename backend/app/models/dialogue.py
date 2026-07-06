from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Dialogue(Base):
    __tablename__ = "dialogues"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, default="")
    is_valid = Column(Boolean, default=True)
    rule = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
