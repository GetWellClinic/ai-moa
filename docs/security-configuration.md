# AI-MOA Security Configuration Guide #
*Copyright © 2026 by Spring Health Corporation, Toronto, Ontario, Canada*<br />
*LICENSE: GNU Affero General Public License Version 3*<br />
**Document Version 2026.02.09**

## Introduction ##

AI-MOA was designed with privacy and security in mind. It gives the control of privacy and security back to the clinic as the installer/user, by reducing the risks of third-party data leaks, and secondary use of data. The application is intended and designed to be installed entirely locally, including the AI-MOA code, the large language model (LLM) engine, the LLMs themselves, the OCR, and docker containers. Communication between the systems is all done locally (within the same server/virtual machine/internal network) and using SSL/TLS when required. External communication with an EMR is conducted as a normal authenticated/secured human user, through encrypted SSL/TLS web connections. All patient data is processed locally and within memory, is not saved on local disks, and discarded when the process is completed.

In order to remain compliant with the privacy and security standards of AI-MOA, the following best practices are recommended for your installation of AI-MOA. We are not responsible for any incorrect setup, misuse, or errors created by you when you do not follow the recommended configuration parameters.

## Disclaimer ##

The information and software provided here is provided as is, and not to be construed as a service agreement, guarantee, nor a contract. We do not warrant the reliability, privacy, or security of your installation of AI-MOA. By installing and using AI-MOA, you are assuming the risks and liability assumed by you and your organization.

We provide the following Security Configuration documentation for your convenience and reminder.

## Secure your Local Network ##

The local internal network that you plan on installing AI-MOA must have it's devices and network secured. It must be a trusted network, with the appropriate processes, controls, and procedures for data systems and human personnel that use the system. This is standard best-practices for any organization.
- Protect your local network with an enterprise-grade firewall (i.e. pfSense)
- Install anti-virus and malware endpoint protection on all your devices on your internal network that humans use
- Keep your systems up-to-date with patches
- Use VPN when appropriate between networks that cross the Internet
- Ensure that only trusted personnel, entities, and devices access the local network through authentication methods such LDAP with user directory services, encrypted password protected Wifi access, MAC address restrictions, network segmentation with routers, switches, and DNS.
- Ensure your human personnel are authorized to use the local network and have been trained with proper process and procedures and protect their user accounts and password, preferably using two-factor authentication methods when accessing systems from the external.
	
## Secure your Server ##

AI-MOA was intended to be installed on a server within your physically protected premises, and within your protected internal network.
- Physically secure your server by putting it in a room/closet with a locked door, accessible only by trusted entities of your organization that follow your processes and procedures.
- The server or virtual machine on which the AI-MOA is to be installed should be a standalone instance, minimizing other applications that may be running on the server, and that may be access by other users for other purposes.
- Only yourself (physician IT expert) or trusted IT administrators should have user accounts and passwords to access this server which contains EMR authentication details in configuration files, and log files. The root access and credentials must be protected and known only to yourself or a trusted IT administrator.
- Ensure that the AI-MOA configuration files, log files, and their directories must be protected and not shared with anyone. Use proper Linux file and directory permissions to limit access to only specific users or groups.
	```
	e.g. -rwxr-x---	aimoa aimoa
	```
- Protect and provide access to the server only through a physical console, or through SSH and VPN.
- Consider whole-disk encryption for the server/VM.

## EMR Credentials Considerations ##

When configuring the AI-MOA user in the EMR, use a separate user account that is not known to anyone else.
- Assign the user role to the lowest required permissions (i.e. "aimoa" role, not an admin role). 
- Always assign the minimum required privileges for aimoa role to limit access. The aimoa role should only have the permissions necessary for AI-MOA to function (write, read, and update for the specific objects).
- Periodically review roles and privileges to ensure that they remain aligned with your organization’s security policies and that no unnecessary permissions are granted.
- Change/rotate the password regularly.

## Co-locate containers, packages on the same server ##

Install all packages and containers within the same server or virtual machine.
- Install the AI-MOA code, the OCR container, and the LLM container on the same server or virtual machine. This ensures that communication between these parts are secured.
- Download and use the large language models only locally on the machine.

## Use SSL/TLS ##

Configure the AI-MOA parameters and docker containers to use SSL/TLS
- Follow the detailed installation and configuration instructions provided in this repository to enable and use SSL/TLS for the EMR, the OCR container API, and the LLM engine docker container.

