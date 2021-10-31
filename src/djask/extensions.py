from flask_bootstrap import Bootstrap
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

bootstrap = Bootstrap()
compress = Compress()
csrf = CSRFProtect()
db = SQLAlchemy()
