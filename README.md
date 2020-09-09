# flask-celery
A simple example to get started with Celery using Redis in Flask

### Installation
```
cd flask-celery
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
cd job
set FLASK_APP=tasks.py (if mac or linux use EXPORT instead of set)
''' also set env variables MAIL_PASSWORD and MAIL_USERNAME. ''' 
flask run
celery -A tasks.celery worker -l info
celery -A tasks.celery beat -l info
```

