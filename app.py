from flask import Flask, json, render_template, redirect, url_for, request, flash, jsonify, abort, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, Poem, Like, Comment, Notification, PageView
import os
import uuid
from werkzeug.utils import secure_filename
# import bleach
from sqlalchemy import func, text, desc
from slugify import slugify
from flask_migrate import Migrate, upgrade
from dotenv import load_dotenv
from flask_cors import CORS
# from passlib.hash import scrypt
# import json
from datetime import datetime, timedelta
import logging

# Environment variables
load_dotenv()

print("DATABASE_URL =", os.getenv("DATABASE_URL"))


def create_app():
    app = Flask(__name__)

    # Use SQLite for simplicity on shared hosting
    db_file = os.path.join(os.path.dirname(__file__), 'mishwrites.db')
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_file}"
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1000024 * 1000024  # 2MB
    # Allow a development preview mode for VS Code mobile preview extensions
    dev_preview = os.getenv('DEV_PREVIEW', '0') in ('1', 'true', 'True')

    # In production we require secure cookies. When using a VS Code preview
    # extension that runs over an embedded frame or non-HTTPS host, relax
    # cookie settings for local development only when DEV_PREVIEW=1.
    if dev_preview:
        app.config['SESSION_COOKIE_SECURE'] = False
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    else:
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    db.init_app(app)
    Migrate(app, db)

    logging.info("✅ SQLite database initialized and migrations set up.")
    return app

app = create_app()

CORS(app, supports_credentials=True)

# Add template filter for local time (assuming UTC+2)
app.jinja_env.filters['localtime'] = lambda dt: dt + timedelta(hours=2) if dt else None


# Disable caching for static files during development
@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    # If dev preview is enabled, allow simple cross-origin framing and
    # credentialed requests from the preview host. We echo back the
    # Origin header when present which is compatible with Access-Control-Allow-Credentials.
    dev_preview = os.getenv('DEV_PREVIEW', '0') in ('1', 'true', 'True')
    if dev_preview:
        origin = request.headers.get('Origin')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        else:
            # No Origin header available — do not set credentials header in this case
            response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    lastmod = datetime.utcnow().date().isoformat()
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{url_for('index', _external=True)}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""
    return Response(xml, mimetype="application/xml")


@app.route('/run-migrations')
def run_migrations():
    upgrade()
    return "Migrations applied"

with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️ Could not create database tables on startup: {e}")
        print("This may be normal if the database is not available yet.")
    # upgrade()  # Uncomment if you want to use migrations

# Login manager setup
login_manager = LoginManager()
login_manager.login_view = "login"  # type: ignore
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------PUSH NOTIFICATIONS & PWA-------#
from pywebpush import webpush, WebPushException
import base64

# Load VAPID keys from environment or use defaults for development
VAPID_PRIVATE_KEY = os.getenv(
    "VAPID_PRIVATE_KEY", 
    "4yGY_ZSv-sWLFCbzm3tSZkSsi_tLtMQVVQK50bruqSM"  # Development key - should be in .env
)
VAPID_PUBLIC_KEY = os.getenv(
    "VAPID_PUBLIC_KEY",
    "BCdRj1CvyIzXn3I356t7oZGpGalj5CqemFYCSds6DyOR8BHW3uy-yUcvnTaE6NQkCDSPZFMlzvtWKcj6k7LQO5g"  # Development key - should be in .env
)
VAPID_CLAIMS = {
    "sub": f"mailto:{os.getenv('VAPID_EMAIL', 'mishackmadubandlela@gmail.com')}"
}

def send_push_notification(subscription_info, message_title="New Notification", message_body="You have a new message.", image_url=None, action_url="/"):
    """
    Send a push notification to a user's subscription
    
    Args:
        subscription_info: The user's push subscription object
        message_title: Title of the notification
        message_body: Body text of the notification
        image_url: Optional image URL for the notification
        action_url: URL to open when notification is clicked
    """
    payload = json.dumps({
        "title": message_title,
        "body": message_body,
        "icon": image_url or "/static/img/NEW/icons/android-chrome-512x512.png",
        "url": action_url,
        "tag": "waveza-notification"
    })

    try:
        logging.debug(f"Sending push to subscription: {subscription_info}")
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
        logging.info(f"✅ Push notification sent: {message_title}")
        return True
    except WebPushException as ex:
        logging.error(f"❌ Web push failed: {repr(ex)}")
        logging.debug(f"Payload was: {payload}")
        return False

def send_push(subscription_info, title, body, url, image_url=None):
    """Enhanced push notification with more details"""
    return send_push_notification(
        subscription_info=subscription_info,
        message_title=title,
        message_body=body,
        action_url=url,
        image_url=image_url
    )


@app.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    """Subscribe to push notifications"""
    subscription_json = request.get_json()
    if not subscription_json:
        return jsonify({'error': 'Invalid subscription data'}), 400

    try:
        # Save subscription object directly (JSON column will handle serialization)
        current_user.push_subscription = subscription_json
        db.session.commit()
        logging.info(f"✅ User {current_user.username} subscribed to push notifications: {subscription_json}")
        return jsonify({'success': True, 'message': 'Subscribed to notifications'}), 201
    except Exception as e:
        logging.error(f"❌ Subscription error: {e}")
        return jsonify({'error': 'Failed to subscribe'}), 500


@app.route('/debug/subscription')
@login_required
def debug_subscription():
    """Return current user's stored push subscription for debugging"""
    sub = current_user.push_subscription
    # try ensure it's JSON serializable
    try:
        return jsonify(subscription=sub or {}), 200
    except Exception as e:
        return jsonify(error=str(e), raw=str(sub)), 500


@app.route('/api/vapid-public-key', methods=['GET'])
def get_vapid_public_key():
    """Get VAPID public key for client-side push subscription"""
    return jsonify({
        'vapidPublicKey': VAPID_PUBLIC_KEY
    }), 200


