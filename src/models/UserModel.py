from .BaseDataModel import BaseDataModel
from models.db_schemes import User
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class UserModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client):
        instance = cls(db_client)
        return instance

    async def get_user_by_username(self, username: str) -> User:
        logger.debug(f"Getting user by username: {username}")
        try:
            async with self.db_client() as session:
                logger.debug("Creating select query for username")
                stmt = select(User).where(User.username == username)
                logger.debug(f"Executing query: {stmt}")
                result = await session.execute(stmt)
                logger.debug("Query executed")
                user = result.scalar_one_or_none()
                logger.debug(f"Query result: {user}")
                return user
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_user_by_username: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_user_by_username: {e}")
            return None

    async def get_user_by_email(self, email: str) -> User:
        logger.debug(f"Getting user by email: {email}")
        try:
            async with self.db_client() as session:
                logger.debug("Creating select query for email")
                stmt = select(User).where(User.email == email)
                logger.debug(f"Executing query: {stmt}")
                result = await session.execute(stmt)
                logger.debug("Query executed")
                user = result.scalar_one_or_none()
                logger.debug(f"Query result: {user}")
                return user
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_user_by_email: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_user_by_email: {e}")
            return None

    async def create_user(self, user: User) -> User:
        logger.debug(f"Creating user: username={user.username}, email={user.email}")
        try:
            async with self.db_client() as session:
                logger.debug("Adding user to session")
                session.add(user)
                logger.debug("Committing transaction")
                await session.commit()
                logger.debug("Refreshing user object")
                await session.refresh(user)
                logger.debug(f"User created successfully with ID: {user.user_id}")
                return user
        except SQLAlchemyError as e:
            logger.error(f"Database error in create_user: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in create_user: {e}")
            raise e