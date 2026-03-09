# 🌊 WaveZA - Inclusive Art Platform

*Discover and share art that speaks to the soul. Connect with artists and express yourself through poetry, stories, and visual arts.*

WaveZA is a modern, cross-platform art sharing platform that has evolved from a traditional Flask web application into a scalable **Flask API + React SPA** architecture, packaged for **mobile (Capacitor)** and **desktop (Tauri)** distribution. Originally a server-side rendered poetry platform, it now offers a seamless user experience across web, mobile, and desktop environments.

---

## 🔄 Transformation Overview

### From: Traditional Flask Web App
- **Server-Side Rendering**: Jinja2 templates, full-page reloads.
- **Monolithic Structure**: Backend and frontend tightly coupled.
- **Web-Only**: Limited to browsers, no native app distribution.
- **Features**: User auth, poem CRUD, categories, profiles, admin panel.

### To: Modern API-Driven SPA with Native Packaging
- **API Backend**: Flask exposes RESTful endpoints (`/api/*`) for all operations.
- **React Frontend**: Single-Page Application with client-side routing, real-time updates.
- **Cross-Platform**: WebView-based mobile apps (Capacitor) and native desktop apps (Tauri).
- **Enhanced UX**: Responsive design, offline capabilities (PWA), installable on app stores.

**Key Changes**:
- Added CORS support for cross-origin requests.
- Converted routes to dual-mode (HTML + JSON).
- Introduced React components for dynamic UI.
- Integrated Capacitor/Tauri for native packaging.
- Maintained backward compatibility for existing web users.

---

## 🏗️ Architecture Diagram

```mermaid
graph TB
    subgraph "User Devices"
        A[Web Browser] --> F[React SPA]
        B["Mobile App (Capacitor)"] --> F
        C["Desktop App (Tauri)"] --> F
    end

    F --> G[Flask API Backend]
    G --> H[SQLAlchemy ORM]
    H --> I["SQLite / PostgreSQL DB"]

    subgraph "External Services"
        J["Cloudinary (Media)"]
        K[Push Notifications]
    end

    G --> J
    G --> K

    subgraph "Development Tools"
        L[React Dev Server]
        M[Flask Dev Server]
        N[Capacitor CLI]
        O[Tauri CLI]
    end

    style F fill:#e1f5fe
    style G fill:#f3e5f5
    style I fill:#e8f5e8
```

**Explanation**:
- **Frontend**: React SPA handles UI, routing, and API calls.
- **Backend**: Flask API manages business logic, auth, and data.
- **Database**: SQLite for dev, PostgreSQL for production.
- **Packaging**: Capacitor wraps React in mobile WebViews; Tauri creates native desktop binaries.
- **Services**: Optional integrations for media uploads and notifications.

---

## 📁 Project Structure

```
WaveZA/
├── app.py                          # Flask API backend (main entry point)
├── models.py                       # SQLAlchemy models (User, Poem, etc.)
├── extensions.py                   # DB and other extensions
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables
├── migrations/                     # Alembic migrations
├── static/                         # Original web assets (CSS, JS, images)
├── templates/                      # Original Jinja2 templates (for legacy)
├── tests/                          # Unit tests
├── frontend/                       # React SPA frontend
│   ├── public/                     # Static assets
│   ├── src/
│   │   ├── components/             # React components (Home, Login, etc.)
│   │   ├── App.tsx                 # Main app with routing
│   │   └── index.tsx               # Entry point
│   ├── package.json                # Node dependencies
│   ├── capacitor.config.ts         # Capacitor config
│   ├── src-tauri/                  # Tauri config and Rust code
│   └── android/ / ios/             # Capacitor native projects
├── PWA_README.md                   # PWA setup details
├── IMPLEMENTATION_SUMMARY.md       # Original features summary
└── README.md                       # This file
```

---

## ✨ Features

### Core Functionality
- **User Authentication**: Register, login, logout with session management.
- **Poem Management**: Create, view, edit poems with categories and media uploads.
- **Social Engagement**: Full CRUD for likes and threaded comments/replies.
- **Profiles**: User dashboards, bio editing, public profiles.
- **Admin Panel**: Moderation, approval workflows, analytics.
- **Categories**: Browse poems by themes (e.g., anxiety, romance).

### New Enhancements
- **API-Driven**: All operations via RESTful endpoints.
- **React UI**: Modern, responsive interface with routing.
- **PWA Support**: Offline access, installable web app.
- **Cross-Platform**: Native mobile and desktop apps.
- **CORS Enabled**: Secure cross-origin communication.
- **File Upload**: Direct image/video upload from React frontend.
- **Offline Backend**: Bundled Flask executable for native apps.