@app.route('/notify')
@login_required
def notify():
    """Send a test push notification to current user (for testing)"""
    if not current_user.push_subscription:
        return jsonify({'error': 'No push subscription found'}), 400

    # ensure we have a dict, whether stored as JSON or string
    sub = current_user.push_subscription
    if isinstance(sub, str):
        try:
            sub = json.loads(sub)
        except Exception:
            logging.error("Failed to parse push_subscription string")
            sub = None
    if not sub:
        return jsonify({'error': 'Invalid push subscription'}), 400

    try:
        success = send_push_notification(
            sub,
            message_title="✨ New Content on WaveZA!",
            message_body="Check out the latest poems in your favorite categories.",
            action_url="/categories"
        )
        return jsonify({
            'success': success,
            'message': 'Notification sent!' if success else 'Failed to send notification'
        }), 200 if success else 500
    except Exception as e:
        logging.error(f"❌ Notification error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/offline')
def offline():
    """Offline fallback page"""
    return render_template('offline.html'), 200


@app.route('/api/notifications')
@login_required
def get_notifications():
    """Get user's notifications (for periodic sync)"""
    try:
        user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
            Notification.timestamp.desc()
        ).limit(5).all()
        
        notifications_data = []
        for notif in user_notifications:
            notifications_data.append({
                'id': notif.id,
                'title': notif.title,
                'body': notif.message,
                'timestamp': notif.timestamp.isoformat() if notif.timestamp else None,
                'read': notif.read
            })
        
        return jsonify({
            'success': True,
            'new_notifications': notifications_data
        }), 200
    except Exception as e:
        logging.error(f"❌ Error fetching notifications: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/track-install', methods=['POST'])
def track_install():
    """Track PWA installation"""
    try:
        # some clients (e.g. the pwa-manager) may send without JSON header
        # so parse leniently
        if request.is_json:
            data = request.get_json(silent=True)
        else:
            # silently ignore payload
            data = None

        if current_user.is_authenticated:
            logging.info(f"📱 PWA installed by {current_user.username}")
        else:
            logging.info("📱 PWA installed by anonymous user")
        return jsonify({'success': True}), 200
    except Exception as e:
        logging.error(f"❌ Error tracking install: {e}")
        return jsonify({'error': str(e)}), 500


# ---------------- Routes ---------------- #

@app.route("/")
def index():
    # Track landing page view
    page_view = PageView(
        page="landing_page",
        user_agent=request.headers.get('User-Agent'),
        ip_address=request.remote_addr
    )
    db.session.add(page_view)
    db.session.commit()
    
    poems = Poem.query.filter_by(approval_status="approved").order_by(Poem.timestamp.desc()).all() # type: ignore

    # Get all categories with count of poems (only approved)
    categories = [(c.category, c[1]) for c in db.session.query(
        Poem.category, func.count(Poem.id) #type: ignore
    ).filter(Poem.approval_status == "approved").group_by(Poem.category).all()]

    # Top 5 for navbar
    nav_categories = categories[:5]

    # Build a mapping of category names to their respective images for use in the template
    category_images = {}
    for cat, _ in nav_categories:
        if cat == "anxiety":
            category_images[cat] = "static/img/POETRY/cat-anxiety.jpg"
        elif cat == "romance":
            category_images[cat] = "static/img/POETRY/cat-loving.jpg"
        elif cat == "depression":
            category_images[cat] = "static/img/POETRY/depression.jpg"
        elif cat == "new_category":
            category_images[cat] = request.form.get("thumbnail")
        else:
            category_images[cat] = "static/img/POETRY/to-love.jpeg"

    return render_template("index.html", poems=poems, categories=categories, nav_categories=nav_categories, category_images=category_images)


@app.route("/api/")
def api_index():
    # Track landing page view
    page_view = PageView(
        page="landing_page",
        user_agent=request.headers.get('User-Agent'),
        ip_address=request.remote_addr
    )
    db.session.add(page_view)
    db.session.commit()
    
    poems = Poem.query.filter_by(approval_status="approved").order_by(Poem.timestamp.desc()).all() # type: ignore

    # Get all categories with count of poems (only approved)
    categories = [(c.category, c[1]) for c in db.session.query(
        Poem.category, func.count(Poem.id) #type: ignore
    ).filter(Poem.approval_status == "approved").group_by(Poem.category).all()]

    # Top 5 for navbar
    nav_categories = categories[:5]

    # Build a mapping of category names to their respective images for use in the template
    category_images = {}
    for cat, _ in nav_categories:
        if cat == "anxiety":
            category_images[cat] = "static/img/POETRY/cat-anxiety.jpg"
        elif cat == "romance":
            category_images[cat] = "static/img/POETRY/cat-loving.jpg"
        elif cat == "depression":
            category_images[cat] = "static/img/POETRY/depression.jpg"
        elif cat == "new_category":
            category_images[cat] = request.form.get("thumbnail")
        else:
            category_images[cat] = "static/img/POETRY/to-love.jpeg"

    return jsonify({
        "poems": [poem.to_dict() for poem in poems],
        "categories": categories,
        "nav_categories": nav_categories,
        "category_images": category_images
    })


# --- Additional API endpoints ---

@app.route("/api/poems", methods=["GET"])
def api_poems():
    poems = Poem.query.filter_by(approval_status="approved").order_by(Poem.timestamp.desc()).all()
    return jsonify({"poems": [p.to_dict() for p in poems]})

@app.route("/api/poem/<int:poem_id>", methods=["GET"])
def api_poem(poem_id):
    poem = Poem.query.get_or_404(poem_id)
    return jsonify({"poem": poem.to_dict()})

@app.route("/api/categories", methods=["GET"])
def api_categories():
    categories = [(c.category, c[1]) for c in db.session.query(
        Poem.category, func.count(Poem.id)
    ).filter(Poem.approval_status == "approved").group_by(Poem.category).all()]
    return jsonify({"categories": categories})

@app.route("/api/category/<name>", methods=["GET"])
def api_category(name):
    poems = Poem.query.filter_by(category=name, approval_status="approved").order_by(Poem.timestamp.desc()).all()
    return jsonify({"poems": [p.to_dict() for p in poems]})
@app.route("/category/<name>", methods=["GET", "POST"])
def category(name):
    poems = Poem.query.filter_by(category=name, approval_status="approved").order_by(Poem.timestamp.desc()).all()

    # Get all categories with counts for navbar or sidebar (only approved)
    nav_categories = [(c.category, c[1]) for c in db.session.query(Poem.category, func.count(Poem.id)).filter(Poem.approval_status == "approved").group_by(Poem.category).all()] #type: ignore
    nav_categories = nav_categories[:2]
    return render_template("category.html", poems=poems, category=name, categories=categories, nav_categories=nav_categories)

@app.context_processor
def inject_nav_categories():
    rows = db.session.query(Poem.category, func.count(Poem.id)).filter(Poem.approval_status == "approved").group_by(Poem.category).all() #type: ignore 
    nav_categories = [(c.category or 'uncategorized', c[1]) for c in rows]
    cat_count = db.session.query(func.count(func.distinct(Poem.category))).filter(Poem.approval_status == "approved").scalar()
    return dict(nav_categories=nav_categories, cat_count=cat_count)


@app.context_processor
def inject_notification_count():
    """Make unread notification count available to all templates."""
    if current_user.is_authenticated:
        try:
            count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        except Exception:
            count = 0
        return dict(unread_notifications_count=count)
    return dict(unread_notifications_count=0)

@app.route("/categories")
def categories():
    categories = [(c.category, c[1]) for c in db.session.query( #type: ignore
        Poem.category, func.count(Poem.id) #type: ignore
    ).filter(Poem.approval_status == "approved").group_by(Poem.category).all()]
    return render_template("categories.html", categories=categories)

@app.route("/poems")
def poems():
    poems = Poem.query.all()
    return render_template("poems.html", poems=poems)

@app.route("/poem/<int:poem_id>/<slug>")
def poem(poem_id, slug):
    poem = Poem.query.get_or_404(poem_id)

    # Check if poem is approved or if user is the author
    if poem.approval_status != "approved" and (not current_user.is_authenticated or current_user.id != poem.author_id):
        flash("This post is not available.", "warning")
        return redirect(url_for("index"))

    # Optional: redirect if slug doesn't match (for SEO consistency)
    if poem.slug != slug:
        return redirect(url_for('poem', poem_id=poem.id, slug=poem.slug))
    
    return render_template("poem.html", poem=poem)


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"]
#         email = request.form.get("email")
#         password = generate_password_hash(request.form.get("password")) #type: ignore

#         if User.query.filter_by(email=email).first():
#             flash("Email already exists!", "warning")
#             return redirect(url_for("register"))

#         new_user = User(email=email, password=password, username=username) #type: ignore
#         db.session.add(new_user)
#         db.session.commit()

#         login_user(new_user)  # ✅ Log them in immediately
#         return redirect(url_for("dashboard"))  # ✅ Avoid loop

#     return render_template("register.html")

# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")

#         if not username or not email or not password:
#             flash("All fields are required!", "danger")
#             return redirect(url_for("register"))

#         if User.query.filter_by(email=email).first():
#             flash("Email already exists!", "warning")
#             return redirect(url_for("register"))

#         hashed_password = generate_password_hash(password)
#         new_user = User(username=username, email=email, password=hashed_password)

#         db.session.add(new_user)
#         db.session.commit()

#         login_user(new_user)
#         flash("Registration successful! Welcome.", "success")
#         return redirect(url_for("dashboard"))

#     return render_template("register.html")

# from passlib.hash import bcrypt, pbkdf2_sha256

@app.route("/register", methods=["GET", "POST"])
@app.route("/api/register", methods=["POST"])
def register():
    # support form submission and JSON API
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        id_number = data.get("id_number", "")
        location = data.get("location", "")
        art_field = data.get("art_field", "")
        popia_consent = data.get("popia_consent") in ("on", True, "true", "True")
        terms_accepted = data.get("terms_accepted") in ("on", True, "true", "True")

        # Basic validation
        if not username or not email or not password:
            if request.is_json:
                return jsonify({"success": False, "message": "Username, email, and password are required."}), 400
            flash("Username, email, and password are required!", "danger")
            return redirect(url_for("register"))
        if not id_number:
            if request.is_json:
                return jsonify({"success": False, "message": "ID Number is required."}), 400
            flash("ID Number is required!", "danger")
            return redirect(url_for("register"))
        if not terms_accepted:
            if request.is_json:
                return jsonify({"success": False, "message": "Terms must be accepted."}), 400
            flash("You must accept the Terms and Conditions!", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({"success": False, "message": "Email already exists."}), 409
            flash("Email already exists!", "warning")
            return redirect(url_for("register"))

        new_user = User(username=username, email=email, password=password, role="user")
        new_user.id_number = id_number
        new_user.location = location
        new_user.art_field = art_field
        new_user.popia_consent = popia_consent
        new_user.terms_accepted = terms_accepted

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        if request.is_json:
            return jsonify({"success": True, "user": {"username": new_user.username, "email": new_user.email}})
        flash("Registration successful! Welcome to WaveZA.", "success")
        return redirect(url_for("dashboard"))
    return render_template("register.html")


# Check which hash type it is
# def verify_password(password, hash):
#     try:
#         return bcrypt.verify(password, hash)
#     except ValueError:
#         # fallback to werkzeug/old hash
#         from werkzeug.security import check_password_hash
#         return check_password_hash(hash, password)


@app.route("/login", methods=["GET", "POST"])
@app.route("/api/login", methods=["POST"])
def login():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if request.is_json:
                return jsonify({"success": True, "user": {"username": user.username, "email": user.email}})
            flash("Login successful", "success")
            return redirect(url_for("dashboard"))
        if request.is_json:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
        flash("Invalid credentials", "danger")
    return render_template("login.html")


@app.route("/logout")
@app.route("/api/logout")
@login_required
def logout():
    logout_user()
    if request.path.startswith('/api'):
        return jsonify({"success": True})
    return redirect(url_for("index"))

@app.route("/dashboard")
@app.route("/api/dashboard")
@login_required
def dashboard():
    poems = Poem.query.filter_by(author_id=current_user.id).order_by(Poem.submitted_at.desc()).all()
    approved_poems = [p for p in poems if p.approval_status == "approved"]
    pending_poems = [p for p in poems if p.approval_status == "pending"]
    rejected_poems = [p for p in poems if p.approval_status == "rejected"]
    total_likes = sum(len(poem.likes) for poem in approved_poems)
    total_comments = sum(len(poem.comments) for poem in approved_poems)
    total_users = User.query.count()
    if request.path.startswith('/api'):
        return jsonify({
            "poems": [p.to_dict() for p in poems],
            "total_poems": len(approved_poems),
            "pending_poems": len(pending_poems),
            "rejected_poems": len(rejected_poems),
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_users": total_users
        })
    return render_template("dashboard.html", 
                         poems=poems, 
                         total_poems=len(approved_poems),
                         pending_poems=len(pending_poems),
                         rejected_poems=len(rejected_poems),
                         total_likes=total_likes, 
                         total_comments=total_comments, 
                         total_users=total_users)

@app.route("/profile") #type: ignore
@login_required
def profile():
    # Show all user's posts for their own profile
    poems = Poem.query.filter_by(author_id=current_user.id).order_by(Poem.submitted_at.desc()).all()
    
    # Count only approved for analytics
    approved_poems = [p for p in poems if p.approval_status == "approved"]
    pending_poems = [p for p in poems if p.approval_status == "pending"]
    rejected_poems = [p for p in poems if p.approval_status == "rejected"]
    
    total_likes = sum(len(poem.likes) for poem in approved_poems)
    total_comments = sum(len(poem.comments) for poem in approved_poems)
    total_users = User.query.count()
    
    return render_template("profile.html", 
                         poems=poems, 
                         total_poems=len(approved_poems),
                         pending_poems=len(pending_poems),
                         rejected_poems=len(rejected_poems),
                         total_likes=total_likes, 
                         total_comments=total_comments, 
                         total_users=total_users)

@app.route("/edit_profile", methods=["GET", "POST"])
@app.route("/api/edit_profile", methods=["POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        data = request.get_json(silent=True)
        if data:
            # JSON update request
            bio = data.get("bio", "").strip()
            selected_categories = data.get("categories", [])
            if not bio:
                return jsonify({"success": False, "message": "Bio is required."}), 400
            current_user.bio = bio
            current_user.preferred_categories = ",".join(selected_categories)
            db.session.commit()
            return jsonify({"success": True, "user": {"username": current_user.username, "bio": current_user.bio}})
        # fallback to form handling below
        bio = request.form.get("bio", "").strip()
        selected_categories = request.form.getlist("categories")  # Get all selected categories
        
        # Validate bio
        if not bio:
            flash("Bio is required.", "danger")
            return redirect(url_for("edit_profile"))
        
        # Handle profile image upload
        profile_image_path = current_user.profile_image
        if "profile_image" in request.files:
            file = request.files["profile_image"]
            if file and file.filename and allowed_file(file.filename):
                # Generate secure filename
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
    
    # Get all available categories
    all_categories = [
        "romance",
        "anxiety",
        "self-introspection",
        "black-consciousness",
        "democracy",
        "depression",
        "pain",
        "love"
    ]
    
    # Get user's current categories
    user_categories = current_user.preferred_categories.split(",") if current_user.preferred_categories else []
    
    return render_template("edit_profile.html", all_categories=all_categories, user_categories=user_categories)


@app.route("/user/<username>")
def public_profile(username):
    """Display public user profile"""
    user = User.query.filter_by(username=username).first()
    
    if not user:
        abort(404)
    
    # Check if profile is public
    if not user.is_public and (not current_user.is_authenticated or current_user.id != user.id):
        flash("This profile is private.", "warning")
        return redirect(url_for("index"))
    
    # Increment profile view count
    user.increment_profile_views()
    db.session.commit()
    
    # Get user's approved poems only (or all if viewing own profile)
    if current_user.is_authenticated and current_user.id == user.id:
        poems = Poem.query.filter_by(author_id=user.id).all()
    else:
        poems = Poem.query.filter_by(author_id=user.id, approval_status="approved").all()
    
    total_likes = sum(len(poem.likes) for poem in poems)
    total_comments = sum(len(poem.comments) for poem in poems)
    
    return render_template("public_profile.html", 
                        profile_user=user, 
                        poems=poems, 
                        total_poems=len(poems),
                        total_likes=total_likes,
                        total_comments=total_comments)


@app.route("/add_custom_category", methods=["POST"])
@login_required
def add_custom_category():
    """Add a custom category"""
    category = request.form.get("category", "").strip()
    
    if not category:
        flash("Category name cannot be empty.", "danger")
        return redirect(url_for("edit_profile"))
    
    if len(category) > 50:
        flash("Category name is too long (max 50 characters).", "danger")
        return redirect(url_for("edit_profile"))
    
    if current_user.add_custom_category(category):
        db.session.commit()
        flash(f"Custom category '{category}' added successfully!", "success")
    else:
        flash("Failed to add custom category.", "danger")
    
    return redirect(url_for("edit_profile"))


@app.route("/toggle_profile_privacy", methods=["POST"])
@login_required
def toggle_profile_privacy():
    """Toggle profile public/private visibility"""
    current_user.is_public = not current_user.is_public
    db.session.commit()
    
    status = "public" if current_user.is_public else "private"
    flash(f"Your profile is now {status}.", "success")
    return redirect(url_for("profile"))


@app.route("/poem/<int:poem_id>/like", methods=["POST"])
@login_required
def like_poem(poem_id):
    poem = Poem.query.get_or_404(poem_id)
    existing_like = Like.query.filter_by(user_id=current_user.id, poem_id=poem.id).first()
    if not existing_like:
        like = Like(user_id=current_user.id, poem_id=poem.id) #type: ignore
        db.session.add(like)
        db.session.commit()
    return redirect(url_for("poem", poem_id=poem.id, slug=poem.slug))


@app.route("/poem/<int:poem_id>/comment", methods=["POST"])
@login_required
def add_comment(poem_id):
    content = request.form.get("content")
    poem = Poem.query.get_or_404(poem_id)   # ensures poem exists

    if not content or not content.strip():
        flash("Comment cannot be empty.", "danger")
        return redirect(url_for("poem", poem_id=poem.id, slug=poem.slug))

    comment = Comment(content=content, user_id=current_user.id, poem_id=poem.id) #type: ignore
    db.session.add(comment)
    db.session.commit()

    return redirect(url_for("poem", poem_id=poem.id, slug=poem.slug))

ALLOWED_TAGS = ["b", "i", "u", "em", "strong", "p", "br", "ul", "ol", "li", "blockquote", "img"]
ALLOWED_ATTRS = {"img": ["src", "alt"]}

# @app.route('/category/<name>')
# def category(name):
#     # Fetch poems or data by category
#     poems_in_category = get_poems_by_category(name)  # your logic here
#     return render_template("category.html", poems=poems_in_category, category=name)


# ==================ADD VIDEO=====================
VIDEO_UPLOAD_FOLDER = 'static/uploads/videos'
ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'webm', 'mov', 'mkv']
app.config['VIDEO_UPLOAD_FOLDER'] = VIDEO_UPLOAD_FOLDER


# ==============REMOTE CLOUDINARY VIDEO SETUP==================
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME") or "",
    api_key=os.getenv("CLOUDINARY_API_KEY") or "",
    api_secret=os.getenv("CLOUDINARY_API_SECRET") or "",
    secure=True
    )

# Determine whether Cloudinary is properly configured. If not, we'll fallback to local storage.
USE_CLOUDINARY = bool(os.getenv("CLOUDINARY_CLOUD_NAME") and os.getenv("CLOUDINARY_API_KEY") and os.getenv("CLOUDINARY_API_SECRET"))
if not USE_CLOUDINARY:
    logging.warning("Cloudinary not configured. Video uploads will be saved locally.")

ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm", "mov"}
ALLOWED_VIDEO_MIMES = {"video/mp4", "video/webm", "video/quicktime"}

def allowed_video(file):
    if not file or not file.filename:
        return False
    # Validate by extension first. Some browsers/clients omit or set an unexpected
    # mimetype when uploading; rely on the filename extension but log mismatches.
    if "." not in file.filename:
        return False
    ext = file.filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        return False

    mimetype = getattr(file, 'mimetype', '') or ''
    if mimetype and not mimetype.startswith('video/'):
        logging.warning("Uploaded video has non-video mimetype '%s' — accepting based on extension", mimetype)

    return True

def upload_video_to_cloudinary(file):
    if not USE_CLOUDINARY:
        raise RuntimeError("Cloudinary not configured")
    result = cloudinary.uploader.upload(
        file,
        resource_type="video",
        folder="poems/videos"
    )
    return result.get("secure_url"), result.get("public_id")


def delete_cloudinary_video(public_id):
    if public_id:
        cloudinary.uploader.destroy(
            public_id,
            resource_type="video"
            )



@app.route("/add_poem", methods=["GET", "POST"])
@login_required
def add_poem():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        category = request.form.get("category")
        new_category = request.form.get("new_category")

        # ---------- VIDEO ----------
        video_file = request.files.get("video")
        video_url = None
        video_public_id = None

        if video_file and allowed_video(video_file):
            # Save to disk first to avoid zero-byte files if the stream is consumed
            video_filename = f"{uuid.uuid4()}_{secure_filename(video_file.filename)}"
            os.makedirs(app.config["VIDEO_UPLOAD_FOLDER"], exist_ok=True)
            video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], video_filename)
            # Ensure we write from the start of the stream
            try:
                video_file.stream.seek(0)
            except Exception:
                pass
            video_file.save(video_path)

            # Try Cloudinary if configured; otherwise keep local path
            if USE_CLOUDINARY:
                try:
                    with open(video_path, 'rb') as vf:
                        cloud_url, cloud_id = upload_video_to_cloudinary(vf)
                    if cloud_url:
                        video_url = cloud_url
                        video_public_id = cloud_id
                    else:
                        video_url = f"uploads/videos/{video_filename}"
                except Exception as e:
                    logging.exception("Cloudinary upload failed, using local file: %s", e)
                    video_url = f"uploads/videos/{video_filename}"
            else:
                video_url = f"uploads/videos/{video_filename}"

        # ---------- THUMBNAIL ----------
        thumbnail_file = request.files.get("thumbnail")
        thumbnail_path = None
        if thumbnail_file and thumbnail_file.filename and allowed_file(thumbnail_file.filename):
            ext = thumbnail_file.filename.rsplit(".", 1)[1].lower()
            thumb_filename = f"thumb_{uuid.uuid4().hex}.{ext}"
            thumb_filepath = os.path.join(app.config["UPLOAD_FOLDER"], thumb_filename)
            thumbnail_file.save(thumb_filepath)
            thumbnail_path = f"uploads/{thumb_filename}"

        poem = Poem(
            title=title,        #type: ignore
            content=content,    #type: ignore
            author=current_user,
            category=category or new_category,  #type: ignore
            thumbnail=thumbnail_path,
            video_url=video_url,
            video_public_id=video_public_id
        )

        poem.excerpt = poem.get_excerpt(300)
        
        # Generate unique slug
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while Poem.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        poem.slug = slug
        
        poem.approval_status = "pending"  # New posts are pending admin approval

        db.session.add(poem)
        db.session.flush()  # Get the poem ID
        
        # Create notification for user
        user_notification = Notification(
            user_id=current_user.id,
            title="Post Submitted",
            message=f"Your post '{title}' has been submitted for admin approval.",
            notification_type="post_submitted",
            poem_id=poem.id
        )
        db.session.add(user_notification)
        
        # Notify all admins about new post
        admins = User.query.filter_by(role="admin").all()
        for admin in admins:
            admin_notification = Notification(
                user_id=admin.id,
                title="New Post Awaiting Review",
                message=f"User {current_user.username} submitted a new post: '{title}'",
                notification_type="new_post_submitted",
                poem_id=poem.id
            )
            db.session.add(admin_notification)
        
        db.session.commit()

        flash("Post submitted for admin approval. You'll be notified once it's reviewed.", "info")
        return redirect(url_for("dashboard"))

    return render_template("add_poem.html")


