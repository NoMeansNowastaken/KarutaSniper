@echo off

net session >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo This script requires administrator privileges.
    echo Please run the script as an administrator.
    pause>nul
    exit /b
)

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed.
    pause>nul
    exit /b
)

echo Installing Python requirements...
pip install -r requirements.txt

echo Downloading Tesseract...
powershell -Command "& { Invoke-WebRequest -Uri 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe' -OutFile 'tesseract-ocr-setup.exe' }"

echo Installing Tesseract...
start /wait tesseract-ocr-setup.exe /S

echo Adding Tesseract to path...
setx /M PATH "%PATH%;C:\Program Files\Tesseract-OCR"

echo.
echo Tesseract installation complete.

echo Cleaning up...
del tesseract-ocr-setup.exe

echo Done.

pause>nul