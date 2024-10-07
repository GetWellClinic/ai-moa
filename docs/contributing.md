# Contributing to AI-MOA

We welcome contributions to the AI-MOA project! This document outlines the process for contributing to the project and guidelines for code style and submission.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```
   git clone https://github.com/your-username/ai-moa.git
   ```
3. Create a new branch for your feature or bug fix:
   ```
   git checkout -b feature/your-feature-name
   ```

## Development Process

1. Make your changes in your feature branch
2. Add or update tests as necessary
3. Ensure all tests pass:
   ```
   python -m unittest discover tests
   ```
4. Update documentation if you're changing functionality
5. Commit your changes:
   ```
   git commit -am "Add a brief description of your changes"
   ```
6. Push to your fork:
   ```
   git push origin feature/your-feature-name
   ```
7. Create a pull request from your fork to the main repository

## Code Style Guidelines

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Write docstrings for all functions, classes, and modules
- Keep functions small and focused on a single task
- Use type hints where appropriate

## Testing Guidelines

- Write unit tests for new functionality
- Update existing tests if you're modifying functionality
- Aim for at least 80% test coverage for new code
- Include both positive and negative test cases

## Documentation Guidelines

- Update README.md if you're adding or changing functionality
- Update API documentation in `docs/api-reference.md` for new or modified classes and methods
- If adding new configuration options, update `docs/configuration.md`
- For significant changes, consider updating or adding to other documentation files in the `docs/` directory

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Update the README.md with details of changes to the interface, if applicable
3. Increase the version numbers in any examples files and the README.md to the new version that this Pull Request would represent
4. Your pull request will be reviewed by maintainers, who may request changes or ask questions
5. Once approved, your pull request will be merged into the main branch

## Reporting Bugs

- Use the GitHub issue tracker to report bugs
- Describe the bug in detail, including steps to reproduce
- Include information about your environment (OS, Python version, etc.)

## Requesting Features

- Use the GitHub issue tracker to suggest new features
- Clearly describe the feature and its potential benefits
- Be open to discussion about the feature's implementation

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

## Questions?

If you have any questions about contributing, please open an issue in the GitHub repository.

Thank you for contributing to AI-MOA!
