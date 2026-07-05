@echo off
cd /d "%~dp0"
 
echo ==> Pulling latest changes...
git pull
if errorlevel 1 goto error
 
echo ==> Installing/updating dependencies...
.\env\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 goto error
 
echo ==> Update complete.
echo If this update introduced new config options, check config.example.json
echo and update your config.json accordingly.
echo.
echo Restart Mycel with: run.bat
pause
exit /b 0
 
:error
echo.
echo Update failed. See error above.
pause
exit /b 1
 
