from .app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_subscribed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False) # List of strings
    correct_answer = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    exam_type = db.Column(db.String(120), nullable=False) # ENEM, Residência, etc.
    difficulty = db.Column(db.String(50), default='medium')
    created_by_ia = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Question {self.id} - {self.subject}>'

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    questions_answered = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    # A cor do quadrado pode ser calculada no frontend ou ter um valor aqui, por simplicidade, vamos calcular no frontend

    user = db.relationship('User', backref=db.backref('progress', lazy=True))

    def __repr__(self):
        return f'<UserProgress {self.user_id} on {self.date}>'

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stripe_customer_id = db.Column(db.String(255), unique=True, nullable=False)
    stripe_subscription_id = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(50), nullable=False) # active, cancelled, past_due, etc.
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('subscription', uselist=False, lazy=True))

    def __repr__(self):
        return f'<Subscription {self.stripe_subscription_id} for user {self.user_id}>'

class AIInteraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    interaction_type = db.Column(db.String(50), nullable=False) # 'question_generation', 'chat'
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('ai_interactions', lazy=True))

    def __repr__(self):
        return f'<AIInteraction {self.id} - {self.interaction_type}>'
