@echo off

echo Installing Python requirements...
pip install -r requirements.txt

echo Downloading Tesseract...
powershell -Command "& { Invoke-WebRequest -Uri 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe' -OutFile 'tesseract-ocr-setup.exe' }"

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