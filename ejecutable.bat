@echo off
SETLOCAL

:: Verificar si Python está instalado
:: Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python no está instalado o no está en el PATH
    echo Por favor instala Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Instalar dependencias
echo Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Error instalando dependencias
    pause
    exit /b 1
)

:: Verificar e instalar FFmpeg
echo Verificando FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo FFmpeg no está instalado, intentando instalar...
    python -c "import os, subprocess; subprocess.call(['python', 'app.py', '--install-ffmpeg'])"
    
    ffmpeg -version >nul 2>&1
    if %errorlevel% neq 0 (
        echo No se pudo instalar FFmpeg automáticamente
        echo Por favor instálalo manualmente desde: https://ffmpeg.org/download.html
        pause
    )
)

:: Ejecutar la aplicación
echo Iniciando la aplicación...
python app.py

pause