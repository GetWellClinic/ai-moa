import re
import yaml
from config import ProviderListManager

def get_provider_list(self):
	"""
    Retrieves a provider ID from the OCR text or defaults to a pre-configured provider ID.

    This method processes the provider list from a file specified in the configuration and attempts to 
    extract a provider ID by querying an AI model using the OCR text and the loaded provider list. If no 
    valid provider ID is found in the model response, the method defaults to a pre-configured provider ID.

    The AI model is queried using a prompt that combines the OCR text with the provider list, and the 
    extracted provider ID is returned if valid. If no provider ID is found, the default provider ID is returned.

    Args:
        None

    Returns:
        tuple: 
            - `True, provider_id` if a valid provider ID is found (either extracted from the AI model or 
              using the default provider ID).
            - `True, default_provider_id` if no valid provider ID is found in the AI response or provider list.

    Example:
        >>> result = manager.get_provider_list()
        >>> print(result)
        (True, 123)  # if a provider ID is successfully extracted
    """
	file_name = self.config.get('provider_list.output_file', '')

	provider_list = self.get_provider_list_filemode(self,file_name)

	default_provider_id = self.default_values.get('default_provider_tagging_id', '')


	if provider_list is None:
	    #If provider list is empty return default provider id for notifiying
	    return True, default_provider_id

	prompt = self.ai_prompts.get('get_provider', '')

	prompt = f"\n{self.ocr_text}.\n" + prompt + str(provider_list)
	text = self.query_prompt(self,prompt)[1]

	match = re.search(r'\b\d+\b', text)

	if match:
	    numerical_value = int(match.group())
	    return True, numerical_value
	else:
	    return True,default_provider_id


def get_provider_list_filemode(self,file_path):
	"""
    Loads the provider list from a YAML file.

    This method attempts to open and read a YAML file containing a list of providers. If the file is found 
    and successfully parsed, it returns the list of providers. If the file is missing or cannot be parsed, 
    an error is logged, and a default empty list is returned. In case of a missing file, the method triggers 
    the generation of the provider list.

    Args:
        file_path (str): The path to the YAML file containing the provider list.

    Returns:
        list: 
            - A list of providers (from the YAML file) if the file is successfully read.
            - An empty list if the file is not found or an error occurs while reading it.

    Example:
        >>> provider_list = manager.get_provider_list_filemode('/path/to/provider_list.yaml')
        >>> print(provider_list)
        [{'provider_id': 123, 'name': 'Provider A'}, {'provider_id': 124, 'name': 'Provider B'}] 
        # a list of providers loaded from the YAML file
    """
	try:
		with open(file_path, 'r') as file:
			provider_list = yaml.safe_load(file)
			return provider_list.get('providers', [])
	except FileNotFoundError:
		manager = ProviderListManager(self)
		manager.generate_provider_list()
		self.logger.error(f"Error: The file {file_path} does not exist.")
		return []
	except yaml.YAMLError as e:
		self.logger.error(f"Error reading YAML file: {e}")
		return []