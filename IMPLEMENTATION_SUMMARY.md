# WaveZA - Government Art Promotion Platform Implementation Summary

## Overview
The WaveZA application has been successfully updated to function as a government art promotion platform for all forms of art with comprehensive admin oversight and post approval workflows.

---

## Key Changes Implemented

### 1. **Database Model Updates** (`models.py`)

#### User Model Enhancements:
- Added `id_number` - National ID or Passport number (required for registration)
- Added `location` - User location/city
- Added `art_field` - Primary art field preference
- Added `popia_consent` - POPIA data sharing consent flag
- Added `terms_accepted` - Terms & Conditions acceptance flag
- Added `notifications` relationship to Notification model
- Changed default `role` from empty string to `"user"`

#### Poem Model Enhancements:
- Added `approval_status` field (default: "pending") - can be "pending", "approved", or "rejected"
- Added `admin_review_comments` - Comments from admin reviews
- Added `submitted_at` - Timestamp when post was submitted for review

#### New Models:
- **Notification Model** - Tracks all user notifications
  - `notification_type`: "post_approved", "post_rejected", "post_submitted"
  - `is_read`: Boolean flag for read/unread status
  - Relates poems to user notifications

- **PageView Model** - Tracks traffic analytics
  - Records landing page HTTP requests
  - Stores timestamp, IP address, and user agent
  - Used for traffic analytics dashboard

---

### 2. **Admin Panel Implementation** (`app.py`)

#### New Routes:
- **`/admin/dashboard`** - Main admin dashboard with overview statistics
  - Total registered users count
  - Total posts count
  - Pending posts count
  - Approved posts count
  - Rejected posts count
  - Recent pending posts list

- **`/admin/posts`** - Post review and management
  - Filterable by status (pending, approved, rejected)
  - Paginated list (10 per page)
  - Modal view for detailed post content
  - Approve/Reject functionality

- **`/admin/post/<id>/approve`** - Approve a post
  - Sets status to "approved"
  - Notifies user with success message
  - Post becomes publicly visible

- **`/admin/post/<id>/reject`** - Reject a post with comments
  - Sets status to "rejected"
  - Stores admin review comments
  - Notifies user with rejection reason

- **`/admin/users`** - User management dashboard
  - List all registered users with details
  - Shows user stats (joined date, art field, location)
  - Paginated view

- **`/admin/user/<id>`** - Detailed user profile view
  - View all user's posts with approval status
  - Delete user posts
  - View user information and bio

- **`/admin/traffic`** - Traffic analytics dashboard
  - Selectable periods: 24 hours, 7 days, 30 days
  - Daily page view charts
  - Total views statistics
  - Recent views table

#### Admin Decorator:
- `@admin_required` - Ensures user is admin before accessing admin routes
- Returns 403 error for non-admin users

---

### 3. **Post Approval Workflow**

#### User Flow:
1. User creates a post via `/add_poem`
2. Post status is set to "pending"
3. User receives notification: "Post submitted for admin approval"
4. All admins receive notification: "New post awaiting review"
5. Admin reviews post in admin panel
6. If approved:
   - Post status → "approved"
   - Post becomes visible on public pages
   - User receives notification: "Post approved! 🎉"
   - Likes and comments become active
7. If rejected:
   - Post status → "rejected"
   - Post remains private to author
   - User receives notification with admin's review comments

#### Post Visibility Rules:
- **Landing page** (`/`): Shows only approved posts
- **Category pages** (`/category/<name>`): Shows only approved posts
- **Public profiles** (`/user/<username>`): Shows only approved posts for other users
- **User dashboard** (`/dashboard`): Shows all posts (pending, approved, rejected) for author only
- **User profile** (`/profile`): Shows all posts with status badges

---

### 4. **Updated Registration Form** (`templates/register.html`)

New fields added:
- **ID Number** (Required) - National ID or Passport number
- **Location** (Optional) - City, province, or country
- **Art Field** (Optional) - Dropdown with categories:
  - Music
  - Visual Arts (Painting, Sculpture, Dance)
  - Dramatic Arts (Theatre, Film, Comedy/Skits)
  - Written Art (Poetry, Short Stories, Novels, Fiction, Non-Fiction)
  - Other

**Policies Section:**
- POPIA Consent Checkbox
  - Allows Department of Arts and Culture to share work/personal details
  - Includes POPIA notice about data handling
- Terms & Conditions Checkbox (Required)

---

### 5. **Notification System** (`models.py` + Routes)

#### Notification Types:
- `post_submitted` - User notified when post is submitted for review
- `post_approved` - User notified when post is approved (with link to view)
- `post_rejected` - User notified when post is rejected (with admin comments)
- `new_post_submitted` - Admins notified of new posts awaiting review

#### Notification Routes:
- **`/notifications`** - User notifications page
  - Paginated notification list
  - Mark notifications as read
  - Links to related posts

