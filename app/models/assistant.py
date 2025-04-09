from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Assistant(BaseModel):
    """
    Assistant model.
    """
    __tablename__ = "assistants"
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Relationships
    entities = relationship("Entity", back_populates="assistant", cascade="all, delete-orphan") 