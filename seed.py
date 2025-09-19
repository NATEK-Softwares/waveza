# seed.py
from app import app, db
from models import User, Poem, Comment, Like
from datetime import datetime, timezone

def run_seed():
    with app.app_context():
        db.drop_all()   # ⚠️ Clears existing tables
        db.create_all()

        # --- Users ---
        writer1 = User(
            username="writer1",
            email="writer1@example.com",
            password="writerpass",  # plain here, will be hashed
            role="writer"
        )

        mishack = User(
            username="OMEGA3",
            email="mishwrites@email.com",
            password="writerpass",  # plain here, will be hashed
            role="writer"
        )

        reader1 = User(
            username="reader1",
            email="reader1@example.com",
            password="readerpass",
            role="reader"
        )

        db.session.add_all([writer1, mishack, reader1])
        db.session.commit()

        # --- Poems ---
        poem1 = Poem(
            title="The Rising Sun",
            content="The sun climbs high, chasing the night away...",
            category="Nature",
            author=writer1
        )

        poem2 = Poem(
            title="Pain Is Art",
            content="Behind the smile, I hide my fears, and cry my silent tears...",
            category="Emotions",
            author=writer1
        )

        db.session.add_all([poem1, poem2])
        db.session.commit()

        # --- Comments ---
        comment1 = Comment(
            content="Beautiful imagery, I love this!",
            user_id=reader1.id,
            poem_id=poem1.id
        )

        comment2 = Comment(
            content="This one touched me deeply ❤️",
            user_id=reader1.id,
            poem_id=poem2.id
        )

        db.session.add_all([comment1, comment2])
        db.session.commit()

        # --- Likes ---
        like1 = Like(user_id=reader1.id, poem_id=poem1.id)
        like2 = Like(user_id=reader1.id, poem_id=poem2.id)

        db.session.add_all([like1, like2])
        db.session.commit()

        print("✅ Database seeded with sample data!")

if __name__ == "__main__":
    run_seed()
