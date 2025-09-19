from app import app
from extensions import db
from flask_migrate import upgrade

with app.app_context():
    # Apply all migrations
    upgrade()
    print("✅ Remote database upgraded successfully!")
