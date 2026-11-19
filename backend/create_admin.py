from app.db.database import SessionLocal
from app.models import User
from app.core.security import hash_password


db = SessionLocal()

try:
    admin = User(
        username="admin",
        email="admin@company.com",
        hashed_password=hash_password("Admin@123"),
        role="ADMIN"
    )

    db.add(admin)
    db.commit()

    print("Admin user created successfully!")

except Exception as e:
    db.rollback()
    print("Error:", e)

finally:
    db.close()