### Technical Highlights
- **Security**: Password hashing, CSRF protection, secure cookies.
- **Media Handling**: Video/image uploads with Cloudinary integration.
- **Notifications**: Push notifications for engagement.
- **Database**: Migrations with Flask-Migrate.
- **Comment System**: Threaded comments with nested replies.
- **Like System**: Toggle likes with real-time count updates.

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.8+** (for Flask backend)
- **Node.js 16+** (for React frontend)
- **Rust** (for Tauri desktop builds)
- **Android Studio** (for Capacitor Android)
- **Xcode** (for Capacitor iOS, macOS only)

### 1. Clone the Repository
```bash
git clone https://github.com/NATEK-Softwares/waveza.git
cd WaveZA
```

### 2. Backend Setup (Flask API)
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL, SECRET_KEY, etc.

# Initialize database
flask db upgrade

# Run backend
flask run  # Runs on http://localhost:5000
```

### 3. Frontend Setup (React SPA)
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start  # Runs on http://localhost:3000
```

### 4. Database Configuration
- **Development**: Uses SQLite (`mishwrites.db`).
- **Production**: Set `DATABASE_URL` to PostgreSQL.
- Run migrations: `flask db upgrade`.

---

## 🛠️ Development Workflow

### Running Locally
1. Start Flask backend: `flask run` (port 5000).
2. Start React frontend: `cd frontend && npm start` (port 3000).
3. Access at `http://localhost:3000` – it proxies API calls to Flask.

### Building for Production
```bash
# Build React app
cd frontend
npm run build

# Sync with Capacitor/Tauri
npx cap sync
npx tauri build
```

### Testing
- **Backend**: `python -m pytest tests/`
- **Frontend**: `cd frontend && npm test`

### Environment Variables (`.env`)
```env
DATABASE_URL=postgresql://postgres:Mishack%4010@localhost:5432/poetrydb  # or PostgreSQL URL
SECRET_KEY=your-a9bbd956810c0a5578882c775d479f6624ba4a1f45cf976c1f0ea6c67405249f
FLASK_ENV=development
VAPID_PUBLIC_KEY=...  # For push notifications
VAPID_PRIVATE_KEY=...
VAPID_EMAIL=your@email.com
DEV_PREVIEW=0  # For VS Code mobile previews
```

---

## 📦 Packaging & Distribution

### Mobile Apps (Capacitor)
WaveZA can be installed as a native mobile app on iOS/Android.

```bash
cd frontend
npm run build
npx cap sync

# Android
npx cap open android  # Opens in Android Studio
# Build APK via Studio

# iOS (macOS)
npx cap open ios     # Opens in Xcode
# Build IPA via Xcode
```

- **App Store Submission**: Follow platform guidelines for icons, screenshots, and metadata.
- **Features**: WebView-based, supports PWA offline mode.

### Desktop Apps (Tauri)
Native desktop executables for Windows, Mac, Linux.

```bash
cd frontend
npx tauri build
```

- **Output**: Executables in `frontend/src-tauri/target/release/`.
- **Installation**: Distribute `.exe`, `.dmg`, or `.deb` files.
- **Requirements**: Rust toolchain installed.

### Web Deployment
- Deploy Flask API to Heroku/Render/Vercel.
- Host React build on Netlify/CDN.
- For PWA: Ensure HTTPS and service worker.

### Offline Backend Bundling
For native apps to work offline, bundle the Flask backend as a standalone executable:

```bash
# Install PyInstaller
pip install PyInstaller

# Create bundled backend
python build_offline_bundle.py
```

This creates:
- `bundled-backend/waveza-backend` (Linux/Mac executable)
- `bundled-backend/waveza-backend.exe` (Windows executable)
- `bundled-backend/start-backend.sh` (startup script)

**Native App Integration**:
- Copy `bundled-backend/` to your Capacitor/Tauri project
- Start the executable when the app launches
- React app automatically detects native context and connects to `localhost:5000`

---

## 📡 API Documentation

The Flask backend exposes RESTful endpoints under `/api/*`. All responses are JSON.

### Authentication
- `POST /api/register` - Register user (body: username, email, password)
- `POST /api/login` - Login (body: username, password)
- `POST /api/logout` - Logout

### Poems
- `GET /api/` - Home data (poems, categories)
- `GET /api/poems` - All approved poems
- `GET /api/poem/<id>` - Poem details
- `POST /api/poem` - Create poem (multipart/form-data: title, content, category, thumbnail, video)
- `GET /api/categories` - List categories
- `GET /api/category/<name>` - Poems in category

### Comments
- `GET /api/poem/<id>/comments` - Get all comments for a poem
- `POST /api/poem/<id>/comment` - Add comment/reply (body: content, parent_id?)
- `DELETE /api/comment/<id>` - Delete comment (author or admin only)

### Likes
- `GET /api/poem/<id>/likes` - Get like status and count
- `POST /api/poem/<id>/like` - Toggle like/unlike

### User
- `GET /api/dashboard` - User dashboard data
- `POST /api/edit_profile` - Update profile (body: bio, categories)

