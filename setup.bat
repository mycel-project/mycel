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

echo Setup complete! You can now run the application.
pause
