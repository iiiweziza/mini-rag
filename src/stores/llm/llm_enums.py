from enum import Enum

class LLMEnums(Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"


class OpenAIEnums(Enum):
    SYSTEM = "system"
    USER =  "user"
    ASSISTANT = "assistant" 

    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"

class CohereEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    DOCUMENT = "search_document"  # this formula in cohere docs 
    QUERY = "search_query"   # this formula in cohere docs


class EmbedDocumentTypeEnums(Enum):
    DOCUMENT = "document"  # from uploaded documents 
    QUERY = "query"        # direct from user query
