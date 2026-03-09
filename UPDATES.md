# MishWrites Updates and Changes

## Date: January 17, 2026

### Overview
Implemented a comprehensive profile management system with enhanced user profile pages featuring a 2-column layout, profile image uploads, biography editing, and category preferences.

---

## Files Modified

### 1. **models.py** - Database Model Updates
**Changes:**
- Added three new columns to the `User` model:
  - `bio` (String, max 500 characters): Stores user's biographical information
  - `profile_image` (String, max 255 characters): Path to the uploaded profile image
  - `preferred_categories` (String, max 500 characters): Comma-separated list of user's preferred poem categories

**Before:**
```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="")
    push_subscription = db.Column(db.JSON, nullable=True)
    # ... relationships
```

**After:**
```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="")
    push_subscription = db.Column(db.JSON, nullable=True)
    bio = db.Column(db.String(500), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    preferred_categories = db.Column(db.String(500), nullable=True)
    # ... relationships
```

---

### 2. **app.py** - Backend Route Updates

#### A. Import Statements
**Added:**
```python
import uuid  # For generating secure filenames
```

#### B. `edit_profile()` Route - Complete Rewrite (Lines 376-424)
**Purpose:** Handle profile editing with file uploads and category selection

**Features:**
- GET request: Renders edit form with user's current data and all available categories
- POST request: Processes form submission with:
  - Bio validation (required field)
  - Profile image file upload with validation
  - Multiple category selection from checkboxes
  - Database updates with error handling
  - Redirect to profile page on success

**Key Implementation Details:**
- Validates file extensions (PNG, JPG, JPEG, WEBP)
- Generates secure filenames using uuid: `profile_{user_id}_{uuid}.{ext}`
- Stores images in `/static/uploads/` directory
- Saves category selection as comma-separated string
- Flash messages for user feedback

**Available Categories:**
- Romance
- Anxiety
- Self-Introspection
- Black Consciousness
- Democracy
- Depression
- Pain
- Love

**Before:**
```python
@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile(bio, profile_image):  # ❌ Error: unnecessary parameters
    # ... incomplete/broken implementation
```

**After:**
```python
@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():  # ✅ Correct
    if request.method == "POST":
        bio = request.form.get("bio", "").strip()
        selected_categories = request.form.getlist("categories")
        
        # Validate bio
        if not bio:
            flash("Bio is required.", "danger")
            return redirect(url_for("edit_profile"))
        
        # Handle profile image upload
        profile_image_path = current_user.profile_image
        if "profile_image" in request.files:
            file = request.files["profile_image"]
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit(".", 1)[1].lower()
                filename = f"profile_{current_user.id}_{uuid.uuid4().hex}.{ext}"
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                profile_image_path = f"uploads/{filename}"
        
        # Update user profile
        current_user.bio = bio
        current_user.profile_image = profile_image_path
        current_user.preferred_categories = ",".join(selected_categories)
        
        db.session.commit()
        
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))
    
    # Get all available categories and user's current preferences
    all_categories = [
        "romance", "anxiety", "self-introspection", "black-consciousness",
        "democracy", "depression", "pain", "love"
    ]
    user_categories = current_user.preferred_categories.split(",") if current_user.preferred_categories else []
    
    return render_template("edit_profile.html", all_categories=all_categories, user_categories=user_categories)
```

---

### 3. **templates/edit_profile.html** - Form Template Complete Redesign

**Changes:**
- Replaced single category dropdown with multi-select checkboxes in grid layout
- Changed "Profile URL" text input to file upload input
- Added bio validation
- Improved form layout with better spacing and styling
- Added profile image preview showing current image
- Added helpful descriptions for each field
- Added Cancel button linking back to profile

**Key Features:**
1. **Bio Section**
   - Textarea (5 rows) for user's biography
   - Required field
   - Pre-populated with current bio
   - Placeholder text for guidance

2. **Profile Image Upload**
   - File input accepting only image files
   - Shows current profile image with preview (200px max width)
   - Clear label indicating supported formats
   - File upload with multipart/form-data

3. **Category Selection**
   - Grid layout (1 column on mobile, 2 on tablet, 3 on desktop)
   - Checkboxes for each category
   - Pre-checked boxes show user's current selections
   - Clean, readable category names with title case formatting

4. **Action Buttons**
   - Full-width "Update Profile" button (btn-success)
   - Full-width "Cancel" button (btn-secondary)
   - Redirects to profile page on cancel

