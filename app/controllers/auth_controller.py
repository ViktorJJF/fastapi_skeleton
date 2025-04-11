from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
import uuid

from app.db.session import get_db
from app.models.user import User
from app.models.auth import ForgotPassword, UserAccess
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    VerificationResponse
)
from app.schemas.user import UserCreate, User as UserSchema, UserInToken
from app.utils.security import verify_password, create_access_token, get_password_hash
from app.utils.error_handling import handle_error, build_error_object
from app.core.config import config
# Assume email utilities are in app.utils.email (needs to be created)
# from app.utils.email import send_registration_email, send_reset_password_email
# Assume request info utilities are in app.utils.request_info (needs to be created)
# from app.utils.request_info import get_ip, get_browser_info, get_country

# --- Helper Functions (similar to NodeJS private functions) --- 

async def _find_user_by_email(email: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def _find_user_by_id(user_id: uuid.UUID, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def _find_user_by_verification_token(token: str, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).filter(User.verification_token == token))
    return result.scalars().first()

async def _find_forgot_password_request(token: str, db: AsyncSession) -> ForgotPassword | None:
    result = await db.execute(
        select(ForgotPassword)
        .filter(ForgotPassword.verification_token == token)
        .filter(ForgotPassword.used == False)
        .filter(ForgotPassword.expires_at > datetime.utcnow())
    )
    return result.scalars().first()

async def _save_user_access(request: Request, user: User, db: AsyncSession):
    try:
        # Placeholder for request info extraction - replace with actual implementation
        ip = "unknown" # get_ip(request)
        browser = "unknown" # get_browser_info(request)
        country = "unknown" # get_country(request)
        
        access_log = UserAccess(
            email=user.email,
            ip=ip,
            browser=browser,
            country=country
        )
        db.add(access_log)
        await db.commit()
    except Exception as e:
        # Log error but don't fail the login/registration
        print(f"Error saving user access log: {e}") 
        await db.rollback() # Rollback UserAccess save if it fails

async def _check_login_attempts(user: User, db: AsyncSession):
    now = datetime.utcnow()
    if user.block_expires and user.block_expires > now:
        raise build_error_object(status.HTTP_409_CONFLICT, "User account is temporarily blocked due to too many failed login attempts.")

    if user.block_expires and user.block_expires <= now:
        # Block expired, reset attempts
        user.login_attempts = 0
        user.block_expires = None
        await db.commit()

async def _handle_failed_login(user: User, db: AsyncSession):
    user.login_attempts += 1
    if user.login_attempts >= config.LOGIN_ATTEMPTS_LIMIT:
        user.block_expires = datetime.utcnow() + timedelta(hours=config.BLOCK_HOURS)
        await db.commit()
        raise build_error_object(status.HTTP_409_CONFLICT, "Incorrect email or password. Account blocked due to too many attempts.")
    else:
        await db.commit()
        raise build_error_object(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password.")

# --- Controller Endpoints --- 

async def register(user_in: UserCreate, request: Request, db: AsyncSession) -> dict:
    """Registers a new user."""
    try:
        existing_user = await _find_user_by_email(user_in.email, db)
        if existing_user:
            raise build_error_object(status.HTTP_400_BAD_REQUEST, "Email already registered")

        hashed_password = get_password_hash(user_in.password)
        verification_token = uuid.uuid4().hex # Generate verification token
        
        db_user = User(
            name=user_in.name,
            email=user_in.email,
            hashed_password=hashed_password,
            role=user_in.role or "SUPERADMIN",
            verification_token=verification_token, # Save token
            verified=False # Start as unverified
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        # Send verification email (Placeholder)
        # await send_registration_email(db_user.email, verification_token)

        # Prepare response payload dictionary
        response_user = UserSchema.model_validate(db_user)
        response_payload_data = {"user": response_user.model_dump()}
        if config.DEBUG: # Include verification token only in debug/dev
            response_payload_data["verification_token"] = verification_token
        
        # Return dictionary for FastAPI to serialize based on response_model
        return {"ok": True, "payload": response_payload_data}

    except Exception as e:
        await db.rollback()
        # Re-raise the exception for the global error handler or handle it
        # If handle_error returns a JSONResponse, this function signature needs adjustment
        # For simplicity, let's re-raise for now, assuming a global handler exists
        # or adapt handle_error to return a dict or raise HTTPExceptions
        # return await handle_error(request, e) # If handle_error returns JSONResponse
        raise e # Re-raise for global handler

async def login(login_data: LoginRequest, request: Request, db: AsyncSession) -> dict:
    """Logs in a user and returns an access token dictionary."""
    try:
        user = await _find_user_by_email(login_data.email, db)
        if not user:
            raise build_error_object(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password.")

        await _check_login_attempts(user, db)
        
        if not verify_password(login_data.password, user.hashed_password):
            await _handle_failed_login(user, db)
            # _handle_failed_login raises exception, so this part won't be reached if failed

        # Temporarily bypass email verification check
        # if not user.verified:
        #      raise build_error_object(status.HTTP_403_FORBIDDEN, "Email not verified. Please check your email.")

        # Reset login attempts on successful login
        user.login_attempts = 0
        user.block_expires = None
        await db.commit()
        await db.refresh(user)

        # Log access (optional)
        await _save_user_access(request, user, db)
        
        # Create token payload
        user_token_data = UserInToken(id=user.id, role=user.role, email=user.email)
        access_token = create_access_token(user=user_token_data)
        
        # Prepare payload dictionary matching TokenResponse schema
        token_payload = TokenResponse(access_token=access_token).model_dump()
        
        # Return dictionary matching ApiResponse structure
        return {"ok": True, "payload": token_payload}

    except Exception as e:
        await db.rollback() # Rollback potential changes in _check_login_attempts or _handle_failed_login
        # Re-raise for global handler (or adapt handle_error)
        # return await handle_error(request, e) 
        raise e

async def verify_email(verify_data: VerifyEmailRequest, request: Request, db: AsyncSession) -> JSONResponse:
    """Verifies a user's email address using a token."""
    try:
        user = await _find_user_by_verification_token(verify_data.token, db)
        if not user:
             raise build_error_object(status.HTTP_404_NOT_FOUND, "Invalid or expired verification token.")
        
        if user.verified:
             raise build_error_object(status.HTTP_400_BAD_REQUEST, "Email already verified.")

        user.verified = True
        user.verification_token = None # Clear token after use
        await db.commit()
        await db.refresh(user)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "payload": VerificationResponse(email=user.email, verified=True).model_dump()}
        )

    except Exception as e:
        await db.rollback()
        return await handle_error(request, e)

async def forgot_password(forgot_data: ForgotPasswordRequest, request: Request, db: AsyncSession) -> JSONResponse:
    """Initiates the password reset process."""
    try:
        user = await _find_user_by_email(forgot_data.email, db)
        if not user:
             # Still return OK to prevent email enumeration attacks
            print(f"Password reset requested for non-existent email: {forgot_data.email}")
            return JSONResponse(status_code=status.HTTP_200_OK, content={"ok": True, "message": "If an account with that email exists, a password reset link has been sent."}) 

        reset_token = uuid.uuid4().hex
        expires = datetime.utcnow() + timedelta(hours=config.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
        
        # Placeholder for request info
        ip = "unknown" # get_ip(request)
        browser = "unknown" # get_browser_info(request)
        country = "unknown" # get_country(request)
        
        forgot_req = ForgotPassword(
            email=user.email,
            verification_token=reset_token,
            expires_at=expires,
            ip_request=ip,
            browser_request=browser,
            country_request=country
        )
        db.add(forgot_req)
        await db.commit()

        # Send password reset email (Placeholder)
        # await send_reset_password_email(user.email, reset_token)
        
        response_payload = {"message": "Password reset email sent.", "email": user.email}
        if config.DEBUG:
             response_payload["reset_token"] = reset_token # Expose token only in debug/dev

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "payload": response_payload}
        )

    except Exception as e:
        await db.rollback()
        return await handle_error(request, e)

async def reset_password(reset_data: ResetPasswordRequest, request: Request, db: AsyncSession) -> JSONResponse:
    """Resets the user's password using a token."""
    try:
        forgot_req = await _find_forgot_password_request(reset_data.token, db)
        if not forgot_req:
             raise build_error_object(status.HTTP_404_NOT_FOUND, "Invalid or expired password reset token.")

        user = await _find_user_by_email(forgot_req.email, db)
        if not user:
             # Should not happen if forgot_req exists, but check anyway
             raise build_error_object(status.HTTP_404_NOT_FOUND, "User associated with token not found.")

        # Update password
        user.hashed_password = get_password_hash(reset_data.new_password)
        # Invalidate the token
        forgot_req.used = True
        forgot_req.ip_changed = "unknown" # get_ip(request)
        forgot_req.browser_changed = "unknown" # get_browser_info(request)
        forgot_req.country_changed = "unknown" # get_country(request)
        
        # Reset login attempts and block status as password is reset
        user.login_attempts = 0
        user.block_expires = None
        
        await db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True, "message": "Password has been reset successfully."}
        )

    except Exception as e:
        await db.rollback()
        return await handle_error(request, e)

# Placeholder for get_refresh_token if implementing refresh tokens
# async def get_refresh_token(request: Request, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> JSONResponse:
#     pass 