pyinstaller -y -F  "%cd%\server.py"
rd /s /q build
pause