from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import secrets

# Flask 앱과 데이터베이스 객체 생성
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from . import routes, models, docker_api  # 앱 초기화 후 라우트와 모델을 임포트

