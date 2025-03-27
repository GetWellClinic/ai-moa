# Aimee AI (AI-MOA) #
## Linux Installation ##
*Copyright © 2024 by Spring Health Corporation, Toronto, Ontario, Canada*<br />
*LICENSE: GNU Affero General Public License Version 3*<br />
**Document Version 2025.03.26**
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
- 16 GB RAM system memory
- NVIDIA RTX video card, minimum 12 GB VRAM

*Recommended*
- 50 GB hard drive space
- 24 GB RAM system memory
- NVIDIA RTX 4060Ti video card, 16 GB VRAM

**Software**
- Ubuntu Server LTS (ie. Ubuntu 22 LTS)
- Python 3.10+ (pre-installed with Ubuntu 22 LTS)
- gcc installed (pre-installed with Ubuntu 22 LTS)
- Git installed
- NVIDIA video card drivers installed
- NVIDIA Container Toolkit drivers installed
- Python pip package manager installed
- Docker installed
- Docker Compose installed
- google-chrome installed

**Accounts**
- Github [https://github.com](https://github.com) user account and personal private access token generated
- Hugging Face [https://huggingface.co](https://huggingface.co) user account and personal private access token generated (Optional)


## Installation (for Linux) ##

**Be sure to change working directory to "install" where this readme.md and installation files are stored, before executing the installation files.**

### 1. Install Ubuntu 22 LTS ###

**Notes:**
If you plan on installing this in a VM such as on ProxMox VE, here are some tips:
- Enable virtualization on the bare metal machine in the BIOS
- Enable IOMMU in BIOS
- Enable [PCI passthrough](https://pve.proxmox.com/wiki/PCI_Passthrough) for Proxmox VE. This is a helpful Youtube [instructional video](https://www.youtube.com/watch?v=TWX3iWcka_0)

### 2. Clone the AI-MOA repository from Github ###

You will need to have your Github user name and a personal access token (generated from your account on Github). Github no longer allows 'git clone' access with passwords, and must use an access token generated from your user account online from Github.
```
cd /opt
sudo git clone https://github.com/getwellclinic/ai-moa.git
cd /opt/ai-moa
```

Change the ownership of files to your username:
```
sudo chown {username} /opt/ai-moa/* -R
```

**Set file permissions to enable run installation scripts**
```
cd /opt/ai-moa/install
ls -l -h
sudo chmod ug+x *.sh
sudo chmod g-x install*
sudo chmod g-x uninstall*
```

Change working directory to "install" for accessing the installation scripts:
```
cd /opt/ai-moa/install
ls -l -h
```

### 3. Install NVIDIA RTX video card drivers ###

Install your GPU in the PCIe slot, boot up your server, and install the video card drivers for your machine.

**Install NVIDIA Video Driver**

Check for NVIDIA video card drivers
```
sudo apt-get update
sudo apt-get install ubuntu-drivers-common
sudo ubuntu-drivers devices
```

Select the best driver to install. Pick the latest recommended one. (ie. nvidia-driver-550)

```
sudo apt-get install nvidia-driver-550
```

Reboot the server for the changes to take effect.
```
sudo shutdown -r now
```

Once system is rebooted, check to see if NVIDIA RTX video card is installed:
``` 
nvidia-smi
```

*You should see something like this:*
```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.120                Driver Version: 550.120        CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU Name 		    Persistence-M | Bus-Id Disp.A 	   | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
| 0 NVIDIA GeForce RTX 4060 Ti Off 	  |  00000000:06:10.0 Off  |		      N/A |
|  0%   49C    P8             17W /  165W |   200MiB /  16380MiB   |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|											  |
+-----------------------------------------------------------------------------------------+
```

### 4. Install NVIDIA Toolkit Container ###

Add the Repository for NVIDIA Container Toolkit
```
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \ && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \ sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \ sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

Update and install the latest nvidia-container-toolkit
```
sudo apt-get update
sudo apt-get install nvidia-container-toolkit
```

Restart the server for the installation to take effect.
```
sudo shutdown -r now
```

### 5. Install Docker and Docker Compose ###

Follow online instructions to install Docker and Docker Compose.

Or

Use our custom "install-docker.sh" script to install automatically:
```
sudo ./install-docker.sh
```

### 6. Configure Docker to use NVIDIA Container Toolkit ###
```
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 7. Install AI LLM Model for LLM Container ###

This installs the default AI Large Language Model for AI-MOA in LLM Container.
```
sudo ./install-model.sh
```

### 8. Install Aimee AI (AI-MOA) ###

This installs "Aimee AI" version of AI-MOA, by setting up custom settings and prerequisites.
```
sudo ./install-aimoa.sh
```

Add your username to the group "aimoa" so it can run AI-MOA:
```
sudo usermod -a -G aimoa {username}
```

### 9. Install *AI-MOA* as a system service (for automatic production use)###

This step installs *AI-MOA* as a system service that automatically starts at system startup/reboot.
If you install this option, both the LLM Container and AI-MOA will start in the background and keep running.

Option 1: Install one workflow "AI-MOA" as a system service (minimum 12 GB VRAM GPU)
- PendingDocs default workflow processing only (full tagging and filing)
- You can customize the default config.yaml to process other queues like IncomingDocs Fax/File/Mail instead.

*This will install ../install/services/ai-moa.service and ../install/services/llm-container.service as a system service in /etc/systemd/system/*
```
sudo ./install-services.sh
```

Option 2: Install the full *Aimee AI Suite* with multiple workflows as a system service (minimum 16 GB VRAM GPU)
- PendingDocs default workflow processing (full tagging and filing)
- IncomingDocs/Fax default workflow processing (full tagging and filing)
- IncomingDocs/File custom workflow processing (files the PDF to patient demographic only, does not tag providers or MRP)

*This will install ai-moa.service, ai-moa-incomingfax.service, ai-moa-incomingfile.service, and llm-container.service*
```
sudo ./install-services-aimee.sh
```

## (Optional) Install a test EMR with OSCAR v.19 Community Edition ##

If you wish to test out AI-MOA with your own free OSCAR v.19 CE, visit OscarGalaxy.org and follow the instructions on installing your own OSCAR.

[Installation instructions for OSCAR EMR v.19 Community Edition](https://oscargalaxy.org/knowledge-base/oscar-19-installation/)


## Configuration ##

To configure your *Aimee AI*, please edit the parameters in the following configuration files.
```
sudo nano ../config/config.yaml
sudo nano ../config/workflow-config.yaml
```

### 1. Edit "../config/config.yaml" file ###

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

### 2. Edit "../config/provider_list.yaml" file ###

Once you run AI-MOA once, it will attempt to automatically upload a Report by Template and generate
a SQL search to extract the provider names and provider_id from your EMR.
It will save to a YAML file, which AI-MOA will use to match to names in documents.

To improve accuracy, edit the YAML file to delete extraneous or unnecessary providers that AI-MOA
does not need to match documents to that name. If there are too many similar providers, it can
confuse the LLM. If some providers have middle names, you can create multiple entries for the same provider; one for
each variation of the first name that could include all or part of the middle name.

```
sudo nano ../config/provider_list.yaml
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

		
## Maintenance Operations ##

*Note: These commands and scripts should be run from subdirectory "/install"*
```
cd install
```

### Starting *AI-MOA* Services ###

If AI-MOA: Aimee AI has been installed as a service, ensure that the LLM Container service and the AI-MOA services are running:
```
sudo service llm-container status
sudo service ai-moa status
sudo service ai-moa-incomingfax status
sudo service ai-moa-incomingfile status
```
To start the services:
```
sudo service llm-container start
sudo service ai-moa start
sudo service ai-moa-incomingfax start
sudo service ai-moa-incomingfile start
```
To stop the services:
```
sudo service llm-container stop
sudo service ai-moa stop
sudo service ai-moa-incomingfax stop
sudo service ai-moa-incomingfile stop
```

### Running *Aimee AI* manually by command line ###

You can run *Aimee AI* manually start/stop with command line.

Stop the Aimee AI system service (ai-moa.service, ai-moa-incomingfax.service)
```
sudo service ai-moa stop
sudo service ai-moa-incomingfax stop
sudo service ai-moa-incomingfile stop
```

Check Aimee AI system status
```
sudo service ai-moa status
sudo service ai-moa-incomingfax status
sudo service ai-moa-incomingfile status
```

Start *Aimee AI* manually
```
./run-aimoa.sh
./run-aimoa-incomingfax.sh
./run-aimoa.-incomingfile.sh

To exit/stop Aimee AI
Ctrl-C
```

**Watching the workflow.logs**

You can also watch realtime logs of AI-MOA.
```
./watch-aimoa-logs.sh
./watch-aimoa-incomingfax-logs.sh
./watch-aimoa-incomingfile-logs.sh

To exit/stop watching
Ctrl-C
```

**AI-MOA Maintenance cron job**

- AI-MOA may accumulate browser temp files in /tmp directory.
- Depending on how a user updates or edits config files, misconfigured file permissions may cause unexpected errors when running the program with user prileges.

Consider installing the `aimoa-cron-maintenance.sh` script in sudoer's crontab to run periodically to fix permissions and clear the /tmp directory files accumulated by AI-MOA.

`sudo crontab -e`

Add the following to the crontab file:
```
1 * * * *	/opt/ai-moa/install/aimoa-cron-maintenance.sh
```

### Start/Stop LLM Container Manually ###

The AI LLM Container runs separately in docker as llm-container and caddy.
If you installed AI-MOA as a system service with "./install-services.sh", then you do not
need to start/stop LLM Container manually.

To start the LLM Container manually:
```
sudo service llm-container stop
sudo ./run-llm.sh
````
To stop the LLM Container manually:
```
sudo ./stop-llm.sh
```

### Upgrading AI-MOA from Github repository ###

You can upgrade to the latest code by doing a Git pull.

Backup the config directory just in case.
```
sudo cp /opt/ai-moa/config /opt/ai-moa/config.backup -r
```
Show the current working branch code (ie. main or dev)
```
cd /opt/ai-moa
git branch --show-current
```
Optional: change the working branch to another branch (ie. dev)
	```
	git checkout dev
	```
If you have modified code, you will need to stash any of your local changes before the Git pull overwrites your changes with the latest Github repo code. (Please note, this procedure will not replace your ../config/* files or delete your ../llm-container/models/* files.)
```
git stash
git pull
```
Fix the permissions for AI-MOA:
```
cd /opt/ai-moa/install
sudo chmod +x fix-aimoa.sh
sudo ./fix-aimoa.sh
```
You can then edit any files for your own custom settings. (ie. Custom ../src/run-aimoa.sh startup parameters, or ../llm-container/docker-compose.yml VRAM parameters)


## Troubleshooting and Tips ##

### Clinic workflow suggestions ###

AI-MOA is not 100% accurate in tagging documents to the correct patient.
We recommend having a human medical office administrator act as `default_error_manager_id` to review the tagged documents by AI-MOA daily for incorrect matches, and manually Refile the document to correct errors.
Unassigned or documents tagged to `default_unidentified_patient_tagging_id` will be also tagged to the medical office administrator (`default_error_manager_id`) to review in their InBox.
A quick way to also review tagged documents is to run a Search in InBox for All documents recently uploaded within a date range (ie. in the last day). The reviewer can use Rapid Review or Preview to review all the AI-MOA work. Pay attention to "Unassigned, Unassigned" documents; and also confirm that the patient name in the document corresponds to the correct demographic tagged in EMR. The reviewer can click "Acknowledge or Next" to confirm that it has been checked by a human.
Any incorrect documents can be sent to Refile and manually corrected through the Incoming Docs document manager.

### Uninstalling Aimee AI ###

To remove "Aimee AI" from running as a system service:
```
sudo ./uninstall-services.sh
```

### Fixing Permissions ###

Sometimes, Aimee AI won't run properly, and your get permission errors in the log, because the permission for user:group are not set properly.

Fix this by running:
```
sudo ./fix-aimoa.sh
```

### AI-MOA is running, but no documents being processed ###

This may happen because of a file lock on config.yaml

Stop AI-MOA first before editing the config.yaml file
```
sudo service ai-moa stop
sudo service ai-moa-incomingfax stop
sudo service ai-moa-incomingfile stop
```

Edit config.yaml and remove file lock by setting "lock:status:false"
```
sudo nano ../config/config.yaml
sudo nano ../config/config-incomingfax.yaml
sudo nano ../config/config-incomingfile.yaml
```
Change setting to "false"
```
lock:
	status: false
```

Restart the AI-MOA service
```
sudo service ai-moa start
sudo service ai-moa-incomingfax start
sudo service ai-moa-incomingfile start
```

### AI-MOA is able to log-in but times out when attempting to retrieve Pending documents in EMR ###

This is sometimes caused by a delay in retrieving too many "Active" documents in the Pending queue. You can check how many documents have not been acknowledged yet in "InBox -> Pending Docs -> Default queue".
To reduce the time for the EMR website to load the list of documents, you can increase the speed of the EMR (increase CPU, increase memory), or you can File/Acknowledge all the stale documents in Pending Docs.
A fast way of bulk setting all stale documents to "Inactive" is through the database. If you have access to the database, you can run these commands:
```
SELECT * FROM queue_document_link WHERE status="A";
UPDATE queue_document_link SET status="I" WHERE status="A" and document_id<######;
```



## Special Thanks ##

This project was made possible through Conestoga College, in part, with funding from
NSERC Applied Research and Technology Partnership Grant
and
Get Well Clinic | Spring Health Corporation


