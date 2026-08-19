@echo off
REM Sincronizacao ZapSign -> Drive (Pascoal & Dyandra Advocacia)
REM Agendar no Task Scheduler do Windows (3x ao dia).
REM Ajuste o caminho abaixo para a pasta onde o projeto foi instalado.
set "PROJETO=C:\PASCOAL_ADVOGADOS"
cd /d "%PROJETO%"
"%LOCALAPPDATA%\Microsoft\WindowsApps\py.exe" "%PROJETO%\SYNC\sync_assinados.py"