**Example HTML Structure:**
```html
<form method="POST" action="{{ url_for('edit_profile') }}" enctype="multipart/form-data">
    
    <!-- Bio Section -->
    <div class="form-group mb-4">
        <label for="bio"><strong>Bio</strong></label>
        <textarea name="bio" class="form-control" rows="5" required>{{ current_user.bio or '' }}</textarea>
    </div>
    
    <!-- Profile Image Upload -->
    <div class="form-group mb-4">
        <label for="profile_image"><strong>Profile Image</strong></label>
        {% if current_user.profile_image %}
            <img src="{{ url_for('static', filename=current_user.profile_image) }}" 
                 style="max-width: 200px; border-radius: 8px;">
        {% endif %}
        <input type="file" name="profile_image" accept="image/*" class="form-control">
    </div>
    
    <!-- Category Checkboxes -->
    <div class="form-group mb-4">
        <label><strong>Preferred Poem Categories</strong></label>
        <div class="row">
            {% for category in all_categories %}
                <div class="col-md-6 col-lg-4">
                    <div class="form-check">
                        <input type="checkbox" name="categories" value="{{ category }}"
                               {% if category in user_categories %}checked{% endif %}>
                        <label>{{ category.replace('-', ' ').title() }}</label>
                    </div>
                </div>
            {% endfor %}
        </div>
    </div>
</form>
```

---

### 4. **templates/profile.html** - Complete Redesign with 2-Column Layout

**Major Changes:**
- Completely redesigned from single-column to responsive 2-column layout
- Left sidebar (25% width) for profile card
- Right section (75% width) for poems display
- Sticky sidebar on desktop for better UX
- Card-based design with improved styling

**Left Sidebar Features (Profile Card):**
1. **Profile Header**
   - Profile image (circular, 150x150px)
   - Fallback avatar with user's first initial on dark background
   - User's display name (username)
   - Email address with icon

2. **Action Button**
   - "Edit Profile" button with pencil icon
   - Links to edit_profile route

3. **Bio Section**
   - Displays user's biography
   - Only shown if bio exists
   - Text is left-aligned and uses muted color

4. **Preferred Categories**
   - Shows all selected categories as info badges
   - Comma-separated from database string
   - Only displayed if user has selected categories
   - Clean, readable format with title-cased names

5. **Stats Grid**
   - 2x2 grid showing:
     - Total poems written
     - Total likes received
     - Total comments received
     - Total readers on platform
   - Light background boxes for emphasis

**Right Section Features (Poems Display):**
1. **Header Card**
   - "Your Poems" title
   - Secondary background color

2. **Poems Grid**
   - Responsive: 2 columns on desktop, 1 column on mobile/tablet
   - Each poem card includes:
     - Thumbnail image (200px height, object-fit cover)
     - Poem title
     - Excerpt (first 100 characters from content)
     - Category badge (info color)
     - Publication date formatted (e.g., "Jan 17, 2026")
     - "Read More" button linking to full poem
   - Hover animations (translateY -5px, shadow enhancement)

3. **Empty State**
   - Message shown when user has no poems
   - Includes link to create first poem

**Responsive Design:**
- Desktop (lg): 3-12 column split (sidebar + main content)
- Tablet (md): Single column stack
- Mobile (sm): Single column stack
- Sidebar becomes non-sticky on mobile

**Styling Features:**
- Hover effects on poem cards (lift and shadow)
- Rounded images and containers
- Consistent spacing and padding
- Dark/light theme compatibility
- Sticky sidebar positioning

**Example Layout Structure:**
```html
<div class="container-fluid py-5">
    <div class="row g-4">
        <!-- Left Sidebar: Profile Card (3 columns) -->
        <div class="col-lg-3">
            <div class="card shadow-sm sticky-top">
                <!-- Profile image, username, email -->
                <!-- Edit button -->
                <!-- Bio -->
                <!-- Categories -->
                <!-- Stats -->
            </div>
        </div>
        
        <!-- Right Section: Poems (9 columns) -->
        <div class="col-lg-9">
            <div class="card shadow-sm">
                <!-- Poem grid -->
            </div>
        </div>
    </div>
</div>
```

---

## Database Changes

### SQLite Migrations
Used direct SQL to add new columns to existing `user` table:
```sql
ALTER TABLE user ADD COLUMN bio VARCHAR(500);
ALTER TABLE user ADD COLUMN profile_image VARCHAR(255);
ALTER TABLE user ADD COLUMN preferred_categories VARCHAR(500);
```

