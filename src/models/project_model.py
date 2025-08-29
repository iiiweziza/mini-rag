from operator import index
from .enums.database_enum import DatabaseEnumType
from .base_data_model import BaseDataModel
from .db_schemes.project import Project

class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        # connect with collection of the db_client 
        self.collection = self.db_client[DatabaseEnumType.COLLECTION_PROJECT_NAME.value]  
       
    # to put init and init_collection in one place becouse one is async and the other is not

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.init_collection()  # Ensure the collection is initialized
        return instance

    async def init_collection(self):
        """
        Initialize the collection by creating indexes based on the Project schema.
        This method is called to ensure that the collection is ready for use.
        """
        all_collections = await self.db_client.list_collection_names()
        if DatabaseEnumType.COLLECTION_PROJECT_NAME.value not in all_collections:
            # if the collection is not exist we will create it
            self.collection = self.db_client[DatabaseEnumType.COLLECTION_PROJECT_NAME.value]
            # create the collection with the indexes from the project schema
            indexes = Project.get_indexes()  # get the indexes from the project schema
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

       #now we want to inser the database but with the schema
    async def insert_project(self,project: Project):
        # we will use the insert_one method to insert the project in the collection
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True)) # to appeare with alies name 
        #insert with project schema and convert it to dict to can insert in the db
        project.id = result.inserted_id
        return project    
    
    async def get_project_or_create_one(self, project_id : str):  # project_id => the uploading id 
        #get project by id form collection
        record = await self.collection.find_one({"project_id":project_id})
        if record is None:
            # if the project is not found we will create a new one
            project = Project(project_id=project_id)
            await self.insert_project(project)
            return project
        return Project(**record)  # convert the record to a project object it was a dict
    
    async def get_all_projects(self, page :int=1,page_size:int=10):
        """
        Comments:
            - Counts the total number of documents in the collection to determine pagination.
            - Calculates the total number of pages based on the page size.
            - Retrieves the appropriate subset of documents for the requested page using skip and limit.
            - Converts each document into a Project instance and appends it to the projects list.
            - Returns the list of projects and the total number of pages.
        """
        total_documents = await self.collection.count_documents({})
        total_pages = (total_documents // page_size) 
        if total_documents % page_size > 0:
            total_pages += 1

        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)
        projects = []    
        async for document in cursor:
            projects.append(Project(**document))

        return projects,total_pages