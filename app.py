from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, Poem, Like, Comment
import os
from werkzeug.utils import secure_filename
# import bleach
from sqlalchemy import func
from slugify import slugify
from flask_migrate import Migrate, upgrade
from dotenv import load_dotenv
# from passlib.hash import scrypt
# import json

# Environment variables
load_dotenv()

print("DATABASE_URL =", os.getenv("DATABASE_URL"))


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB (fixed calc)
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["SESSION_COOKIE_SAMESITE"] = 'Lax'

    db.init_app(app)
    Migrate(app, db)
    print("✅ Database initialized and migrations set up.")
    print("Database URL =", os.getenv("DATABASE_URL"))
    return app

app = create_app()

with app.app_context():
    db.create_all()
    # upgrade()  # Uncomment if you want to use migrations

# Login manager setup
login_manager = LoginManager()
login_manager.login_view = "login"  # type: ignore
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



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
        category = request.form.get("category")
        new_category = request.form.get("new category")
        profile_image = request.form.get("profile")  # optional
        bio = request.form.get("bio")

        # if not category:
        category = category or new_category #request.form.get("new category")
        # else:
        #     return redirect(url_for("poem", poem_id=poem.id, slug=poem.slug))


        if not bio or not category:
            flash("Bio and content are required.", "danger")
            return redirect(url_for("add_poem"))
        
        if not profile_image:
            return None

        # Generate slug (already done in model __init__, but safe to enforce)
        # profile.slug = slugify(profile)

        # Save to database
        db.session.add(profile)
        db.session.commit()

        flash("Poem published successfully!", "success")
        return redirect(url_for("profile")) # poem_id=poem.id, slug=profile.slug))

    return render_template("edit_profile.html")


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


@app.route("/add_poem", methods=["GET", "POST"])
@login_required
def add_poem():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        category = request.form.get("category")
        new_category = request.form.get("new category")
        file = request.files.get("thumbnail")
        thumbnail = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            thumbnail = f"uploads/{filename}"  # relative to 'static/

        # if not category:
        category = category or new_category #request.form.get("new category")
        # else:
        #     return redirect(url_for("poem", poem_id=poem.id, slug=poem.slug))


        if not title or not content:
            flash("Title and content are required.", "danger")
            return redirect(url_for("add_poem"))

        # Create the Poem object
        poem = Poem(
            title=title,
            content=content,
            author=current_user,
            category=category, #type: ignore
            new_category=new_category, #type: ignore
            thumbnail=thumbnail, #type: ignore
        )


        # Generate excerpt
        poem.excerpt = poem.get_excerpt(length=300)

        # Generate slug (already done in model __init__, but safe to enforce)
        poem.slug = slugify(title)

        # Save to database
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
        clean_content = raw_content #bleach.clean(raw_content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
        poem.content = clean_content   # ✅ now modifying instance, not class

        poem.category = request.form.get("category")
        if not poem.category:
            poem.category = request.form.get("new category")
        # else:
        #     return redirect(url_for("poem", poem_id=poem.id, slug=poem.slug))

        poem.thumbnail = request.form.get("thumbnail") or poem.thumbnail

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
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

import uuid

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
