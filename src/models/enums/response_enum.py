'''Here we will define the response enums.'''
from enum import Enum
class ResponseEnumSignal(Enum):
    '''This class will define the response enums. 
    The response enums will be used in all the controllers. 
    The response enums will be used to define the response status and message.'''

    SUCCESS = "Successful_operation"
    SIZE_LIMIT_EXCEEDED = "File size limit exceeded"
    TYPE_NOT_ALLOWED = "File type not allowed"
    FILE_NOT_FOUND = "File not found"
    FILE_UPLOADED = "File uploaded successfully"
    FILE_DELETED = "File deleted successfully"
    FILE_UPDATED = "File updated successfully"
    FILE_NOT_UPDATED = "File not updated"
    FILE_NOT_DELETED = "File not deleted"
    UPLOADED = "File uploaded successfully"
    FAILED_PROCESS = "File process failed"
    NO_FILES_FOUND = "No files found for the project"
    FILE_ID_ERROR = "No files found for the given file ID"
    PROJECT_NOT_FOUND = "Project not found"
    VECTOR_DB_INSERTION_FAILED = "Vector DB insertion failed"
    CHUNKS_INDEXED_SUCCESSFULLY = "Chunks indexed in vector DB successfully"
    COLLECTION_INFO_RETRIEVED = "Collection info retrieved successfully"
    VECTOR_DB_SEARCH_SUCCESS = "Vector db search results retrieved successfully"
    VECTOR_DB_SEARCH_FAILED = "Vector db search failed"
    RAG_ANSWER_FAILED = "RAG answer failed"
    RAG_ANSWER_SUCCESS = "RAG answer succeeded"
    INVALID_INPUT_TYPE = "Invalid input type. Must be file or URL."
    URL_NOT_ACCESSIBLE = "URL is not accessible"
    URL_VALID = "URL is valid"
    URL_ERROR = "Error occurred while validating URL"
    INVALID_URL = "Invalid URL format"
    