@echo off
REM This custom script installs Get Well Clinic's version of AI-MOA (Aimee AI)
REM Note: To correctly use automatic detection of AI-MOA path, this script must be installed and run in subdirectory 'windows'
REM Version 2025.02.21

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
if not exist %AIMOA%\llm-container\models mkdir %AIMOA%\llm-container\models
cd %AIMOA%\llm-container\models
REM Download default AI LLM model
echo Downloading default AI-MOA LLM model from Hugging Face...
bitsadmin.exe /transfer "Download-LLM" /priority FOREGROUND "https://huggingface.co/RichardErkhov/mistralai_-_Mistral-7B-Instruct-v0.3-gguf/resolve/main/Mistral-7B-Instruct-v0.3.Q8_0.gguf" "$AIMOA\llm-container\models\"

REM Specify the environmental variables for model name for use by LLM container and AI-MOA
echo Using the following LLM model...
REM This environmental variable must be set before running AI-MOA
REM Default: set MODEL_NAME="\models\Mistral-7B-Instruct-v0.3.Q8_0.gguf"
set MODEL_NAME="\models\Mistral-7B-Instruct-v0.3.Q8_0.gguf"
echo %MODEL_NAME%

REM Note:
REM You can download other AI models in GGUF format from Hugging Face and install them in models folder to use.
REM Remember to specify the model name in AIMOA/src/config.yaml

echo "Script completed..."
pause