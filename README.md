This website is built on the django in python framework.

To open it, you need python 3.13.0

To check the python version in cmd use: python --version command

To check the django version in cmd use: py -m django --version

Create file with Scripts to activate (unless it exists): python -m venv myVenv

To run the application, you must activate django (in source file): ./myVenv/Scripts/activate

If you create venv you must install django in myVenv: pip install django

If u have problem with system: ""The error you're encountering is related to PowerShell's script execution policy, which is set to prevent the running of scripts for security reasons. To resolve this and activate your virtual environment, you can modify the execution policy temporarily or permanently."" Run the following command to allow script execution for this session: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

To active the server, you must runserver: py manage.py runserver

To run server add in console:
pip install django-allauth
pip install django-requests
pip install PyJWT  
pip install cryptography
