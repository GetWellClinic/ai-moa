# AI-MOA Security Configuration Guide #
*Copyright © 2024 by Spring Health Corporation, Toronto, Ontario, Canada*<br />
*LICENSE: GNU Affero General Public License Version 3*<br />
**Document Version 2026.01.30**

## Introduction ##

AI-MOA was designed with privacy and security in mind. It gives the control of privacy and security back to the clinic as the installer/user, by reducing the risks of third-party data leaks, and secondary use of data. The application is intended and designed to be installed all locally, including the AI-MOA code, the large language model (LLM) engine, the LLMs itself, the OCR, and docker containers. Communication between the systems are all done locally (within the same server/virtual machine/internal network) and using SSL/TLS when required. External communication with an EMR is conducted as a normal authenticated/secured human user, through encrypted SSL/TLS web connections. All patient data is processed locally and within memory, is not saved on local disks, and discarded when the process is completed.

In order to remain compliant with the privacy and security standards of AI-MOA, the following best practices are recommended for your installation of AI-MOA. We are not responsible for any incorrect setup, misuse, or errors created by you when you do not follow the recommended configuration parameters.

## Release and Waiver ##

The information and software provided here is provided as is, and not to be construed as a service agreement, guarantee, nor a contract. We do not warrant the reliability, privacy, or security of your installation of AI-MOA. By installing and using AI-MOA, you are assuming the risks and liability under you and your organization.

We provide the following Security Configuration documentation for your convenience and reminder.

## Secure your Local Network ##

The local internal network that you plan on installing AI-MOA must have it's devices and network secured. It must be a trusted network, with the appropriate processes, controls, and procedures for data systems and human personnel that use the system. This is standard best-practices for any organization.

	- Protect your local network with an enterprise-grade firewall (ie. pfSense)
	- Install anti-virus and malware endpoint protection on all your devices on your internal network that humans use
	- Keep your systems up-to-date with patches
	- Use VPN when appropriate between networks that cross the Internet
	- Ensure that only trusted personnel, entities, and devices access the local network through authentication methods such LDAP with user directory services, encrypted password protected Wifi access, MAC address restrictions, network segmentation with routers, switches, and DNS.
	- Ensure your human personnel are authorized to use the local network and have been trained with proper process and procedures and protect their user accounts and password, preferably using two-factor authentication methods when accessing systems from the external.
	
## Secure your Server ##

AI-MOA was intended to be installed on a server within your physical protected premise, and within your protected internal network.

	- Physically secure your server by putting it in a room/closet with a locked door, accessible only by trusted entities of your organization that follow your processes and procedures.
	- The server or virtual machine on which the AI-MOA is to be installed should be a standalone instance, minimizing other applications that may be running on the server, and that may be access by other users for other purposes.
	- Only yourself (physician IT expert) or trusted IT administrators should have user accounts and passwords to access this server which contains EMR authentication details in configuration files. The root access and credentials must be protected an known only to yourself or a trusted IT administrator.
	- Ensure that the AI-MOA configuration files and their directories must be protected and not shared with anyone. Use proper Linux file and directory permissions to limit access to only specific users or groups.
		```e.g. -rwxr-x---	aimoa aimoa```
	- Protect and provide access to the server only through a physical console, or through SSH and VPN.

## Co-locate containers, packages on the same server ##

Install all packages and containers within the same server or virtual machine.

	- Install the AI-MOA code, the OCR container, and the LLM container on the same server or virtual machine. This ensures that communication between these parts are secured.
	- Download and use the large language models only locally on the machine.

## Use SSL/TLS ##

Configure the AI-MOA parameters and docker containers to use SSL/TLS

	- Follow the detailed installation and configuration instructions provided in this repository to enable and use SSL/TLS for the EMR, the OCR container API, and the LLM engine docker container.

## Use generic or obfuscated filenames for PDFs ##

To further protect privacy, configure your other external process that ingest PDFs from faxes, scans, or from the EMR to use generic or obfuscated filenames (not patient names). The log files on AI-MOA do not record any details of the PDF contents, however, it does list the filenames in the logs for error tracking purposes. To prevent inadvertant exposure of PHI, please do not name filenames with PHI identifiers.

## Use of cloud hosted virtual machines ##

AI-MOA was not intended for cloud hosted virtual machine installation. If you do choose this route, we recommend that the instance is a virtual private cloud that has firewall protection, and VPN access with private keys. Similar to the above mentioned policies and procedures must be maintained for your organization that control and has direct oversight of this VPC.

We also do not recommend separating the LLM or OCR components, unless you can ensure the privacy and security of offloading the LLM or OCR components under the same standards. This is out of scope of this document.


