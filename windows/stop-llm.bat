echo off
REM Shutdown script for local AI LLM Docker Containers
REM Version 2025.02.23

REM Set current directory
set CURRENT=%CD%
REM Automatic detection of base directory
cd ..
set AIMOA=%CD%
REM Override by specifying the full path to AI-MOA base directory:
REM AIMOA=C:\opt\ai-moa

REM Confirm directory of installed AI-MOA:
echo Currently specifying the following as the base directory for AI-MOA...
echo %AIMOA%

echo This 'stop-llm.bat' is for stopping AI LLM Container by command line.
echo You do not need to run this if you have installed AI LLM Container in Windows Task Scheduler.
echo	( Hint: You can stop scheduled tasks in Windows Task Scheduler.)
timeout /t 3

REM SPECIFY LLM Model to be used with AI-MOA:

REM Option 1:
REM Specify local GGUF LLM Model in local "\models\*" directory, use relative path:
REM Default: export MODEL_NAME="\models\Mistral-7B-Instruct-v0.3.Q8_0.gguf"
set MODEL_NAME="\models\Mistral-7B-Instruct-v0.3.Q8_0.gguf"
echo Using LLM model: %MODEL_NAME%

REM Option 2:
REM Get Hugging Face LLM models directly from website, need to sign-in with Hugging Face user token to download models:
set HF_TOKEN="{private_token}"
REM set MODEL_NAME="RichardErkhov/Mistral-7B-Instruct-v0.3.Q8_0.gguf"
REM set MODEL_NAME="microsoft/Phi-3.5-mini-instruct"
echo HuggingFace private token set: %HF_TOKEN%

REM Run AI LLM Containers:
REM Note: Two containers will stop, one for Aphrodite LLM container, the other is Caddy which operates the encrypted reverse proxy for SSL/TLS
REM cd %AIMOA%\llm-container
REM docker compose down -d

echo Halting AI LLM Containers...
docker compose -f %AIMOA%\llm-container\docker-compose.yml down

REM Check LLM and Caddy docker containers running
timeout /t 3
docker ps -a

REM Returning to previous path location
cd %CURRENT%

echo "Script completed..."
pause