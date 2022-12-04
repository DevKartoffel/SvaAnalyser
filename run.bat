@REM This porgram runs python in an virtual enviroment

@REM Test if vnv exist
if EXIST venv\ (
    echo "Viruel enviroment already exists"
) else (
    @REM Create virtual enviroment
    CALL init.bat
)
CALL .\venv\Scripts\activate.bat
python __main__.py

pause