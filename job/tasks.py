
from flask import Flask, request, jsonify
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from flask_mail import Mail, Message
import os

app = Flask(__name__)
logger = get_task_logger(__name__)
app.config.from_object('celeryconfig')

def make_celery(app):
    #Celery configuration
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL']
    )
    #can be used in celeryconfig as used
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587 
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = 'example@email.com'
    app.config['CELERYBEAT_SCHEDULE'] = {
        # Executes every minute
        'periodic_task-every-minute': {
            'task': 'periodic_task',
            'schedule': crontab(minute="*")
        }
    }   
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

mail = Mail(app)
celery = make_celery(app)

@celery.task(name='periodic_task')
def send_async_email(email_data):
    """Background task to send an email with Flask-Mail."""
    msg = Message(email_data['subject'],
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[email_data['to']])
    msg.body = email_data['body']
    with app.app_context():
        mail.send(msg)



@app.route('/mails', methods=["POST"])
def view():
    request_data = request.get_json()
    # send the email
    email_data = {
        'subject': request_data['subject'],
        'to': request_data['recipient'],
        'body': request_data['body']
    }
    send_async_email.delay(email_data)
    return jsonify({'message': 'mail will be sent'})


if __name__ == "__main__":
    app.run(debug = True)