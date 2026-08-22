@echo off
cd /d "%~dp0.."
 
echo ==> Checking nodeenv...
.\env\Scripts\python.exe -c "import nodeenv" 2>nul
if errorlevel 1 (
    echo ==> Installing nodeenv...
    .\env\Scripts\pip.exe install nodeenv
    if errorlevel 1 exit /b 1
)
 
if not exist .\env\Scripts\node.exe (
    echo ==> Installing Node.js into the virtual environment...
    .\env\Scripts\nodeenv.exe -p
    if errorlevel 1 exit /b 1
) else (
    echo ==> Node.js already installed, skipping.
)
 
echo ==> Installing Node dependencies ^(npm^)...
.\env\Scripts\npm.cmd install --prefix .\node_deps
if errorlevel 1 exit /b 1
 
