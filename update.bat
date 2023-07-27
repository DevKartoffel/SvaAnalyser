@REM This updates you branch and auto installs requirements
git pull --tags origin main

CALL .\venv\Scripts\activate.bat
 
pip install -r requirements.txt

pause