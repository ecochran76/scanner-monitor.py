@echo off
REM Ensure the correct Anaconda environment is activated

REM Path to the Anaconda activate script
set CONDA_ACTIVATE_PATH=C:\ProgramData\anaconda3\Scripts\activate.bat

REM Name of the Anaconda environment
set CONDA_ENV_NAME=condaenv

REM Path to the directory where your .BAT file (and Python script) is located
set SCRIPT_DIR=%~dp0

REM Name of your Python script
set SCRIPT_NAME=scanner-monitor.py

REM Activate the Anaconda environment
call %CONDA_ACTIVATE_PATH% %CONDA_ENV_NAME%

REM Change to the script directory
cd /d %SCRIPT_DIR%

REM Run the Python script
python %SCRIPT_NAME%

REM Keep the command prompt open to view any output (optional)
REM pause
