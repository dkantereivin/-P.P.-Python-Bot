@ECHO OFF
TITLE Discord Bot
CALL ../venv/Scripts/activate.bat
python ../src/app.py
ECHO Discord bot closed down.
PAUSE
