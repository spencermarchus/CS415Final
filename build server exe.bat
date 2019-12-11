pyinstaller -y -F  "%cd%\server.py"
rd /s /q build
del /s /q *.spec
pause