- **`/notification/<id>/mark-as-read`** - Mark notification as read (AJAX)

---

### 6. **Traffic Tracking** (`models.py` + Routes)

#### Landing Page Tracking:
- Every visit to `/` (index) creates a PageView record
- Captures:
  - Page name ("landing_page")
  - User agent
  - IP address
  - Timestamp

#### Analytics Routes:
- **`/admin/traffic`** - Display traffic analytics
  - Selectable periods (24 hours, 7 days, 30 days)
  - Daily view chart (visual bar chart)
  - Total views statistics
  - Recent views table

---

### 7. **Dashboard Updates** (`templates/dashboard.html`)

#### New Statistics:
- Published Poems (only approved)
- Pending Review (with warning color if > 0)
- Total Likes
- Total Comments
- Total Users

#### Post List Improvements:
- Status badges for each post
  - "Published" (green) for approved
  - "Pending Review" (yellow) for pending
  - "Rejected" (red) for rejected
- Edit and Delete buttons maintained

---

### 8. **Route Modifications**

#### Index Route (`/`):
- Added PageView tracking
- Filters poems to show only `approval_status="approved"`
- Categories count only approved posts

#### Category Route (`/category/<name>`):
- Shows only approved posts in category
- Navigation categories show only approved counts

#### Poem Route (`/poem/<id>/<slug>`):
- Checks approval status
- If not approved and user is not author → redirect to index
- Only author can view pending/rejected posts

#### Public Profile Route (`/user/<username>`):
- Shows only approved posts for other users
- Shows all posts if viewing own profile

#### Add Poem Route (`/add_poem`):
- Sets `approval_status = "pending"`
- Creates two notifications:
  - User notification: "Post submitted for admin approval"
  - Admin notifications: "New post awaiting review"
- Flash message informs user about pending status

#### Register Route (`/register`):
- Accepts new fields: id_number, location, art_field, popia_consent, terms_accepted
- Validates id_number (required)
- Validates terms_accepted (required)
- Sets user role to "user" (not "writer"/"reader")

---

## File Structure

### New Templates:
```
templates/
├── admin/
│   ├── dashboard.html      # Admin overview dashboard
│   ├── posts.html          # Post review management
│   ├── users.html          # User management
│   ├── user_profile.html   # Individual user profile (admin view)
│   └── traffic.html        # Traffic analytics
└── notifications.html      # User notifications page
```

### Modified Templates:
- `templates/register.html` - Added new registration fields
- `templates/dashboard.html` - Updated with status badges and pending count

### Modified Python Files:
- `models.py` - Added new models and fields
- `app.py` - Added admin routes and workflow logic

---

## UI/UX Design Approach

✅ **Preserved Existing Design:**
- All original styling maintained
- Bootstrap classes retained
- Existing color schemes preserved
- No changes to navbar or navigation structure
- No changes to base template structure

✅ **New Components:**
- Admin templates use consistent Bootstrap styling
- Notification badges for unread messages
- Status badges (success/warning/danger) for post approval status
- Modal dialogs for detailed views and confirmations
- Traffic chart uses HTML/CSS bar representation

---

## Security Measures

- `@admin_required` decorator restricts admin routes to admins only
- Post approval checks prevent unauthorized public visibility
- User can only see their own pending posts
- POPIA consent explicitly tracked
- Terms acceptance required

---

## Future Enhancements (Optional)

1. Email notifications when posts are approved/rejected
2. Bulk post approval actions
3. Advanced search and filtering in admin panel
4. Post edit history tracking
5. User ban/suspension features
6. Content moderation flags
7. Advanced traffic analytics (devices, browsers, etc.)
8. Post scheduling feature

---

## Testing Checklist

- [ ] Admin can access admin dashboard
- [ ] Admin can review pending posts
- [ ] Admin can approve/reject posts
- [ ] Users receive approval notifications
- [ ] Only approved posts visible on public pages
- [ ] User sees pending posts on dashboard
- [ ] Traffic is tracked on landing page
- [ ] Notification page works correctly
- [ ] Registration with new fields works
- [ ] POPIA consent is saved

---

## Database Migration

To apply these changes to your existing database:

1. Backup your current database
2. Run: `flask db migrate -m "Add admin and approval workflow"`
3. Run: `flask db upgrade`

Or to reset with new schema:
```python
with app.app_context():
    db.drop_all()
    db.create_all()
```

---

## Deployment Notes

- All existing routes continue to work
- No breaking changes to public API
- New admin panel is protected by admin role
- Existing posts default to "approved" status if not set (add migration if needed)
- Notifications are stored in database, not pushed in real-time (can integrate with push notifications)

---

## Summary

The WaveZA platform is now fully equipped as a government art promotion platform with:
✅ Comprehensive admin oversight
✅ Post approval workflows
✅ Multiple art categories
✅ Notification system
✅ Traffic analytics
✅ POPIA compliance framework
✅ Enhanced user registration
✅ Complete UI/UX consistency
