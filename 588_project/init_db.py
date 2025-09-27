from app import db, Member

db.create_all()

members = [
    Member(name="Jaywynn Unfair", facebook_link="https://www.facebook.com/jaywynn.588"),
    Member(name="Well Winterfell", facebook_link="https://www.facebook.com/dwsasc")
]

db.session.add_all(members)
db.session.commit()
print("Database initialized with sample members!")
