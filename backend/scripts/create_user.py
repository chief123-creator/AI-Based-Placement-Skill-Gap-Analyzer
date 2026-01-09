#!/usr/bin/env python
import argparse
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.exc import IntegrityError

def create_user(email, full_name, password, role='student'):
    db = SessionLocal()
    try:
        hashed = get_password_hash(password)
        user = User(email=email, full_name=full_name, hashed_password=hashed, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f'Created user: id={user.id}, email={user.email}')
    except IntegrityError:
        db.rollback()
        print('Error: email already exists')
    except Exception as e:
        db.rollback()
        print('Error:', e)
    finally:
        db.close()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--email', required=True)
    p.add_argument('--name', default='Test User')
    p.add_argument('--password', default='16')
    p.add_argument('--role', default='student')
    args = p.parse_args()
    create_user(args.email, args.name, args.password, args.role)
