from pathlib import Path
import os

PRODUCTION = os.getenv('DEPLOYMENT_SCOPE') == 'PRODUCTION'

APP_PATH_PREFIX = '/tfm'

BASE_DIR = Path(__file__).parent

class Config:
  SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        str(BASE_DIR.joinpath('db.sqlite'))
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  
DATA_PATH = str(BASE_DIR.joinpath('data/')).replace('\\', '/')