from flask import Flask, request, jsonify
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuração do Banco de Dados
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configuração JWT
jwt = JWTManager(app)

# Importar modelos e rotas aqui para evitar importações circulares
from .models import User, Question, UserProgress, Subscription, AIInteraction
from .auth import auth_bp
from .questions import questions_bp
from .progress import progress_bp
from .ai import ai_bp
from .subscription import subscription_bp
# from .routes import auth_bp, questions_bp, progress_bp, subscription_bp, ai_bp

# Registrar Blueprints (quando criados)
app.register_blueprint(auth_bp)
app.register_blueprint(questions_bp)
app.register_blueprint(progress_bp)
app.register_blueprint(subscription_bp)
app.register_blueprint(ai_bp)

@app.route('/')
def hello_world():
    return 'Hello, World! This is the Quiz Backend!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

