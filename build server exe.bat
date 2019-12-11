pyinstaller -y -F  "C:/Users/Spencer/Documents/CS415Final/server.py"
rd /q /s build
del /q /s *.spec
pause