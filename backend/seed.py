import os
from datetime import date, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Ensure environment is loaded
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

from app.database import engine, Base, SessionLocal
from app.models import User, Item, UserRole, ItemType
from app.auth import get_password_hash


def seed_database():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Seed Admin
        admin_email = os.getenv("ADMIN_EMAIL", "admin@recoverease.in").lower().strip()
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin@123")
        admin_name = os.getenv("ADMIN_NAME", "Institute Head")

        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                name=admin_name,
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                role=UserRole.INSTITUTE_HEAD.value,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"-> Seeded Admin User: {admin_email}")
        else:
            print(f"-> Admin User {admin_email} already exists.")

        # 2. Seed Regular Demo Users
        demo_users_data = [
            {"name": "Alex Chen", "email": "alex@recoverease.in", "password": "User@123"},
            {"name": "Priya Sharma", "email": "priya@recoverease.in", "password": "User@123"},
            {"name": "Marcus Johnson", "email": "marcus@recoverease.in", "password": "User@123"},
        ]

        created_users = {}
        for u in demo_users_data:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                user_obj = User(
                    name=u["name"],
                    email=u["email"],
                    password_hash=get_password_hash(u["password"]),
                    role=UserRole.USER.value,
                )
                db.add(user_obj)
                db.commit()
                db.refresh(user_obj)
                created_users[u["email"]] = user_obj
                print(f"-> Seeded User: {u['email']}")
            else:
                created_users[u["email"]] = existing

        # 3. Seed Sample Items (Lost & Found for instant testing and matching)
        today = date.today()
        alex = created_users.get("alex@recoverease.in", admin)
        priya = created_users.get("priya@recoverease.in", admin)
        marcus = created_users.get("marcus@recoverease.in", admin)

        existing_items_count = db.query(Item).count()
        if existing_items_count == 0:
            sample_items = [
                # Lost / Found Pair 1: Dell Laptop
                {
                    "title": "Lost Dell XPS 15 Laptop with Charger",
                    "description": "Black Dell XPS 15 laptop in a dark grey protective sleeve, left along with a 130W USB-C charger and sticker on lid.",
                    "location": "Central Library 2nd Floor Study Room B",
                    "date": today - timedelta(days=2),
                    "type": ItemType.LOST.value,
                    "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop&q=60",
                    "posted_by": alex.id,
                    "handed_over": False,
                },
                {
                    "title": "Found Dell Laptop Charger with Grey Sleeve",
                    "description": "Found a 130W Dell USB-C charger and an empty grey laptop sleeve on the desk near the window.",
                    "location": "Library 2nd Floor Quiet Area",
                    "date": today - timedelta(days=1),
                    "type": ItemType.FOUND.value,
                    "image_url": "https://images.unsplash.com/photo-1619725002198-6a689b72f41d?w=800&auto=format&fit=crop&q=60",
                    "posted_by": priya.id,
                    "handed_over": False,
                },

                # Lost / Found Pair 2: Blue Hydro Flask Bottle
                {
                    "title": "Lost Matte Blue Hydro Flask Water Bottle",
                    "description": "32oz cobalt blue Hydro Flask bottle with mountain stickers and a black flex straw cap.",
                    "location": "University Sports Complex Gym Bench",
                    "date": today - timedelta(days=3),
                    "type": ItemType.LOST.value,
                    "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800&auto=format&fit=crop&q=60",
                    "posted_by": marcus.id,
                    "handed_over": False,
                },
                {
                    "title": "Found Blue Water Bottle with Stickers",
                    "description": "Recovered a blue vacuum-insulated stainless steel water bottle with multiple stickers from the sports hall bleachers.",
                    "location": "Sports Complex Front Desk",
                    "date": today - timedelta(days=2),
                    "type": ItemType.FOUND.value,
                    "image_url": "https://images.unsplash.com/photo-1559839914-17aae19cec71?w=800&auto=format&fit=crop&q=60",
                    "posted_by": admin.id,
                    "handed_over": False,
                },

                # Item 3: Car Keys
                {
                    "title": "Lost Toyota Car Key with Red Lanyard",
                    "description": "Single Toyota smart key fob attached to a red woven nylon lanyard and a small bronze whistle.",
                    "location": "Engineering Block Car Parking Lot",
                    "date": today - timedelta(days=4),
                    "type": ItemType.LOST.value,
                    "image_url": "https://images.unsplash.com/photo-1622547748225-3fc4abd2cca0?w=800&auto=format&fit=crop&q=60",
                    "posted_by": priya.id,
                    "handed_over": False,
                },
                {
                    "title": "Found Toyota Smart Key Fob",
                    "description": "Found a Toyota car key fob near Parking Pillar C4. Handed in at the Campus Security checkpoint.",
                    "location": "Security Office Gate 1",
                    "date": today - timedelta(days=3),
                    "type": ItemType.FOUND.value,
                    "image_url": "https://images.unsplash.com/photo-1584438784894-089d6a62b8fa?w=800&auto=format&fit=crop&q=60",
                    "posted_by": alex.id,
                    "handed_over": True,
                },
            ]

            for item_info in sample_items:
                item_obj = Item(**item_info)
                db.add(item_obj)
            db.commit()
            print(f"-> Seeded {len(sample_items)} initial sample Lost & Found items.")
        else:
            print("-> Items already exist in database; skipping sample items.")

        print("Database seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
