SECRET_KEY = '2021strangepinglin2021'
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:@Jsjs1995627@localhost:5432/strangepinglin'
SQLALCHEMY_ENGINE_OPTIONS = {'encoding': 'utf-8', 'json_serializer': lambda obj: obj, 'echo': False}
SQLALCHEMY_TRACK_MODIFICATIONS = False
SESSION_PERMANENT = False

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'strangepinglin@gmail.com'
MAIL_PASSWORD = 'wyzyrodqmpttacxh'
MAIL_DEFAULT_SENDER = ("坪林尋怪地圖", "strangepinglin@gmail.com")