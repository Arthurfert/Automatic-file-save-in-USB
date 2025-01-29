@echo off
setlocal enabledelayedexpansion

REM Ouvrir une nouvelle fenêtre de terminal et exécuter ce script
start cmd /k "%~dp0%~nx0"

for /f "tokens=*" %%D in ('wmic logicaldisk where "drivetype=2" get deviceid ^| find ":"') do (
    set "DEV=%%D"
    echo !DEV! is a USB device, info:
    wmic diskdrive where "DeviceID='!DEV!'" get /format:list
    for /f "tokens=*" %%P in ('wmic partition where "DeviceID='!DEV!'" get name ^| find ":"') do (
        echo Has partitions %%P
    )
    echo.
)

endlocal
exit /b 0