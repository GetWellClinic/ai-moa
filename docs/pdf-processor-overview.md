# PDF Text Processor (Without LLM) Overview

## Configuration Update

Update your AIMOA configuration based on your requirements.

## workflow-config-pdf-processor.yaml
In your `workflow-config-pdf-processor.yaml` file, update the following (recommended) workflow to configure AIMOA with the PDF text processor

```yaml

workflow:
  steps:
    - name: extract_text_from_pdf_file
      true_next: pif_pdf
      false_next: release_lock
    - name: pif_pdf
      true_next: release_lock
      false_next: get_category_types
```

To add a default description to each category, go to the `workflow-config-pdf-processor.yaml` file and under the required category after description (modify as required) add the following:
```yaml
default_description: >
      This will be the default document description for this category when using pdf processor.
```

The description in the JSON (PDF file) takes the highest priority. If it's not present, the default above will be used.

## config-pdf-processor.yaml

In your `config-pdf-processor.yaml` file, use the following fields to configure AIMOA with the PDF text processor:

### `pdf_processor: pdf_tag`
- **Type**: String  
- **Description**: Unique tag identifier for AIMOA to find the JSON from the PDF file. Can be changed to any value to match the tag in the PDF file.  
- **Example**: `pdf_processor: `
`pdf_tag : '#ai-moa'`

With the above workflow configurations, AIMOA will process PDF documents (both pending and inbox) containing text data, using an LLM only when necessary.