from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database.connection import Base

class ForgotPassword(Base):
    __tablename__ = "forgot_passwords"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, index=True)
    verification_token = Column(String, unique=True, index=True, nullable=False)
    used = Column(Boolean(), default=False)
    ip_request = Column(String, nullable=True)
    browser_request = Column(String, nullable=True)
    country_request = Column(String, nullable=True)
    ip_changed = Column(String, nullable=True)
    browser_changed = Column(String, nullable=True)
    country_changed = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False) # Add expiration for security

    # Optional: Link to user table if needed
    # user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

class UserAccess(Base):
    __tablename__ = "user_access"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, index=True)
    ip = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    country = Column(String, nullable=True)
    access_time = Column(DateTime(timezone=True), server_default=func.now())

    # Optional: Link to user table
    # user_id = Column(UUID(as_uuid=True), ForeignKey("users.id")) 