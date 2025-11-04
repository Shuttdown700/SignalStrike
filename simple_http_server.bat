@echo off
setlocal enabledelayedexpansion

:: ==================================================
:: Simple LAN File Server - Python HTTP Server
:: ==================================================

echo.
echo Starting HTTP server in current directory: %cd%
echo.

:: --- Get the first non-loopback IPv4 address ---
set "ip="
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /c:"IPv4 Address" ^| findstr /v "127.0.0.1"') do (
    set "ip=%%A"
    goto :foundIP
)
:foundIP
set "ip=!ip: =!"  :: Remove spaces

if "!ip!"=="" (
    echo Could not detect a LAN IP address.
) else (
    echo Server will be accessible at:
    echo     http://!ip!:8000
)
echo.

:: --- Get Wi-Fi SSID ---
set "ssid="
for /f "tokens=2 delims=:" %%B in ('netsh wlan show interfaces ^| findstr /c:"SSID" ^| findstr /v "BSSID"') do (
    set "ssid=%%B"
    goto :foundSSID
)
:foundSSID
set "ssid=!ssid:~1!"  :: remove leading space

if "!ssid!"=="" (
    echo Wi-Fi SSID not detected.
) else (
    echo Connected Wi-Fi SSID: !ssid!
)
echo.

:: --- Start Python HTTP server ---
python -m http.server 8000

pause
endlocal
