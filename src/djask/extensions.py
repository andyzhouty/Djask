from flask_bootstrap import Bootstrap
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from .db import Model

bootstrap = Bootstrap()
compress = Compress()
csrf = CSRFProtect()
db = SQLAlchemy(model_class=Model)
