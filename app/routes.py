from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, login_required, logout_user, current_user

from app import app, db, login_manager  # login_manager를 app 모듈에서 임포트
from app.models import User

from app.docker_api import *


# flask_login 에 필요한 user_loader
# id 를 기반으로 사용자 객체를 반환
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
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
# @login_required
def admin():
    # Check if the current user has the role 'admin' or 'manager'
    # if current_user.role not in ['admin', 'manager']:
    #     flash('You do not have permission to access this page.')
    #     return redirect(url_for('/'))  # 또는 다른 적절한 페이지로 리다이렉트
    
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

        elif action == 'escalate_permission':
            if(current_user.role=="admin"):
                user = User.query.get(user_id)
                if user:
                    user.role = 'admin'
                    db.session.commit()
                    flash('User Permission Updated')
                else:
                    flash('User not found')
            else:
                flash("You are not admin")

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
    api_key = current_user.api_key
    if request.method == 'POST':
        container_name = request.form.get('container_name', '')
        unique_container_name = f"{container_name}_{api_key}"
        
        if '_' in container_name:
            flash('컨테이너 이름에는 언더스코어(_) 문자를 사용할 수 없습니다.', 'error')
            return render_template('profile.html')

        command = request.form.get('command', '')
        
        if current_user.tickets > 0:
            try:
                # 여러 개의 포트 매핑 예시
                available_ports = find_available_ports(count=5)  # 예를 들어 3개의 포트를 찾음
                print(available_ports)
                
                # 포트 매핑 설정
                port_mappings = {
                    '22/tcp': available_ports[0],  # 포트 22를 available_ports[0]에 매핑
                    '445/tcp': available_ports[1]  # 포트 445를 available_ports[1]에 매핑
                }
                # Docker 컨테이너 생성 및 실행
                result = create_and_run_container(unique_container_name, port_mappings)
                
                if result['success']:
                    # TODO : Container ID GET 로직
                    container_id = result['container_id']

                    flash(f'컨테이너가 성공적으로 생성되었습니다. ID: {container_id}', 'success')
                    # 티켓 수 감소
                    current_user.tickets -= 1
                    db.session.commit()
                else:
                    # TODO : 에러 처리
                    flash(f'컨테이너 생성 오류: {result["error"]}', 'error')
            except Exception as e:
                flash(f'오류 발생: {str(e)}', 'error')
        else:
            flash('사용 가능한 티켓이 없습니다. 지원 팀에 문의하여 티켓을 추가하세요.', 'error')

    return render_template('profile.html')
