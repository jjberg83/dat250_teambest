import os

# contains application-wide configuration, and is loaded in __init__.py

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess' # TODO: Use this with wtforms
    DATABASE = 'database.db'
    UPLOAD_PATH = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'} # Might use this at some point, probably don't want people to upload any file type

    #reCAPTCHA configuration
    RECAPTCHA_PUBLIC_KEY = os.environ.get(
        '6Le8iA8iAAAAAPhyntZcF2vaR08uOth1Lw-j6aB6')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('6Le8iA8iAAAAAF1DLx6EeX6G4jdZwZ2pbnDfJ9ZJ')
