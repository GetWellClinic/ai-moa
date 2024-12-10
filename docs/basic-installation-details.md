## Steps for Installation

### 1. Clone the Repository

First, clone the repository to your local machine. Open your terminal and run the following command:

`git clone https://github.com/GetWellClinic/ai-moa.git`

Checkout the branch you will be using. For example, git checkout dev-gwc

### 2. Create and Activate the Virtual Environment
Create a Python virtual environment for the project. This step ensures that the dependencies are installed in an isolated environment and do not interfere with your system's Python environment.

Run the following command to create the virtual environment:

`python -m venv aimoa`

Next, activate the virtual environment:

On Linux/macOS:

`source aimoa/bin/activate`

On Windows:

`.\aimoa\Scripts\activate`

When the virtual environment is activated, your terminal prompt should change to show the virtual environment name (e.g., (aimoa)).

### 3. Install Dependencies

Once your virtual environment is active, navigate to the src/ directory (if not already in it) and run the `install.sh` script to install all required dependencies.

`cd src/`

Make the install.sh script executable

`chmod +x install.sh`

Run the installation script

`./install.sh`

The `install.sh` script will handle the installation of Python dependencies and any other setup required for the project.


# O19 Setup for AI-MOA

To set up O19 for integration with AI-MOA, you will need to configure several settings to ensure the application works correctly. Here’s a step-by-step breakdown of what you need to configure:

1. Demographic Document Categories and default values
2. Providers list
3. User account for LLM in O19
4. Default demographic / provider details
5. Other details


### 1. Demographic Document Categories and default values

For example consider the below configuration details in `workflow-config.yaml` file

workflow-config.yaml

### AI Prompts (Mandatory)
ai_prompts:
  category_types_prompt: >
  	Prompt for category types

### Document Categories (Mandatory)
document_categories:
  - name: Lab
    default_tagger: 99
    description: >
      Description about category for user understanding (not for LLM)
    tasks:
      - name: get_document_description
        prompt: >
        	Prompt for category description

The `category_types_prompt` in `ai_prompts` defines the prompt for identifying the document type based on the information provided. Once the LLM identifies the document type, it will refer to `document_categories` and select the corresponding type based on the `name`. It will then execute the `get_document_description` task to generate a description for the document type.

For this, all the categories added to `category_types_prompt` and `document_categories` should be defined in O19, so that when the document is updated by AI-MOA in O19, the expected results are obtained.

In O19 Use Administration -> System Management -> Demographic Document Categories to add these categories.

The ones being used by AI-MOA are `advertisement, consent, consult, diagnostics, econsult, insurance, lab, legal, miscellaneous, oldchart, others, pathology, pharmacy, photo, radiology, referral, request, requisition`

The `default_tagger` in `document_categories` is used to tag the provider only for document types that belong to this category. In the above the provider with id `99` will be tagged if the document type is `Lab`

workflow-config.yaml

### default values (Mandatory)
default_values:
  default_provider_tagging_id:
    127
  default_unidentified_patient_tagging_id:
    285
  default_unidentified_patient_tagging_name: >
    CONFIDENTIAL, UNATTACHED
  default_unidentified_patient_tagging_dob: >
    2010-02-28
  default_category: >
    Miscellaneous

`default_category` will be used as the default category if the system is unable to identify the document's category. You can set this to any available category in the O19 (Demographic Document Categories).

### 2. Providers List

config.yaml

### Provider list configuration, for generating or managing provider data.
provider_list:
  output_file: ../config/provider_list.yaml  #Output file for storing the provider list.
  template_file: ../config/template_providerlist.txt  #Template file for provider list formatting.

The AI-MOA uses `provider_list.yaml` to reduce the time taken to look up the provider. The system will upload the template `template_providerlist.txt` to O19 to generate the `provider_list.yaml`. The system should be able to do this if it has the necessary permissions. If it is not able to do this, upload the `template_providerlist.txt` to Administration -> Reports -> Reports by Template -> Add Template. You can manually remove unused providers from the `provider_list.yaml` file, or you can remove them from O19 if they are no longer needed before running the script. (Mandatory)

### 3. User account for LLM in O19

config.yaml

### EMR (Electronic Medical Record) configuration for connecting to an EMR system.
emr:
  base_url: http://127.0.0.1:8080/oscar  # Base URL for the EMR system.
  verify-HTTPS: false # Set this to true to verify the SSL certificates for o19.
  document_folder: pending  # Folder where pending documents to be processed are stored in o19.
  incoming_folder: File  # Folder where incoming documents to be processed are stored in o19.
  incoming_folder_queue: '1'  # Queue number for processing incoming files.
  password: passpwd  # Password for EMR login.
  pin: '123'  # PIN for EMR login.
  system_type: o19  # Type of system, 'o19'.
  username: emr  # Username for EMR login.

