pyinstaller -y -F  "%cd%\server.py"
rd /q /s build
del /q /s *.spec
pause