import typing as t
from djask import Djask
from djask.admin import Admin
from djask.auth.models import User



app = Djask(__name__)
admin_ext = Admin() # initialize the admin site
admin_ext.init_app(app)

db = app.db

@app.before_first_request
def init_db():
    db.create_all()
    admin = User(username="test", is_admin=True)
    admin.set_password("password")
    db.session.add(admin)
    db.session.commit()
