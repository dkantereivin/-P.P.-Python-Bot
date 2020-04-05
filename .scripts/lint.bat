@ECHO OFF
TITLE Discord Bot
CALL venv/Scripts/activate.bat
python -m black --target-version py38 ../src/modules
python -m black --target-version py38 ../src/app.py
ECHO Discord bot closed down.
PAUSE
