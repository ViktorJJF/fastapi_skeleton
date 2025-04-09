from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr
import inflect
import json

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
    
    def to_dict(self):
        """
        Convert model instance to dictionary with datetime serialization.
        """
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Convert datetime objects to ISO format
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
        return result
    
    def to_json(self):
        """
        Convert model instance to JSON string.
        """
        return json.dumps(self.to_dict()) 