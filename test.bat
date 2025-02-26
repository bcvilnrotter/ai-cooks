@echo off
echo Testing AI Cooks application...
python test_app.py
if %ERRORLEVEL% EQU 0 (
    echo Test completed successfully!
) else (
    echo Test failed with error code %ERRORLEVEL%
)
pause
