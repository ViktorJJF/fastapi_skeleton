from sqlalchemy import Column, String

from app.models.base import BaseModel


class City(BaseModel):
    """
    City model for demonstration.
    """
    name = Column(String, unique=True, index=True, nullable=False)
    country = Column(String, nullable=False)
    description = Column(String, nullable=True) 