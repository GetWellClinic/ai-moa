# Aimee AI (AI-MOA) #
*Copyright © 2024 by Spring Health Corporation*
*Toronto, Ontario, Canada*
LICENSE: GNU Affero General Public License Version 3

*Document Version 2024.12.08*

### Introduction: ###

Aimee AI is a sweet, polite, and helpful medical office assistant that sorts, labels, describes the content of documents,
tags to ordering provider, and attaches faxes/scans to the patient's chart in the EMR. We have developed her as
an AI-MOA (AI Medical Office Assistant) that is locally hosted so no private data leaves the server.

### Requirements: ###

**Hardware**
- 50 GB hard drive space
- 32 GB RAM memory
- NVIDIA RTX video card, minimum 12 GB VRAM

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


### Installation ###

**Be sure to change working directory to ""gwc-aimee"" where this readme.md and installation files are stored when running the installation files.**

1. Install Ubuntu 22 LTS

**Notes:**
If you plan on installing this in a VM such as on ProxMox VE, here are some tips:
- Enable virtualization on the bare metal machine in the BIOS
- Enable IOMMU in BIOS
- Enable [PCI passthrough](https://pve.proxmox.com/wiki/PCI_Passthrough) for Proxmox VE. This is a helpful Youtube [instructional video](https://www.youtube.com/watch?v=TWX3iWcka_0)

2. Install NVIDIA RTX video card drivers

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

3. Install NVIDIA Toolkit Container

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

4. Install Docker and Docker Compose

Follow online instructions to install Docker and Docker Compose.

Or

Use our custom "install-docker.sh" scrip to install automatically:
```
sudo ./install-docker.sh
```

5. Configure Docker to use NVIDIA Container Toolkit
```
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

6. Install AI LLM Container

This installed the default AI Lare Language Model Docker Container for AI-MOA.
```
sudo ./install-llm.sh
```

7. Install Aimee AI (AI-MOA)

This installs "Aimee AI" version of AI-MOA, by setting up custom settings and prerequisites.
```
./install-aimoa.sh
```

8. Install *Aimee AI* as a system service (Recommended)

This optional step, installs *Aimee AI* as a system service that automatically starts at system startup/reboot.
If you install this option, both the LLM Container and AI-MOA will start in the background and keep running.

Install "Aimee AI" as a sytem service
```
./install-aimoa.sh
```


### Configuration ###

To configure your *Aimee AI*, please edit the parameters in the following configuration files.
```
sudo nano ../config/config.yaml
sudo nano ../src/workflow-config.yaml
```

1. Edit "../config/config.yaml" file

Particularly, pay attention to the section on "emr" that is unique to your EMR server.
```
emr:
	base_url:
	username:
	password:
	pin:
```

When you are ready to process documents, edit the "../src/workflow-config.yaml" file to the last document
in your EMR from where you want to start AI-MOA to start processing documents.
The default "pending: 9999999" has been set at a very unlikely high number to prevent default installations
from processing live documents until you are ready.

To find out what is the last document uploaded:
- upload a test PDF to InBox via "Doc Upload".
- click on the star beside the InBox* which lists all the Unassigned documents.
- view the latest uploaded document, usually at the top of the list "Not, Assigned (NEW)"
- examine the URL and look for "&segmentID=####", this number is the document ID.
- enter this document ID as the "pending" number
```
inbox:
	pending: #######
```
** WARNING ** Once you save this config.yaml file with the new pending ###,
your AI-MOA will likely start processing the InBox PDF documents !

** Check if there is a lock on config.yaml file: **
During processing, there is "lock:status:true" on the config files. However, this may sometimes be left on
inadvertantly and prevent the AI-MOA from processing the next file.
Sometimes, you may need to reset the "lock:status:false".
```
lock:
	status: false
```

2. Edit "../config/provider_list.yaml" file

Once you run AI-MOA once, it will attempt to automatically upload a Report by Template and generate
a SQL search to extract the provider names and provider_id from your EMR.
It will save to a YAML file, which AI-MOA will use to match to names in documents.

To improve accuracy, edit the YAML file to delete extraneous or unneccessary providers that AI-MOA
does not need to match documents to that name. If there are too many similar providers, it can
confuse the LLM.

```
sudo nano ../config/provider_list.yaml
```

If you do not see this file, wait, or check out the next steps to run AI-MOA manually at command line.


### Running *Aimee AI* manually by command line ###

You can run *Aimee AI* manually start/stop with command line.

Stop the Aimee AI system service (ai-moa.service)
```
sudo service ai-moa stop
```

Check Aimee AI system status
```
sudo service status
```

Start *Aimee AI* manually
```
./run-aimoa.sh

To exit/stop Aimee AI
Ctrl-C
```

**Watching the workflow.logs**

You can also watch realtime logs of AI-MOA.
```
./watch-aimoa-logs.sh

To exit/stop watching
Crtl-C
```


### Start/Stop LLM Container ###

The AI LLM Container runs separately in docker as llm-container and caddy.
If you installed AI-MOA as a system service with "./install-services.sh", then you do not
need to start/stop LLM Container manually.

To stop the LLM Container manually:
```
sudo ./stop-llm.sh
```

To start the LLM Container manually:
```
sudo ./run-llm.sh
````

### Troubleshooting ###

#### Uninstalling Aimee AI ####

To remove "Aimee AI" from running as a system service:
```
sudo ../uninstall-aimoa.sh
```

#### Fixing Permissions ####

Sometimes, Aimee AI won't run propertly because the permission for user:group are not set properly.

Fix this by running:
```
sudo ./fix-aimoa.sh
```

#### AI-MOA is running, but no documents being process ####

This may happen because of a file lock on config.yaml

Edit config.yaml and remove file lock by setting "lock:status:false"
```
sudo nano ../config/config.yaml
```
Change setting to "false"
```
lock:
	status: false
```


## Special Thanks ##

This project was made possible through Conestoga College, in part, with funding from
NSERC Applied Research and Technology Partnership Grant
and
Get Well Clinic | Spring Health Corporation


