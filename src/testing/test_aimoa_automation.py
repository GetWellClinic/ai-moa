
import unittest
from unittest.mock import MagicMock, patch
import auth, config, processors, ai_moa_utils  # Import from your src modules
from processors.workflow import Workflow
from auth.session_manager import SessionManager
from auth.login_manager import LoginManager
from config.config_manager import ConfigManager
from ai_moa_utils.logging_setup import setup_logging
from aimoa_automation import AIMOAAutomation  # Adjust import according to actual file


class TestAIMOAAutomation(unittest.TestCase):

    @patch('config.config_manager.ConfigManager')
    @patch('auth.session_manager.SessionManager')
    @patch('auth.login_manager.LoginManager')
    @patch('processors.workflow.Workflow')
    def test_initialization(self, MockWorkflow, MockLoginManager, MockSessionManager, MockConfigManager):
        # Mocking the classes
        mock_config = MagicMock()
        mock_session_manager = MagicMock()
        mock_login_manager = MagicMock()
        mock_workflow = MagicMock()

        MockConfigManager.return_value = mock_config
        MockSessionManager.return_value = mock_session_manager
        MockLoginManager.return_value = mock_login_manager
        MockWorkflow.return_value = mock_workflow

        # Initializing AIMOAAutomation with mocked objects
        aim_automation = AIMOAAutomation('../config.yaml', '../workflow-config.yaml')

        # Assert that the objects were properly initialized
        self.assertIsInstance(aim_automation, AIMOAAutomation)
        MockConfigManager.assert_called_once_with('../config.yaml', '../workflow-config.yaml')
        MockWorkflow.assert_called_once_with(mock_config, mock_session_manager, mock_login_manager)

    @patch('processors.workflow.Workflow')
    def test_process_workflow(self, MockWorkflow):
        # Mocking the workflow execution
        mock_workflow = MagicMock()
        MockWorkflow.return_value = mock_workflow

        # Creating an instance of AIMOAAutomation
        aim_automation = AIMOAAutomation('../config.yaml', '../workflow-config.yaml')

        # Running the workflow
        aim_automation.process_workflow()

        # Assert that the workflow method was called
        mock_workflow.execute_workflow.assert_called_once()

    @patch('processors.workflow.Workflow')
    def test_process_workflow_with_error(self, MockWorkflow):
        # Simulate an exception being raised by the workflow
        mock_workflow = MagicMock()
        mock_workflow.execute_workflow.side_effect = Exception("Test Error")
        MockWorkflow.return_value = mock_workflow

        aim_automation = AIMOAAutomation('../config.yaml', '../workflow-config.yaml')

        with self.assertRaises(Exception):
            aim_automation.process_workflow()


class TestCleanup(unittest.TestCase):

    @patch('auth.session_manager.SessionManager')
    @patch('ai_moa_utils.logging_setup.logging')
    def test_cleanup(self, MockLogging, MockSessionManager):
        # Mocking the session manager close method
        mock_session_manager = MagicMock()
        MockSessionManager.return_value = mock_session_manager
        mock_logger = MagicMock()
        MockLogging.getLogger.return_value = mock_logger

        aim_automation = AIMOAAutomation('../config.yaml', '../workflow-config.yaml')

        aim_automation.cleanup()

        # Ensure the session manager's close method was called
        mock_session_manager.close.assert_called_once()

        # Ensure the logger handlers were closed
        self.assertTrue(mock_logger.removeHandler.called)


if __name__ == "__main__":
    unittest.main()
