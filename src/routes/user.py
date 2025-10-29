from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from routes.schemes.user import UserCreate, UserLogin, UserResponse, ProjectResponse, Token, TokenRefresh
from controllers.UserController import UserController
from controllers.ProjectController import ProjectController
from models.db_schemes import User, Project
from models.UserModel import UserModel
from models.ProjectModel import ProjectModel
from helpers.config import get_settings, Settings
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

user_router = APIRouter(
    prefix="/api/v1/user",
    tags=["api_v1", "user"],
)

def get_rsa_keys():
    settings = get_settings()
    
    logger.debug("Reading RSA keys from paths")
    logger.debug(f"Private key path: {settings.JWT_PRIVATE_KEY_PATH}")
    logger.debug(f"Public key path: {settings.JWT_PUBLIC_KEY_PATH}")
    
    # Read private key
    with open(settings.JWT_PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()
    
    # Read public key
    with open(settings.JWT_PUBLIC_KEY_PATH, "r") as f:
        public_key = f.read()
        
    logger.debug("Successfully read RSA keys")
    return private_key, public_key

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    settings = get_settings()
    logger.debug("Creating access token")
    
    try:
        private_key, public_key = get_rsa_keys()
    except Exception as e:
        logger.error(f"Failed to read RSA keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not read RSA keys in access token creation"
        )
    
    to_encode = data.copy()
    logger.debug(f"Data to encode: {to_encode}")
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    logger.debug(f"Data with expiration: {to_encode}")
    
    try:
        encoded_jwt = jwt.encode(to_encode, private_key, algorithm=settings.JWT_ALGORITHM)
        logger.debug("Successfully created access token")
        return encoded_jwt
    except Exception as e:
        logger.error(f"JWT encoding error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token"
        )

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    settings = get_settings()
    logger.debug("Creating refresh token")
    
    try:
        private_key, public_key = get_rsa_keys()
    except Exception as e:
        logger.error(f"Failed to read RSA keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not read RSA keys in refresh token creation"
        )
    
    to_encode = data.copy()
    logger.debug(f"Data to encode: {to_encode}")
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    logger.debug(f"Data with expiration: {to_encode}")
    
    try:
        encoded_jwt = jwt.encode(to_encode, private_key, algorithm=settings.JWT_ALGORITHM)
        logger.debug("Successfully created refresh token")
        return encoded_jwt
    except Exception as e:
        logger.error(f"JWT encoding error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create refresh token"
        )

@user_router.post("/register", response_model=dict)
async def register_user(user_data: UserCreate, request: Request):
    logger.debug("=== STARTING USER REGISTRATION PROCESS ===")
    logger.debug(f"Raw user_data object: {user_data}")
    logger.debug(f"User data type: {type(user_data)}")
    
    # Deep inspection of the password field
    logger.debug("=== PASSWORD INSPECTION ===")
    logger.debug(f"Password attribute: {user_data.password}")
    logger.debug(f"Password type: {type(user_data.password)}")
    logger.debug(f"Password length: {len(user_data.password)}")
    logger.debug(f"Password repr: {repr(user_data.password)}")
    
    # CRITICAL: Validate password length before any processing
    if len(user_data.password.encode('utf-8')) > 72:
        logger.error(f"Password exceeds 72 bytes limit: {len(user_data.password.encode('utf-8'))} bytes")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is too long. Password must be 72 bytes or less when encoded in UTF-8."
        )
    logger.debug("Password length validation passed")
    
    # Check if it's actually a string or something else
    if not isinstance(user_data.password, str):
        logger.error(f"PASSWORD IS NOT A STRING! It's a {type(user_data.password)}")
        logger.error(f"Password value: {user_data.password}")
        # Try to convert it to string
        try:
            original_password = user_data.password
            user_data.password = str(user_data.password)
            logger.debug(f"Converted password from {type(original_password)} to string: {user_data.password}")
            logger.debug(f"New password length: {len(user_data.password)}")
        except Exception as e:
            logger.error(f"Failed to convert password to string: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password format"
            )
    
    logger.debug(f"Username: {user_data.name}")
    logger.debug(f"Email: {user_data.email}")
    logger.debug(f"Is superuser: {user_data.is_superuser}")
    
    user_controller = UserController()
    
    try:
        logger.debug("Checking if user already exists")
        # Check if user already exists
        user_model = await UserModel.create_instance(request.app.db_client)
        logger.debug("Created user model instance")
        
        existing_user = await user_model.get_user_by_email(user_data.email)
        logger.debug(f"Existing user check result: {existing_user}")
        
        if existing_user:
            logger.debug("User already exists, raising exception")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        logger.debug("Proceeding with user creation")
        # Create new user (password truncation handled in User.hash_password)
        try:
            logger.debug(f"About to hash password for user {user_data.email}")
            logger.debug(f"Password length: {len(user_data.password)}")
            logger.debug(f"Password type: {type(user_data.password)}")
            
            # Add one more check right before hashing
            logger.debug("=== FINAL PASSWORD CHECK BEFORE HASHING ===")
            logger.debug(f"Final password: {user_data.password}")
            logger.debug(f"Final password type: {type(user_data.password)}")
            logger.debug(f"Final password length: {len(user_data.password)}")
            logger.debug(f"Final password repr: {repr(user_data.password)}")
            
            # Let's also test with a direct import of the User model
            logger.debug("Testing direct import of User model")
            from models.db_schemes.minirag.schemes.user import User as DirectUser
            logger.debug(f"Direct User model imported: {DirectUser}")
            
            logger.debug("About to call DirectUser.hash_password")
            hashed_password = DirectUser.hash_password(user_data.password)
            logger.debug("Password hashed successfully")
        except Exception as e:
            logger.error(f"Password hashing error during registration: {e}")
            logger.error(f"Password value: {user_data.password}")
            logger.error(f"Password repr: {repr(user_data.password)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password processing failed: {str(e)}"
            )
            
        logger.debug("Creating user object")
        user = User(
            username=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=user_data.is_superuser
        )
        logger.debug("User object created")
        
        logger.debug("Saving user to database")
        created_user = await user_model.create_user(user)
        logger.debug(f"User saved to database with ID: {created_user.user_id}")
        
        # Create access and refresh tokens
        logger.debug("Creating access and refresh tokens")
        settings = get_settings()
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
        
        logger.debug("Creating access token")
        access_token = create_access_token(
            data={"sub": created_user.email, "user_id": created_user.user_id}, 
            expires_delta=access_token_expires
        )
        logger.debug("Access token created")
        
        logger.debug("Creating refresh token")
        refresh_token = create_refresh_token(
            data={"sub": created_user.email, "user_id": created_user.user_id}, 
            expires_delta=refresh_token_expires
        )
        logger.debug("Refresh token created")
        
        logger.debug("=== REGISTRATION PROCESS COMPLETED SUCCESSFULLY ===")
        return {
            "user_id": created_user.user_id,
            "username": created_user.username,
            "email": created_user.email,
            "is_active": created_user.is_active,
            "is_superuser": created_user.is_superuser,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        logger.debug("HTTP exception caught, re-raising")
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        logger.error(f"Registration error type: {type(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@user_router.post("/login", response_model=Token)
async def login_user(user_data: UserLogin, request: Request):
    logger.debug("Starting user login process")
    logger.debug(f"Login data: email={user_data.email}")
    
    settings = get_settings()
    user_controller = UserController()
    
    try:
        logger.debug("Authenticating user")
        user = await user_controller.authenticate_user(
            db_client=request.app.db_client,
            username=user_data.email,  # Using email as username for login
            password=user_data.password
        )
        logger.debug(f"Authentication result: {user}")
        
        if not user:
            logger.debug("Authentication failed, incorrect credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug("Creating access and refresh tokens")
        # Create access and refresh tokens
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
        
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.user_id}, 
            expires_delta=access_token_expires
        )
        logger.debug("Access token created")
        
        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.user_id}, 
            expires_delta=refresh_token_expires
        )
        logger.debug("Refresh token created")
        
        logger.debug("Login process completed successfully")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        logger.debug("HTTP exception caught, re-raising")
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        logger.error(f"Login error type: {type(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@user_router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(token_data: TokenRefresh, request: Request):
    logger.debug("Starting token refresh process")
    settings = get_settings()
    
    try:
        private_key, public_key = get_rsa_keys()
    except Exception as e:
        logger.error(f"Failed to read RSA keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not read RSA keys"
        )
    
    try:
        logger.debug("Decoding refresh token")
        payload = jwt.decode(token_data.refresh_token, public_key, algorithms=[settings.JWT_ALGORITHM])
        logger.debug(f"Token payload: {payload}")
        
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        token_type: str = payload.get("type")
        
        logger.debug(f"Token data - email: {email}, user_id: {user_id}, type: {token_type}")
        
        if email is None or user_id is None:
            logger.debug("Invalid token data")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if token_type != "refresh":
            logger.debug("Invalid token type")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug("Verifying user exists and is active")
        # Verify user still exists and is active
        user_model = await UserModel.create_instance(request.app.db_client)
        user = await user_model.get_user_by_email(email)
        logger.debug(f"User lookup result: {user}")
        
        if not user or not user.is_active:
            logger.debug("User not found or inactive")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug("Creating new access and refresh tokens")
        # Create new access and refresh tokens
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
        
        access_token = create_access_token(
            data={"sub": email, "user_id": user_id}, 
            expires_delta=access_token_expires
        )
        logger.debug("New access token created")
        
        refresh_token = create_refresh_token(
            data={"sub": email, "user_id": user_id}, 
            expires_delta=refresh_token_expires
        )
        logger.debug("New refresh token created")
        
        logger.debug("Token refresh process completed successfully")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except JWTError as e:
        logger.error(f"JWT error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        logger.debug("HTTP exception caught, re-raising")
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        logger.error(f"Token refresh error type: {type(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )