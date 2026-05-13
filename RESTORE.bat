@echo off
echo Restoring all deleted files... Please wait a moment.
git restore .
git checkout .
echo.
echo Done! All your city folders and service pages should be completely restored.
echo You can close this window now.
pause
