# AI-MOA Security Hardening Guide #

## Introduction ##

AI-MOA was designed with privacy and security in mind. It gives control of privacy and security back to the clinic as the installer/user, by reducing the risks of third-party data leaks and secondary use of data. The application is intended and designed to be installed entirely locally, including the AI-MOA code, the large language model (LLM) engine, the LLMs themselves, the OCR, and Docker containers.

Communication between the systems is all done locally (within the same server/VM/internal network) and using SSL/TLS. External communication with an EMR is conducted as a normal authenticated/secured human user, through encrypted SSL/TLS web connections. AI-MOA is designed to minimize persistent storage of patient data and process data locally and primarily in memory wherever operationally feasible. Organizations deploying AI-MOA remain responsible for ensuring that operating systems, containers, logging systems, backups, and infrastructure are configured securely to prevent unauthorized retention or disclosure of protected information.

The following security, operational, and deployment requirements are mandatory for all production installations of AI-MOA. Improper setup, misuse, or failure to follow these requirements may compromise privacy, security, regulatory compliance, system integrity, and patient safety.

## Secure Your Local Network ##
- Protect your internal network with an enterprise-grade firewall.
- Use VM firewalls to restrict all unnecessary ports.
- Install antivirus and malware protection on all devices.
- Keep systems up-to-date with patches.
- Use VPN when appropriate for external connections.
- Restrict network access to authorized personnel and devices.
-Use two-factor authentication where possible.

 ## Secure Your Server ##
- Physically secure your server or VM.
- Minimize other applications on the AI-MOA host.
- Assign server access only to trusted IT personnel.
- Use strict Linux permissions for AI-MOA files (-rwxr-x--- aimoa aimoa).
- Access server only through physical console, SSH, or VPN.
- Consider full-disk encryption.

## EMR Credentials ##
- Use a dedicated EMR account with least privilege.
- Assign only necessary permissions for AI-MOA operations.
- Rotate passwords regularly and review roles periodically.

## Containers, Packages, and LLM/OCR Documentation ##
- Install AI-MOA, OCR, and LLM containers locally on the same server/VM.
- Always use the specific LLM and OCR versions referenced in the official documentation. Deviating from these versions may introduce compatibility issues or security vulnerabilities.
- Using an external LLM or OCR component involves downloading or connecting to software from sources that may not be verified, which could introduce significant security risks. Only officially vetted and approved LLM/OCR versions should be used to mitigate potential threats. AI-MOA does not perform this automatically. This configuration can only be performed manually, and any security risks associated with it are the responsibility of the IT administrator or the person in charge.

## Use SSL/TLS ##
AI-MOA enforces SSL/TLS for all communications, including the EMR interface, OCR API, and LLM container. Disabling or bypassing SSL/TLS may lead to compatibility issues and significant security vulnerabilities.

## PDF Handling and JSON Workflow ##
- Use generic or obfuscated filenames for PDFs; do not include PHI.
- Only ingest human-verified trusted PDFs.
- Enable JSON workflow for restricted trusted queues (IncomingDocs/File) only, to avoid mislabeling.

## Bulk Demographics (PIF) ##
- Only trusted SQL or CSV sources may be used.
- Human verification of bulk demographic record creation is mandatory.
- Document the source and maintain procedural records.

## Human-in-the-Loop ##
- Always assign an MOA as error_manager.
- Conduct multiple trial runs where humans check all outputs.
- Daily review by MOA and health providers of AI-MOA outputs.
- Ensure verification of demographics before each patient encounter.
- Ingested PDFs must be human-verified trusted documents.

## Administrative Access ##
- Role separation: SysAdmin, OpManager, SecOfficer.
- Least privilege, dual approval for critical actions.
- Monthly review of logs; access reviewed every 6 months.
- SSH key rotation and secure management.

## Backup and Recovery ##
- Encrypt backups at rest and in transit.
- Before performing any system backups, ensure that all sensitive credentials and confidential information in the AI-MOA configuration files are removed or redacted to prevent accidental exposure.
- Delete logs containing sensitive file names before backup.

