taskkill /fi "WINDOWTITLE eq Electro*"
taskkill /f /t /im openconsole.exe
echo.
echo Closing EW Targeting App...
ping 127.0.0.1 -n 6 > nul