from ..llm_interface import LLMInterface
from ..llm_enums import OpenAIEnums
from openai import OpenAI
import logging

class OpenAIProvider(LLMInterface):

    def __init__(self,api_key: str, api_url: str= None,
                 default_input_max_characters: int = 1024,
                 default_output_max_tokens: int = 1024,
                 default_temperature: float = 0.7,
                 ):
        
        self.api_key = api_key
        self.base_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature

        self.generation_model_id = None
        self.embeddings_model_id = None
        self.embedding_size = None


        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url if self.base_url and len(self.base_url) > 0 else None
        )
        self.enums = OpenAIEnums
        self.logger = logging.getLogger(__name__)

    # Functions to set models and parameters
    def process_text(self, text: str):
        """
        Process the input text to ensure it meets the requirements for OpenAI.
        This can include truncating or formatting the text as needed.
        """
        return text[:self.default_input_max_characters].strip()  # Truncate to max characters and strip whitespace
    
    def set_generate_model(self, model_name: str):
        self.generation_model_id = model_name

    def set_embeddings_model(self, model_name: str, embedding_size: int):
        self.embeddings_model_id = model_name
        self.embedding_size = embedding_size

    def generate_text(self, prompt: str, chat_history: list = [],
                      max_output_tokens: int = None, temperature: float = None):
        # Implementation for generating text using OpenAI API
        
        if not self.client:
            self.logger.error("OpenAI client is not initialized.")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model is not set.")
            return None
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_output_max_tokens
        temperature = temperature if temperature else self.default_temperature

        chat_history.append(
            self.abstract_prompt(prompt = prompt, role=OpenAIEnums.USER.value)
        )

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
        )

        if not response or not response.choices or len(response.choices) == 0:
            self.logger.error("No response from OpenAI, error while generating text.")
            return None

        return response.choices[0].message.content
    


    def embed_text(self, text: str, document_type: str= None):
        # Implementation for embedding text using OpenAI API
        if not self.client:
            self.logger.error("OpenAI client is not initialized.")
            return None
        if not self.embeddings_model_id:
            self.logger.error("Embeddings model for OpenAI is not set.")
            return None
        response = self.client.embeddings.create(
            model=self.embeddings_model_id,
            input=text
        )
        if not response or not response.data or len(response.data) == 0:
            self.logger.error("Error while embedding text.")
            return None
        return response.data[0].embedding
    
    def abstract_prompt(self, prompt: str, role: str):    # used it in generation text 
        # Implementation for abstracting prompt using OpenAI API
        return {
            "role": role,
            "content": self.process_text(prompt)
        }