## Use generic or obfuscated filenames for PDFs ##

To further protect privacy, configure your other external processes that ingest PDFs from faxes, scans, or from the EMR to use generic or obfuscated filenames (not personal health information or PHI). The log files on AI-MOA do not record any details of the PDF contents; however, they do list the filenames in the logs for error tracking purposes. To prevent inadvertent exposure of PHI, please do not give file names with PHI identifiers.
As a safety measure, you may want to routinely delete log files.

## Use of cloud hosted virtual machines ##

AI-MOA was not intended for cloud hosted virtual machine installation. If you do choose this route, we recommend that the instance is a virtual private cloud that has firewall protection, and VPN access with private keys. Similar to the above mentioned policies and procedures must be maintained by your organization, which controls and has direct oversight of this VPC.

We also do not recommend separating the LLM or OCR components, unless you can ensure the privacy and security of offloading the LLM or OCR components under the same standards. This is out of scope of this document.

## Considerations for Backup Procedures ##

If you use some backup system for your server, be aware of how and where your backup stores the backup files. Ensure that the backup system is encrypted at rest, and that the transfer is through encrypted tunnels. It is best if you are able to delete/remove the password credentials in the AI-MOA configuration files before backup.
The log files contain PDF file names. If the filenames are labelled with sensitive information, you should delete the log files before backup.

## Database connections ##

AI-MOA does not provide a database. If you use the SQL database connection functionality, please ensure that the database is secured as per best-practices. For example, the SQL database can be installed on the same local VM host as AI-MOA, and allowing only localhost access. For external SQL database connections, consider enabling encrypted SQL server connections.

## Other config.yaml parameters ##

The following settings are also recommended for best security, and should be default settings:
- disable local storing of files
- disable logging of prompt output in the logs
- disable/mask filenames in the logs
- enable SSL/TLS for all outbound connections

## Using JSON option for filing documents ##

Enable the JSON function in the workflow-config.yaml workflow for a restricted trusted filing process, such as using it only on IncomingDocs/File queue, not the usual Fax ingestion queue. This allows for human selection of trusted documents to file (scanning and uploading to the EMR to the specific IncomingDocs/File queue) and allows AI-MOA to use the JSON feature only on that queue to avoid wrong tagging/labelling of PDFs.

## Clinic Process and Procedures ##

Although AI-MOA outputs likely perform on average better than a novice human medical office administrator who also makes mistakes, do not rely on AI-MOA to replace the usual human clinical administrative best practices. The outputs of AI-MOA are not 100%, just as human outputs are not 100%. Practice the Swiss Cheese Model of healthcare risk mitigation which recommends building multiple redundant checks and balances that allow a process pathway (in this case, AI-MOA is one, and human interventions and processes are another) so that system errors (the holes of multiple layers) do not line up, and are caught by each subsequent layer for check.

Always keep the "human in the loop": (Mandatory)
- Ensure that the parameter "error_manager" is correctly assigned to an actual human medical office administrator (MOA) who will review and manually correct unsure or incorrect outputs from AI-MOA.
- Assign a human MOA on a daily rotation/regular basis to conduct an EMR document Search for the past day's AI-MOA tagging results, and manually review ALL results for accuracy, and make edits/corrections as required.
- Continue clinic administrative best practices of human verification of patient demographic data (with viewing the healthcard and confirming contact details) before each clinical encounter point (i.e. every time patient checks in for an appointment).

## Enforcing Administrative Access Policy ##

1. Purpose

The purpose of this policy is to define the procedures governing administrative access to the AI-MOA host environment and to enforce role separation between system maintenance and operational oversight. This policy aims to minimize risks of insider threats, accidental misconfigurations, and unauthorized access to sensitive patient data by implementing controls over administrative privileges.

2. Scope

This policy applies to all personnel, contractors, and vendors who require administrative access to the AI-MOA host environment, including servers, virtual machines, and associated systems.

3. Administrative Access Control

Access Roles:
 - System Administrator (SysAdmin): Responsible for system maintenance, updates, patching, and infrastructure management. This role will not have access to operational oversight functions or patient data.
 - Operational Manager (OpManager): Oversees the day-to-day functionality of the AI-MOA system, including monitoring AI outputs, auditing logs, and ensuring compliance with clinical workflows.
 - Security Officer (SecOfficer): Responsible for reviewing system security, monitoring user activity, and ensuring the integrity of data and system access controls.

