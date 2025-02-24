# Aimee AI (AI-MOA) #
## Windows Installation ##
*Copyright © 2024 by Spring Health Corporation, Toronto, Ontario, Canada*<br />
*LICENSE: GNU Affero General Public License Version 3*<br />
**Document Version 2025.02.24**
<p align="center">
  <img src="https://getwellclinic.ca/images/GetWellClinic/Logos-Icons/AimeeAI-pc.png" alt="Aimee AI">
</p>

## Introduction: ##

Aimee AI is a helpful medical office assistant that sorts, labels, describes the content of documents,
tags to ordering provider, and attaches faxes/scans to the patient's chart in the EMR. Aimee AI operates locally,
so no private data leaves the server.

*"Aimee" was the name of an actual MOA who once worked with us at Get Well Clinic. We pay tribute to the many MOA's
who have worked at our clinic, who managed to keep their cool in the face of patient suffering, and still provided
excellent customer service in this demanding and thankless occupation. We hope this project will help reduce the
healthcare team's administrative burden, so we can dedicate ourselves to the very human activity that is healthcare.*

### Requirements: ###

**Hardware**

*Minimum*
- 15 GB disk space
- 24 GB RAM memory
- NVIDIA RTX video card, minimum 12 GB VRAM

*Recommended*
- 50 GB hard drive space
- 32 GB RAM memory
- NVIDIA RTX 4060 video card, 16 GB VRAM

**Software**
- Windows 10+
- Windows Subsystem for Linux (WSL 2)
- Python 3.10+
- Git installed
- NVIDIA video card drivers installed
- NVIDIA Container Toolkit drivers installed
- Python pip package manager installed
- Docker installed
- Docker Compose installed
- Google Chrome browser installed

