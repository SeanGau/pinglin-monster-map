#rename this file to config.py
SECRET_KEY = ''
SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/dbname'
SQLALCHEMY_ENGINE_OPTIONS = {'encoding': 'utf-8', 'json_serializer': lambda obj: obj, 'echo': False}
SQLALCHEMY_TRACK_MODIFICATIONS = False
SESSION_PERMANENT = False
UPLOAD_FOLDER = "./static/img/monsters"

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'username@gmail.com'
MAIL_PASSWORD = 'ApplicationPassword'
MAIL_DEFAULT_SENDER = ("Sender Name", "username@gmail.com")