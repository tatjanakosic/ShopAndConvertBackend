from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail, Message

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    # ✅ This must be present and correctly configured
    CORS(app,
         supports_credentials=True,
         origins=["http://localhost:3000"],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "OPTIONS", "PATCH", "PUT"])
    
    

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    return app
