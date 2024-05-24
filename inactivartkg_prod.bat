@echo off

call venv\Scripts\activate.bat
python manage.py incTkg --settings=config.settings.production
exit