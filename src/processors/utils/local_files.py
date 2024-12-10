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

import os

def get_local_documents(self):
    """
    Retrieves the first file from a local directory and sets it in the shared state.

    This method checks the specified input directory for files. If any files are found, it reads the 
    first file and sets the file content and its name into the shared state for further processing.

    The file is read in binary mode and stored in the shared state under two keys:
    - `current_file`: Stores the binary content of the file.
    - `current_file_name`: Stores the name of the file.

    The directory to search for the files is configurable through the `document_processor.local.input_directory` 
    setting, with a default value of '/app/input'.

    Args:
        None

    Returns:
        bool: 
            - `True` if a file is found, read successfully, and its content is stored in the shared state.
            - `False` if no files are found in the specified directory.
        
        Example:
            >>> result = get_local_documents()
            >>> print(result)
            True  # If a file was found and processed, or False if no file was found.
    
    Logs:
        - Logs the execution of the task using the logger: `Executing task get_local_documents`.

    Raises:
        OSError: If there is an issue accessing the directory or reading the file.
    """
    self.logger.info(f"Executing task get_local_documents")
    input_directory = self.config.get('document_processor.local.input_directory', '/app/input')
    files = [f for f in os.listdir(input_directory) if os.path.isfile(os.path.join(input_directory, f))]
    if files:
        file_path = os.path.join(input_directory, files[0])
        with open(file_path, 'rb') as file:
            file_bytes = file.read()
        self.config.set_shared_state('current_file', file_bytes)
        self.config.set_shared_state('current_file_name', files[0])
        return True
    return False