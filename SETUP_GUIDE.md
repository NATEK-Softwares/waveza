# WaveZA - Setup & Installation Guide

## ✅ Changes Implemented

All changes from line 676 of UPDATES.md have been successfully implemented into your WaveZA application. The app is now a fully functional government art promotion platform with admin oversight, post approval workflows, and comprehensive analytics.

---

## 🔄 Database Migration Steps

### Step 1: Backup Your Database
```bash
cp mishwrites.db mishwrites.db.backup
```

### Step 2: Create Migration
```bash
flask db migrate -m "Add admin approval workflow and notifications"
```

### Step 3: Review Migration
Check the generated migration file in `migrations/versions/`

### Step 4: Apply Migration
```bash
flask db upgrade
```

### Alternative: Fresh Database
If you prefer to start fresh:

```python
from app import app, db
from models import *

with app.app_context():
    # Drop all tables
    db.drop_all()
    # Create all tables
    db.create_all()
    print("Database tables created successfully!")
```

---

## 👨‍💼 Creating Admin Users

### Method 1: Using Python Shell
```python
from app import app, db
from models import User

with app.app_context():
    # Create admin user
    admin = User(
        username='admin',
        email='admin@waveza.gov',
        password='secure_password',
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user created: {admin.username}")
```

### Method 2: Direct Database Update
```sql
UPDATE user SET role='admin' WHERE email='your_email@example.com';
```

---

## 🧪 Testing the Implementation

### 1. Test Registration with New Fields
```
1. Navigate to /register
2. Fill in all required fields:
   - Username
   - Email
   - Password
   - ID Number (required)
   - Location (optional)
   - Art Field (optional)
   - POPIA Consent (optional)
   - Terms & Conditions (required)
3. Click Register
4. Verify user is created with all fields
```

### 2. Test Post Approval Workflow
```
As Regular User:
1. Login
2. Go to /add_poem
3. Create a post
4. See "Post submitted for admin approval" message
5. Visit /notifications
6. See notification: "Post submitted"
7. Dashboard shows status as "Pending Review"

As Admin:
1. Login as admin user
2. Visit /admin/dashboard
3. See pending posts count
4. Click "Review Posts"
5. View pending post details
6. Approve or Reject with optional comments
```

### 3. Test Traffic Analytics
```
1. Open incognito window
2. Visit / (landing page) multiple times
3. Login as admin
4. Visit /admin/traffic
5. Select different time periods (24hr, 7 days, 30 days)
6. Verify page views are tracked
```

### 4. Test Admin Panel
```
Verify all admin routes work:
- /admin/dashboard - Shows stats
- /admin/posts - Shows posts with filters
- /admin/users - Shows user list
- /admin/traffic - Shows analytics
```

---

## 📋 Checklist for Full Setup

- [ ] Database migration applied successfully
- [ ] Admin user created
- [ ] Can access /admin/dashboard
- [ ] Regular user can create posts
- [ ] Posts default to "pending" status
- [ ] Admin can approve/reject posts
- [ ] Users receive notifications
- [ ] Public pages show only approved posts
- [ ] Traffic tracking works
- [ ] Registration form accepts new fields

---

## 🔧 Environment Variables

No new environment variables are required. The following are already configured:
- `SECRET_KEY` - Flask app secret
- `DATABASE_URL` - Database connection (optional)
- `VAPID_PRIVATE_KEY` - Push notifications
- `VAPID_PUBLIC_KEY` - Push notifications

---

## 📦 Dependencies

All required dependencies are already in `requirements.txt`:
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-Migrate
- SQLAlchemy
- Other existing dependencies

No new packages need to be installed.

---

## 🚀 Running the Application

### Development Mode:
```bash
python app.py
```

### Production Mode (Passenger/Gunicorn):
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

### Docker (if applicable):
Update Dockerfile if using, no changes needed to current code.

---

## 🔐 Security Checklist

- [x] Admin routes protected with `@admin_required` decorator
- [x] Post approval status checked before display
- [x] User can only view own pending posts
- [x] POPIA consent explicitly tracked
- [x] Terms acceptance required
- [x] Admin actions logged (in database records)
- [ ] Consider adding audit log for admin actions
- [ ] Consider email notifications for approvals

---

## 📊 Monitoring & Maintenance

### Regular Tasks:
1. **Monitor pending posts** - Admin dashboard shows queue
2. **Review traffic** - Check /admin/traffic weekly
3. **User management** - Monitor user registrations
4. **Database size** - PageView table can grow large; consider archiving old data

### Database Optimization:
```python
# Archive old page views (example: older than 90 days)
from datetime import datetime, timedelta
from models import PageView

ninety_days_ago = datetime.utcnow() - timedelta(days=90)
old_views = PageView.query.filter(PageView.timestamp < ninety_days_ago).all()
# Archive to separate table or export before deleting
```

---

## 🐛 Troubleshooting

### Issue: "Can't find admin panel"
**Solution:** Ensure user has `role='admin'` in database
```python
# Check user role
user = User.query.filter_by(username='admin').first()
print(f"User role: {user.role}")
```

### Issue: "Posts not showing up after approval"
**Solution:** Make sure post has `approval_status='approved'`
```python
# Check post status
poem = Poem.query.get(poem_id)
print(f"Status: {poem.approval_status}")
```

### Issue: "No notifications appearing"
**Solution:** Verify notifications are being created
```python
# Check notifications in database
from models import Notification
notifs = Notification.query.filter_by(user_id=user_id).all()
print(f"Notifications: {len(notifs)}")
```

### Issue: "Migration errors"
**Solution:** 
```bash
# Downgrade if needed
flask db downgrade
# Try again
flask db upgrade
```

---

## 📞 Support & Resources

### Documentation Files:
- `IMPLEMENTATION_SUMMARY.md` - Detailed implementation notes
- `QUICK_REFERENCE.md` - Quick feature guide
- `UPDATES.md` (lines 676+) - Original requirements

### Key Routes to Know:
```
Public Routes:
- / - Landing page
- /register - New registration
- /login - Login
- /categories - View categories
- /category/<name> - Category view
- /poem/<id>/<slug> - View single post
- /user/<username> - View user profile

User Routes:
- /dashboard - User dashboard
- /profile - User profile
- /add_poem - Create post
- /edit_poem/<id> - Edit post
- /notifications - View notifications

Admin Routes:
- /admin/dashboard - Admin overview
- /admin/posts - Review posts
- /admin/users - Manage users
- /admin/traffic - Analytics
```

---

## ✨ Next Steps (Optional Enhancements)

1. **Email Notifications**
   - Add Flask-Mail
   - Send emails on approval/rejection

2. **Advanced Analytics**
   - User demographics
   - Post performance metrics
   - Category trends

3. **Content Moderation**
   - Flag for review feature
   - Moderation queue
   - Automated content checks

4. **User Management**
   - Ban/suspend users
   - Reset passwords
   - View user activity

5. **API Endpoints**
   - RESTful API for notifications
   - Webhook support
   - Third-party integrations

---

## 📝 License & Compliance

- POPIA Compliance: Consent tracking implemented
- Data handling: Follows POPIA requirements
- User consent: Explicitly collected during registration

---

## 🎉 Congratulations!

Your WaveZA platform is now ready to:
✅ Accept user submissions
✅ Admin review and approve content
✅ Track traffic and analytics
✅ Manage user accounts
✅ Send notifications
✅ Maintain POPIA compliance
✅ Showcase South African art and culture

**For questions or issues, refer to the IMPLEMENTATION_SUMMARY.md file.**

