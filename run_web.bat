@echo off
chcp 65001 > nul
title Радиолюбителски Тест - Клас 2 (Уеб Приложение)
cd /d "%~dp0"
echo Стартиране на уеб сървър и отваряне в браузър...

py -3 --version >nul 2>&1
if not errorlevel 1 goto run_with_py

python --version >nul 2>&1
if not errorlevel 1 goto run_with_python

choice /C YN /M "Искате ли да инсталираме Python и да продължим?"
if errorlevel 2 goto cancel

where winget >nul 2>&1
if errorlevel 1 goto no_winget

echo Инсталиране на Python 3.13...
winget install --id Python.Python.3.13 --exact --scope user --accept-source-agreements --accept-package-agreements
if errorlevel 1 goto install_failed

set "INSTALLED_PYTHON=%LocalAppData%\Programs\Python\Python313\python.exe"
if exist "%INSTALLED_PYTHON%" goto run_with_installed_python

py -3 --version >nul 2>&1
if not errorlevel 1 goto run_with_py
python --version >nul 2>&1
if not errorlevel 1 goto run_with_python

echo Python was installed, but Windows cannot find its executable. Close this window and try again.
pause
exit /b 1

:no_winget
echo winget was not found. Install Python 3 manually, then run this file again.
pause
exit /b 1

:install_failed
echo Python installation failed. Please install Python 3 manually and try again.
pause
exit /b 1

:cancel
echo Стартирането е отменено.
exit /b 0

:run_with_py
py -3 web_app.py
goto end

:run_with_python
python web_app.py
goto end

:run_with_installed_python
"%INSTALLED_PYTHON%" web_app.py

:end
pause