`base_url`: This specifies the base address or endpoint for the EMR system. (Mandatory)

`verify-HTTPS`: This setting determines whether the system will verify SSL/TLS certificates when making requests to the O19 platform.

`document_folder`: Specifies the folder (in this case, named `pending`) where documents that are waiting to be processed will be stored within the O19 system.
To use `incoming_docs` folder change `pending` to `incoming`

`password`: Password for O19 login. (Mandatory)

`pin`: PIN for O19 login. (Mandatory)

`username`: Username for O19 login. (Mandatory)


### 4. Default demographic / provider details (Mandatory)

workflow-config.yaml

#default values
default_values:
  default_provider_tagging_id:
    127
  default_unidentified_patient_tagging_id:
    285
  default_unidentified_patient_tagging_name: >
    CONFIDENTIAL, UNATTACHED
  default_unidentified_patient_tagging_dob: >
    2010-02-28
  default_category: >
    Miscellaneous

The `default_provider_tagging_id` in `default_values` is used to tag the provider by default for all the document types.

The values `default_unidentified_patient_tagging_id`, `default_unidentified_patient_tagging_name`, and `default_unidentified_patient_tagging_dob` will be used to tag the document to a demographic if the LLM is unable to find the correct demographic from the O19.
You can set this based on your O19.


# LLM Setup for O19

### AI configuration for interacting with the AI-MOA service.
ai:
  uri: https://localhost:3334/v1/chat/completions  # URI endpoint for AI model interactions.
  verify-HTTPS: false # Set this to true to verify the SSL certificates for LLM api's.

`uri`: URI endpoint for AI model (Mandatory)

`verify-HTTPS`: To verify the SSL certificates for LLM api's.

### LLM (Large Language Model) configuration, including model parameters for AI interactions.
llm:
  character: Assistant  # Character or role the AI model will take (Assistant).
  chat_template: '{{ bos_token }}{% for message in messages %}{% if (message[''role'']
    == ''user'') != (loop.index0 % 2 == 0) %}{{ raise_exception(''Conversation roles
    must alternate user/assistant/user/assistant...'') }}{% endif %}{% if message[''role'']
    == ''user'' %}{{ ''[INST] '' + message[''content''] + '' [/INST]'' }}{% elif message[''role'']
    == ''assistant'' %}{{ message[''content''] + eos_token}}{% else %}{{ raise_exception(''Only
    user and assistant roles are supported!'') }}{% endif %}{% endfor %}'
  model: /models/Mistral-7B-Instruct-v0.3.Q8_0.gguf  # Path to the model file being used.
  temperature: 0.1  # Temperature for controlling the randomness of model responses.
  top_p: 0.1  # Top-p sampling for controlling diversity of responses (related to nucleus sampling).


`model`: Path to the model file being used. (Mandatory)

For better results leave other LLM configurations as it is.

Please read [llm-container.md](llm-container.md) for more details

# 5. Other details

config.yaml

### AI-MOA document processor configuration.
aimoa_document_processor:
  type: o19  # Type of document processor being used, 'o19' or 'local'.

`type`: Type of document processor being used, 'o19' or 'local'.

### Inbox configuration.
inbox:
  pending: 99999999  # Last processed file ID in the inbox, should be set to your last processed file in the inbox.

`pending`: Last processed file ID in the inbox, should be set to your last processed file in the inbox. (Mandatory)

### Lock configuration, to control access to shared resources.
lock:
  status: false  # Indicates whether a lock is active or not (false means no lock).

status: Indicates whether a lock is active or not (false means no lock). Set this to false if the AI-MOA is giving message like `Lock is set`. If the `lock` is set it wont process any files unless it set to `false`. (Mandatory)

### OCR (Optical Character Recognition) configuration, specifying the device and settings for document scanning.
ocr:
  device: cuda:0  # Device used for OCR processing.
  enable_gpu: true  # Whether to enable GPU support for OCR (faster processing).
  page_limit: 20  # Maximum number of pages to process in OCR; if the document exceeds this limit, additional pages will be ignored.


`device`: Device used for OCR processing. 

`enable_gpu`: Whether to enable GPU support for OCR (faster processing).

`page_limit`: Maximum number of pages to process in OCR; if the document exceeds this limit, additional pages will be ignored.


### Chrome browser configuration for headless operation.
chrome:
  options:
    headless: false  # Whether to run Chrome in headless mode (without GUI). False means it will run with a GUI.

`headless`: Whether to run Chrome in headless mode (without GUI). False means it will run with a GUI.