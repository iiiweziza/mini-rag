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