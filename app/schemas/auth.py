from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

# Schema for requesting a password reset
class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address to send reset instructions to")

# Schema for resetting the password
class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Password reset verification token")
    new_password: str = Field(..., min_length=6, description="New password (min 6 characters)")

# Schema for user login
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

# Schema for verifying email
class VerifyEmailRequest(BaseModel):
    token: str = Field(..., description="Email verification token")

# Schema for the response after successful login or token refresh
class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type (usually bearer)")

# Schema for the payload within the JWT access token
class TokenPayload(BaseModel):
    sub: str # Subject (usually user ID or email)
    exp: Optional[int] = None
    user_id: UUID
    role: str
    email: EmailStr
    # Add other relevant claims like iat (issued at), etc.

# Schema for user verification status
class VerificationResponse(BaseModel):
    email: EmailStr
    verified: bool 