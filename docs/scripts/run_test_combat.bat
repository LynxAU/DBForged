@echo off
cd /d c:\Games\Dev\DBForged\Agents\MiniMax\live
set PYTHONPATH=c:\Games\Dev\DBForged\Agents\MiniMax
set DJANGO_SETTINGS_MODULE=server.conf.settings
python test_combat_direct.py
