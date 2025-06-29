from operator import index
from .base_data_model import BaseDataModel
from .enums.database_enum import DatabaseEnumType
from models.db_schemes.assets_files import AssetsFiles 
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
            indexes = AssetsFiles.get_indexes()  # get the indexes from the project schema
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index.get("name"),
                    unique=index.get("unique", False)
                )

    async def insert_asset(self, asset: AssetsFiles):
        """
        Insert an asset into the collection.
        :param asset: An instance of AssetsFiles to be inserted.
        :return: The inserted asset with its ID populated.
        """
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id
        return asset
    
    async def get_all_project_assets(sef,project_id: str):
        """
        Retrieve all assets associated with a specific project.
        :param project_id: The ID of the project to retrieve assets for.
        :return: A list of AssetsFiles objects associated with the project.
        """
        return await self.collection.find({
            "asset_project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id
        }).to_list(length=None)
