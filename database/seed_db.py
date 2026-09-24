import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import SessionLocal, Base, engine
from database.models import User
import bcrypt

def seed():
    print("Setting up SQLite Database fallback and seeding users...")
    # Initialize DB (in place of alembic for local zero-setup dev)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    if db.query(User).first():
        print("Database already seeded.")
        return

    # Seed 4 role accounts
    users_to_seed = [
        {"username": "admin", "password": "password123", "role": "Administrator"},
        {"username": "operator", "password": "password123", "role": "Operator"},
        {"username": "analyst", "password": "password123", "role": "Analyst"},
        {"username": "evaluator", "password": "competition_eval", "role": "Evaluator"},
    ]
    
    os.makedirs("documentation", exist_ok=True)
    with open("documentation/demo_credentials.md", "w") as f:
        f.write("# Demo Credentials\n\n")
        f.write("Do NOT use these in production.\n\n")
        
        for u in users_to_seed:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(u["password"].encode("utf-8"), salt).decode("utf-8")
            
            user = User(
                username=u["username"],
                password_hash=hashed,
                role=u["role"]
            )
            db.add(user)
            f.write(f"- **Role:** {u['role']}\n  - Username: `{u['username']}`\n  - Password: `{u['password']}`\n\n")
            
    db.commit()
    db.close()
    print("Seeded exactly 4 users and exported demo_credentials.md")

if __name__ == "__main__":
    seed()