## Deployment and Monitoring ##
- Isolated VM/server deployment with restricted access.
- Regular OS and container patching.
- Encrypted backup of access logs.
- Annual external audit recommended.
- Security training for all admins, operational managers, and security officers.


# Mandatory Deployment and Security Requirements #

The AI-MOA Security Hardening Guide, Administrative Access Policy, deployment procedures, and associated checklists constitute mandatory requirements for all production deployments of AI-MOA.

All clinics, healthcare organizations, IT administrators, and deployment personnel are required to review, implement, and maintain these controls prior to installation, integration with clinical systems, or processing of patient information.

These requirements define the minimum security, operational, and governance standards for AI-MOA deployments and are intended to reduce privacy, security, operational, and patient-safety risks.

Failure to implement these requirements may result in, but is not limited to:

- Increased cybersecurity and privacy risk
- Unauthorized access to patient information
- Regulatory non-compliance
- Data integrity issues
- Misconfiguration of AI-MOA components
- Unsafe clinical or operational outcomes

Organizations deploying AI-MOA are responsible for ensuring:

- All mandatory security controls are implemented
- Administrative access policies are enforced
- Human verification procedures are followed
- Required audits and reviews are completed
- Deployment and operational checklists are fully completed before go-live

AI-MOA should not be deployed into production environments unless all mandatory deployment, security, and operational requirements have been satisfied and documented.

# Mandatory Deployment Acceptance Checklist #

AI-MOA must not be deployed into production clinical environments until all items in this checklist have been completed, verified, and formally approved by the responsible organization.

## Infrastructure and Network ##
- Enterprise firewall configured
- VM/server firewall configured
- Unnecessary ports disabled
- VPN configured where required
- TLS/SSL enabled for all communications
- Operating system fully patched
- Antivirus/malware protection installed

##  Server and Container Security ##
- Dedicated or isolated VM/server deployed
- Physical/server access restricted
- Linux file permissions configured correctly
- Containers installed locally
- Approved LLM/OCR versions verified
- Containers not running in privileged mode
- Backup encryption enabled

## Access Control ##
- Dedicated EMR account configured
- Least privilege permissions verified
- Administrative role separation implemented
- Multi-factor authentication enabled where possible
- SSH keys securely managed and rotated

## Data Handling ##
- Trusted PDF ingestion process established
- PHI removed from filenames/logs where required
- JSON workflow restricted to trusted queues
- Bulk demographic import procedures documented

## Human Review and Clinical Oversight ##
- MOA assigned as error_manager
- Human verification workflow completed
- Trial validation runs completed
- Daily review procedures established
- Clinical/provider review process documented

## Logging, Monitoring, and Recovery ##
- Audit logging enabled
- Backup procedures tested
- Log review procedures documented
- Recovery procedures validated

## Final Approval ##

Deployment approval must be completed by:

- System Administrator
- Operational Manager
- Security Officer
- Clinic or Organizational Leadership

Production deployment must not proceed until all checklist items have been completed and approved.

## Disclaimer ##

The software and accompanying documentation are provided “as is,” without any express or implied warranty. By installing, configuring, or using AI-MOA, you and your organization assume all associated risks and responsibilities related to deployment, security, compliance, operational use, and patient safety.

This documentation is intended to provide security, operational, and deployment guidance for AI-MOA installations. While the controls and procedures described in this guide are designated as mandatory requirements for production deployments, they do not guarantee complete security, regulatory compliance, system availability, or protection against all vulnerabilities, threats, misconfigurations, or human error.

Security threats, healthcare regulations, infrastructure requirements, and industry best practices continuously evolve. Organizations deploying AI-MOA remain solely responsible for independently evaluating, implementing, monitoring, and maintaining appropriate administrative, technical, physical, and clinical safeguards based on their own environment, risk assessments, regulatory obligations, and professional judgment.