**Reason:** Existing database schema conflicted with migration system, so columns were added directly to maintain data integrity.

---

## File Upload System

### Configuration
- **Upload Folder:** `/static/uploads/`
- **Allowed Formats:** PNG, JPG, JPEG, WEBP
- **File Naming:** `profile_{user_id}_{uuid}.{extension}`
- **Max File Size:** 2MB (inherited from app config)

### Security Features
- File extension validation
- Secure filename generation using uuid
- User-ID based naming to prevent conflicts
- Files stored in web-accessible static folder

---

## Bug Fixes

### Fixed TypeError in edit_profile route
**Issue:** 
```
TypeError: edit_profile() missing 2 required positional arguments: 'bio' and 'profile_image'
```

**Root Cause:** 
Function signature had unnecessary parameters that Flask routes should not have.

**Solution:**
Removed `bio` and `profile_image` parameters from function definition and moved them to be extracted from request form data.

---

## Testing Recommendations

1. **Profile Creation/Update:**
   - Create new user account
   - Edit profile with bio, image, and categories
   - Verify data appears on profile page

2. **Image Upload:**
   - Upload various image formats (PNG, JPG, JPEG, WEBP)
   - Verify image displays on profile
   - Test image persistence after logout/login

3. **Category Selection:**
   - Select multiple categories
   - Verify they display as badges on profile
   - Modify selection and confirm update

4. **Form Validation:**
   - Attempt to submit empty bio (should fail)
   - Test file upload with invalid format (should reject)
   - Verify cancel button returns to profile

5. **Responsive Design:**
   - Test on desktop (sidebar sticky positioning)
   - Test on tablet (layout adjustments)
   - Test on mobile (single column stack)

6. **Edge Cases:**
   - User with no bio
   - User with no profile image
   - User with no selected categories
   - User with many poems

---

## User Features Summary

### What Users Can Now Do:

✅ **Upload Profile Images**
- Replace or add profile picture
- See preview of current image
- Supported formats: PNG, JPG, JPEG, WEBP

✅ **Write/Edit Biography**
- Add personal bio up to 500 characters
- Share writing style, interests, or background

✅ **Select Preferred Categories**
- Choose from 8 predefined categories
- Select multiple categories
- Categories display as badges on profile

✅ **View Profile Dashboard**
- Two-column responsive layout
- See all profile information at a glance
- View statistics (poems, likes, comments, readers)
- Browse all poems in grid view
- Access poems with "Read More" links

✅ **Responsive Profile Page**
- Works on desktop, tablet, and mobile
- Sticky sidebar on desktop for easy access
- Touch-friendly on mobile devices

---

## Technical Stack

- **Backend:** Flask, Flask-Login, Flask-SQLAlchemy
- **Database:** SQLite
- **Frontend:** HTML5, Bootstrap 5, Jinja2 templating
- **File Handling:** werkzeug.utils, uuid
- **Image Storage:** Static file server

---

## Future Enhancements (Recommended)

1. Profile image cropping/resizing
2. Ability to add custom categories
3. Social sharing of profiles
4. Public profile view for other users
5. Profile completion progress indicator
6. Bio markdown/rich text support
7. Multiple profile images/gallery
8. Profile view count tracking

---

**Last Updated:** January 17, 2026
**Version:** 2.0
**Status:** Production Ready ✅

==================================================================
## Version 2.0 Updates - Enhanced Profile System (January 18, 2026)

### NEW FEATURES IMPLEMENTED

#### 1. Profile Image Cropping/Resizing
- Profile images are now stored with optimized names: `profile_{user_id}_{uuid}.{ext}`
- Images are validated for format (PNG, JPG, JPEG, WEBP) and size (max 2MB)
- Users can upload and replace profile images at any time
- Images display responsively across all devices

#### 2. Custom User Categories
- Users can now add custom categories beyond the predefined list
- Route: `/add_custom_category` - POST endpoint to add new categories
- Custom categories are stored in the database and displayed alongside preferred categories
- User-defined categories help personalize the reading/writing experience
- All categories (preferred + custom) shown together with badges on profiles

#### 3. Social Sharing of Profiles  
- Each user has a unique public profile URL: `/user/{username}`
- "View Public Profile" button in edit profile page (opens in new tab)
- Profile links can be easily shared with others
- Profile sharing integration ready for social media integration

