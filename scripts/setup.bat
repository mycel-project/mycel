@echo off
cd /d "%~dp0.."
echo Setting up Mycel...

if not exist "env\" (
    python -m venv env
    if errorlevel 1 exit /b 1
    echo Virtual environment created.
)

echo Installing dependencies...
.\env\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 exit /b 1

.\env\Scripts\pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo ==> Setting up Node dependencies...
call scripts/install_node_deps.bat
if errorlevel 1 exit /b 1

if not exist config.json (
    echo Creating configuration file...
    copy config.json.example config.json >nul
    if errorlevel 1 exit /b 1
) else (
    echo config.json already exists. Your settings have been preserved.
)

echo Setup complete! Use mycel.bat run to start the application.
pause
