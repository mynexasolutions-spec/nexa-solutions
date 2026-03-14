from datetime import datetime
from app import create_app
from extensions import db
from app.models.blog import BlogPost, Category

app = create_app()

with app.app_context():
    # 1. Clean Sweep: Delete old data and create new tables
    db.drop_all()
    db.create_all()
    print("Step 1: Local database wiped and tables recreated.")

    # 2. Add your professional Nexa categories
    cat_tech = Category(name="TECHNOLOGY")
    cat_ai = Category(name="AI & AUTOMATION")
    cat_strategy = Category(name="BUSINESS STRATEGY")
    cat_web = Category(name="WEB ARCHITECTURE")

    db.session.add_all([cat_tech, cat_ai, cat_strategy, cat_web])
    db.session.commit()
    print("Step 2: Professional categories added.")

    # 3. Add high-quality Demo Posts linked to these categories
    posts = [
        BlogPost(
            title="The Future of Generative AI in 2026",
            slug="future-ai-2026",
            summary="How Nexa is implementing LLMs to automate business workflows.",
            content="Detailed insights into the next generation of AI automation...",
            author_name="Zobiya Hussain",
            is_published=True,
            category_id=cat_ai.id,
            published_at=datetime.utcnow()
        ),
        BlogPost(
            title="Scaling React Applications with Django",
            slug="scaling-react-django",
            summary="A deep dive into the architecture used for the Nexa Solutions platform.",
            content="Best practices for full-stack integration and performance...",
            author_name="Zobiya Hussain",
            is_published=True,
            category_id=cat_web.id,
            published_at=datetime.utcnow()
        ),
        BlogPost(
            title="Why Data Security is the New Business Strategy",
            slug="data-security-strategy",
            summary="Protecting enterprise assets in an increasingly digital world.",
            content="Moving beyond simple firewalls to proactive security measures...",
            author_name="Sadiq Ali",
            is_published=True,
            category_id=cat_strategy.id,
            published_at=datetime.utcnow()
        )
    ]

    db.session.add_all(posts)
    db.session.commit()
    print(f"Step 3: {len(posts)} demo posts created successfully!")

print("\nSUCCESS: Your local DB is clean and ready.")