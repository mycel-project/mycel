@echo off
echo Setting up Mycel backend...

:: Create virtual environment if it doesn't exist
if not exist "env\" (
    python -m venv env
    echo Virtual environment created.
)

:: Install dependencies
echo Installing dependencies...
.\env\Scripts\python.exe -m pip install --upgrade pip
.\env\Scripts\pip install -r requirements.txt

if not exist config.json (
    echo Creating configuration file...
    copy config.example.json config.json
) else (
    echo config.json already exists. Your settings have been preserved.
)

echo Setup complete! You can now run the application.
pause
