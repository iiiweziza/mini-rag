from .enums.database_enum import DatabaseEnumType
from .base_data_model import BaseDataModel
from .db_schemes import DataChunk
from bson.objectid import ObjectId
from sqlalchemy.future import select
from sqlalchemy import func, delete

class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance

    async def create_chunk(self, chunk: DataChunk):

        async with self.db_client() as session:
            async with session.begin():
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
        return chunk

    async def get_chunk(self, chunk_id: str):

        async with self.db_client() as session:
            result = await session.execute(select(DataChunk).where(DataChunk.chunk_id == chunk_id))
            chunk = result.scalar_one_or_none()
        return chunk

    async def insert_many_chunks(self, chunks: list, batch_size: int=100):

        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i:i+batch_size]
                    session.add_all(batch)
            await session.commit()
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: int):
        async with self.db_client() as session:
            stmt = delete(DataChunk).where(DataChunk.chunk_project_id == project_id)
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount
    
    async def get_project_chunks(self, project_id: int, page_no: int=1, page_size: int=50):
        try:
            # Add debug logging
            print(f"Searching for chunks with project_id: {project_id}")
            async with self.db_client() as session:
                stmt = select(DataChunk).where(DataChunk.chunk_project_id == project_id).offset((page_no - 1) * page_size).limit(page_size)
                result = await session.execute(stmt)
                records = result.scalars().all()
            return records
        except Exception as e:
            print(f"Error in get_project_chunks: {str(e)}")
            return []

        ###
        
    async def count_project_chunks(self, project_id: int):
        """
        Count the number of chunks for a given project.
        """
        async with self.db_client() as session:
            result = await session.execute(
                select(func.count(DataChunk.chunk_id)).where(DataChunk.chunk_project_id == project_id)
            )
            count = result.scalar_one()
        return count
        
    async def get_collection_info(self):
        """
        Get information about the chunks collection/table.
        """
        async with self.db_client() as session:
            # Get total count
            count_result = await session.execute(select(func.count(DataChunk.chunk_id)))
            count = count_result.scalar_one()
            
            # We can't easily get size info like in MongoDB, so returning what we can
            return {
                "count": count,
                "size": 0,  # Not easily available in PostgreSQL
                "avgObjSize": 0  # Not easily available in PostgreSQL
            }
        
    async def get_project_chunks_bulk(self, project_id: int, limit: int = 1000):
        """
        Get all chunks for a project in one query with a limit.
        """
        print(f"Fetching chunks for project_id: {project_id}")
        try:
            async with self.db_client() as session:
                stmt = select(DataChunk).where(DataChunk.chunk_project_id == project_id).limit(limit)
                result = await session.execute(stmt)
                chunks = result.scalars().all()
                
                total_chunks = len(chunks)
                print(f"Found {total_chunks} chunks for project {project_id}")
                if chunks:
                    print(f"Sample chunk text: {chunks[0].chunk_text[:100]}")
                return chunks
        except Exception as e:
            print(f"Error getting project chunks: {str(e)}")
            return []

   