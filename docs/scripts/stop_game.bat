@echo off
REM DBForged Stop Script - MiniMax Agent
REM This script stops the Evennia game server

cd /d c:\Games\Dev\DBForged\Agents\MiniMax\live
set PYTHONPATH=c:\Games\Dev\DBForged\Agents\MiniMax
python -m evennia stop
