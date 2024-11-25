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
from unittest.mock import patch, MagicMock
from aimoa_automation import schedule_tasks  # Import schedule_tasks from the correct module


class TestScheduleTasks(unittest.TestCase):

    @patch('aimoa_automation.AIMOAAutomation')
    @patch('aimoa_automation.os.getenv')
    def test_schedule_tasks(self, mock_getenv, MockAIMOAAutomation):
        # Mock the environment variables
        mock_getenv.side_effect = lambda key, default=None: '../config.yaml' if key == 'CONFIG_FILE' else '../workflow-config.yaml'

        # Mocking AIMOAAutomation
        mock_aimoa = MagicMock()
        MockAIMOAAutomation.return_value = mock_aimoa

        schedule_tasks()

        # Assert that the AIMOAAutomation process_workflow method was called
        mock_aimoa.process_workflow.assert_called_once()


if __name__ == "__main__":
    unittest.main()
