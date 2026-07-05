@echo off
cd /d "%~dp0"
 
echo ==> Pulling latest changes...
git pull
if errorlevel 1 goto error
 
echo ==> Installing/updating dependencies...
.\env\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 goto error
 
echo ==> Checking config.json for new options...
.\env\Scripts\python.exe merge_config.py
 
echo ==> Update complete.
echo Restart Mycel with: run.bat
pause
exit /b 0
 
:error
echo.
echo Update failed. See error above.
pause
exit /b 1
 
