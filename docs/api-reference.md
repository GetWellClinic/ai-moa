# AI-MOA API Reference

## auth

### LoginManager

```python
class LoginManager:
    def __init__(self, config: ConfigManager)
    def login_with_selenium(self, driver) -> str
    def login_with_requests() -> Tuple[requests.Session, bool]
    def is_login_successful(self, current_url: str) -> bool
```

### SessionManager

```python
class SessionManager:
    def __init__(self, config: ConfigManager)
    def login() -> bool
    def get_session() -> requests.Session
```

### DriverManager

```python
class DriverManager:
    def __init__(self, config: ConfigManager)
    def get_driver() -> webdriver.Chrome
```

## config

### ConfigManager

```python
class ConfigManager:
    def __init__(self, config_file: str = 'config/config.yaml', workflow_config_file: str = 'config/workflow-config.yaml')
    def load_config(self, file_path: str) -> Dict[str, Any]
    def get(self, key: str, default: Any = None) -> Any
    def get_workflow(self, key: str, default: Any = None) -> Any
    def set_in_memory(self, key: str, value: Any)
    def get_in_memory(self, key: str, default: Any = None) -> Any
```

### ProviderListManager

```python
class ProviderListManager:
    def __init__(self, config: ConfigManager)
    def login() -> None
    def upload_template_file() -> bool
    def generate_provider_list() -> None
    def find_template_id(self, tbody: BeautifulSoup) -> Optional[str]
    def fetch_provider_data(self, template_id: str) -> Optional[str]
    def save_provider_list(self, provider_data: Optional[str]) -> None
```

## processors.document

### DocumentProcessor

```python
class DocumentProcessor:
    def __init__(self, config: ConfigManager, session)
    def get_file_content(self, name: str) -> bool
    def process_documents(self, login_url: str, login_successful_callback: Callable) -> str
```

## processors.pdf

### PdfProcessor

```python
class PdfProcessor:
    def __init__(self, config: ConfigManager, session_manager)
    def process_pdfs(self, login_url: str, login_successful_callback: Callable) -> str
    def get_pdf_content(self, name: str) -> Optional[bytes]
```

### PdfFetcher

```python
class PdfFetcher:
    def __init__(self, config: ConfigManager, session)
    def get_pdf_content(self, name: str) -> Optional[bytes]
```

## processors.workflow

### WorkflowProcessor

```python
class WorkflowProcessor:
    def __init__(self, config: ConfigManager, session_manager)
    def process_workflow(self, login_url: str, login_successful_callback: Callable)
    def execute_workflow_step(self, step_name: str, *args, **kwargs)
```

### WorkflowStepExecutor

```python
class WorkflowStepExecutor:
    def __init__(self, session_manager, config)
    def execute_step(self, step_name: str, *args, **kwargs)
```

### WorkflowTaskManager

```python
class WorkflowTaskManager:
    @task()
    def process_workflow_task(self, process_func: Callable, *args, **kwargs)
    @task()
    def execute_workflow_step_task(self, execute_func: Callable, step_name: str, *args, **kwargs)
```

For detailed information on each method and its parameters, refer to the docstrings in the source code.
