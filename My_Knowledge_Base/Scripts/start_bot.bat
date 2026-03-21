@echo off
:: Запускает bot_trigger.py в скрытом окне
:: Добавь этот .bat в автозагрузку: Win+R → shell:startup → скопируй ярлык сюда

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%.."

:: Загружаем переменные окружения
if exist "%SCRIPT_DIR%.env.bat" call "%SCRIPT_DIR%.env.bat"

C:\Python314\python.exe -X utf8 "%SCRIPT_DIR%bot_trigger.py" >> "%SCRIPT_DIR%bot.log" 2>&1
