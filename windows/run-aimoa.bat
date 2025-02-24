@echo off
REM This custom script installs Get Well Clinic's version of AI-MOA (Aimee AI)
REM Note: To correctly use automatic detection of AI-MOA path, this script must be installed and run in subdirectory 'windows'
REM Version 2025.02.21

REM Set current directory
set CURRENT=%CD%
REM Automatic detection of base directory
cd ..
set AIMOA=%CD%
AIPYTHONENV=%AIMOA%\.env
REM Override by specifying the full path for AI-MOA base directory and Python virtual environment that contains the installed python pre-requisite packages:
REM set AIMOA=C:\opt\ai-moa
REM set AIPYTHONENV=C:\opt\virtualenv\aimoa

REM Confirm base directory of AI-MOA:
echo Currently specifying the following as the base directory for AI-MOA...
echo %AIMOA%
echo(
echo This 'run-aimoa.bat' is for starting AI-MOA by command line. You do not need to run this if you have installed AI-MOA in Windows Task Scheduler."
echo 	( Hint: To run AI-MOA automatically and continously, set up AI-MOA in Windows Task Scheduler)
timeout /t 3

REM Activate Python virtual environment with installed pre-requisite packages
%AIMOA%\.env\Scripts\activate

REM Export environment variables specifying location of config files
set CONFIG_FILE=%AIMOA%\config\config.yaml
set WORKFLOW_CONFIG_FILE=%AIMOA%\config\workflow-config.yaml

REM Option to disable warnings when using a self-signed SSL certificate for servers, quiet the logging
set PYTHONWARNINGS="ignore:Unverified HTTPS request"

REM Display environment variables on console
echo Specifying the following environmental variables for AI-MOA...
echo %CONFIG_FILE%
echo %WORKFLOW_CONFIG_FILE%
echo %PYTHONWARNINGS%

REM Command to start AI-MOA
echo Starting AI-MOA...
cd %AIMOA%\src
python.exe main.py --config %AIMOA%\config\config.yaml --workflow-config %AIMOA%\config\workflow-config.yaml --reset-lock --cron-interval */1 --run-immediately

REM Returning to previous path location
cd %CURRENT%

