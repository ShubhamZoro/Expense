import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configurations
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 465)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None or False
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'in.shubhamshekhar@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'zzqtpxqqblgrqmbn'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'in.shubhamshekhar@gmail.com'
    MAIL_DEBUG = os.environ.get('MAIL_DEBUG') or True
