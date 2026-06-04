@echo off
chcp 65001 >nul 2>&1

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Pythonが見つかりませんでした。
    echo https://www.python.org/downloads/ からPythonをインストールしてください。
    echo インストール時に「Add Python to PATH」にチェックを入れてください。
    echo.
    pause
    exit /b 1
)

python "%~dp0standalone.py"
pause
