pyinstaller -y -F  "%cd%\peer.py"
rd /q /s build
del /q /s *.spec
pause