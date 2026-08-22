@echo off
if "%~1"=="setup" (
    call scripts\setup.bat
) else if "%~1"=="run" (
    call scripts\run.bat
) else if "%~1"=="update" (
    call scripts\update.bat
) else (
    echo Usage: mycel.bat {setup^|run^|update}
)
