pyinstaller -y -F  "%cd%\peer.py"
rd /s /q build
del /s /q *.spec
pause 

