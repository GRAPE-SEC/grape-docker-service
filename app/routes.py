from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, login_required, logout_user, current_user

from app import app, db, login_manager  # login_manager를 app 모듈에서 임포트
from app.models import User

import docker

# Docker 클라이언트 초기화
client = docker.from_env()

# flask_login 에 필요한 user_loader
# id 를 기반으로 사용자 객체를 반환
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('profile'))
        else:
            flash('Invalid API key.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        email = request.form.get('email')
        user_id = request.form.get('user_id')
        tickets = request.form.get('tickets', type=int)  # 티켓 수를 정수형으로 가져옴

        if action == 'create':
            if User.query.filter_by(username=username).first():
                flash('Username already exists.')
            else:
                new_user = User(username=username, email=email)
                new_user.generate_api_key()  # API 키 생성
                db.session.add(new_user)
                db.session.commit()
                flash(f'User created successfully with API key: {new_user.api_key}')
        elif action == 'delete':
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                flash('User deleted successfully.')
            else:
                flash('User not found.')
                
        elif action == 'update_tickets':
            user = User.query.get(user_id)
            if user:
                user.tickets = tickets
                db.session.commit()
                flash('User tickets updated successfully.')
            else:
                flash('User not found.')

    users = User.query.all()
    return render_template('admin.html', users=users)

@app.before_request
def require_api_key():
    # 모든 요청에서 API 키를 확인합니다
    if request.endpoint in ['protected_page', 'profile']:
        api_key = request.headers.get('api_key')
        return api_key
        if not api_key or not User.query.filter_by(api_key=api_key).first():
            abort(403)  # API 키가 없거나 유효하지 않을 경우 접근 거부


@app.route('/protected_page')
def protected_page():
    return 'This is a protected page. You have valid API key!'

# 유저 페이지(API 키에 따라 다른 페이지)
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        command = request.form.get('command', '')
    else:
        if current_user.tickets > 0:
            try:
                success=1
                if(success):
                    container_id = response.json().get('container_id')
                    flash(f'컨테이너가 성공적으로 생성되었습니다. ID: {container_id}')
                    # 티켓 수 감소
                    current_user.tickets -= 1
                    db.session.commit()
                else:
                    flash(f'컨테이너 생성 오류: {response.json().get("error", "알 수 없는 오류")}')
            except Exception as e:
                flash(f'오류 발생: {str(e)}')
        else:
            flash('사용 가능한 티켓이 없습니다. 지원 팀에 문의하여 티켓을 추가하세요.')

    return render_template('profile.html')