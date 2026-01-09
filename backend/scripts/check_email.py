#!/usr/bin/env python
import argparse
from app.database import SessionLocal
from app.models.user import User

def email_exists(email: str) -> bool:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first() is not None
    finally:
        db.close()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--email", required=True, help="Email to check")
    args = p.parse_args()
    exists = email_exists(args.email)
    print(f"Email '{args.email}' exists: {exists}")
