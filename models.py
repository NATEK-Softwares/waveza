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
import markdown as md


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)  # stores HASH, not plain password
    role = db.Column(db.String(20), default="user")  # "user", "admin"
    push_subscription = db.Column(db.JSON, nullable=True)
    bio = db.Column(db.String(500), nullable=True)  # User bio
    profile_image = db.Column(db.String(255), nullable=True)  # Profile image path
    preferred_categories = db.Column(db.String(500), nullable=True)  # Comma-separated list of categories
    custom_categories = db.Column(db.String(500), nullable=True)  # User-defined custom categories
    profile_views = db.Column(db.Integer, default=0)  # Profile view count tracking
    is_public = db.Column(db.Boolean, default=True)  # Public profile visibility
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Account creation date
    id_number = db.Column(db.String(50), nullable=True)  # ID Number for registration
    location = db.Column(db.String(200), nullable=True)  # User location
    art_field = db.Column(db.String(100), nullable=True)  # Art field preference
    popia_consent = db.Column(db.Boolean, default=False)  # POPIA data sharing consent
    terms_accepted = db.Column(db.Boolean, default=False)  # T&Cs acceptance

    poems = db.relationship("Poem", backref="author", lazy=True)
    comments = db.relationship("Comment", backref="user", lazy=True)
    likes = db.relationship("Like", backref="user", lazy=True)
    notifications = db.relationship("Notification", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, raw_password: str) -> None:
        """Hash and store password securely"""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verify stored hash against a raw password"""
        return check_password_hash(self.password, raw_password)

    def __init__(self, username: str, email: str, password: str, role=None) -> None:
        self.username = username
        self.email = email
        self.set_password(password)  # ✅ hash automatically
        self.role = role if role else "reader"

    def __repr__(self) -> str:
        return f"<User {self.username}>"
    
    def get_profile_completion_percentage(self) -> int:
        """Calculate profile completion percentage (0-100)"""
        completion = 0
        fields = {
            'username': 20,
            'email': 20,
            'bio': 20,
            'profile_image': 20,
            'preferred_categories': 20
        }
        
        if self.username:
            completion += fields['username']
        if self.email:
            completion += fields['email']
        if self.bio:
            completion += fields['bio']
        if self.profile_image:
            completion += fields['profile_image']
        if self.preferred_categories:
            completion += fields['preferred_categories']
        
        return min(completion, 100)
    
    def get_all_categories(self) -> list:
        """Get both preferred and custom categories as a list"""
        categories = []
        if self.preferred_categories:
            categories.extend([cat.strip() for cat in self.preferred_categories.split(',') if cat.strip()])
        if self.custom_categories:
            categories.extend([cat.strip() for cat in self.custom_categories.split(',') if cat.strip()])
        return list(set(categories))  # Remove duplicates
    
    def add_custom_category(self, category: str) -> bool:
        """Add a custom category"""
        if not category or len(category.strip()) == 0:
            return False
        category = category.strip().lower()
        if self.custom_categories:
            existing = [cat.strip() for cat in self.custom_categories.split(',')]
            if category not in existing:
                self.custom_categories += f",{category}"
        else:
            self.custom_categories = category
        return True
    
    def increment_profile_views(self) -> None:
        """Increment profile view count"""
        self.profile_views = (self.profile_views or 0) + 1
    
    def get_bio_html(self) -> Markup:
        """Render bio as markdown HTML"""
        if not self.bio:
            return Markup("")
        
        # Convert markdown to HTML
        html = md.markdown(self.bio, extensions=['nl2br'])
        
        # Sanitize HTML to prevent XSS
        soup = BeautifulSoup(html, "html.parser")
        
        # Only allow safe tags
        allowed_tags = {'p', 'br', 'strong', 'em', 'u', 'code', 'a', 'ul', 'ol', 'li', 'blockquote', 'h1', 'h2', 'h3'}
        
        for tag in soup.find_all():
            if tag.name not in allowed_tags:
                tag.unwrap()
        
        # Add target="_blank" to links
        for link in soup.find_all('a'):
            link['target'] = '_blank'
            link['rel'] = 'noopener noreferrer'
        
        return Markup(str(soup))


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
    video_url = db.Column(db.Text)
    video_public_id = db.Column(db.String(255))
    slug = db.Column(db.String(200), unique=True, nullable=False)  # ✅ NEW COLUMN
    approval_status = db.Column(db.String(20), default="pending")  # "pending", "approved", "rejected"
    admin_review_comments = db.Column(db.Text, nullable=True)  # Admin's review comments
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)  # When post was submitted
    history_date = db.Column(db.DateTime, nullable=True)  # Date for history posts (month/year)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comments = db.relationship("Comment", backref="poem", lazy=True, cascade="all, delete-orphan")
    likes = db.relationship("Like", backref="poem", lazy=True, cascade="all, delete-orphan")

    def __init__(self, title: str, content: str, author, category: str = None, new_category: str = None, thumbnail: str = None, video_url=None, video_public_id=None, history_date=None): #type: ignore
        self.title = title
        self.content = content
        self.author = author
        self.category = category
        self.thumbnail = thumbnail
        self.slug = slugify(title)  # ✅ auto-generate slug
        self.video_url = video_url
        self.video_public_id = video_public_id
        self.history_date = history_date


    def __repr__(self):
        return f"<Poem {self.title}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "category": self.category,
            "excerpt": self.excerpt,
            "thumbnail": self.thumbnail,
            "video_url": self.video_url,
            "slug": self.slug,
            "approval_status": self.approval_status,
            "author": self.author.username if self.author else None,
            "likes_count": len(self.likes),
            "comments_count": len(self.comments)
        }
    
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
    
    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "parent_id": self.parent_id,
            "replies": [reply.to_dict() for reply in self.replies] if self.replies else []
        }


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    poem_id = db.Column(db.Integer, db.ForeignKey("poem.id"), nullable=False)

    def __init__(self, user_id: int, poem_id: int) -> None:
        self.user_id = user_id
        self.poem_id = poem_id

    def __repr__(self) -> str:
        return f"<Like user={self.user_id} poem={self.poem_id}>"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    poem_id = db.Column(db.Integer, db.ForeignKey("poem.id"), nullable=False)

    def __init__(self, user_id: int, poem_id: int) -> None:
        self.user_id = user_id
        self.poem_id = poem_id

    def __repr__(self) -> str:
        return f"<Like user={self.user_id} poem={self.poem_id}>"


class Notification(db.Model):
    """User notifications for post approvals, rejections, and admin alerts"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # "post_approved", "post_rejected", "new_post_submitted"
    poem_id = db.Column(db.Integer, db.ForeignKey("poem.id"), nullable=True)  # Related poem
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to Poem
    poem = db.relationship("Poem", backref="notifications")
    
    def __init__(self, user_id: int, title: str, message: str, notification_type: str, poem_id: int = None) -> None:
        self.user_id = user_id
        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.poem_id = poem_id
    
    def __repr__(self) -> str:
        return f"<Notification {self.title}>"


class PageView(db.Model):
    """Track page views and traffic analytics"""
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(200), nullable=False)  # e.g., "landing_page"
    user_agent = db.Column(db.String(500), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, page: str, user_agent: str = None, ip_address: str = None) -> None:
        self.page = page
        self.user_agent = user_agent
        self.ip_address = ip_address
    
    def __repr__(self) -> str:
        return f"<PageView {self.page} at {self.timestamp}>"
