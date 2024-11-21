
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
