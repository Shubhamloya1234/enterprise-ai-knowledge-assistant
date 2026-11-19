from getpass import getpass

from app.db.database import SessionLocal
from app.models import User
from app.core.security import hash_password

ACCOUNTS = {
    "admin": "ADMIN",
    "manager1": "MANAGER",
    "employee1": "EMPLOYEE",
}

def main():
    db = SessionLocal()

    try:
        users = {}

        for username, expected_role in ACCOUNTS.items():
            user = db.query(User).filter(User.username == username).first()

            if not user:
                raise ValueError(f"Account not found: {username}")

            if user.role != expected_role:
                raise ValueError(f"Unexpected role for {username}: {user.role}")

            users[username] = user

        new_passwords = {}

        for username in ACCOUNTS:
            while True:
                password = getpass(f"New password for {username}: ")
                confirm = getpass(f"Confirm password for {username}: ")

                if password != confirm:
                    print("Passwords do not match. Try again.")
                    continue

                if len(password) < 12:
                    print("Use at least 12 characters.")
                    continue

                if len(password.encode("utf-8")) > 72:
                    print("Password must be no longer than 72 UTF-8 bytes.")
                    continue

                new_passwords[username] = hash_password(password)
                break

        for username, hashed_password in new_passwords.items():
            users[username].hashed_password = hashed_password

        db.commit()
        print("\nAll three passwords have been reset successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

if __name__ == "__main__":
    main()
