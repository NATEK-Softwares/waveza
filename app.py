from flask import Flask, render_template, redirect, url_for, request, flash
# from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
# from models import db, User, Poem, Like, Comment
from extensions import db
from models import User, Poem, Like, Comment
import os
# from werkzeug.utils import secure_filename
# import bleach
from sqlalchemy import func
from slugify import slugify
from flask_migrate import Migrate
from dotenv import load_dotenv

# Environment variables
load_dotenv()

app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://mish_writes:Admin@localhost:5432/poetrydb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = 2 * 3024 * 3024  # 2MB

db.init_app(app)
migrate = Migrate(app, db)

# db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login" #type: ignore
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- Routes ---------------- #


@app.route("/")
def index():
    poems = Poem.query.order_by(Poem.id.desc()).all()

    # Get all categories with count of poems
    categories = [(c.category, c[1]) for c in db.session.query(
        Poem.category, func.count(Poem.id) #type: ignore
    ).group_by(Poem.category).all()]

    # Top 5 for navbar
    nav_categories = categories[:5]

    return render_template(
        "index.html", poems=poems, categories=categories, nav_categories=nav_categories
    )

@app.route("/category/<name>")
def category(name):
    poems = Poem.query.filter_by(category=name).order_by(Poem.id.desc()).all()

    # Get all categories with counts for navbar or sidebar
    nav_categories = [(c.category, c[1]) for c in db.session.query(Poem.category, func.count(Poem.id)).group_by(Poem.category).all()] #type: ignore
    nav_categories = nav_categories[:5]

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

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "warning")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash("Registration successful! Welcome.", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password): #type: ignore
            login_user(user)
            flash("Login successful", "success")
            return redirect(url_for("dashboard"))
        else:
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
    # total_readers = sum(len(user.user_id) for user in UserMixin)
    return render_template("dashboard.html", poems=poems, total_poems=len(poems), total_likes=total_likes, total_comments=total_comments, total_users=total_users)

@app.route("/profile") #type: ignore
@login_required
def profile():
    poems = Poem.query.filter_by(author_id=current_user.id).all()
    total_likes = sum(len(poem.likes) for poem in poems)
    total_comments = sum(len(poem.comments) for poem in poems)
    total_users = User.query.count()

    return render_template("profile.html", poems=poems, total_poems=len(poems), total_likes=total_likes, total_comments=total_comments, total_users=total_users)

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
        # new_category = request.form.get("new cateogry")
        thumbnail = request.form.get("thumbnail")  # optional

        if not category:
            category = request.form.get("new category")
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
            # new_category=new_category, #type: ignore
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
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
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
        db.create_all()
    app.run(debug=True)
