# COPYRIGHT © 2024 by Spring Health Corporation <office(at)springhealth.org>
# Toronto, Ontario, Canada
# SUMMARY: This file is part of the Get Well Clinic's original "AI-MOA" project's collection of software,
# documentation, and configuration files.
# These programs, documentation, and configuration files are made available to you as open source
# in the hopes that your clinic or organization may find it useful and improve your care to the public
# by reducing administrative burden for your staff and service providers.
# NO WARRANTY: This software and related documentation is provided "AS IS" and WITHOUT ANY WARRANTY of any kind;
# and WITHOUT EXPRESS OR IMPLIED WARRANTY OF SUITABILITY, MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.
# LICENSE: This software is licensed under the "GNU Affero General Public License Version 3".
# Please see LICENSE file for full details. Or contact the Free Software Foundation for more details.
# ***
# NOTICE: We hope that you will consider contributing to our common source code repository so that
# others may benefit from your shared work.
# However, if you distribute this code or serve this application to users in modified form,
# or as part of a derivative work, you are required to make your modified or derivative work
# source code available under the same herein described license.
# Please notify Spring Health Corp <office(at)springhealth.org> where your modified or derivative work
# source code can be acquired publicly in its latest most up-to-date version, within one month.
# ***

from .local_files import get_local_documents
from .ocr import has_ocr, extract_text_doctr, extract_text_doctr_api, extract_text_from_pdf_file
from .llm import query_prompt
from .pif import query_pif, get_fht_tickler_config, update_fht_tickler_config, get_postal_code_category, new_patient_details, update_patient_details, search_patient, create_tickler, fill_element
from .pdf_processor import pif_pdf

__all__ = ['get_local_documents' , 'has_ocr', 'extract_text_from_pdf_file', 'extract_text_doctr', 'extract_text_doctr_api', 'query_prompt', 'query_pif', 'get_postal_code_category', 'new_patient_details', 'update_patient_details', 'search_patient', 'create_tickler', 'get_fht_tickler_config', 'update_fht_tickler_config', 'fill_element', 'pif_pdf']
