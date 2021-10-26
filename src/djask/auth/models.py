from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base, AbstractConcreteBase

Base = declarative_base()


class User(AbstractConcreteBase, Base):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    name = db.Column(db.String(128))
    email = db.Column(db.String(256), unique=True)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