### Other
- `GET /api/notifications` - User notifications
- `POST /api/track-install` - Track PWA installs

**Example Request**:
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}' \
  --cookie-jar cookies.txt
```

**Response**:
```json
{"success": true, "user": {"username": "user", "email": "user@example.com"}}
```

---

## 🤝 Contributing

1. Fork the repo.
2. Create a feature branch: `git checkout -b feature/new-feature`.
3. Commit changes: `git commit -m 'Add new feature'`.
4. Push: `git push origin feature/new-feature`.
5. Open a Pull Request.

### Guidelines
- Follow PEP 8 for Python, ESLint for React.
- Add tests for new features.
- Update this README for changes.

---

## � Updates

### March 9, 2026 - Complete Feature Implementation

#### 1. **Full Comment/Like CRUD System** ✅
Complete social engagement features implemented in both backend and React frontend.

**Backend API Endpoints**:
- `GET /api/poem/<id>/comments` - Fetch all comments with threaded replies
- `POST /api/poem/<id>/comment` - Add new comments or replies (supports `parent_id` for nested replies)
- `DELETE /api/comment/<id>` - Delete comments (author or admin only)
- `GET /api/poem/<id>/likes` - Get current like status and total like count
- `POST /api/poem/<id>/like` - Toggle like/unlike for authenticated users

**React Frontend Updates**:
- Enhanced `PoemDetail.tsx` with full comment system
- Threaded reply functionality with visual indentation
- Real-time like counter with heart icon toggle
- Comment author and timestamp display
- Dynamic comment loading and updates
- Comment deletion capability

**Database Models**:
- Added `to_dict()` method to Comment model for JSON serialization
- Supports nested comment threads via `parent_id` relationships

#### 2. **File Upload from React** ✅
Direct image and video uploads from the React frontend to the Flask backend.

**Frontend Features** (AddPoem.tsx):
- Thumbnail image upload (JPG, PNG, WebP)
  - File size validation: Max 5MB
  - Preview of selected file with size display
  - Type validation before upload
  
- Video upload (MP4, WebM, MOV)
  - File size validation: Max 50MB
  - Supported formats: MP4, WebM, MOV, MKV
  - Progress feedback during upload
  - Error handling with user-friendly messages

**Backend Implementation**:
- Updated `/api/poem` endpoint to accept `multipart/form-data`
- Automatic file validation (extension + mimetype)
- Cloudinary integration for video storage (fallback to local)
- UUID-based filename generation to prevent collisions
- Local storage at `static/uploads/videos/` as fallback

**File Handling**:
```bash
Thumbnails: static/uploads/
Videos: static/uploads/videos/
Cloudinary: Secondary video storage option
```

#### 3. **Offline Backend Bundling** ✅
Flask backend packaged as standalone executable for native app distribution.

**Build Tools Created**:
- `build_offline_bundle.py` - Automated build script using PyInstaller
- Generates platform-specific executables:
  - Linux/Mac: `waveza-backend` (ELF executable)
  - Windows: `waveza-backend.exe`
  - All platforms: `start-backend.sh` startup script

**Intelligent API URL Detection** (New `api.ts`):
- Automatically detects native app context (Capacitor/Tauri)
- Routes to `localhost:5000` in native apps for offline operation
- Routes to configured API server in web browsers
- Global axios configuration with credentials support

**React Component Updates**:
All components now use centralized API configuration:
- `Home.tsx`, `Login.tsx`, `Register.tsx`
- `Dashboard.tsx`, `EditProfile.tsx`
- `PoemDetail.tsx`, `AddPoem.tsx`
- All API calls use relative paths via configured base URL

**Native App Integration**:
1. Copy `bundled-backend/` to Capacitor/Tauri projects
2. Start the backend executable on app launch
3. React automatically connects to local server
4. Works fully offline with bundled database

**Building the Bundle**:
```bash
python3 build_offline_bundle.py
# Creates: bundled-backend/waveza-backend (or .exe)
```

#### 4. **Dependencies Added** ✅
Enhanced `requirements.txt` with production-ready dependencies:
- `Flask-CORS` - Cross-origin request support for API
- `PyInstaller` - Executable bundling for offline apps
- `cloudinary` - Optional media storage integration

#### 5. **Updated API Documentation** ✅
README now includes:
- Comment endpoints with examples
- Like endpoints and toggle mechanism
- File upload specifications
- Example API requests and responses
- Offline bundling instructions

---

## �📄 License

Licensed under the MIT License. See [LICENSE.txt](LICENSE.txt) for details.

---

## 🙏 Acknowledgments

- Original Flask app inspired by poetry sharing platforms.
- React, Capacitor, and Tauri communities for excellent tooling.
- Built with ❤️ for inclusive art expression.

---

*WaveZA: Where art meets community. 🌟*

📖 With this README, any developer can **understand, set up, and extend WaveZA** confidently.

---
