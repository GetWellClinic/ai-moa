@echo off
REM This custom script installs Get Well Clinic's version of AI-MOA (Aimee AI)
REM Note: To correctly use automatic detection of AI-MOA path, this script must be installed and run in subdirectory 'windows'
REM Version 2025.02.21

REM Hardware Requirements:
REM	NVIDIA RTX video card installed with at least 12 GB VRAM

REM Software Requirements:
REM	NVIDIA graphics drivers installed
REM	Docker installed
REM	Docker Compose installed
REM NVIDIA Container Toolkit installed
REM	AI-MOA installed in preferably in \opt\ai-moa directory
REM Python 3.10+ installed
REM	Python package installed:
REM		pip
REM		virtualenv

REM Automatic detection of base directory
cd ..
set AIMOA=%CD%

REM Installation
echo(
echo AI-MOA (Aimee AI) will be installed and setup with the following specified base directory for AI-MOA...
echo(
echo %AIMOA%
echo(
echo ...if the above directory is not the correct base directory for AI-MOA, please Ctrl-C to cancel installation now...!
pause

REM Create directories if not exist
if not exist %AIMOA%\logs mkdir %AIMOA%\logs
if not exist %AIMOA%\config mkdir %AIMOA%\config
if not exist %AIMOA%\src\static mkdir %AIMOA%\src\static
if not exist %AIMOA%\app mkdir %AIMOA%\app
if not exist %AIMOA%\app\input mkdir %AIMOA%\app\input
if not exist %AIMOA%\app\output mkdir %AIMOA%\app\output
if not exist %AIMOA%\llm-container\models mkdir %AIMOA%\llm-container\models

REM Create config files from template
copy src\config.yaml.example config\config.yaml
copy src\config-incomfingfax.yaml.example config\config-incomingfax.yaml
copy src\workflow-config.yaml.example config\workflow-config.yaml
copy src\workflow-incomingfax.yaml.example config\workflow-incomingfax.yaml
copy src\template_providerlist.txt config\

echo ...remember to edit the config files in ..\config\* to customize to your installation.

REM Missing provider list will cause AI-MOA to regenerate the list
echo Removing provider_list for clean start...
pause
del config\provider_list.yaml
del src\provider_list.yaml

REM Confirm your local timezone is set:
echo %date%, %time:~0,5%
tzutil /g
echo(
echo ...please confirm that above details of your system has your correct desired timezone...
echo ...if your timezone is not set properly, your document files may be marked with the wrong dates...!
echo(
pause

REM Create Python virtual environment for AI-MOA libraries and dependency packages:
echo Creating python virtual environment for AI-MOA dependencies...
timeout /t 5
cd %AIMOA%
virtualenv --python python %AIMOA%\.env
REM Install python dependencies for AI-MOA from requirements.txt
echo Installing Python libraries and dependencies required for running AI-MOA in python virual environment...
timeout /t 5
REM Activate virtual environment and install in python packages in virtual environment
%AIMOA%\.env\Scripts\activate
pip install -r %AIMOA%\src\requirements.txt

REM Install Google Chrome
echo(
echo REMEMBER to download and install Google Chrome browser...AI-MOA requires Google Chrome to work !
echo(

echo "Script completed..."
pause