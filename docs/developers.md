# AI-MOA Developers Guide

## Adding to the code:

AI-MOA follows the Explicit Module Export approach along with a Workflow Engine, which allows the workflow to be controlled without editing the Python code. The main advantage of the system is that it is loosely coupled. The logic of a function can be altered without modifying the core code by creating a new function and replacing the function in the workflow itself. The system also supports before and after functions by utilizing shared variable implementation within the workflow. Additionally, different workflows can be created to perform various tasks. The system uses Huey to manage the execution of code at specified intervals.

## New Module

#### Files needed:
#### your_module/__init__.py
#### your_module/your_python_file.py
#### processors/workflow/emr_workflow.py
#### workflow-config.yaml


1. Create a new module by adding a new folder to the `src/` directory.
2. Create an `__init__.py` file to define the methods that will be used in the application.
3. Create the Python file with the required functions and save it in the module folder.
4. Import the functions into the Workflow class using the import statement, and add the functions as variables to access them from anywhere during the workflow execution.
5. Add the function to the `workflow-config.yaml` file based on the required functionality.
6. Test the code and check the logs to verify if the function is being triggered.


## Before and After functions

Before and after functions can be implemented; there is no global method to do that. However, you can take advantage of the workflow design if you need to modify the data before passing it to another function, or to update the data once it has been processed by a function. Simply follow the new module instructions and update the workflow based on your requirements.

`self.config.set_shared_state(step['name'], result)`` is the method used to save data after each function call. All data will be accessible within the execution cycle of the workflow. The first parameter will be a boolean, and the second will be the return value of the function, if it has one.

Each shared data can be accessed using the get method. For example, `self.config.get_shared_state('filter_results')` accesses the data returned by the `filter_results` function.

## Overriding functions

Instead of modifying a core function, create a new module and replace the function in the `workflow-config.yaml`. This way, the code can be maintained without conflicts.


For detailed explanations of each functions and configurations, refer to the comments in the base code and example configuration files.