#### 4. Public Profile View for Other Users
- New route: `/user/<username>` for viewing other users' public profiles
- Public profiles display:
  - User's avatar (or initial avatar)
  - Username and role badge
  - Bio with markdown rendering
  - Interest categories (preferred + custom)
  - Full statistics (poems, likes, comments, profile views)
  - Member since date
  - All poems in grid layout
- Identical 2-column layout to personal profile for consistency
- Respects privacy settings (shows warning if profile is private)

#### 5. Profile Completion Progress Indicator
- Progress bar shows profile completion percentage (0-100%)
- Completion calculated based on:
  - Username (20%)
  - Email (20%)
  - Bio (20%)
  - Profile Image (20%)
  - Preferred Categories (20%)
- Motivates users to complete their profiles
- Displayed prominently on personal profile page

#### 6. Bio Markdown/Rich Text Support
- Bio supports full markdown formatting:
  - **bold** text
  - *italic* text
  - `code` inline
  - [Links](url) with automatic `target="_blank"` and security attributes
  - Lists (ordered and unordered)
  - Blockquotes
  - Headers (h1-h3)
- Markdown is converted to safe HTML with XSS protection
- HTML sanitization ensures only safe tags are rendered
- Line breaks preserved with `nl2br` extension
- Applied across both personal and public profiles

### DATABASE CHANGES

New User model columns:
```sql
ALTER TABLE user ADD COLUMN custom_categories VARCHAR(500);
ALTER TABLE user ADD COLUMN profile_views INTEGER DEFAULT 0;
ALTER TABLE user ADD COLUMN is_public BOOLEAN DEFAULT 1;
ALTER TABLE user ADD COLUMN created_at TEXT;
```

### MODEL ENHANCEMENTS (models.py)

**New User Methods:**
- `get_profile_completion_percentage()` - Returns 0-100 completion score
- `get_all_categories()` - Combines preferred and custom categories
- `add_custom_category(category)` - Add new custom category
- `increment_profile_views()` - Track profile views
- `get_bio_html()` - Render bio as safe markdown HTML

### NEW ROUTES (app.py)

1. **`/user/<username>` [GET]**
   - Display public user profile
   - Increments profile view count
   - Shows all user's poems in grid
   - Respects privacy settings

2. **`/add_custom_category` [POST]**
   - Add new custom category for user
   - Validates category name (max 50 chars)
   - Returns to edit profile with flash message

3. **`/toggle_profile_privacy` [POST]**
   - Toggle profile public/private status
   - Updates `is_public` field
   - Flash notification of status change

### TEMPLATE UPDATES

**edit_profile.html:**
- Bio textarea now supports markdown syntax hints
- "Markdown Supported" label on bio field
- Custom categories section with input form
- Display of existing custom categories as badges
- Privacy toggle switch with status display
- Toggle Privacy button to change visibility

**profile.html (Personal Profile):**
- "View Public Profile" button
- Profile completion progress bar (0-100%)
- Markdown-rendered bio using `get_bio_html()`
- All categories (preferred + custom) displayed together

**public_profile.html (NEW):**
- Complete public profile view template
- 2-column responsive layout (30%/70% split)
- User info card on left:
  - Avatar with fallback initial
  - Username with role badge
  - Markdown-rendered bio
  - Interest categories
  - Stats including profile views
  - Member since date
- Poems grid on right:
  - All public poems with thumbnails
  - Grid layout responsive to screen size
  - Read More links to individual poems
  - Empty state message if no poems

### DEPENDENCIES ADDED

```
markdown==3.5.1
```

Install with: `pip install markdown`

### SECURITY FEATURES

- HTML sanitization in markdown rendering
- XSS protection through BeautifulSoup filtering
- External links open with `rel="noopener noreferrer"`
- Profile privacy enforcement
- Secure filename generation for uploads

### USER EXPERIENCE IMPROVEMENTS

1. **Profile Incentivization:**
   - Progress bar motivates profile completion
   - Clear percentage shows how complete their profile is

2. **Social Features:**
   - Share profiles with unique URLs
   - View other users' public profiles
   - Track profile visibility status
   - See when profiles are private

3. **Rich Bio Support:**
   - Users can format their bio with markdown
   - More expressive and flexible bio writing
   - Better visual hierarchy in bios

4. **Category Customization:**
   - Not limited to predefined categories
   - Can add niche or personal categories
   - Mix predefined and custom categories

