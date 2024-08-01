from app import app, db
from app.models import User
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run the Flask app with optional reset_admin.')
    parser.add_argument('--reset-admin', action='store_true', help='Create a new admin user and reset the database.')

    args = parser.parse_args()
    app.config['RESET_ADMIN'] = args.reset_admin


    with app.app_context():
        db.create_all()  # 유저 데이터베이스 테이블 생성

        # 리셋 모드이면 기존 admin 을 모두 삭제
        if app.config['RESET_ADMIN']:
            admin_users = User.query.filter_by(role='admin').all()
            for user in admin_users:
                print(f'Deleting admin user: {user.username} with API key: {user.api_key}')
                db.session.delete(user)
            
            db.session.commit()

            # 새 admin 을 추가 후, console 에 생성한 admin 의 api-key 출력
            new_admin = User(username='default_admin', email='',role='admin')
            new_admin.generate_api_key()
            db.session.add(new_admin)
            db.session.commit()
            print(f"New admin created with API key: {new_admin.api_key}")


    app.run(host='0.0.0.0', port=8000, debug=True)

