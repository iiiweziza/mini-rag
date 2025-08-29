import os

class TemplateParser:
    """
    A template parser for handling multi-language string templates in the LLM system.
    This class manages template loading and variable substitution across different languages,
    with fallback support to a default language.

    The template structure follows:
    stores/llm/templates/locales/
        ├── en/                 # Default language templates
        │   ├── group1.py      # Template group files
        │   └── group2.py
        └── ar/                 # Additional language templates
            ├── group1.py
            └── group2.py

    Each group file contains template strings that can be substituted with variables.
    """

    def __init__(self, language: str=None, default_language='en'):
        """
        Initialize the template parser with language settings.

        Args:
            language (str, optional): The preferred language code (e.g., 'en', 'ar').
                                    If None, default_language will be used.
            default_language (str): The fallback language code. Defaults to 'en'.
        """
        # Get the absolute path to the template directory
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language
        self.language = None

        # Set the initial language, validating against available locales
        self.set_language(language)

    def set_language(self, language: str):
        """
        Set the parser's active language, falling back to default if necessary.

        Args:
            language (str): The language code to set (e.g., 'en', 'ar')

        The method will:
        1. Use default_language if no language is provided
        2. Verify if the requested language exists in the locales directory
        3. Fall back to default_language if the requested language is not available
        """
        if not language:
            self.language = self.default_language

        # Check if the language directory exists
        language_path = os.path.join(self.current_path, "locales", language)
        if os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_language

    def get(self, group: str, key: str, vars: dict={}):
        """
        Retrieve and process a template string from the specified group and key.

        Args:
            group (str): The template group name (corresponds to the Python module name)
            key (str): The specific template key within the group
            vars (dict): Variables to substitute in the template

        Returns:
            str: The processed template string with variables substituted
            None: If the template cannot be found or loaded

        Example:
            parser.get('errors', 'not_found', {'item': 'document'})
            # Might return: "The document was not found in the database"
        """
        if not group or not key:
            return None
        
        # Try to locate the template file in the current language
        group_path = os.path.join(self.current_path, "locales", self.language, f"{group}.py" )  # EX: rag.py file
        targeted_language = self.language
        # Fall back to default language if the template doesn't exist in current language
        if not os.path.exists(group_path):
            group_path = os.path.join(self.current_path, "locales", self.default_language, f"{group}.py" )
            targeted_language = self.default_language

        # Return None if template file doesn't exist in either language
        if not os.path.exists(group_path):
            return None
        
        # Dynamically import the template module for the targeted language
        # The import path follows the package structure: stores.llm.templates.locales.<language>.<group> 
        #Example: stores.llm.templates.locales.en.rag
        try:
            module = __import__(f"stores.llm.templates.locales.{targeted_language}.{group}", fromlist=[group])
        except ImportError:
            # Return None if module import fails
            return None

        if not module:
            return None
        
        try:
            # Get the template string from the module using the provided key
            key_attribute = getattr(module, key)
            # Substitute the variables in the template and return the result
            # The template should be a string.Template object that supports the substitute method
            # Example: document_prompt or system_prompt
            return key_attribute.substitute(vars)
        except (AttributeError, ValueError, KeyError) as e:
            # Return None if:
            # - AttributeError: key doesn't exist in the module
            # - ValueError: template string is invalid
            # - KeyError: required variable is missing from vars dict
            return None