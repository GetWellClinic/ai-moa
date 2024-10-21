import os

def check_for_file(self):
    self.logger.info(f"Executing task check_for_file")
    input_directory = self.config.get('document_processor.local.input_directory', '/app/input')
    files = [f for f in os.listdir(input_directory) if os.path.isfile(os.path.join(input_directory, f))]
    if files:
        self.config.set_shared_state('current_file', files[0])
        return True
    return False