# simple JSON-only version that accepts title/content/category
@app.route("/api/poem", methods=["POST"])
@login_required
def api_add_poem():
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Handle multipart form data (with files)
        title = request.form.get("title")
        content = request.form.get("content")
        category = request.form.get("category")
        
        # Handle file uploads
        thumbnail_file = request.files.get("thumbnail")
        video_file = request.files.get("video")
    else:
        # Handle JSON data
        data = request.get_json() or {}
        title = data.get("title")
        content = data.get("content")
        category = data.get("category")
        thumbnail_file = None
        video_file = None
    
    if not title or not content:
        return jsonify({"success": False, "message": "Title and content required"}), 400
    
    poem = Poem(
        title=title,
        content=content,
        author=current_user,
        category=category,
    )
    poem.excerpt = poem.get_excerpt(300)
    
    # slug generation
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    while Poem.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    poem.slug = slug
    poem.approval_status = "pending"
    
    # Handle thumbnail upload
    if thumbnail_file and allowed_file(thumbnail_file.filename):
        filename = secure_filename(thumbnail_file.filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        thumbnail_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        poem.thumbnail = f"uploads/{filename}"
    
    # Handle video upload
    if video_file and allowed_video(video_file):
        video_filename = f"{uuid.uuid4()}_{secure_filename(video_file.filename)}"
        os.makedirs(app.config["VIDEO_UPLOAD_FOLDER"], exist_ok=True)
        video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], video_filename)
        try:
            video_file.stream.seek(0)
        except Exception:
            pass
        video_file.save(video_path)
        
        # Upload to Cloudinary if configured
        if USE_CLOUDINARY:
            try:
                with open(video_path, 'rb') as vf:
                    cloud_url, cloud_id = upload_video_to_cloudinary(vf)
                if cloud_url:
                    poem.video_url = cloud_url
                    poem.video_public_id = cloud_id
                else:
                    poem.video_url = f"uploads/videos/{video_filename}"
            except Exception as e:
                logging.exception("Cloudinary upload failed, using local file: %s", e)
                poem.video_url = f"uploads/videos/{video_filename}"
        else:
            poem.video_url = f"uploads/videos/{video_filename}"
    
    db.session.add(poem)
    db.session.commit()
    return jsonify({"success": True, "poem": poem.to_dict()})


