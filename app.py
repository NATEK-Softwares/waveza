from flask import Flask, json, render_template, redirect, url_for, request, flash, jsonify, abort, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, Poem, Like, Comment
import os
import uuid
from werkzeug.utils import secure_filename
# import bleach
from sqlalchemy import func, text
from slugify import slugify
from flask_migrate import Migrate, upgrade
from dotenv import load_dotenv
# from passlib.hash import scrypt
# import json
from datetime import datetime

# Environment variables
load_dotenv()

print("DATABASE_URL =", os.getenv("DATABASE_URL"))


def create_app():
    app = Flask(__name__)
    
    # Use PostgreSQL if DATABASE_URL is set, otherwise use SQLite for local development
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        # Local SQLite database for development
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mishwrites.db"
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB (fixed calc)
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = 'Lax'

    db.init_app(app)
    Migrate(app, db)
    print("✅ Database initialized and migrations set up.")
    print("Database URL =", app.config["SQLALCHEMY_DATABASE_URI"])
    return app

app = create_app()

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

# ----------------PUSH NOTIFICATIONS-------#
from pywebpush import webpush, WebPushException


def send_push_notification(subscription_info, message_title="New Notification", message_body="You have a new message.", url="/"):
    payload = json.dumps({
        "title": message_title,
        "body": message_body,
        # "url": url
    })

    try:
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
    except WebPushException as ex:
        print("Web push failed: {}", repr(ex))

VAPID_PRIVATE_KEY = "4yGY_ZSv-sWLFCbzm3tSZkSsi_tLtMQVVQK50bruqSM"
VAPID_PUBLIC_KEY = "BCdRj1CvyIzXn3I356t7oZGpGalj5CqemFYCSds6DyOR8BHW3uy-yUcvnTaE6NQkCDSPZFMlzvtWKcj6k7LQO5g"
VAPID_CLAIMS = {
    "sub": "mailto:mishackmadubandlela@gmail.com"
    }

def send_push(subscription_info, title, body, url):
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps({
                "title": title,
                "body": body,
                "url": url
            }),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
    except WebPushException as ex:
        print("Web push failed:", repr(ex))


@app.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    subscription_json = request.get_json()
    if not subscription_json:
        return jsonify({'error': 'Invalid subscription data'}), 400

    # Save subscription JSON as string in the current user's record
    current_user.push_subscription = json.dumps(subscription_json)
    db.session.commit()

    return jsonify({'success': True}), 201


@app.route('/notify')
@login_required
def notify():
    if not current_user.push_subscription:
        return "No subscription for user", 400

    subscription_info = json.loads(current_user.push_subscription)
    send_push_notification(
        subscription_info,
        message_title="New Poem Published!",
        message_body="Check out the latest poem in your favorite category.",
        # url="/latest-poem"  # or wherever you want users to go
    )
    return "Notification sent!"


# ---------------- Routes ---------------- #

@app.route("/")
def index():
    poems = Poem.query.order_by(Poem.id.desc()).all() # type: ignore

    # Get all categories with count of poems
    categories = [(c.category, c[1]) for c in db.session.query(
        Poem.category, func.count(Poem.id) #type: ignore
    ).group_by(Poem.category).all()]

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

@app.route("/category/<name>", methods=["GET", "POST"])
def category(name):
    poems = Poem.query.filter_by(category=name).order_by(Poem.id.desc()).all()

    # Get all categories with counts for navbar or sidebar
    nav_categories = [(c.category, c[1]) for c in db.session.query(Poem.category, func.count(Poem.id)).group_by(Poem.category).all()] #type: ignore
    nav_categories = nav_categories[:2]
    return render_template("category.html", poems=poems, category=name, categories=categories, nav_categories=nav_categories)

@app.context_processor
def inject_nav_categories():
    rows = db.session.query(Poem.category, func.count(Poem.id)).group_by(Poem.category).all() #type: ignore 
    nav_categories = [(c.category or 'uncategorized', c[1]) for c in rows]
    return dict(nav_categories=nav_categories)

@app.route("/categories")
def categories():
    categories = [(c.category, c[1]) for c in db.session.query( #type: ignore
        Poem.category, func.count(Poem.id) #type: ignore
    ).group_by(Poem.category).all()]
    return render_template("categories.html", categories=categories)

@app.route("/poems")
def poems():
    poems = Poem.query.all()
    return render_template("poems.html", poems=poems)

