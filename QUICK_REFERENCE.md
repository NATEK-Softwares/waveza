# WaveZA Platform - Quick Reference Guide

## 🚀 New Features Overview

### Admin Dashboard
**URL:** `/admin/dashboard`
- Overview of all platform metrics
- Quick stats: Users, Posts, Pending, Approved, Rejected
- Recent pending posts list
- Links to detailed management sections

### Post Approval System
**Process:**
1. User creates post → Status: **Pending**
2. Notification sent to user & all admins
3. Admin reviews in `/admin/posts`
4. Admin approves → Post goes **Live** → User notified
5. Admin rejects → Post **Hidden** → User notified with reason

### Admin Panel Routes

| Route | Purpose | Features |
|-------|---------|----------|
| `/admin/dashboard` | Overview | Stats, metrics, recent posts |
| `/admin/posts?status=pending` | Review posts | Filter by status, modal view, approve/reject |
| `/admin/users` | Manage users | List all users with details |
| `/admin/user/<id>` | User profile | View user posts, delete posts |
| `/admin/traffic` | Analytics | Landing page traffic, daily views, graphs |

### User Notifications
**URL:** `/notifications`
- View all notifications
- Filter by type (approved, rejected, submitted)
- Link to related posts
- Mark as read functionality

### Registration Form
**New Fields:**
- ID Number (Required)
- Location (Optional)
- Art Field (Optional) - Dropdown menu
- POPIA Consent Checkbox
- Terms & Conditions Checkbox (Required)

### Art Field Categories
```
- Music
- Visual Arts
  - Painting
  - Sculpture
  - Dance
- Dramatic Arts
  - Theatre
  - Film & Video
  - Comedy/Skits
- Written Art
  - Poetry
  - Short Stories
  - Novels
  - Fiction
  - Non-Fiction
- Other
```

---

## 📊 Post Status Flow

```
User Creates Post
         ↓
    PENDING ← User Notification: "Awaiting Review"
         ↓
    Admin Reviews
    ↙         ↘
APPROVED     REJECTED
   ↓            ↓
PUBLIC      PRIVATE
User Notified  User Notified
Post Live      with Comments
```

---

## 🔒 Admin Requirements
- User role must be "admin"
- Access controlled via `@admin_required` decorator
- Redirects non-admins to dashboard

---

## 📱 Notifications
**Automatic Notifications:**
- Post submitted for review (to user)
- New post awaiting review (to all admins)
- Post approved (to user)
- Post rejected with comments (to user)

---

## 📈 Traffic Analytics
**Tracked Data:**
- Landing page (`/`) visits
- User agent information
- IP address
- Timestamp

**Views Available:**
- 24 Hours
- 7 Days
- 30 Days

---

## 🗂️ File Changes Summary

### New Files Created:
```
templates/admin/dashboard.html
templates/admin/posts.html
templates/admin/users.html
templates/admin/user_profile.html
templates/admin/traffic.html
templates/notifications.html
IMPLEMENTATION_SUMMARY.md
```

### Modified Files:
```
models.py - Added User fields, new models
app.py - Added admin routes, workflow
templates/register.html - New form fields
templates/dashboard.html - Status badges
```

---

## 🔧 Database Migrations

**Run migrations:**
```bash
flask db migrate -m "Add admin and approval workflow"
flask db upgrade
```

**Or reset database:**
```python
from app import app, db
with app.app_context():
    db.drop_all()
    db.create_all()
```

---

## 🧪 Testing the Features

### Test Admin Access:
1. Create user with `role='admin'`
2. Login as admin
3. Visit `/admin/dashboard`

### Test Post Approval:
1. Login as regular user
2. Create post
3. Check notification
4. Login as admin
5. Visit `/admin/posts?status=pending`
6. Approve/Reject post
7. Check user notifications

### Test Traffic Tracking:
1. Visit landing page (/)
2. Admin visits `/admin/traffic`
3. See page view recorded

---

## 🎨 UI Design Notes

✅ **Preserved:**
- Original navbar design
- Color schemes
- Bootstrap styling
- Dashboard layout
- Card components

✅ **Added:**
- Status badges (approved/pending/rejected)
- Modal dialogs for post review
- Admin panel with clean tables
- Traffic chart visualization
- Notification badges

---

## ⚡ Key Implementation Details

### Approval Status Values:
- `"pending"` - Awaiting admin review (default for new posts)
- `"approved"` - Visible on public pages
- `"rejected"` - Only visible to author

### Notification Types:
- `"post_submitted"` - User: post submitted for review
- `"new_post_submitted"` - Admin: new post to review
- `"post_approved"` - User: post approved
- `"post_rejected"` - User: post rejected

### User Roles:
- `"user"` - Regular user (default)
- `"admin"` - Administrator

---

## 📝 POPIA Compliance

- Explicit consent checkbox on registration
- Data handling notice included
- Tracks consent status in database
- Can be used for data access requests

---

## 🚨 Important Notes

1. **Existing Posts:** Don't have approval_status set. Add migration to default to "approved":
   ```python
   # In migration
   op.add_column('poem', sa.Column('approval_status', sa.String(20), server_default='approved'))
   ```

2. **Admin Creation:** You'll need to manually set `role='admin'` for admin users in database or create admin creation route.

3. **Push Notifications:** System stores notifications in database. Integrate with push service if needed.

4. **Email Notifications:** Optional enhancement - not yet integrated.

---

## 💡 Future Enhancements

- [ ] Email notifications
- [ ] Bulk actions in admin panel
- [ ] Advanced search/filtering
- [ ] Post edit history
- [ ] User ban/suspension
- [ ] Content moderation flags
- [ ] Advanced analytics
- [ ] Post scheduling
- [ ] API endpoints for notifications
- [ ] Webhook support

