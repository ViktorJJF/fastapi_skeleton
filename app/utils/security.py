import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Union, Any
import uuid

from jose import jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import config
from app.schemas.auth import TokenPayload
from app.schemas.user import UserInToken

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = config.ALGORITHM

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a hashed password."""
    # Use passlib's verify method
    # return pwd_context.verify(plain_password, hashed_password)
    # Or use bcrypt directly if User model uses bcrypt directly
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hashes a plain text password."""
    # Use passlib's hash method
    # return pwd_context.hash(password)
    # Or use bcrypt directly if User model uses bcrypt directly
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(user: UserInToken, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a JWT access token."""
    if expires_delta:
        expire_dt = datetime.utcnow() + expires_delta
    else:
        expire_dt = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire_timestamp = int(expire_dt.timestamp())

    # Create the initial payload using the Pydantic model
    token_payload_model = TokenPayload(
        sub=str(user.id), # Already string
        exp=expire_timestamp,
        user_id=user.id, # Still UUID here
        role=user.role,
        email=user.email
    )
    
    # Dump the model to a dictionary
    to_encode = token_payload_model.model_dump()
    
    # --- Explicitly convert UUID to string in the dictionary --- 
    if isinstance(to_encode.get('user_id'), uuid.UUID):
        to_encode['user_id'] = str(to_encode['user_id'])
    # ----------------------------------------------------------
    
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenPayload]:
    """Decodes a JWT access token."""
    try:
        payload = jwt.decode(
            token, config.SECRET_KEY, algorithms=[ALGORITHM]
        )
        # Validate payload structure using Pydantic model
        token_data = TokenPayload(**payload)
        
        # Optional: Check if token has expired (already done by jwt.decode often, but explicit check can be added)
        # if token_data.exp is not None and datetime.utcfromtimestamp(token_data.exp) < datetime.utcnow():
        #     return None # Token expired
        
        return token_data
    except (jwt.JWTError, jwt.ExpiredSignatureError, ValidationError) as e:
        print(f"Token decode error: {e}") # Log error
        return None # Token is invalid or expired 