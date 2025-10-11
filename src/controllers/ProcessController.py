import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.document_loaders import CSVLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import NotionDBLoader
from models import ProcessingEnum
from typing import List
from dataclasses import dataclass

@dataclass
class Document:
    page_content: str
    metadata: dict

class ProcessController(BaseController):
    def crawl_and_extract(self, url, max_pages=5):
        visited = set()
        to_visit = [url]
        results = []
        while to_visit and len(visited) < max_pages:
            current_url = to_visit.pop(0)
            if current_url in visited:
                continue
            try:
                resp = requests.get(current_url, timeout=10)
                soup = BeautifulSoup(resp.text, "html.parser")
                main_text = ' '.join([tag.get_text() for tag in soup.find_all(['p', 'h1', 'h2', 'h3'])])
                results.append({'url': current_url, 'text': main_text})
                visited.add(current_url)
                for link in soup.find_all('a', href=True):
                    href = urljoin(current_url, link['href'])
                    if urlparse(href).netloc == urlparse(url).netloc and href not in visited:
                        to_visit.append(href)
            except Exception:
                continue
        return results

    def __init__(self, project_id: str):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self, file_id: str):
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id: str):
        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(
            self.project_path,
            file_id
        )
        if not os.path.exists(file_path):
            return None
        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")
        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        if file_ext == ProcessingEnum.DOCX.value:
            return UnstructuredWordDocumentLoader(file_path)
        if file_ext == ProcessingEnum.CSV.value:
            return CSVLoader(file_path)
        if file_ext == ProcessingEnum.HTML.value:
            return UnstructuredHTMLLoader(file_path)
        if file_ext == ProcessingEnum.MD.value:
            return UnstructuredMarkdownLoader(file_path)
        if file_ext == ProcessingEnum.XLSX.value:
            return UnstructuredExcelLoader(file_path)
        if file_ext == ProcessingEnum.WEB.value:
            # file_id is expected to be a URL string for web
            return WebBaseLoader(file_id)
        if file_ext == ProcessingEnum.NOTION.value:
            # file_id is expected to be a Notion DB URL or ID
            # You may need to pass integration_token and database_id as required by NotionDBLoader
            # Example: NotionDBLoader(integration_token, database_id)
            # Here, just a placeholder usage:
            return NotionDBLoader(file_id)
        return None

    def get_file_content(self, file_id: str):

        loader = self.get_file_loader(file_id=file_id)
        if loader:
            return loader.load()

        return None

    def process_file_content(self, file_content: list, file_id: str,
                            chunk_size: int=100, overlap_size: int=20):

        file_content_texts = [
            rec.page_content
            for rec in file_content
        ]

        file_content_metadata = [
            rec.metadata
            for rec in file_content
        ]

        # chunks = text_splitter.create_documents(
        #     file_content_texts,
        #     metadatas=file_content_metadata
        # )

        chunks = self.process_simpler_splitter(
            texts=file_content_texts,
            metadatas=file_content_metadata,
            chunk_size=chunk_size,
        )

        return chunks

    def process_simpler_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int, splitter_tag: str="\n"):
        
        full_text = " ".join(texts)

        # split by splitter_tag
        lines = [ doc.strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) > 1 ]

        chunks = []
        current_chunk = ""

        for line in lines:
            current_chunk += line + splitter_tag
            if len(current_chunk) >= chunk_size:
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata={}
                ))

                current_chunk = ""

        if len(current_chunk) >= 0:
            chunks.append(Document(
                page_content=current_chunk.strip(),
                metadata={}
            ))

        return chunks


    

