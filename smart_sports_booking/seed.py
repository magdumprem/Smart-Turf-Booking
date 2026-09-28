from app import app, db, Ground

with app.app_context():
    # 1. Drop all existing tables to refresh schema changes
    db.drop_all()
    
    # 2. Re-create all tables with the new columns
    db.create_all()
    
    # 3. Insert sample grounds with price_per_hour
    g1 = Ground(name="Apex Turf A", sport_type="Football", location="Sector 4", price_per_hour=600, status="Available")
    g2 = Ground(name="Smash Court", sport_type="Badminton", location="Indoor Hall 2", price_per_hour=400, status="Available")
    g3 = Ground(name="Thunder Arena", sport_type="Cricket", location="Ground B", price_per_hour=800, status="Available")
    
    db.session.add_all([g1, g2, g3])
    db.session.commit()
    print("✅ Database reset and seeded successfully!")