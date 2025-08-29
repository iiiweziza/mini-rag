from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def set_generate_model(self, model_name: str):
        """Set the model to be used for generation."""
        pass

    @abstractmethod
    def set_embeddings_model(self, model_name: str , empedding_size:int):
        """Set the model to be used for embeddings."""
        pass

    @abstractmethod
    def generate_text(self, prompt:str ,chat_history: list=[] , 
                      max_output_tokens: int = None , temperature: float = None):
        """Generate text based on the provided prompt."""
        pass

    @abstractmethod
    def embed_text(self, text: str, document_type: str= None):
        """Generate embeddings for the provided text."""
        pass

    @abstractmethod
    def abstract_prompt(self, prompt: str, role: str):
        """An abstract method that must be implemented by subclasses."""
        pass
