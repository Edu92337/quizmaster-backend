from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .app import db
from .models import Question, User, UserProgress

questions_bp = Blueprint("questions", __name__, url_prefix="/questions")

@questions_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_questions():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_subscribed:
        return jsonify({"msg": "Assinatura necessária para gerar questões"}), 403

    data = request.get_json()
    subject = data.get("subject")
    num_questions = data.get("num_questions", 5)
    exam_type = data.get("exam_type")

    if not subject or not exam_type:
        return jsonify({"msg": "Assunto e tipo de prova são obrigatórios"}), 400

    # Se o usuário especificou um prompt para IA, usar a IA para gerar
    prompt_ia = data.get("prompt_ia")
    if prompt_ia:
        from .ai import client as openai_client # Importar o cliente OpenAI
        from .models import AIInteraction # Importar o modelo AIInteraction
        import json

        generated_questions = []
        for _ in range(num_questions):
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4.1-mini", # Ou outro modelo adequado
                    messages=[
                        {"role": "system", "content": f"Você é um especialista em {subject} para {exam_type} e cria questões de múltipla escolha. Formate a saída como um objeto JSON com as chaves 'question_text', 'options' (uma lista de strings) e 'correct_answer' (uma string que corresponde a uma das opções)."},
                        {"role": "user", "content": f"Crie uma questão de múltipla escolha sobre {prompt_ia}."}
                    ],
                    response_format={ "type": "json_object" }
                )
                ia_response_content = response.choices[0].message.content
                generated_question_data = json.loads(ia_response_content)

                new_question = Question(
                    text=generated_question_data["question_text"],
                    options=generated_question_data["options"],
                    correct_answer=generated_question_data["correct_answer"],
                    subject=subject,
                    exam_type=exam_type,
                    difficulty="dynamic",
                    created_by_ia=True
                )
                db.session.add(new_question)
                generated_questions.append(new_question)

                ai_interaction = AIInteraction(
                    user_id=current_user_id,
                    interaction_type="question_generation",
                    prompt=prompt_ia,
                    response=ia_response_content
                )
                db.session.add(ai_interaction)

            except Exception as e:
                # Logar o erro ou retornar uma mensagem de erro específica
                print(f"Erro ao gerar questão com IA: {str(e)}")
                continue # Tentar gerar a próxima questão

        db.session.commit()
        return jsonify([{"id": q.id, "text": q.text, "options": q.options} for q in generated_questions]), 200

    # Caso contrário, buscar questões existentes no banco de dados
    existing_questions = Question.query.filter_by(subject=subject, exam_type=exam_type).limit(num_questions).all()
    if not existing_questions:
        return jsonify({"msg": "Nenhuma questão encontrada para os critérios especificados."}), 404

    return jsonify([{"id": q.id, "text": q.text, "options": q.options} for q in existing_questions]), 200

@questions_bp.route("/<int:question_id>/answer", methods=["POST"])
@jwt_required()
def answer_question(question_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    question = Question.query.get(question_id)

    if not user or not question:
        return jsonify({"msg": "Usuário ou questão não encontrada"}), 404

    data = request.get_json()
    user_answer = data.get("answer")

    is_correct = (user_answer == question.correct_answer)

    # Atualizar progresso do usuário
    today = datetime.now().date()
    user_progress = UserProgress.query.filter_by(user_id=current_user_id, date=today).first()

    if not user_progress:
        user_progress = UserProgress(user_id=current_user_id, date=today)
        db.session.add(user_progress)

    user_progress.questions_answered += 1
    if is_correct:
        user_progress.correct_answers += 1

    db.session.commit()

    return jsonify({"is_correct": is_correct, "correct_answer": question.correct_answer}), 200

@questions_bp.route("/<int:question_id>", methods=["GET"])
@jwt_required()
def get_question(question_id):
    question = Question.query.get(question_id)
    if not question:
        return jsonify({"msg": "Questão não encontrada"}), 404
    return jsonify({
        "id": question.id,
        "text": question.text,
        "options": question.options,
        "subject": question.subject,
        "exam_type": question.exam_type,
        "difficulty": question.difficulty
    }), 200

from datetime import datetime # Importar aqui para evitar importação circular com models.py

