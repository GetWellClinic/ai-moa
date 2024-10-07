# AI-MOA Workflow System

The AI-MOA workflow system is designed to process medical documents through a series of configurable steps. This document outlines the workflow structure and how to customize it.

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

To add a new workflow step:

1. Add the step to the `workflow.steps` section in `workflow-config.yaml`
2. Implement the corresponding method in the `Workflow` class (`src/processors/workflow/emr_workflow.py`)
3. Update the `execute_workflow` method to include your new step

Example of adding a new step:

```python
def new_custom_step(self, previous_result):
    # Implementation
    pass
```

## Testing Workflow Changes

After making changes to the workflow:

1. Run the `full_workflow_test.py` script to test the entire workflow
2. Use `prompt_testing_script.py` to test specific AI prompts and document classification

For more detailed information on testing, refer to the [Testing Guide](testing.md).
