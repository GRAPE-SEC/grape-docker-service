from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
import binascii

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    api_key = db.Column(db.String(36), unique=True, nullable=True)  # API 키 추가
    tickets = db.Column(db.Integer, default=0) # docker container 생성 티켓

    def generate_api_key(self):
        # API 키를 랜덤하게 생성
        self.api_key = binascii.hexlify(os.urandom(24)).decode()
        return self.api_key

    @staticmethod
    def verify_api_key(api_key):
        # 주어진 API 키가 유효한지 확인합니다.
        return User.query.filter_by(api_key=api_key).first() is not None

    def __repr__(self):
        return f'<Port {self.port_number}>'