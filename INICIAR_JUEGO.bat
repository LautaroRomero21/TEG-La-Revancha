@echo off
cd /d "%~dp0teg_revancha"
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo No se pudo instalar Pygame. Revisa tu instalacion de Python.
    pause
    exit /b 1
)
python main.py
pause
