from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from passlib.context import CryptContext
from sqlalchemy.orm import relationship
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Setup logging to catch passlib warnings
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

# Create a robust password hashing context (avoid bcrypt backend issues)
try:
    logger.debug("Initializing pwd_context with pbkdf2_sha256")
    pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        deprecated="auto"
    )
    logger.debug("pwd_context created successfully")
    logger.debug(f"pwd_context schemes: {pwd_context.schemes()}")
except Exception as e:
    logger.error(f"Failed to create pwd_context: {e}")
    raise

class User(SQLAlchemyBase):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    projects = relationship("Project", back_populates="user")

    def verify_password(self, plain_password: str) -> bool:
        logger.debug("=== ENTERING verify_password METHOD ===")
        logger.debug(f"Input password type: {type(plain_password)}")
        logger.debug(f"Input password value: '{plain_password}'")
        logger.debug(f"Input password length: {len(str(plain_password)) if plain_password else 0}")
        logger.debug(f"Input password repr: {repr(plain_password)}")
        
        try:
            # Ensure we're working with a string
            if not isinstance(plain_password, str):
                plain_password = str(plain_password)
                logger.debug("Converted password to string")
                
            # Truncate password to 72 bytes if necessary - this is critical for bcrypt
            password_bytes = plain_password.encode('utf-8')
            logger.debug(f"Password bytes length: {len(password_bytes)}")
            
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
                plain_password = password_bytes.decode('utf-8', errors='ignore')
                logger.debug("Password truncated to 72 bytes")
            else:
                logger.debug("Password is within 72 bytes limit, no truncation needed")
                
            logger.debug(f"Final password for verification: '{plain_password}'")
            logger.debug(f"Final password length: {len(plain_password)}")
            logger.debug(f"Final password repr: {repr(plain_password)}")
            logger.debug("Calling pwd_context.verify")
            result = pwd_context.verify(plain_password, self.hashed_password)
            logger.debug(f"Password verification result: {result}")
            logger.debug("=== EXITING verify_password METHOD ===")
            return result
        except Exception as e:
            # Log the error but don't expose it to the user
            logger.error(f"Password verification error: {e}")
            logger.error(f"Password value at time of error: {plain_password}")
            logger.error(f"Password repr at time of error: {repr(plain_password)}")
            return False

    @staticmethod
    def hash_password(password: str) -> str:
        logger.debug("Starting password hashing")
        logger.debug(f"Input password type: {type(password)}")
        logger.debug(f"Input password value: '{password}'")
        logger.debug(f"Input password length: {len(str(password)) if password else 0}")
        logger.debug(f"Input password repr: {repr(password)}")
        
        try:
            # Ensure we're working with a string
            if not isinstance(password, str):
                password = str(password)
                logger.debug("Converted password to string")
                
            # Truncate password to 72 bytes if necessary
            password_bytes = password.encode('utf-8')
            logger.debug(f"Password bytes length: {len(password_bytes)}")
            logger.debug(f"Password bytes: {password_bytes}")
            
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
                password = password_bytes.decode('utf-8', errors='ignore')
                logger.debug("Password truncated to 72 bytes")
            else:
                logger.debug("Password is within 72 bytes limit, no truncation needed")
            
            logger.debug(f"Final password for hashing: '{password}'")
            logger.debug(f"Final password length: {len(password)}")
            logger.debug(f"Final password repr: {repr(password)}")
            
            # Hash the password using configured context
            logger.debug("Calling pwd_context.hash")
            logger.debug(f"Passlib context schemes: {pwd_context.schemes()}")
            hashed = pwd_context.hash(password)
            logger.debug("Password hashed successfully")
            logger.debug(f"Hashed password length: {len(hashed) if hashed else 0}")
            return hashed
        except Exception as e:
            # Log the specific error
            logger.error(f"Password hashing error: {e}")
            logger.error(f"Password value at time of error: {password}")
            logger.error(f"Password repr at time of error: {repr(password)}")
            # Re-raise the exception so it can be handled upstream
            raise