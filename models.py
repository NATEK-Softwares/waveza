from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
import re
from unidecode import unidecode
from markupsafe import Markup
from bs4 import BeautifulSoup
from slugify import slugify
from extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)  # stores HASH, not plain password
    role = db.Column(db.String(20), default="")  # "writer" or "reader"
    push_subscription = db.Column(db.JSON, nullable=True)

    poems = db.relationship("Poem", backref="author", lazy=True)
    comments = db.relationship("Comment", backref="user", lazy=True)
    likes = db.relationship("Like", backref="user", lazy=True)

    def set_password(self, raw_password: str) -> None:
        """Hash and store password securely"""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verify stored hash against a raw password"""
        return check_password_hash(self.password, raw_password)

    def __init__(self, username: str, email: str, password: str, role: str = "writer") -> None:
        self.username = username
        self.email = email
        self.set_password(password)  # ✅ hash automatically
        self.role = role

    def __repr__(self) -> str:
        return f"<User {self.username}>"

def slugify(text: str) -> str:
    text = unidecode(text).lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.String(500), nullable=False) #NEW COLUMN
    profile_image = db.Column(db.String(255)) #NEW COLUMN
    slug = db.Column(db.String(200), unique=True, nullable=False) #NEW COLUMN

class Poem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    category = db.Column(db.String(100), nullable=True)
    excerpt = db.Column(db.Text)
    thumbnail = db.Column(db.String(255))
    slug = db.Column(db.String(200), unique=True, nullable=False)  # ✅ NEW COLUMN


    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comments = db.relationship("Comment", backref="poem", lazy=True, cascade="all, delete-orphan")
    likes = db.relationship("Like", backref="poem", lazy=True, cascade="all, delete-orphan")

    def __init__(self, title: str, content: str, author, category: str = None, new_category: str = None, thumbnail: str = None): #type: ignore
        self.title = title
        self.content = content
        self.author = author
        self.category = category
        new_category = new_category
        self.thumbnail = thumbnail
        self.slug = slugify(title)  # ✅ auto-generate slug

    def __repr__(self):
        return f"<Poem {self.title}>"
    
    def get_excerpt(self, length=300):
        """
        Generate a clean excerpt from HTML content.
        Keeps line breaks but strips unsafe tags.
        """
        soup = BeautifulSoup(self.content, "html.parser")
        text = soup.get_text("\n")  # preserve line breaks
        excerpt = text[:length].rstrip()
        if len(text) > length:
            excerpt += "..."
        return Markup(excerpt)



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    poem_id = db.Column(db.Integer, db.ForeignKey("poem.id"), nullable=False)

    parent_id = db.Column(db.Integer, db.ForeignKey("comment.id"), nullable=True)
    replies = db.relationship("Comment", backref=db.backref("parent", remote_side=[id]), lazy=True)

    def __init__(self, content: str, user_id: int, poem_id: int, parent_id: int = None) -> None: #type: ignore
        self.content = content
        self.user_id = user_id
        self.poem_id = poem_id
        self.parent_id = parent_id

    def __repr__(self) -> str:
        return f"<Comment {self.content[:20]}...>"


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    poem_id = db.Column(db.Integer, db.ForeignKey("poem.id"), nullable=False)

    def __init__(self, user_id: int, poem_id: int) -> None:
        self.user_id = user_id
        self.poem_id = poem_id

    def __repr__(self) -> str:
        return f"<Like user={self.user_id} poem={self.poem_id}>"
