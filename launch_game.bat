@echo off
REM DBForged Launch Script
REM This script launches the Evennia game server with the correct PYTHONPATH

cd /d "%~dp0live"
set PYTHONPATH=%~dp0
python -m evennia start
