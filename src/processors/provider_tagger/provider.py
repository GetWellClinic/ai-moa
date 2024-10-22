import re
import yaml
from config import ProviderListManager

def get_provider_list(self):

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