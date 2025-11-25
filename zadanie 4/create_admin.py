from database import SessionLocal, engine
from models import User, Base
import auth

Base.metadata.create_all(bind=engine)

db = SessionLocal()

admin_user = db.query(User).filter(User.username == "admin").first()

if not admin_user:
    hashed_pass = auth.hash_password("admin123")

    new_admin = User(
        username="admin",
        hashed_password=hashed_pass,
        roles="ROLE_ADMIN,ROLE_USER"
    )

    db.add(new_admin)
    db.commit()
    print("Użytkownik 'admin' (hasło: 'admin123') został utworzony.")
else:
    print("Użytkownik 'admin' już istnieje.")

db.close()