# ================== COMMENT API ENDPOINTS ==================

@app.route("/api/poem/<int:poem_id>/comments", methods=["GET"])
def api_get_comments(poem_id):
    """Get all comments for a poem"""
    poem = Poem.query.get_or_404(poem_id)
    comments = Comment.query.filter_by(poem_id=poem_id).order_by(Comment.timestamp.asc()).all()
    
    comments_data = []
    for comment in comments:
        comments_data.append({
            "id": comment.id,
            "content": comment.content,
            "timestamp": comment.timestamp.isoformat() if comment.timestamp else None,
            "user_id": comment.user_id,
            "username": comment.user.username if comment.user else None,
            "parent_id": comment.parent_id
        })
    
    return jsonify({"success": True, "comments": comments_data})


@app.route("/api/poem/<int:poem_id>/comment", methods=["POST"])
@login_required
def api_add_comment(poem_id):
    """Add a comment to a poem"""
    data = request.get_json() or {}
    content = data.get("content")
    parent_id = data.get("parent_id")  # For nested replies
    
    if not content or not content.strip():
        return jsonify({"success": False, "message": "Comment cannot be empty"}), 400
    
    poem = Poem.query.get_or_404(poem_id)
    
    comment = Comment(
        content=content.strip(),
        user_id=current_user.id,
        poem_id=poem_id,
        parent_id=parent_id
    )
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "comment": {
            "id": comment.id,
            "content": comment.content,
            "timestamp": comment.timestamp.isoformat() if comment.timestamp else None,
            "user_id": comment.user_id,
            "username": comment.user.username,
            "parent_id": comment.parent_id
        }
    })


