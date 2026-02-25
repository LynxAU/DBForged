@echo off
REM DBForged Launch Script - MiniMax Agent
REM This script launches the Evennia game server with the correct PYTHONPATH
REM 
REM Set EVENNIA_SERVER_ID to a unique identifier for this agent instance
REM Example: set EVENNIA_SERVER_ID=agent1-minimax

REM Set unique server identifier (can be overridden by setting EVENNIA_SERVER_ID env var)
if "%EVENNIA_SERVER_ID%"=="" (
    set EVENNIA_SERVER_ID=minimax-%RANDOM%
)

echo Starting DBForged with Server ID: %EVENNIA_SERVER_ID%

title DBForgedMiniMax-%EVENNIA_SERVER_ID%
cd /d c:\Games\Dev\DBForged\Agents\MiniMax\DBForged
set PYTHONPATH=c:\Games\Dev\DBForged\Agents\MiniMax\DBForged
python -m evennia start
