from application import app
from app import db
from app.models import User

with app.app_context():
    admin = User(nome="leo", email="leoogura@hotmail.com")
    admin.set_senha("senhaSegura1234")
    db.session.add(admin)
    db.session.commit()

    print("Admin criado com sucesso!")

