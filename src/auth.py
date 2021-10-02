from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from src import app

login_manager = LoginManager()
login_manager.init_app(app)
