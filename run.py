from app import app, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 유저 데이터베이스 테이블 생성
    app.run(host='0.0.0.0', port=8000, debug=True)