@app.route("/api/comment/<int:comment_id>", methods=["DELETE"])
@login_required
def api_delete_comment(comment_id):
    """Delete a comment (only by comment author or admin)"""
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.user_id != current_user.id and current_user.role != "admin":
        return jsonify({"success": False, "message": "Not authorized"}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({"success": True})


# ================== LIKE API ENDPOINTS ==================

@app.route("/api/poem/<int:poem_id>/like", methods=["POST"])
@login_required
def api_like_poem(poem_id):
    """Like or unlike a poem"""
    poem = Poem.query.get_or_404(poem_id)
    existing_like = Like.query.filter_by(user_id=current_user.id, poem_id=poem_id).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({"success": True, "liked": False, "likes_count": len(poem.likes)})
    else:
        # Like
        like = Like(user_id=current_user.id, poem_id=poem_id)
        db.session.add(like)
        db.session.commit()
        return jsonify({"success": True, "liked": True, "likes_count": len(poem.likes)})


@app.route("/api/poem/<int:poem_id>/likes", methods=["GET"])
def api_get_likes(poem_id):
    """Get like status and count for a poem"""
    poem = Poem.query.get_or_404(poem_id)
    liked = False
    
    if current_user.is_authenticated:
        existing_like = Like.query.filter_by(user_id=current_user.id, poem_id=poem_id).first()
        liked = existing_like is not None
    
    return jsonify({
        "success": True,
        "liked": liked,
        "likes_count": len(poem.likes)
    })





@app.route("/edit_poem/<int:poem_id>", methods=["GET", "POST"])
@login_required
def edit_poem(poem_id):
    poem = Poem.query.get_or_404(poem_id)

    if poem.author_id != current_user.id:
        flash("You are not allowed to edit this poem.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        poem.title = request.form["title"]

        # Update slug when title changes
        base_slug = slugify(poem.title)
        slug = base_slug
        counter = 1
        existing_poem = Poem.query.filter_by(slug=slug).first()
        while existing_poem and existing_poem.id != poem.id:
            slug = f"{base_slug}-{counter}"
            counter += 1
            existing_poem = Poem.query.filter_by(slug=slug).first()
        poem.slug = slug

        raw_content = request.form["content"]
        poem.content = raw_content

        poem.category = request.form.get("category")
        if not poem.category:
            poem.category = request.form.get("new category")

        # ---------- THUMBNAIL ----------
        thumb_file = request.files.get("thumbnail")
        if thumb_file and allowed_file(thumb_file.filename):
            filename = secure_filename(thumb_file.filename)
            thumb_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            poem.thumbnail = f"uploads/{filename}"

        # ---------- VIDEO ----------
        video_file = request.files.get("video")
        if video_file and allowed_video(video_file):
            video_filename = f"{uuid.uuid4()}_{secure_filename(video_file.filename)}"
            os.makedirs(app.config["VIDEO_UPLOAD_FOLDER"], exist_ok=True)
            video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], video_filename)
            try:
                video_file.stream.seek(0)
            except Exception:
                pass
            video_file.save(video_path)

            # If Cloudinary is available, try uploading from the saved file
            if USE_CLOUDINARY:
                try:
                    with open(video_path, 'rb') as vf:
                        cloud_url, cloud_id = upload_video_to_cloudinary(vf)
                    if cloud_url:
                        poem.video_url = cloud_url
                        poem.video_public_id = cloud_id
                    else:
                        poem.video_url = f"uploads/videos/{video_filename}"
                except Exception as e:
                    logging.exception("Cloudinary upload failed during edit, using local file: %s", e)
                    poem.video_url = f"uploads/videos/{video_filename}"
            else:
                poem.video_url = f"uploads/videos/{video_filename}"

        db.session.commit()
        flash("Poem updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit_poem.html", poem=poem)




