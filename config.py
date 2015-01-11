import os

WTF_CSRF_ENABLED = True
SECRET_KEY = 'what-do-you-want'

POSTS_PER_PAGE = 3

basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
OAUTH_CREDENTIALS = {
    'twitter': {
        'id': 'L0qOWNCyaUSltIAbqN4F1Qs7x',
        'secret': 'F0kYoGA6n2lIWxJVwFTvUHt99AvH5AbYo81DdkQ90iOWHaNbQv'
    },
    'facebook': {
        'id': '878798145503824',
        'secret': '4ae20303f2effbc70707d9be0c41a287'
    }
}

MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['nakulpathak3008@gmail.com']