**Accounts**
- Github [https://github.com](https://github.com) user account and personal private access token generated
- Hugging Face [https://huggingface.co](https://huggingface.co) user account and personal private access token generated (Optional)


## Installation (for Windows) ##

### 1. Install Python 3.10+ ###

Python, PyTorch, and CUDA support needs to tightly matched with versions that are compatible with each other. For example, Pytorch on Windows only support Python 3.9-3.12 (as of Feb 2025). Python 2.x is not supported.

*Check Python, PyTorch, CUDA Toolkit version compatibility*

https://pytorch.org/get-started/locally/

*CUDA Toolkit Downloads, for your reference*

https://developer.nvidia.com/cuda-downloads

For example, a working combination is: Python 3.10, PyTorch 2.2, and CUDA 11.8

AI-MOA was tested to work on Python 3.10. You may install higher versions of Python, but be sure that Pytorch is supported for that version and that there is also an NVIDIA CUDA Toolkit available for that version as well. You can install also multiple versions of Python on the same Windows, just reference the version you want to use when invoking a python script.

Download and install the latest Python 3.10.x:

https://www.python.org/downloads/windows/

*Tip: Create a folder C:\Tools, and install Python in a subdirectory under Tools ie. C:\Tools\Python3.10
This makes it easier to reference the full path of python.exe when using command line or adding it to Windows Task Scheduler.*

Be sure to add Python to your PATH in Windows Environment variables so that invoking the `python` command by command prompt anywhere will run a default Python without requiring to enter the full path of where Python is installed.

### 2. Install virtualenv package for creating Python virtual environments ###

Open a Command Prompt in Windows (as administrator).

```
pip install virtualenv
```

### 3. Install Git for Windows ###

Download and install Git for Windows:

https://git-scm.com/downloads/win

### 4. Install Google Chrome ###

Download and install Google Chrome:

https://www.google.com/chrome

### 5. Update NVIDIA Graphics Card Drivers ###

Be sure to update your NVIDIA Graphics Card Drivers:

https://www.nvidia.com/en-in/drivers/nvidia-update/

You may or may not need an NVIDIA CUDA Toolkit 11.8:

https://developer.nvidia.com/cuda-11-8-0-download-archive

Check the status of your NVIDIA graphics card:
```
nvidia-smi
```

You should see something like this:
```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 572.47                 Driver Version: 572.47         CUDA Version: 12.8     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                  Driver-Model | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 4060 Ti   WDDM  |   00000000:01:00.0  On |                  N/A |
|  0%   49C    P8             14W /  165W |     484MiB /  16380MiB |      1%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
```

### 6. Install Docker and Docker Compose for Windows ###

Download and install Docker:

https://docs.docker.com/desktop/setup/install/windows-install/

### 7. Enable Docker Desktop for Windows to support WSL 2 (Windows Subsystem for Linux) GPU Paravirtualization (GPU-PV) on NVIDIA graphics cards ###

Read these instructions and install Windows Subsystem for Linux (WSL 2) and enable WSL2 backend support in Docker Desktop:

https://docs.docker.com/desktop/features/gpu/

### 8. Clone the AI-MOA repository from Github ###

You will need to have your Github user name and a personal access token (generated from your account on Github). Github no longer allows 'git clone' access with passwords, and must use an access token generated from your user account online from Github.
```
cd \
cd opt
sudo git clone https://github.com/getwellclinic/ai-moa.git
cd ai-moa
```

Change working directory to "install" for accessing the installation scripts:
```
cd \
cd opt\ai-moa\windows
dir
```

### 9. Install AI LLM Model for LLM Container ###

Download the AI LLM from Huggingface and copy to `opt\aimoa\llm-container\models\` directory:

https://huggingface.co/RichardErkhov/mistralai_-_Mistral-7B-Instruct-v0.3-gguf

*(Choose the Q8 version "Mistral-7B-Instruct-v0.3.Q8_0.gguf")*

Or you can execute this batch installation script to download and install the default AI Large Language Model for AI-MOA in LLM Container.
```
cd \
cd opt\ai-moa\windows
.\install-model.bat
```

### 10. Install Aimee AI (AI-MOA) ###

This installs "Aimee AI" version of AI-MOA, by setting up custom settings and prerequisites.
```
.\install-aimoa.bat
```

### 11. Create a Windows Task Scheduler for Aimee AI ###

If you want AI-MOA to start automatically on Windows startup, and run continuously, create Windows Tasks Schedules.

Open "Windows Task Schedule" and create a new scheduled task with the following parameters:

Create a Task: "LLM-Container"
- Security Options: run task as an administrator account
- Triggers: "At startup"
- Actions: Program/script "C:\opt\ai-moa\windows\run-llm.bat"
- Settings: Disable "Stop the task if it runs longer than"; Enable "Run task as soon as possible after a scheduled start is missed"; If the task fails, restart every "5 minutes" for "3" times; If the task is already running, then the following rule applies: "Do not start a new instance".

Create a Task: "AI-MOA"
- Security Options: run task as an administrator account
- Triggers: "At startup"; Delay task for 30 seconds. 
- Actions: Program/script "C:\opt\ai-moa\windows\run-aimoa.bat"
- Settings: Disable "Stop the task if it runs longer than"; Enable "Run task as soon as possible after a scheduled start is missed"; If the task fails, restart every "5 minutes" for "3" times; Disable "Stop the task if it runs longer than"; If the task is already running, then the following rule applies: "Do not start a new instance".

Alternative: You can install AI-MOA "run-aimoa.bat" as a Windows Service (so it restarts if unexpected crashes). Consider https://nssm.cc/

**To start AI-MOA, be sure to manually start LLM-Container and AI-MOA in Windows Task Scheduler, or reboot Windows to see if it starts automatically.**



## (Optional) Install a test EMR with OSCAR v.19 Community Edition ##

If you wish to test out AI-MOA with your own free OSCAR v.19 CE, visit OscarGalaxy.org and follow the instructions on installing your own OSCAR.

[Installation instructions for OSCAR EMR v.19 Community Edition](https://oscargalaxy.org/knowledge-base/oscar-19-installation/)

## Configuration ##

To configure your *Aimee AI*, please edit the parameters in the following configuration files in a text editor:
```
..\config\config.yaml
..\config\workflow-config.yaml
```

### 1. Edit "..\config\config.yaml" file ###

Particularly, pay attention to the section on "emr" that is unique to your EMR server.
```
emr:
	base_url:
	username:
	password:
	pin:
```

When you are ready to process documents, edit the "..\config\workflow-config.yaml" file to the last document
in your EMR from where you want to start AI-MOA to start processing documents.
The default "pending: 9999999" and "incoming: '2125-01-01 00:00:00'" has been set at a very unlikely high number to prevent default installations from processing live documents until you are ready.

If using PendingDocs, to find out what is the last document uploaded:
- upload a test PDF to InBox via "Doc Upload".
- click on the star beside the InBox* which lists all the Unassigned documents.
- view the latest uploaded document, usually at the top of the list "Not, Assigned (NEW)"
- examine the URL and look for "&segmentID=####", this number is the document ID.
- enter this document ID as the "pending" number

If using IncomingDocs, just specify in a date and timestamp for PDF files to start processing from:
```
inbox:
	pending: #######
	incoming: '2125-01-01 00:00:00'
```
**WARNING** Once you save this config.yaml file with the new pending ###,
your AI-MOA will likely start processing the InBox PDF documents !

**Check if there is a lock on config.yaml file:**
During processing, there is "lock:status:true" on the config files. However, this may sometimes be left on
inadvertantly and prevent the AI-MOA from processing the next file.
Sometimes, you may need to reset the "lock:status:false".
```
lock:
	status: false
```

### 2. Edit "..\config\provider_list.yaml" file ###

Once you run AI-MOA once, it will attempt to automatically upload a Report by Template and generate
a SQL search to extract the provider names and provider_id from your EMR.
It will save to a YAML file, which AI-MOA will use to match to names in documents.

To improve accuracy, edit the YAML file to delete extraneous or unnecessary providers that AI-MOA
does not need to match documents to that name. If there are too many similar providers, it can
confuse the LLM. If some providers have middle names, you can create multiple entries for the same provider; one for
each variation of the first name that could include all or part of the middle name.

```
..\config\provider_list.yaml
```

If you do not see this file, wait, or complete the configuration steps and then start Aimee AI manually by command line (See section: Maintenance Operations)

### 3. Create new EMR user: AI, MOA ###

**Create AI MOA user in EMR**

Aimee AI will access the EMR with a user account you create for her.

1. Login to EMR
2. Administration -> Add a Provider Record:
	- Provider No: **200**
	- Last Name: AI
	- First Name: MOA
	- Sites Assigned: (select your site)
	- Status: Active
3. Administration -> Assign Role to Provider:
	- Find Provider No. **200** (MOA AI)
		- Add "doctor" role
		- Add "receptionist" role
	- Scroll to bottom: Update Primary EMR Role:
		- Select Provider: AI, MOA
		- Assign AI, MOA primary Role: **receptionist**
		- Click "Update Primary EMR Role" to save settings.
4. Administration -> Add a Login Record:
	- Create new user for Aimee AI
		- User Name: aimoa
		- Password: *********
		- Confirm: *********
		- Provider No: **200**
		- Expiry Date: (**uncheck box**)
		- Time Cycling Pin (2FA): **No**
		- Pin (remote) Enable: **Checkmark**/yes
		- Pin (local) Enable: (uncheck or check)
		- Force Password Reset: **No**
		- Save settings by clicking "Add Record"
5. Update "config.yaml" file with AI, MOA login information.
(Please note: be sure to secure the server installation from any unauthorized access or use.)

**Create CONFIDENTIAL, UNATTACHED patient demographic record in EMR**

Aimee AI will file documents that do not have any corresponding patient record in the EMR to a generic chart for audit, tracking, and recovery purposes. This allows you to find records that are unattached to an actual patient, and make corrections (reattach to correct file). You may also use this to file away advertisements and junk faxes. It is best practice to label the document with the document's patient name, so your staff can do a search in the Document Manager to retrieve it if it was a mistake to file it in "CONFIDENTIAL, UNATTACHED"

1. Login to EMR
2. Click "Search" for a patient.
	- Enter "confidential" and click "Search", to check if existing patient record named "CONFIDENTIAL, UNATTACHED"
	- If one exist, then note down the demographic number of this chart, to specify as the "default_unidentified_patient_tagging_name:" field in "workflow-config.yaml"
3. Create Demographic:
	- Click "Create Demographic" and create a new chart
		- Lastname: CONFIDENTIAL
		- Firstname: UNATTACHED
		- Health Card Type: Other
4. Update "workflow-config.yaml"
	- Note the Demographic Number for "CONFIDENTIAL, UNATTACHED" and enter it as the "default_unidentified_patient_tagging_name:" for the YAML file.

**Create missing Document Categories**

AI-MOA is developed for identify and tagging according to certain Document Category Types as defined in "workflow-config.yaml".
	Some category names are missing in the default EMR installation. Check for document category types and create these missing categories so you can see the labels that Aimee AI tag.

1. Login to EMR
2. Administration -> System Management -> Document Categories:
		- Under "Demographic Document Categories", Show "all or 100" categories
		- Check for the presence of this standard Document Categories, and "Add New" for any missing categories (or Update Status to make them "A" - Active)

	**AI-MOA Standard Document Categories**

	- advertisement
	- consent
	- consult
	- diagnostics
	- insurance
	- lab
	- legal
	- miscellaneous
	- notification
	- oldchart
	- *others*
	- pathology
	- pharmacy
	- photo
	- radiology
	- referral
	- request
	- requisition


## Troubleshooting and Tips ##

### Clinic workflow suggestions ###

AI-MOA is not 100% accurate in tagging documents to the correct patient. We recommend having a human medical office administrator act as `default_error_manager_id` to review the tagged documents by AI-MOA daily for incorrect matches, and manually Refile the document to correct errors. Unassigned or documents tagged to `default_unidentified_patient_tagging_id` will be also tagged to the medical office administrator (`default_error_manager_id`) to review in their InBox. A quick way to also review tagged documents is to run a Search in InBox for All documents recently uploaded within a date range (ie. in the last day). The reviewer can use Rapid Review or Preview to review all the AI-MOA work. Pay attention to "Unassigned, Unassigned" documents; and also confirm that the patient name in the document corresponds to the correct demographic tagged in EMR. The reviewer can click "Acknowledge or Next" to confirm that it has been checked by a human. Any incorrect documents can be sent to Refile and manually corrected through the Incoming Docs document manager.

### Manually Starting/Stopping Aimee AI ###

If AI-MOA is not running automatically as a Windows Task Scheduler, you can start and stop AI-MOA manually:

To Start Aimee AI:
```
cd windows
start-llm.bat
run-aimoa.bat
(Press Ctrl-C to stop AI-MOA)
```

To Stop AI LLM Container:
```
stop-llm.bat
```


## Special Thanks ##

This project was made possible through Conestoga College, in part, with funding from
NSERC Applied Research and Technology Partnership Grant
and
Get Well Clinic | Spring Health Corporation