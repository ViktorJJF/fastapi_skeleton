from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean

from app.models.Base import BaseModel


class Assistant(BaseModel):
    """
    Assistant model.
    """

    __tablename__ = "assistants"

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
