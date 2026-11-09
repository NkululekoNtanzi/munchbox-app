from app.database import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    if db.query(models.Product).first():
        print("Database already seeded.")
        db.close()
        return

    products = [
        {"name": "Solo Box", "category": "Savory Boxes", "base_price": 65.00},
        {"name": "Classic Savoury Box", "category": "Savory Boxes", "base_price": 120.00},
        {"name": "Party Box (100 items)", "category": "Event Platters", "base_price": 450.00},
        {"name": "Mega Box (150 items)", "category": "Event Platters", "base_price": 650.00},
        {"name": "Movie Night Box", "category": "Specials", "base_price": 95.00},
        {"name": "Christmas Sweet Box (Solo)", "category": "Festive", "base_price": 85.00},
        {"name": "Valentine Sweet Box (Solo)", "category": "Specials", "base_price": 85.00},
        {"name": "Mix & Match Box", "category": "Custom", "base_price": 110.00}
    ]

    for p in products:
        db.add(models.Product(**p))
    db.commit()
    db.close()
    print("MunchBox official products seeded successfully!")

if __name__ == "__main__":
    seed_database()