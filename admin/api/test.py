import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from admin.service.service import hash_password
from admin.model.model import Admin
from database.database import SessionLocal

db = SessionLocal()

admin = Admin(
    email="livingtheadventure369@gmail.com",
    password=hash_password("Living369#1407")
)

db.add(admin)
db.commit()
db.close()
