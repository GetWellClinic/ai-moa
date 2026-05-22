# AI-MOA Security Hardening Guide #

## Security Checklist (Quick Reference) ##



| Area                        | Action                                                                                                                                                                                                         |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Local Network**           | Enterprise firewall, antivirus, patched devices, VPN for external networks, restrict access to trusted personnel/devices, two-factor authentication, VM firewall restricting all unnecessary ports |
| **Server Security**         | Locked physical location, standalone VM/server, minimal other apps, Linux permissions on AI-MOA directories (`-rwxr-x--- aimoa aimoa`), physical/SSH access only, full-disk encryption optional                |
| **EMR Credentials**         | Dedicated account, least privilege, periodic review, password rotation                                                                                                                                         |
| **Containers & Packages**   | Install AI-MOA, OCR, and LLM containers locally on the same server/VM, use exact LLM/OCR versions as in documentation. If using external LLM, require new TRA/jurisdiction review and clinical leadership approval       |
| **SSL/TLS**                 | Enforce for all communications (EMR, OCR API, LLM container)                                                                                                                                                    |
| **PDF Handling**            | Generic or obfuscated filenames, delete logs if containing PHI, only ingest human-verified trusted PDFs                                                                                                        |
| **Backups**                 | Encrypt at rest, use encrypted transfer, remove AI-MOA credentials, delete sensitive logs                                                                                                                      |
| **Database Security**       | Localhost-only if possible, encrypted connections for remote SQL, follow best practices                                                                                                                        |
| **Trusted JSON**            | Only use JSON workflow on trusted queues (IncomingDocs/File), human-selected PDFs                                                                                                                              |
| **Bulk Demographics (PIF)** | Only trusted SQL/CSV sources, document source, human review before commit                                                                                                                                      |
| **Human-in-the-Loop**       | Assign MOA as `error_manager`, review outputs daily, verify demographics for each patient, trial run where human checks all outputs, health provider review of all documents                                   |
| **Administrative Access**   | Role separation (SysAdmin, OpManager, SecOfficer), least privilege, dual approval for critical actions, logs reviewed monthly, access reviewed every 6 months                                                  |
| **Deployment & Monitoring** | Isolated server/VM, regular patches, encrypted backup of logs, SSH key rotation, staff security training, annual external audit                                                                                |

## Introduction ##

AI-MOA was designed with privacy and security in mind. It gives control of privacy and security back to the clinic as the installer/user, by reducing the risks of third-party data leaks and secondary use of data. The application is intended and designed to be installed entirely locally, including the AI-MOA code, the large language model (LLM) engine, the LLMs themselves, the OCR, and Docker containers.

Communication between the systems is all done locally (within the same server/VM/internal network) and using SSL/TLS. External communication with an EMR is conducted as a normal authenticated/secured human user, through encrypted SSL/TLS web connections. All patient data is processed locally, in memory, not saved on disks, and discarded when the process is completed.

The following best practices are recommended for your installation of AI-MOA. Improper setup, misuse, or failure to follow these parameters may compromise privacy and security.

## Disclaimer ##

The software and accompanying documentation are provided 'as is,' without any express or implied warranty. By installing and using AI-MOA, you and your organization assume all associated risks and liabilities. This guide does not guarantee complete security; rather, it outlines industry-standard security protocols, which are subject to ongoing updates, emerging threats, and the professional judgment of your organization’s security team.

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