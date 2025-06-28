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
            await self.collection.create_indexes(
                index["key"],
                name = index["name"],
                unique = index["unique"]
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
        if record is None:
            return None
        return DataChunk(**record)

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