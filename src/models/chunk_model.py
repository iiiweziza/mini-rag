from .enums.database_enum import DatabaseEnumType
from .base_data_model import BaseDataModel
from .db_schemes.data_chunk import DataChunk
from bson.objectid import ObjectId
from pymongo import InsertOne
from operator import index

class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        # connect with collection of the db_client 
        self.collection = self.db_client[DatabaseEnumType.COLLECTION_CHUNKS_NAME.value]

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
        if DatabaseEnumType.COLLECTION_CHUNKS_NAME.value not in all_collections:
            # if the collection is not exist we will create it
            self.collection = self.db_client[DatabaseEnumType.COLLECTION_CHUNKS_NAME.value]
            # create the collection with the indexes from the project schema
            indexes = DataChunk.get_indexes()  # get the indexes from the chunk schema
            for index in indexes:
                 await self.collection.create_index(
                     index["key"],
                     name=index.get("name"),
                     unique=index.get("unique", False)
                    )

    async def insert_chunk(self, chunk: DataChunk):
        """
        Inserts a DataChunk into the database.
        """
        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))  # Convert DataChunk to dict and insert it
        chunk._id = result.inserted_id
        return chunk
    
    async def get_chunk_by_id(self, chunk_id: str):
        """
        Retrieves a DataChunk by its ID.
        """
        record = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        
    async def count_project_chunks(self, project_id: str):
        """
        Count the number of chunks for a given project.
        """
        return await self.collection.count_documents({"project_id": project_id})
        
    async def get_collection_info(self):
        """
        Get information about the chunks collection.
        """
        stats = await self.db_client.command("collstats", DatabaseEnumType.COLLECTION_CHUNKS_NAME.value)
        return {
            "count": stats.get("count", 0),
            "size": stats.get("size", 0),
            "avgObjSize": stats.get("avgObjSize", 0)
        }
        
    async def get_project_chunks_bulk(self, project_id: str, limit: int = 1000):
        """
        Get all chunks for a project in one query with a limit.
        Uses the string project_id, not MongoDB's _id.
        """
        print(f"Fetching chunks for project_id: {project_id}")
        try:
            cursor = self.collection.find({"project_id": project_id}).limit(limit)
            chunks = await cursor.to_list(length=limit)
            total_chunks = len(chunks)
            print(f"Found {total_chunks} chunks for project {project_id}")
            if chunks:
                print(f"Sample chunk content: {chunks[0].get('content', '')[:100]}")
            return [DataChunk(**chunk) for chunk in chunks]
        except Exception as e:
            print(f"Error getting project chunks: {str(e)}")
            return []

    async def insert_many_chunks(self, chunks: list[DataChunk], batch_size: int = 100):
        """
        Inserts multiple DataChunks into the database.
        """
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            records = [
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]           #take every batch of chunks and convert them to InsertOne objects and Insert them in the db
            await self.collection.bulk_write(records) # bulk_write is used to insert many documents at once
        return len(chunks)    

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        """
        Deletes all chunks associated with a specific project ID.
        """
        result = await self.collection.delete_many(
            {"project_id":project_id}
        )
        return result.deleted_count  # Returns the number of deleted documents
    
    async def get_all_project_chunks(self, project_id: ObjectId, page_no: int = 1, page_size: int = 50):
        """
        Retrieves all chunks associated with a specific project ID.
        page_size refers to the maximum number of chunk records returned per page when retrieving chunks for a specific project.
        """
        try:
            # Add debug logging
            print(f"Searching for chunks with project_id: {project_id}")
            
            # Use the correct field name from the schema
            query = {"project_id": str(project_id)}  # Convert ObjectId to string as per schema
            records = await self.collection.find(query).skip(
                (page_no - 1) * page_size).limit(page_size).to_list(length=None)

            print(f"Found {len(records)} records")
            if records:
                print(f"Sample record: {records[0]}")
            
            return [DataChunk(**record) for record in records]
        except Exception as e:
            print(f"Error in get_all_project_chunks: {str(e)}")
            return []