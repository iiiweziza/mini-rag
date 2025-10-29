from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum
from sqlalchemy.future import select
from sqlalchemy import func

class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance

    async def create_project(self, project: Project):
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)
        
        return project

    async def get_project_or_create_one(self, project_id: str, user_id: int = None):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Project).where(Project.project_id == project_id)
                result = await session.execute(query)
                project = result.scalar_one_or_none()
                if project is None:
                    project_rec = Project(
                        project_id = project_id,
                        user_id = user_id  # Associate project with user if provided
                    )

                    project = await self.create_project(project=project_rec)
                    return project
                else:
                    return project

    async def get_all_projects(self, page: int=1, page_size: int=10, user_id: int = None):

        async with self.db_client() as session:
            async with session.begin():
                # If user_id is provided, filter projects by user
                query = select(Project)
                if user_id:
                    query = query.where(Project.user_id == user_id)
                
                total_documents_query = select(func.count(Project.project_id))
                if user_id:
                    total_documents_query = total_documents_query.where(Project.user_id == user_id)
                    
                total_documents = await session.execute(total_documents_query)
                total_documents = total_documents.scalar_one()

                total_pages = total_documents // page_size
                if total_documents % page_size > 0:
                    total_pages += 1

                query = query.offset((page - 1) * page_size).limit(page_size)
                projects = await session.execute(query).scalars().all()

                return projects, total_pages

    async def get_user_projects(self, user_id: int):
        async with self.db_client() as session:
            stmt = select(Project).where(Project.user_id == user_id)
            result = await session.execute(stmt)
            projects = result.scalars().all()
        return projects