@echo off

REM Activar el entorno virtual
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo Error: No se pudo activar el entorno virtual.
    exit /b %ERRORLEVEL%
)
REM Ejecutar el comando de Django
python manage.py TareaActiveDirectory  --settings=config.settings.production 
if %ERRORLEVEL% neq 0 (
    echo Error: El comando de Django fallo.
    exit /b %ERRORLEVEL%
)

echo Operacion completada con exito.
exit /b 0