@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route("/history")
def history():
    selected_date = request.args.get('date')  # Format: YYYY-MM or YYYY

    # Get all approved history posts
    history_posts = Poem.query.filter_by(category="history", approval_status="approved").order_by(Poem.history_date.desc()).all()

    # Get unique years for dropdown
    years = set()
    for post in history_posts:
        if post.history_date:
            years.add(post.history_date.year)
    years = sorted(years, reverse=True)

    # Filter posts by selected date
    if selected_date:
        if len(selected_date) == 4:  # Year only
            year = int(selected_date)
            filtered_posts = [p for p in history_posts if p.history_date and p.history_date.year == year]
        elif len(selected_date) == 7:  # Year-Month
            try:
                filter_date = datetime.strptime(selected_date + "-01", "%Y-%m-%d")
                filtered_posts = [p for p in history_posts if p.history_date and 
                                p.history_date.year == filter_date.year and 
                                p.history_date.month == filter_date.month]
            except ValueError:
                filtered_posts = history_posts[:6]  # Default to latest 6
        else:
            filtered_posts = history_posts[:6]  # Default to latest 6
    else:
        filtered_posts = history_posts[:6]  # Default to latest 6

    # Group posts by 5-year intervals for display
    grouped_posts = {}
    for post in filtered_posts:
        if post.history_date:
            year = post.history_date.year
            interval_start = (year // 5) * 5
            interval = f"{interval_start}-{interval_start + 4}"
            if interval not in grouped_posts:
                grouped_posts[interval] = []
            grouped_posts[interval].append(post)

    return render_template("history.html", 
                         posts=filtered_posts, 
                         grouped_posts=grouped_posts,
                         years=years, 
                         selected_date=selected_date)


@app.route("/delete_poem/<int:poem_id>", methods=["POST"])
@login_required
def delete_poem(poem_id):
    poem = Poem.query.get_or_404(poem_id)
    if poem.author_id != current_user.id:
        flash("You are not allowed to delete this poem.", "danger")
        return redirect(url_for("dashboard"))

    db.session.delete(poem)
    db.session.commit()
    flash("Poem deleted successfully!", "success")
    return redirect(url_for("dashboard"))


# Configure uploads
# UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload_image", methods=["POST"])
@login_required
def upload_image():
    if "image" not in request.files:
        return {"error": "No file part"}, 400
    file = request.files["image"]

    if file.filename == "":
        return {"error": "No selected file"}, 400

    if file and allowed_file(file.filename):
        # Generate secure random filename with same extension
        ext = file.filename.rsplit(".", 1)[1].lower() #type: ignore
        filename = f"{uuid.uuid4().hex}.{ext}"

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        return {"url": url_for("static", filename="uploads/" + filename)}
    return {"error": "Invalid file type"}, 400


# ================== ADMIN PANEL ROUTES ==================

def admin_required(f):
    """Decorator to check if user is admin"""
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != "admin":
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@app.route("/add_history_post", methods=["GET", "POST"])
@admin_required
def add_history_post():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        history_date_str = request.form.get("history_date")  # Format: YYYY-MM

        # Parse history_date
        if history_date_str:
            try:
                history_date = datetime.strptime(history_date_str + "-01", "%Y-%m-%d")  # Add day 1
            except ValueError:
                flash("Invalid history date format.", "danger")
                return redirect(url_for("add_history_post"))
        else:
            flash("History date is required.", "danger")
            return redirect(url_for("add_history_post"))

        # ---------- VIDEO ----------
        video_file = request.files.get("video")
        video_url = None
        video_public_id = None

        if video_file and allowed_video(video_file):
            # Save to disk first to avoid zero-byte files if the stream is consumed
            video_filename = f"{uuid.uuid4()}_{secure_filename(video_file.filename)}"
            os.makedirs(app.config["VIDEO_UPLOAD_FOLDER"], exist_ok=True)
            video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], video_filename)
            # Ensure we write from the start of the stream
            try:
                video_file.stream.seek(0)
            except Exception:
                pass
            video_file.save(video_path)

            # Try Cloudinary if configured; otherwise keep local path
            if USE_CLOUDINARY:
                try:
                    with open(video_path, 'rb') as vf:
                        cloud_url, cloud_id = upload_video_to_cloudinary(vf)
                    if cloud_url:
                        video_url = cloud_url
                        video_public_id = cloud_id
                    else:
                        video_url = f"uploads/videos/{video_filename}"
                except Exception as e:
                    logging.exception("Cloudinary upload failed, using local file: %s", e)
                    video_url = f"uploads/videos/{video_filename}"
            else:
                video_url = f"uploads/videos/{video_filename}"

        # ---------- THUMBNAIL ----------
        thumbnail_file = request.files.get("thumbnail")
        thumbnail_path = None
        if thumbnail_file and thumbnail_file.filename and allowed_file(thumbnail_file.filename):
            ext = thumbnail_file.filename.rsplit(".", 1)[1].lower()
            thumb_filename = f"thumb_{uuid.uuid4().hex}.{ext}"
            thumb_filepath = os.path.join(app.config["UPLOAD_FOLDER"], thumb_filename)
            thumbnail_file.save(thumb_filepath)
            thumbnail_path = f"uploads/{thumb_filename}"

        poem = Poem(
            title=title,        #type: ignore
            content=content,    #type: ignore
            author=current_user,
            category="history",  #type: ignore
            thumbnail=thumbnail_path,
            video_url=video_url,
            video_public_id=video_public_id,
            history_date=history_date
        )

        poem.excerpt = poem.get_excerpt(300)
        poem.slug = slugify(title)  #type: ignore
        poem.approval_status = "approved"  # Admin posts are auto-approved

        db.session.add(poem)
        db.session.commit()

        flash("History post created successfully!", "success")
        return redirect(url_for("history"))

    return render_template("add_history_post.html")


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    """Admin dashboard with overview stats"""
    total_users = User.query.count()
    total_posts = Poem.query.count()
    pending_posts = Poem.query.filter_by(approval_status="pending").count()
    approved_posts = Poem.query.filter_by(approval_status="approved").count()
    rejected_posts = Poem.query.filter_by(approval_status="rejected").count()
    
    # Get recent pending posts
    recent_pending = Poem.query.filter_by(approval_status="pending").order_by(Poem.submitted_at.desc()).limit(5).all()
    
    return render_template("admin/dashboard.html",
                         total_users=total_users,
                         total_posts=total_posts,
                         pending_posts=pending_posts,
                         approved_posts=approved_posts,
                         rejected_posts=rejected_posts,
                         recent_pending=recent_pending)


