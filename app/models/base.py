from datetime import datetime, date
from typing import Optional
import inflect
import json

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Integer

# Initialize inflect engine for pluralization
p = inflect.engine()


class BaseModel(DeclarativeBase):
    """
    Base model for all database models.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    @classmethod
    def __tablename__(cls) -> str:
        """
        Generate __tablename__ automatically from class name, using plural form.
        """
        return p.plural(cls.__name__.lower())

    def to_dict(self):
        """
        Convert model instance to dictionary with datetime and date serialization.
        """
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Convert datetime and date objects to ISO format
        for key, value in result.items():
            if isinstance(value, (datetime, date)):
                result[key] = value.isoformat()
        return result

    def to_json(self):
        """
        Convert model instance to JSON string.
        """
        return json.dumps(self.to_dict())
