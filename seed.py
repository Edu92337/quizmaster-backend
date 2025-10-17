import json
from app import app, db
from models import Question

def load_questions_from_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    return questions_data

def seed_questions():
    with app.app_context():
        # Apagar questões existentes para evitar duplicatas
        db.session.query(Question).delete()

        # Carregar questões do ENEM
        enem_questions = load_questions_from_json('initial_questions/enem.json')
        for q_data in enem_questions:
            new_question = Question(**q_data)
            db.session.add(new_question)

        # Carregar questões de Residência Médica
        residencia_questions = load_questions_from_json('initial_questions/residencia_medica.json')
        for q_data in residencia_questions:
            new_question = Question(**q_data)
            db.session.add(new_question)

        db.session.commit()
        print("Banco de dados populado com questões iniciais!")

if __name__ == "__main__":
    seed_questions()

