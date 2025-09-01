from .base_controller import BaseController
from .project_controller import ProjectController
from models.enums import processingEnumType
import os 
from langchain_community.document_loaders import TextLoader,PyMuPDFLoader, UnstructuredExcelLoader,UnstructuredHTMLLoader,UnstructuredMarkdownLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders.web_base import WebBaseLoader
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from langchain.schema import Document


class ProcessingController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()  # Pass the settings to the BaseController constructor
        print(f"ProcessingController.__init__ called with project_id: {project_id}")
        self.project_dir = ProjectController().get_project_dir(project_id=project_id)
        print(f"ProcessingController.project_dir set to: {self.project_dir}")

    def get_file_extension(self,file_id : str):
        """
        Get the file extension from the file ID.  
        Type of file == file extension
        """
        file_extension = os.path.splitext(file_id)[-1]
        return file_extension

    def _create_web_loader(self, url: str):
        """Create a custom web loader for URLs"""
        print(f"Creating custom web loader for URL: {url}")
        
        class CustomWebLoader:
            def __init__(self, url):
                self.url = url
            
            def load(self):
                try:
                    print(f"Fetching content from URL: {self.url}")
                    response = requests.get(self.url, timeout=30, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    response.raise_for_status()
                    
                    print(f"Response status: {response.status_code}")
                    print(f"Content type: {response.headers.get('content-type', 'unknown')}")
                    
                    # Parse HTML content
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text content
                    text = soup.get_text()
                    
                    # Clean up whitespace
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    print(f"Extracted text length: {len(text)} characters")
                    
                    # Create a Document object
                    from langchain.schema import Document
                    return [Document(
                        page_content=text,
                        metadata={"source": self.url, "content_type": "web_page"}
                    )]
                    
                except Exception as e:
                    print(f"Error fetching URL content: {e}")
                    raise e
        
        return CustomWebLoader(url)

    def get_input_loader(self,file_id : str):
        """
        Get the file loader based on the file extension or URL.
        """
        print(f"get_input_loader called with: {file_id}")
        print(f"file_id type: {type(file_id)}")
        print(f"file_id length: {len(file_id)}")
        print(f"file_id starts with http: {file_id.startswith('http') if isinstance(file_id, str) else 'N/A'}")
        
        # Primary URL check - if it starts with http:// or https://, treat as URL
        if file_id.startswith(('http://', 'https://')):
            print(f"Detected URL by prefix: {file_id}")
            return self._create_web_loader(file_id)
        
        # Secondary URL check using urlparse
        try:
            parsed = urlparse(file_id)
            print(f"URL parsing result: scheme={parsed.scheme}, netloc={parsed.netloc}")
            print(f"URL parsing result: path={parsed.path}, query={parsed.query}, fragment={parsed.fragment}")
            if all([parsed.scheme, parsed.netloc]):
                print(f"Detected URL by urlparse: {file_id}")
                return self._create_web_loader(file_id)
            else:
                print(f"URL parsing failed: missing scheme or netloc")
        except Exception as e:
            print(f"URL parsing failed: {e}")
            pass  # Not a URL, continue with file processing

        # If we reach here, it's not a URL, so treat as file
        file_extension = self.get_file_extension(file_id)
        file_path = os.path.join(self.project_dir, file_id)

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.") 

        if file_extension == processingEnumType.TXT.value:
            return TextLoader(file_path, encoding="utf-8")
        elif file_extension == processingEnumType.CSV.value:
            return CSVLoader(file_path)
        elif file_extension == processingEnumType.MARKDOWN.value:
            return UnstructuredMarkdownLoader(file_path)
        elif file_extension == processingEnumType.PDF.value:
            return PyMuPDFLoader(file_path)
        elif file_extension == processingEnumType.HTML.value:
            return UnstructuredHTMLLoader(file_path)
        elif file_extension == processingEnumType.XLSX.value:
            return UnstructuredExcelLoader(file_path, mode="elements")
        else:
            # Try generic unstructured loader for unknown file types
            return UnstructuredLoader(file_path)
            
    def get_input_content(self,file_id : str):
        """
        Get the file content using the appropriate loader.
        """
        print(f"get_input_content called with: {file_id}")
        loader = self.get_input_loader(file_id)
        if loader:
            print(f"Loader created successfully: {type(loader)}")
            print(f"Loader class: {loader.__class__.__name__}")
            try:
                print(f"About to call loader.load()...")
                content = loader.load()
                print(f"Content loaded successfully: {len(content) if content else 0} documents")
                if content:
                    print(f"First document preview: {content[0].page_content[:100]}...")
                return content
            except Exception as e:
                print(f"Error loading content: {e}")
                print(f"Error type: {type(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                return None
        else:
            print("No loader created")
            return None

    def process_input_content(self,file_content:str,file_id:str,chunk_size:int=100,chunk_overlap:int=20):
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