import os

def get_local_documents(self):
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