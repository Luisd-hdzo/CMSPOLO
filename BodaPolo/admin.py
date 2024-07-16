from main import app, db, User

with app.app_context():
    admin = User(username='admin')
    admin.set_password('adminpassword')
    db.session.add(admin)
    db.session.commit()

print("Admin user created successfully.")
