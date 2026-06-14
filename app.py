import os
from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import uuid
from models import db, User, Role

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Core Configurations (Now pulling from .env)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT')

# Initialize Extensions
db.init_app(app)
bcrypt = Bcrypt(app)

# Setup Flask-Security Datastore
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@app.route('/')
def home():
    return "Trekking Management System"

if __name__ == '__main__':
    app.run() # Removed debug=True here since FLASK_DEBUG=1 in .env handles it