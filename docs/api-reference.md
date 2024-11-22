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
    def save_workflow_config(self) -> None
    def save_config(self) -> None
    def load_config(self, file_path: str) -> Dict[str, Any]
    def reload_config(self) -> None
    def get(self, key: str, default: Any = None) -> Any
    def get_workflow(self, key: str, default: Any = None) -> Any
    def update_lock_status(self, status: bool) -> None
    def update_pending_inbox(self, file_name: str) -> None
    def update_incoming_inbox(self, file_name: str) -> None
    def update_pending_retries(self, times: int) -> None
    def update_incoming_retries(self, times: int) -> None
    def workflow_steps(self) -> List[Dict[str, Any]]
    def document_categories(self) -> List[str]
    def ai_prompts(self) -> Dict[str, str]
    def default_values(self) -> Dict[str, str]
    def set_in_memory(self, key: str, value: Any)
    def get_in_memory(self, key: str, default: Any = None) -> Any
    def set_shared_state(self, key: str, value: Any)
    def get_shared_state(self, key: str, default: Any = None) -> Any
    def clear_shared_state(self)
```

### ProviderListManager

```python
class ProviderListManager:
    def __init__(self, workflow)
    def login(self) -> None
    def upload_template_file(self) -> bool
    def check_template_file(self) -> None
    def generate_provider_list(self) -> None
    def find_template_id(self, tbody: BeautifulSoup) -> Optional[str]
    def fetch_provider_data(self, template_id: str) -> Optional[str]
    def save_provider_list(self, provider_data: Optional[str]) -> None

```

## processors.workflow

### Workflow

```python
class WorkflowProcessor:
    def __init__(self, config: ConfigManager, session_manager: SessionManager, login_manager: LoginManager) -> None:
    def execute_task(self, step: Dict[str, Any]) -> Any:
    def execute_workflow(self) -> None:
```

For detailed information on each method and its parameters, refer to the docstrings in the source code.
