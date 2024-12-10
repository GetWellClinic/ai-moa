# AI-MOA Frequently Asked Questions (FAQ)

This document addresses common questions about the AI-MOA project. If you don't find an answer to your question here, please check the other documentation files or open an issue on the GitHub repository.

## General Questions

### Q: What is AI-MOA?
A: AI-MOA (AI-powered Medical Office Assistant) is an automated system designed to process medical documents, manage workflows, and integrate with the O19 Electronic Medical Record (EMR) system.

### Q: What programming language is AI-MOA written in?
A: AI-MOA is primarily written in Python.

### Q: Is AI-MOA open-source?
A: Yes, AI-MOA is open-source and licensed under the GNU Affero General Public License v3.0.

## Setup and Installation

### Q: What are the system requirements for running AI-MOA?
A: AI-MOA requires Python 3.9+, Docker (optional, for containerized deployment), and Chrome WebDriver (for Selenium-based operations).

### Q: How do I install AI-MOA?
A: Please refer to the `getting-started.md` file for detailed installation instructions.

### Q: Can I run AI-MOA without Docker?
A: Yes, you can run AI-MOA directly on your system without Docker. However, using Docker is recommended for easier deployment and consistency across different environments.

## Configuration and Customization

### Q: How do I configure AI-MOA?
A: Configuration is done through the `config.yaml` and `workflow-config.yaml` files. Please refer to the `configuration.md` file for detailed information.

### Q: Can I customize the workflow steps?
A: Yes, you can customize the workflow steps by modifying the `workflow-config.yaml` file. See the `workflow.md` file for more information.

## Integration and Compatibility

### Q: Does AI-MOA work with EMR systems other than O19?
A: Currently, AI-MOA is designed to work specifically with the O19 EMR system. Integration with other EMR systems would require significant modifications.

### Q: Can AI-MOA process documents in languages other than English?
A: The current version is primarily designed for English documents. Processing documents in other languages may require additional configuration and possibly modifications to the OCR and AI components.

## Performance and Scalability

### Q: How many documents can AI-MOA process per day?
A: The processing capacity depends on various factors including hardware specifications, network speed, and complexity of documents. In general, AI-MOA is designed to handle a high volume of documents efficiently.

### Q: Can AI-MOA be scaled for larger medical practices?
A: Yes, AI-MOA can be scaled by adjusting the configuration, increasing hardware resources, and potentially implementing load balancing for high-volume scenarios.

## Troubleshooting and Support

### Q: What should I do if I encounter an error?
A: First, check the `troubleshooting.md` file for common issues and their solutions. If your issue isn't addressed there, please check the application logs and open an issue on the GitHub repository with a detailed description of the problem.

### Q: Is there commercial support available for AI-MOA?
A: Currently, AI-MOA is a community-supported open-source project. Commercial support options may be available in the future.

## Contributing

### Q: How can I contribute to AI-MOA?
A: Contributions are welcome! Please read the `contributing.md` file for guidelines on how to contribute to the project.

### Q: I have an idea for a new feature. How can I suggest it?
A: Feature suggestions are appreciated. Please open an issue on the GitHub repository describing your feature idea in detail.

Remember, this FAQ is a living document and will be updated as new questions arise and the project evolves.
