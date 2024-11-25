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

import unittest
from unittest.mock import patch
from config import config_manager  # Import from the config module


class TestConfigFileCheck(unittest.TestCase):
    
    @patch('os.path.exists')
    def test_config_files_exist(self, mock_exists):
        # Mocking file existence for both files
        mock_exists.side_effect = lambda x: x in ["../config.yaml", "../workflow-config.yaml"]
        
        try:
            config_manager.check_config_files_exist('../config.yaml', '../workflow-config.yaml')
            # If no exception is raised, the test passes
            mock_exists.assert_any_call('../config.yaml')
            mock_exists.assert_any_call('../workflow-config.yaml')
        except FileNotFoundError:
            self.fail("FileNotFoundError raised unexpectedly!")

    @patch('os.path.exists')
    def test_missing_config_file(self, mock_exists):
        # Mocking file existence for one file
        mock_exists.side_effect = lambda x: x == "../config.yaml"
        
        with self.assertRaises(FileNotFoundError):
            config_manager.check_config_files_exist('../config.yaml', '../workflow-config.yaml')


if __name__ == "__main__":
    unittest.main()