Role Separation:
 - System Administration: SysAdmins handle all technical aspects of the environment, including server maintenance, software updates, and configuration changes.
 - Operational Oversight: OpManagers handle day-to-day operations, monitor system performance, and verify outputs of the AI-MOA system.
 - Security & Auditing: SecOfficers maintain the security of the system by monitoring administrative access logs, reviewing audit trails, and ensuring access control procedures are followed.

4. Administrative Access Procedures

 - Least Privilege Access: Administrative access will be granted based on the principle of least privilege, ensuring that users only have the permissions necessary to perform their job functions.
 - Access Review and Approval: All access requests for administrative privileges must be submitted in writing and approved by both the SysAdmin and the Security Officer before access is granted.
 - Monitoring and Logging: All administrative access will be logged, and logs will be reviewed by the Security Officer on a monthly basis. Logs will include details of the actions taken, user identity, and timestamps.

5. Dual Control & Approval Mechanisms

 - Critical Actions: Any critical administrative actions (e.g., system configuration changes, access to sensitive data) must require dual approval: one from the SysAdmin and one from the Security Officer. These actions must also be documented and reviewed periodically.
 - Escalation Process: In the event of critical system issues or changes, the access of multiple authorized personnel will be required to ensure thorough review and verification of the decision-making process.

6. Periodic Access Review

 - Access Review Frequency: Administrative access rights will be reviewed every 6 months to ensure that only necessary privileges are maintained and that no unauthorized access has been granted.
 - Role Modifications: If a user's role or responsibilities change, their access privileges must be immediately reviewed and modified to reflect the new role.

7. Enforcement

Violations of this policy will result in disciplinary action, which may include, but are not limited to, revocation of administrative access and other actions as per company policy.

## Secure Deployment Guidelines ##

1. Role Separation in AI-MOA Deployment

To maintain the integrity and security of the AI-MOA environment, clear role separation between administrative tasks (system maintenance) and operational oversight will be enforced. The following roles are defined within the deployment environment:

 - System Administrator (SysAdmin): Manages the physical and virtual infrastructure, including server configuration, patching, and overall system health.
 - Operational Manager (OpManager): Oversees daily usage, verifying AI-MOA outputs, monitoring system performance, and addressing any operational issues.
 - Security Officer (SecOfficer): Ensures the security of the environment by auditing access logs, monitoring activity, and enforcing security protocols.

2. Access Procedures for AI-MOA Host Environment

 - Administrative Access: Admin access to the AI-MOA host environment will only be granted based on the principle of least privilege, where each user’s access is restricted to the minimum level of privilege required for their tasks.
 - Access Approval: Access to administrative functions will require approval from both the SysAdmin and the Security Officer. All requests for administrative access must be documented and reviewed.

3. Monitoring and Audit Trails

 - Logging of Administrative Access: All administrative access to the AI-MOA host environment will be logged. Logs will include:
	- User identity (and role)
	- Action taken (e.g., configuration change, file access)
	- Timestamp
	- Affected system component
 - Audit Review: Logs will be reviewed by the Security Officer on a monthly basis to detect unauthorized access or abnormal activities. Any anomalies will be flagged for further investigation.

4. Backup and Encryption of Access Logs

 - Log Backup: All logs related to administrative access, including system maintenance and operational oversight, will be encrypted at rest and backed up in accordance with the clinic's backup procedures.
 - Log Retention: Logs will be retained for at least 12 months to support auditing and security investigations.

5. Security of Administrative Accounts

 - SSH Key Management: SSH keys used for remote access must be managed securely, and all keys should be regularly rotated to minimize risk.

6. Role-Specific Configuration and Deployment

 - Secure Deployment: The deployment of AI-MOA should always occur within a secure environment, preferably on an isolated server or virtual machine with access restricted to authorized personnel.
 - Update and Patch Management: AI-MOA components, including the host operating system, containers (OCR, LLM), and related infrastructure, must be updated regularly with security patches.

7. User Training

 - Administrator Training: All system administrators, operational managers, and security officers will undergo security training to ensure they understand their roles and responsibilities in safeguarding patient data and clinic operations.

8. Enforcement and Auditing

 - Compliance: Non-compliance with the guidelines will result in corrective actions, which may include, but are not limited to, revocation of administrative access and other actions as per company policy.
 - Audit and Review: The deployment and access protocols will be audited at least once every 12 months by an external third-party security reviewer to ensure compliance with the guidelines and best practices.