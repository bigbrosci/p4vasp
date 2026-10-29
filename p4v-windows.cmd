@echo off
setlocal
rem Development launcher. A self-contained EXE bundle is not available yet.
if not defined P4VASP_MSYS2 set "P4VASP_MSYS2=C:\msys64"
set "P4VASP_PYTHON=%P4VASP_MSYS2%\ucrt64\bin\python.exe"
if not exist "%P4VASP_PYTHON%" (
    echo MSYS2 UCRT64 Python not found. Set P4VASP_MSYS2 to your MSYS2 folder.
    pause
    exit /b 1
)
set "PATH=%P4VASP_MSYS2%\ucrt64\bin;%PATH%"
set "P4VASP_HOME=%~dp0"
set "PYTHONPATH=%~dp0lib;%PYTHONPATH%"
"%P4VASP_PYTHON%" "%~dp0p4v.py" %*
set "P4VASP_EXIT=%ERRORLEVEL%"
if not "%P4VASP_EXIT%"=="0" pause
exit /b %P4VASP_EXIT%