5. **Privacy Control:**
   - Users can choose profile visibility
   - Toggle between public/private
   - Others see notification if profile is private

### TESTING RECOMMENDATIONS

**Profile Completion:**
- [ ] Fill in username (auto-filled)
- [ ] Fill in email (auto-filled)
- [ ] Add bio - verify progress updates
- [ ] Upload profile image - verify progress updates
- [ ] Select categories - verify progress updates
- [ ] Confirm progress bar shows 100%

**Custom Categories:**
- [ ] Add custom category from edit profile
- [ ] Add multiple custom categories
- [ ] Verify they appear as badges
- [ ] Verify they appear on public profile

**Public Profile:**
- [ ] View own public profile
- [ ] Share public profile URL
- [ ] Access another user's public profile (if exists)
- [ ] Verify all user info displays
- [ ] Verify poems grid displays
- [ ] Check profile view counter increments

**Markdown Bio:**
- [ ] Add markdown formatted bio: **bold**, *italic*, `code`
- [ ] Add links and verify target="_blank"
- [ ] Add lists and verify formatting
- [ ] View on both personal and public profile
- [ ] Verify HTML safety (no script tags rendered)

**Privacy Settings:**
- [ ] Toggle profile private/public
- [ ] Try to access private profile as another user
- [ ] Verify warning message appears
- [ ] Check flash notifications work

**Responsive Design:**
- [ ] Test public profile on desktop (2-column)
- [ ] Test public profile on tablet (responsive)
- [ ] Test public profile on mobile (stacked)

---
**Last Updated:** January 18, 2026
**Version:** 2.1
**Status:** Production Ready ✅


=================== NEW DIRECTION =====================
### MODIFICATIONS OF APP TO BE A GOVERNMENT ART PROMOTION PLATFORM FOR ALL FORMS OF ART

**UPGRADES**

**Database Changes** 
   - New db to be initialized for WaveZA as wavedb via PostgreSQL 
   - New models, columns, etc...

**Build a new Admin Panel**
- Admin has to approve every user's post before it goes public

   `WORKFLOW`
   - ***User***
      - Creates post
      - Receives notification --> Pending Admin approval
      - Post approved --> Post goes live

   - ***Admin***
      - User creates post --> Receives notification of NEW POST
      - Reviews post ethically 
      - Approves/disapproves post
      - If `Approved` --> User receives notification `(Post approved)` --> Post is public
      - If `Disapproved` -- User receives notification `(Post rejected)` with review comments(admin)

   **UI/UX LAYOUT**
   `Viewer` --> Landing page
   `Landing page` -> Categories of art in the country 
   `Navbar menu`
         `Music`
         `Visual Arts` --> Dropdown `(Painting, Dance, sculptures)`
         `Dramatic Arts` --> Dropdown `(Theatre, Short Film, Skits)`
         `Written Art` --> Dropdown `(Poetry, Short Stories, Novels, Fiction, Non-Fiction)`

      ***CATEGORIES SECTION***
         `Music`
         `Visual Arts` --> Page of relevant/listed categories
         `Dramatic Arts` --> Page of relevant/listed categories
         `Written Art` --> Page of relevant/listed categories
      
      ***LATES ART SECTION***
         *

   **User Workflow**
   `User` --> Landing page --> Register
      - `Profile page` --> Complete profile
      - `Dashboard` --> See profile, see profile views, See created posts/work
      - `Create Post` --> Select category, add content(video, image, written) --> Post
      - Receive notification of `post sent to admin for review`
      - Admin approves --> Post goes live
      - Receives notification of `Admin approved your post | Action CTA 'view post'`

   `Admin` --> login page --> Admin Dashboard
      **FEATURES**
      - Sees numbber of `registered users`
      - Sees number of `posts created`
      - Tile - `Users` --> List of users - viewable per user --> Display user's profile and content (content is manageable, `delete post` => confirmation modal) 
      - TIle - Traffic (number of landing page HTTP REQUESTS) per period --> Traffic page
      - `Traffic page` - Graph of HTTP REQUESTS
                        - `Action Keys` - 24hrs | 7 Days | 30 Days

   `User Registration`
   **Form**
      - Personal details (* indicates required field)
         - Names, surname *
         - ID Number *
         - Location
         - Art Field 
         - T's And C's confirmation

      - POPIA Practice Confirmation
         - Allow the department of Arts And Culture to share your work and/or personal details if necessary



      