@app.route("/poem/<int:poem_id>/<slug>")
def poem(poem_id, slug):
    poem = Poem.query.get_or_404(poem_id)

    # Optional: redirect if slug doesn’t match (for SEO consistency)
    if poem.slug != slug:
        return redirect(url_for('view_poem', poem_id=poem.id, slug=poem.slug))
    
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
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Basic validation
        if not username or not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for("register"))

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "warning")
            return redirect(url_for("register"))

        # Hash the password using scrypt
        print(f"Hashing password...")
        # hashed_password = bcrypt.hash(password)
        print(f"Successfully hashed password. Done!")
        # print(f"Hashed password: {hashed_password}")
        # hashed_password = generate_password_hash(password)

        # Create user and save to DB
        new_user = User(username=username, email=email, password=password)
        print(f"Adding new user to database: USER TABLE")
        db.session.add(new_user)
        db.session.commit()
        print(f"{new_user} Successfully added. Done")

        # Log the user in
        login_user(new_user)
        print(f"User {new_user} logged in successfully")
        print(f"Logged in user: {new_user}")
        flash("Registration successful! Welcome.", "success")
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
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(f"Password from form: {password}")
        print(f"Username from form: {username}")

        user = User.query.filter_by(username=username).first()
        print(f"Username to query: {username}")

        if user:
            print(f"✅ User {user} found (password check skipped)")
            login_user(user)
            print("✅ User logged in:", user.username)
            flash("Login successful", "success") #Password check skipped
            return redirect(url_for("dashboard"))
        else:
            print(f"❌ Login failed for:", username)
            flash("Invalid credentials", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    poems = Poem.query.filter_by(author_id=current_user.id).all()
    total_likes = sum(len(poem.likes) for poem in poems)
    total_comments = sum(len(poem.comments) for poem in poems)
    total_users = User.query.count()
    return render_template("dashboard.html", poems=poems, total_poems=len(poems), total_likes=total_likes, total_comments=total_comments, total_users=total_users)

@app.route("/profile") #type: ignore
@login_required
def profile():
    poems = Poem.query.filter_by(author_id=current_user.id).all()
    total_likes = sum(len(poem.likes) for poem in poems)
    total_comments = sum(len(poem.comments) for poem in poems)
    total_users = User.query.count()
    return render_template("profile.html", poems=poems, total_poems=len(poems), total_likes=total_likes, total_comments=total_comments, total_users=total_users)

@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
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
    
    # Get user's poems
    poems = Poem.query.filter_by(author_id=user.id).all()
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
    cloud_name="YOUR_CLOUD_NAME",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    secure=True
)

ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm", "mov"}
ALLOWED_VIDEO_MIMES = {"video/mp4", "video/webm", "video/quicktime"}

def allowed_video(file):
    if not file or not file.filename:
        return False

    ext = file.filename.rsplit(".", 1)[1].lower()
    return (
        "." in file.filename
        and ext in ALLOWED_VIDEO_EXTENSIONS
        and file.mimetype in ALLOWED_VIDEO_MIMES
    )

def upload_video_to_cloudinary(file):
    result = cloudinary.uploader.upload(
        file,
        resource_type="video",
        folder="poems/videos"
    )
    return result["secure_url"], result["public_id"]


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
        new_category = request.form.get("new category")

        # ---------- VIDEO ----------
        video_file = request.files.get("video")
        video_url = None
        video_public_id = None

        if video_file and allowed_video(video_file):
            video_url, video_public_id = upload_video_to_cloudinary(video_file)

        poem = Poem(
            title=title,
            content=content,
            author=current_user,
            category=category or new_category,
            video_url=video_url,
            video_public_id=video_public_id
        )

        poem.excerpt = poem.get_excerpt(300)
        poem.slug = slugify(title)

        db.session.add(poem)
        db.session.commit()

        flash("Poem published successfully!", "success")
        return redirect(url_for("poem", poem_id=poem.id, slug=poem.slug))

    return render_template("add_poem.html")




@app.route("/edit_poem/<int:poem_id>", methods=["GET", "POST"])
@login_required
def edit_poem(poem_id):
    poem = Poem.query.get_or_404(poem_id)

    if poem.author_id != current_user.id:
        flash("You are not allowed to edit this poem.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        poem.title = request.form["title"]

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
        if video_file and allowed_video(video_file.filename):
            video_filename = f"{uuid.uuid4()}_{secure_filename(video_file.filename)}"
            video_path = os.path.join(app.config["VIDEO_UPLOAD_FOLDER"], video_filename)
            video_file.save(video_path)
            poem.video_url = f"uploads/videos/{video_filename}"

        db.session.commit()
        flash("Poem updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit_poem.html", poem=poem)




@app.route('/contact')
def contact():
    return render_template('contact.html')


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


# Run
if __name__ == "__main__":
    with app.app_context():
        # db.create_all()
        # upgrade() # Apply all pending migrations to the remote database
        print("Applying migrations...")
        # upgrade()
        print("✅ Migrations applied!")
    app.run(debug=True)
