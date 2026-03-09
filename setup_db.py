#!/usr/bin/env python
"""
WaveZA Database Setup Script
Resets database with new schema and creates admin credentials
"""

import os
import sys
from app import app, db
from models import User

def reset_database():
    """Drop all tables and recreate with new schema"""
    print("=" * 60)
    print("WaveZA Database Reset & Setup")
    print("=" * 60)
    
    with app.app_context():
        print("\n1. Dropping existing tables...")
        try:
            db.drop_all()
            print("   ✓ Tables dropped successfully")
        except Exception as e:
            print(f"   ✗ Error dropping tables: {e}")
            return False
        
        print("\n2. Creating new tables with updated schema...")
        try:
            db.create_all()
            print("   ✓ Tables created successfully")
        except Exception as e:
            print(f"   ✗ Error creating tables: {e}")
            return False
        
        print("\n3. Creating admin user credentials...")
        try:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@waveza.gov',
                password='admin123',  # Simple password for testing
                role='admin'
            )
            admin.id_number = "0000000000"
            admin.location = "South Africa"
            admin.art_field = "admin"
            admin.popia_consent = True
            admin.terms_accepted = True
            
            db.session.add(admin)
            db.session.commit()
            
            print("   ✓ Admin user created successfully")
            print(f"     Username: {admin.username}")
            print(f"     Email: {admin.email}")
            print(f"     Password: admin123")
            print(f"     Role: {admin.role}")
        except Exception as e:
            print(f"   ✗ Error creating admin user: {e}")
            return False
        
        print("\n4. Creating test regular user...")
        try:
            # Create test user
            test_user = User(
                username='testuser',
                email='test@waveza.gov',
                password='test123',
                role='user'
            )
            test_user.id_number = "1111111111"
            test_user.location = "Cape Town"
            test_user.art_field = "poetry"
            test_user.popia_consent = True
            test_user.terms_accepted = True
            
            db.session.add(test_user)
            db.session.commit()
            
            print("   ✓ Test user created successfully")
            print(f"     Username: {test_user.username}")
            print(f"     Email: {test_user.email}")
            print(f"     Password: test123")
            print(f"     Role: {test_user.role}")
        except Exception as e:
            print(f"   ✗ Error creating test user: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ Database setup completed successfully!")
        print("=" * 60)
        
        print("\n📋 Test Credentials:")
        print("-" * 60)
        print("ADMIN LOGIN:")
        print("  URL: http://localhost:5000/login")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Access: /admin/dashboard for admin panel")
        print()
        print("TEST USER LOGIN:")
        print("  Username: testuser")
        print("  Password: test123")
        print("  Access: /dashboard for user dashboard")
        print("-" * 60)
        
        return True

if __name__ == '__main__':
    success = reset_database()
    sys.exit(0 if success else 1)
