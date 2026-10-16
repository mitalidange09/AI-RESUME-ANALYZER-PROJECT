from app import app
from werkzeug.security import generate_password_hash
from models import db, User


def create_admin():
    with app.app_context():
        existing = User.query.filter_by(email='admin@example.com').first()
        if existing:
            print('Admin already exists: admin@example.com')
            return

        admin = User(
            name='Admin User',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            phone='0000000000',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin created successfully.')
        print('Email: admin@example.com')
        print('Password: admin123')
        print('IMPORTANT: Change this password before production use.')


if __name__ == '__main__':
    create_admin()
