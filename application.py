from flask import Flask
from watchlist import watchlist_blueprint
import os

application = Flask(__name__)
application.register_blueprint(watchlist_blueprint)
application.config['SECRET_KEY'] = os.environ['FLASK_SECRET']

if __name__ == '__main__':
    application.run(debug=True)
