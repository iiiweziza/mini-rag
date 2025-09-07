from operator import index
from .base_data_model import BaseDataModel
from .enums.database_enum import DatabaseEnumType
from models.db_schemes.assets_files import Asset 
from bson import ObjectId


class AssetModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        # connect with collection of the db_client 
        self.collection = self.db_client[DatabaseEnumType.COLLECTION_ASSETS_NAME.value]  
       
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
        if DatabaseEnumType.COLLECTION_ASSETS_NAME.value not in all_collections:
            # if the collection is not exist we will create it
            self.collection = self.db_client[DatabaseEnumType.COLLECTION_ASSETS_NAME.value]
            # create the collection with the indexes from the project schema
            indexes = Asset.get_indexes()  # get the indexes from the project schema
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index.get("name"),
                    unique=index.get("unique", False)
                )

    async def insert_asset(self, asset: Asset):
        """
        Insert an asset into the collection.
        :param asset: An instance of Asset to be inserted.
        :return: The inserted asset with its ID populated.
        """
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id
        return asset

    async def get_asset_by_mongodb_id(self, project_id: str, mongodb_id: str):
        """
        Get an asset by its MongoDB ID.
        :param project_id: The project ID the asset belongs to
        :param mongodb_id: The MongoDB ID of the asset (_id field)
        :return: The asset if found, None otherwise
        """
        try:
            asset_id = ObjectId(mongodb_id)
            print(f"Looking for asset with _id: {asset_id}")
            # First try to find just by _id to see if the asset exists at all
            asset_doc = await self.collection.find_one({
                "_id": asset_id
            })
            if not asset_doc:
                print(f"No asset found with _id: {asset_id}")
                return None
            
            print(f"Found asset: {asset_doc}")
            print(f"Asset project_id: {asset_doc.get('asset_project_id')}, Looking for project_id: {project_id}")
            
            # Now check if it belongs to the correct project
            if str(asset_doc.get('asset_project_id')) == str(project_id):
                return Asset(**asset_doc)
            else:
                print(f"Asset found but belongs to different project. Expected: {project_id}, Found: {asset_doc.get('asset_project_id')}")
                return None
        except Exception as e:
            print(f"Error in get_asset_by_mongodb_id: mongodb_id={mongodb_id}, project_id={project_id}, error={str(e)}")
            return None
    
    async def get_all_project_assets(self, project_id, asset_type: str):
        """
        Retrieve all assets associated with a specific project, sorted by publish date descending.
        """
        records = await self.collection.find({
            "$or": [
                {"asset_project_id": project_id},
                {"asset_project_id": str(project_id)}
            ],
            "asset_type": asset_type,
        }).sort("asset_published", -1).to_list(length=None)
        return [Asset(**record) for record in records]


    async def get_asset_by_id(self,project_id , asset_file_id:str):
        """
        Retrieve a specific asset by its ID.
        :param project_id: The ID of the project the asset belongs to.
        :param asset_file_id: The ID of the asset file to retrieve.
        :return: An Asset object if found, None otherwise.
        """
        record = await self.collection.find_one({
            "$or": [
        {"asset_project_id": project_id},
        {"asset_project_id": str(project_id)}
       ],
            "asset_name": asset_file_id
        })
        return Asset(**record) if record else None
