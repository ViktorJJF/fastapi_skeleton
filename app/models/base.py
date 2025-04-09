from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr
import inflect

from app.database.connection import Base

# Initialize inflect engine for pluralization
p = inflect.engine()


class BaseModel(Base):
    """
    Base model for all database models.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate __tablename__ automatically from class name, using plural form.
        """
        return p.plural(cls.__name__.lower()) 