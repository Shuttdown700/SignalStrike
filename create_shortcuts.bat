@echo off
setlocal enabledelayedexpansion

:: Get the current directory
set "CURR_DIR=%CD%"
set "DESKTOP=%USERPROFILE%\Desktop"

:: Shortcut creation function
:: %1 = Target Path, %2 = Shortcut Name, %3 = Icon Path (optional)
call :CreateShortcut "%CURR_DIR%" "%DESKTOP%\Folder - EW Targeting App.lnk" "%CURR_DIR%\icons\desktop_shortcuts\folder.ico"

:: Define the batch files for which shortcuts should be created
for %%F in (map_download.bat launch.bat update_code.bat update_requirements.bat run_tests.bat) do (
    set "BATCH_FILE=%%F"
    set "SHORTCUT_PATH=%DESKTOP%\%%~nF.lnk"

    if not exist "!SHORTCUT_PATH!" (
        set "ICON_PATH=%CURR_DIR%\icons\desktop_shortcuts\%%~nF.ico"
        if exist "!ICON_PATH!" (
            call :CreateShortcut "%CURR_DIR%\!BATCH_FILE!" "!SHORTCUT_PATH!" "!ICON_PATH!"
        ) else (
            call :CreateShortcut "%CURR_DIR%\!BATCH_FILE!" "!SHORTCUT_PATH!"
        )
    ) else (
        echo Shortcut for !BATCH_FILE! already exists, skipping...
    )
)

echo.
echo Shortcuts created successfully!
echo.
exit /b

:: Function to create a shortcut using PowerShell
:CreateShortcut
set "TARGET=%~1"
set "SHORTCUT=%~2"
set "ICON=%~3"

if not exist "%SHORTCUT%" (
    echo Creating shortcut: %SHORTCUT%
    powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%TARGET%'; $Shortcut.WorkingDirectory = '%CURR_DIR%'; if ('%ICON%' -ne '') { $Shortcut.IconLocation = '%ICON%' }; $Shortcut.Save()"
) else (
    echo.
    echo Shortcut %SHORTCUT% already exists.
    echo.
)
exit /b
