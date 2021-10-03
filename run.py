from src import app
from flaskwebgui import FlaskUI

# To convert to gui: make sure to set dubug to False and uncomment JS script

if __name__ == "__main__":
    # app.run()
    FlaskUI(app, width=1600, height=1000, maximized=True).run()
