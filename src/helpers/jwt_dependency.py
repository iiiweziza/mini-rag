from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional
from helpers.config import get_settings
from models.db_schemes import User
from models import UserModel

security = HTTPBearer()

def get_rsa_public_key():
    settings = get_settings()
    
    # Read public key
    with open(settings.JWT_PUBLIC_KEY_PATH, "r") as f:
        public_key = f.read()
        
    return public_key

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_client=None
):
    settings = get_settings()
    public_key = get_rsa_public_key()
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            public_key, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # If db_client is provided, verify user exists and is active
        if db_client:
            user_model = await UserModel.create_instance(db_client)
            user = await user_model.get_user_by_email(email)
            
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return user
            
        # If no db_client, just return user info from token
        return {
            "email": email,
            "user_id": user_id
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )