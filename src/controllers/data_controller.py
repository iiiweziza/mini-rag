from fastapi import UploadFile
from .base_controller import BaseController
from models.enums import ResponseEnumSignal
from .project_controller import ProjectController
from models.enums import ResponseEnumSignal, InputTypeEnum

import logging
import re
import os
from urllib.parse import urlparse
import requests
from typing import Union, Tuple
import aiofiles


class DataController(BaseController):
    '''here we will define the data controller 
    the data controller will take from super class BaseControllers''' 

    def __init__(self):
        super().__init__()  # Pass the settings to the BaseController constructor
        self.logger = logging.getLogger(__name__)

    def validate_input(self, input_data: Union[UploadFile, str]) -> Tuple[bool, str, InputTypeEnum]:
        """Validate if the input is a file or URL and check its validity"""
        if isinstance(input_data, UploadFile):
            return self.validate_file(input_data)
        elif isinstance(input_data, str):
            return self._validate_url(input_data)
        else:
            return False, ResponseEnumSignal.INVALID_INPUT_TYPE.value, InputTypeEnum.UNKNOWN

    def validate_file(self, file:UploadFile) -> Tuple[bool, str, InputTypeEnum]:
        '''this function will validate the file type and size'''
        # here we want to check about type and size of the file and that is logic so we will build it in controller file 
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPE:
            return False, ResponseEnumSignal.TYPE_NOT_ALLOWED.value, InputTypeEnum.FILE
        if file.size > self.app_settings.FILE_MAX_SIZE:
            return False, ResponseEnumSignal.SIZE_LIMIT_EXCEEDED.value, InputTypeEnum.FILE
        return True, ResponseEnumSignal.UPLOADED.value, InputTypeEnum.FILE
    
    def _validate_url(self, url: str) -> Tuple[bool, str, InputTypeEnum]:
        """Validate basic URL accessibility"""
        print(f"Validating URL: {url}")
        try:
            parsed = urlparse(url)
            print(f"URL parsed: scheme={parsed.scheme}, netloc={parsed.netloc}")
            if not all([parsed.scheme, parsed.netloc]):
                print(f"URL validation failed: missing scheme or netloc")
                return False, ResponseEnumSignal.INVALID_URL.value, InputTypeEnum.URL

            print(f"Making HEAD request to: {url}")
            response = requests.head(url, timeout=10, allow_redirects=True)
            print(f"Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"URL validation failed: status code {response.status_code}")
                return False, ResponseEnumSignal.URL_NOT_ACCESSIBLE.value, InputTypeEnum.URL

            print(f"URL validation successful")
            return True, ResponseEnumSignal.URL_VALID.value, InputTypeEnum.URL

        except requests.RequestException as e:
            print(f"URL validation error: {str(e)}")
            self.logger.error(f"URL validation error: {str(e)}")
            return False, ResponseEnumSignal.URL_ERROR.value, InputTypeEnum.URL
    
    def generate_unique_input_or_file_path(self, org_file_name: str, project_id: str):
        '''this function will generate a unique file path for the uploaded file'''
        random_string = self.generate_random_string()
        project_dir_path = ProjectController().get_project_dir(project_id=project_id)

        clean_file_name = self.get_clean_input_or_file_name(org_file_name)

        new_clean_file_path = os.path.join(project_dir_path,
                                           random_string + "_" + clean_file_name)
        
        while os.path.exists(new_clean_file_path):
            random_string = self.generate_random_string()
            new_clean_file_path = os.path.join(project_dir_path,
                                               random_string + "_" + clean_file_name)
            
        return new_clean_file_path , random_string + "_" + clean_file_name  
                                         
    
    def get_clean_input_or_file_name(self, org_file_name: str):
        """Return a clean file name with only alphanumeric characters, underscores, and dots."""
   
        clean_file_name = org_file_name.strip().replace(" ", "_")
        clean_file_name = re.sub(r'[^\w.]', '', clean_file_name)
        return clean_file_name

    async def process_file_upload(
        self, 
        request, 
        Project_id: str, 
        project, 
        data_controller, 
        file: UploadFile, 
        app_settings
    ):
        """Handle file upload processing"""
        # Validate file
        is_valid, result_signal, input_type = data_controller.validate_file(file=file)
        if not is_valid:
            return result_signal

        # Generate file path and save file
        project_dir_path = ProjectController().get_project_dir(project_id=Project_id)
        file_path, file_id = data_controller.generate_unique_input_or_file_path(
            org_file_name=file.filename,
            project_id=Project_id
        )
        
        try:
            async with aiofiles.open(file_path, 'wb') as out_file:
                while chunk := await file.read(app_settings.FILE_CHUNK_SIZE):
                    await out_file.write(chunk)
        except Exception as e:      
            self.logger.error(f"Error saving file: {e}")
            return ResponseEnumSignal.FILE_NOT_SAVED.value
        
        # Store file asset in database
        from models.assets_model import AssetModel
        from models.db_schemes.assets_files import AssetsFiles
        from models.enums import AssetsEnumType
        
        asset_model = await AssetModel.create_instance(db_client=request.app.client_db)
        
        asset_resource = AssetsFiles(
            asset_project_id=project.id,
            asset_type=AssetsEnumType.ASSETS_FILE.value,
            asset_name=file_id,
            asset_size=os.path.getsize(file_path),
        )
        
        asset_record = await asset_model.insert_asset(asset=asset_resource)
        
        return {
            "Result": result_signal,
            "File ID": str(asset_record.id),
            "Type": "file",
            "Filename": file.filename
        }

    async def process_url_upload(
        self, 
        request, 
        Project_id: str, 
        project, 
        data_controller, 
        url: str, 
        chunk_size: int, 
        chunk_overlap: int
    ):
        """Handle URL upload processing"""
        # Validate URL
        print(f"About to validate URL: {url}")
        is_valid, result_signal, input_type = data_controller.validate_input(url)
        print(f"Validation result: is_valid={is_valid}, result_signal={result_signal}, input_type={input_type}")
        if not is_valid:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=422,
                content={"error": result_signal}
            )
        
        # Generate unique ID for the URL
        url_id = data_controller.generate_random_string() + "_url"
        
        # Process the URL content directly
        try:
            from controllers import ProcessingController
            from models.assets_model import AssetModel
            from models.db_schemes.assets_files import AssetsFiles
            from models.enums import AssetsEnumType
            from models.chunk_model import ChunkModel
            from models.db_schemes.data_chunk import DataChunk
            
            processing_controller = ProcessingController(project_id=Project_id)
            
            # Get content from URL
            print(f"Processing URL: {url}")
            print(f"URL type: {type(url)}")
            print(f"URL length: {len(url)}")
            print(f"URL starts with http: {url.startswith('http')}")
            print(f"URL contains 'http': {'http' in url}")
            print(f"URL contains 'https': {'https' in url}")
            print(f"URL contains '://': {'://' in url}")
            print(f"About to call processing_controller.get_input_content with: {url}")
            print(f"Project ID: {Project_id}")
            url_content = processing_controller.get_input_content(url)
            if not url_content:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=422,
                    content={"error": "Failed to load content from URL"}
                )
            print(f"URL content loaded successfully. Number of documents: {len(url_content)}")
            
            # Process content into chunks
            chunks = processing_controller.process_input_content(
                file_content=url_content,
                file_id=url_id,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            # Store URL asset in database
            asset_model = await AssetModel.create_instance(db_client=request.app.client_db)
            
            asset_resource = AssetsFiles(
                asset_project_id=project.id,
                asset_type=AssetsEnumType.ASSETS_FILE.value,
                asset_name=url_id,
                asset_size=len(str(url_content)),  # Approximate size
            )
            
            asset_record = await asset_model.insert_asset(asset=asset_resource)
            
            # Store chunks in database
            chunk_model = await ChunkModel.create_instance(db_client=request.app.client_db)
            
            for i, chunk in enumerate(chunks):
                chunk_data = DataChunk(
                    project_id=str(project.id),  # Convert ObjectId to string
                    content=chunk.page_content,
                    chunk_index=i,
                    source_file=url_id,
                    chunks_file_asset_id=asset_record.id,
                    chunk_metadata=chunk.metadata
                )
                await chunk_model.insert_chunk(chunk=chunk_data)
            
            return {
                "Result": "URL processed successfully",
                "URL ID": str(asset_record.id),
                "Chunks Created": len(chunks),
                "URL": url,
                "Type": "url"
            }
            
        except Exception as e:
            self.logger.error(f"Error processing URL: {e}")
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to process URL: {str(e)}"}
            )