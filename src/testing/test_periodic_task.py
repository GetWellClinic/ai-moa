
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
