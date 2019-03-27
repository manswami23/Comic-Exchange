# run.py

import os

from app import create_app

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://.....'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
if __name__ == '__main__':
    app.run()
