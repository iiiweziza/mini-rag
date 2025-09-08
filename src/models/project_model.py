from operator import index
from .enums.database_enum import DatabaseEnumType
from .base_data_model import BaseDataModel
from .db_schemes import Project
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

  
       #now we want to inser the database but with the schema
    async def create_project(self, project: Project):
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)
        
        return project

    
    async def get_project_or_create_one(self, project_id: str):
        async with self.db_client() as session:
            # Convert project_id to integer for comparison with the database column
            project_id_int = None
            try:
                project_id_int = int(project_id)
            except ValueError:
                # If conversion fails, create a new project with an auto-generated ID
                # But first check if there are any existing projects to avoid creating multiple
                query = select(func.count(Project.project_id))
                result = await session.execute(query)
                project_count = result.scalar_one()
                
                if project_count > 0:
                    # Get the first project if one already exists
                    query = select(Project)
                    result = await session.execute(query)
                    project = result.scalars().first()
                    return project
                else:
                    # Create a new project with auto-generated ID if no projects exist
                    project_rec = Project()
                    project = await self.create_project(project=project_rec)
                    return project
                
            # First check if project already exists
            query = select(Project).where(Project.project_id == project_id_int)
            result = await session.execute(query)
            project = result.scalar_one_or_none()
            
            if project is None:
                # Try to create a project with the specified ID
                project_rec = Project(project_id=project_id_int)
                try:
                    project = await self.create_project(project=project_rec)
                except Exception as e:
                    # If there's an integrity error (duplicate key), fetch the existing project
                    if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                        # Fetch the existing project with this ID
                        result = await session.execute(query)
                        project = result.scalar_one_or_none()
                        if project is None:
                            # If still None, get any existing project to avoid creating multiple
                            query = select(Project)
                            result = await session.execute(query)
                            project = result.scalars().first()
                            if project is None:
                                # This shouldn't happen, but as a fallback create with auto-generated ID
                                project_rec = Project()
                                project = await self.create_project(project=project_rec)
                    else:
                        # Re-raise if it's a different error
                        raise
            return project
    async def get_all_projects(self, page: int=1, page_size: int=10):

        async with self.db_client() as session:
            async with session.begin():

                total_documents = await session.execute(select(
                    func.count( Project.project_id )
                ))

                total_documents = total_documents.scalar_one()

                total_pages = total_documents // page_size
                if total_documents % page_size > 0:
                    total_pages += 1

                query = select(Project).offset((page - 1) * page_size ).limit(page_size)
                projects = await session.execute(query).scalars().all()

                return projects, total_pages