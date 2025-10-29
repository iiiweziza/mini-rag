from .BaseController import BaseController
from models.db_schemes import User
from models.UserModel import UserModel
from fastapi import HTTPException, status
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class UserController(BaseController):
    def __init__(self):
        super().__init__()

    async def create_user(self, db_client, username: str, email: str, password: str, is_superuser: bool = False) -> User:
        logger.debug(f"Starting user creation: username={username}, email={email}")
        
        try:
            # Check if user already exists
            logger.debug("Creating user model instance")
            user_model = await UserModel.create_instance(db_client)
            logger.debug("Checking for existing username")
            
            existing_user = await user_model.get_user_by_username(username)
            logger.debug(f"Existing username check result: {existing_user}")
            
            if existing_user:
                logger.debug("Username already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            
            logger.debug("Checking for existing email")
            existing_email = await user_model.get_user_by_email(email)
            logger.debug(f"Existing email check result: {existing_email}")
            
            if existing_email:
                logger.debug("Email already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # Create new user (password truncation handled in User.hash_password)
            logger.debug("Hashing password")
            try:
                hashed_password = User.hash_password(password)
                logger.debug("Password hashed successfully")
            except Exception as e:
                logger.error(f"Password hashing error in UserController: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Password processing failed: {str(e)}"
                )
                
            logger.debug("Creating user object")
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                is_superuser=is_superuser
            )
            logger.debug("User object created")
            
            logger.debug("Saving user to database")
            created_user = await user_model.create_user(user)
            logger.debug(f"User saved with ID: {created_user.user_id}")
            
            return created_user
        except HTTPException:
            logger.debug("HTTP exception caught, re-raising")
            raise
        except Exception as e:
            logger.error(f"User creation error in UserController: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed"
            )

    async def authenticate_user(self, db_client, username: str, password: str) -> Optional[User]:
        logger.debug(f"Starting user authentication: username={username}")
        
        try:
            logger.debug("Creating user model instance")
            user_model = await UserModel.create_instance(db_client)
            
            # First try to find by username
            logger.debug("Looking up user by username")
            user = await user_model.get_user_by_username(username)
            
            # If not found, try to find by email
            if not user:
                logger.debug("User not found by username, trying email")
                user = await user_model.get_user_by_email(username)
            
            logger.debug(f"User lookup result: {user}")
            
            if not user:
                logger.debug("User not found")
                return None
                
            logger.debug("Verifying password")
            try:
                if not user.verify_password(password):
                    logger.debug("Password verification failed")
                    return None
            except Exception as e:
                logger.error(f"Password verification error in UserController: {e}")
                return None
                
            logger.debug("Authentication successful")
            return user
        except Exception as e:
            logger.error(f"User authentication error in UserController: {e}")
            return None