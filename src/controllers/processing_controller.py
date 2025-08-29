from .base_controller import BaseController
from .project_controller import ProjectController
from models.enums import processingEnumType
import os 
from langchain_community.document_loaders import TextLoader,PyMuPDFLoader        #.text
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ProcessingController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()  # Pass the settings to the BaseController constructor
        self.project_dir = ProjectController().get_project_dir(project_id=project_id)

    def get_file_extension(self,file_id : str):
        """
        Get the file extension from the file ID.  
        Type of file == file extension
        """
        file_extension = os.path.splitext(file_id)[-1]
        return file_extension

    def get_file_loader(self,file_id : str):
        """
        Get the file loader based on the file extension.
        """
        file_extension = self.get_file_extension(file_id)
        file_path =os.path.join(self.project_dir, file_id)

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.") 

        if file_extension == processingEnumType.TXT.value:
            return TextLoader(file_path ,encoding="utf-8")
            
        elif file_extension == processingEnumType.PDF.value:
            
            return PyMuPDFLoader(file_path)
            
    def get_file_content(self,file_id : str):
        """
        Get the file content using the appropriate loader.
        """
        loader = self.get_file_loader(file_id)
        if loader:
            return loader.load()
        return None

    def process_file_content(self,file_content:str,file_id:str,chunk_size:int=100,chunk_overlap:int=20):
        """
        Process the file content using the RecursiveCharacterTextSplitter.
        """
        text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len
            )
            
        file_content_texts=[
            rec.page_content
            for rec in file_content
            ]

        file_content_metadata=[
            rec.metadata
            for rec in file_content
            ]

        chunks = text_splitter.create_documents(file_content_texts,
                                                    metadatas=file_content_metadata,
                                                    )
            
        return chunks