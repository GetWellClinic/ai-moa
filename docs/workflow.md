# AI-MOA Workflow System

The AI-MOA workflow system is designed to process medical documents through a series of configurable steps. This document outlines the workflow structure and how to customize it.

## Shared State

The AI-MOA workflow system uses a shared state mechanism to pass information between tasks. This is implemented using the `ConfigManager` class, which provides methods to set, get, and clear shared state data.

### Using Shared State in Workflow Steps

Each workflow step can access and modify the shared state:

```python
def some_workflow_step(self):
    # Get data from shared state
    previous_result = self.config.get_shared_state('previous_step_result')
    
    # Process data
    result = process_data(previous_result)
    
    # Store result in shared state
    self.config.set_shared_state('current_step_result', result)
    
    return True  # or False, depending on the result
```

The shared state is cleared at the beginning of each workflow execution to ensure a clean slate for each run.

## Workflow Structure

The workflow is defined in `src/workflow-config.yaml` and consists of:

1. Workflow steps
2. Document categories
3. AI prompts

### Workflow Steps

Each step in the workflow is defined with:

- `name`: The step's identifier
- `true_next`: The next step if the current step succeeds
- `false_next`: The next step if the current step fails

Example:

```yaml
workflow:
  steps:
    - name: has_ocr
      true_next: extract_text_from_pdf_file
      false_next: extract_text_doctr
```

### Document Categories

Document categories define how different types of medical documents should be processed. Each category includes:

- `name`: Category identifier
- `description`: Detailed description of the category
- `tasks`: List of tasks to perform for this category

Example:

```yaml
document_categories:
  - name: Lab
    description: "Laboratory test results..."
    tasks:
      - name: get_document_description
        prompt: "Act as if you are a medical office assistant..."
```

### AI Prompts

AI prompts are used to guide the AI model in processing documents. They are defined in the `ai_prompts` section of the configuration.

Example:

```yaml
ai_prompts:
  build_prompt: "For the following question, if confidence level is more than 85%..."
  get_patient_name: "Answer only to the following question in two words..."
```

## Customizing the Workflow

To customize the workflow:

1. Edit `src/workflow-config.yaml`
2. Add or modify workflow steps
3. Update document categories as needed
4. Adjust AI prompts for your specific requirements

## Implementing New Workflow Steps

When implementing new workflow steps, make sure to use the shared state mechanism to pass data between steps:

```python
def new_custom_step(self):
    # Get data from previous steps
    data = self.config.get_shared_state('some_key')
    
    # Process the data
    result = process_data(data)
    
    # Store the result for next steps
    self.config.set_shared_state('new_key', result)
    
    return True  # or False, depending on the result
```