@app.route("/admin/posts")
@admin_required
def admin_posts():
    """Admin view all posts for review"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'pending', type=str)
    
    if status not in ['pending', 'approved', 'rejected']:
        status = 'pending'
    
    posts = Poem.query.filter_by(approval_status=status).order_by(Poem.submitted_at.desc()).paginate(page=page, per_page=10)
    # counts for status buttons
    pending_count = Poem.query.filter_by(approval_status='pending').count()
    approved_count = Poem.query.filter_by(approval_status='approved').count()
    rejected_count = Poem.query.filter_by(approval_status='rejected').count()

    return render_template("admin/posts.html", posts=posts, status=status,
                           pending_count=pending_count,
                           approved_count=approved_count,
                           rejected_count=rejected_count)


@app.route("/admin/post/<int:poem_id>/approve", methods=["POST"])
@admin_required
def approve_post(poem_id):
    """Approve a post"""
    poem = Poem.query.get_or_404(poem_id)
    
    poem.approval_status = "approved"
    db.session.commit()
    
    # Notify user about approval
    notification = Notification(
        user_id=poem.author_id,
        title="Post Approved! 🎉",
        message=f"Your post '{poem.title}' has been approved and is now live!",
        notification_type="post_approved",
        poem_id=poem.id
    )
    db.session.add(notification)
    db.session.commit()
    
    # Send push notification if user has subscription
    if poem.author.push_subscription:
        # normalize subscription to dict
        sub = poem.author.push_subscription
        if isinstance(sub, str):
            try:
                sub = json.loads(sub)
            except Exception as e:
                logging.error("Could not decode stored subscription for user %s: %s", poem.author.username, e)
                sub = None
        if sub:
            try:
                send_push_notification(
                    sub,
                    message_title="Post Approved! 🎉",
                    message_body=f"Your post '{poem.title}' has been approved and is now live!",
                    action_url=f"/poem/{poem.slug}"
                )
            except Exception as e:
                logging.exception("Failed to send push notification: %s", e)
        else:
            logging.warning("No valid subscription found when approving post %s for user %s", poem.id, poem.author.username)
    
    flash(f"Post '{poem.title}' has been approved.", "success")
    return redirect(request.referrer or url_for("admin_posts"))


@app.route("/admin/post/<int:poem_id>/reject", methods=["POST"])
@admin_required
def reject_post(poem_id):
    """Reject a post"""
    poem = Poem.query.get_or_404(poem_id)
    comments = request.form.get("comments", "").strip()
    
    poem.approval_status = "rejected"
    poem.admin_review_comments = comments
    db.session.commit()
    
    # Notify user about rejection
    notification = Notification(
        user_id=poem.author_id,
        title="Post Not Approved",
        message=f"Your post '{poem.title}' was not approved. Review comments: {comments if comments else 'No comments provided.'}",
        notification_type="post_rejected",
        poem_id=poem.id
    )
    db.session.add(notification)
    db.session.commit()
    
    flash(f"Post '{poem.title}' has been rejected.", "warning")
    return redirect(request.referrer or url_for("admin_posts"))


@app.route("/admin/users")
@admin_required
def admin_users():
    """Admin view all users"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=10)
    
    return render_template("admin/users.html", users=users)


@app.route("/admin/user/<int:user_id>")
@admin_required
def admin_user_profile(user_id):
    """Admin view user profile and their posts"""
    user = User.query.get_or_404(user_id)
    posts = Poem.query.filter_by(author_id=user.id).order_by(Poem.timestamp.desc()).all()
    
    return render_template("admin/user_profile.html", user=user, posts=posts)


@app.route("/admin/user/<int:user_id>/post/<int:poem_id>/delete", methods=["POST"])
@admin_required
def admin_delete_post(user_id, poem_id):
    """Admin delete a user's post"""
    poem = Poem.query.get_or_404(poem_id)
    
    if poem.author_id != user_id:
        flash("Post does not belong to this user.", "danger")
        return redirect(url_for("admin_user_profile", user_id=user_id))
    
    db.session.delete(poem)
    db.session.commit()
    
    flash(f"Post '{poem.title}' has been deleted.", "warning")
    return redirect(url_for("admin_user_profile", user_id=user_id))


@app.route("/admin/traffic")
@admin_required
def admin_traffic():
    """Traffic and analytics dashboard"""
    period = request.args.get('period', 7, type=int)  # 7, 30, 365 days
    
    # Calculate date range
    if period == 1:
        start_date = datetime.utcnow() - timedelta(hours=24)
        period_label = "24 Hours"
    elif period == 7:
        start_date = datetime.utcnow() - timedelta(days=7)
        period_label = "7 Days"
    else:  # 30
        start_date = datetime.utcnow() - timedelta(days=period)
        period_label = f"{period} Days"
    
    # Get page views for the period
    page_views = PageView.query.filter(PageView.timestamp >= start_date).all()
    
    # Group by date for analytics
    daily_views = {}
    for view in page_views:
        # convert stored UTC to local for grouping
        local_ts = view.timestamp + timedelta(hours=2)
        date_key = local_ts.strftime("%Y-%m-%d")
    
    # Sort by date
    sorted_views = dict(sorted(daily_views.items()))
    
    return render_template("admin/traffic.html",
                         page_views=page_views,
                         daily_views=sorted_views,
                         period=period,
                         period_label=period_label,
                         total_views=len(page_views))


@app.route("/notifications")
@login_required
def notifications():
    """User notifications page"""
    page = request.args.get('page', 1, type=int)
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template("notifications.html", notifications=notifications)


@app.route("/notification/<int:notification_id>/mark-as-read", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})


# Run
if __name__ == "__main__":
    with app.app_context():
        # db.create_all()
        # upgrade() # Apply all pending migrations to the remote database
        print("Applying migrations...")
        # upgrade()
        print("✅ Migrations applied!")
    # If running a VS Code preview that loads the app from another host,
    # bind to 0.0.0.0 when DEV_PREVIEW is enabled so the preview can reach it.
    dev_preview = os.getenv('DEV_PREVIEW', '0') in ('1', 'true', 'True')
    if dev_preview:
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
    else:
        app.run(debug=True)
