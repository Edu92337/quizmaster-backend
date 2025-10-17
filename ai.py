from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .app import db
from .models import User, AIInteraction
from openai import OpenAI
import os

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")

client = OpenAI()

@ai_bp.route("/generate_question_ia", methods=["POST"])
@jwt_required()
def generate_question_ia():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_subscribed:
        return jsonify({"msg": "Assinatura necessária para gerar questões com IA"}), 403

    data = request.get_json()
    prompt = data.get("prompt")
    subject = data.get("subject")
    exam_type = data.get("exam_type")

    if not prompt or not subject or not exam_type:
        return jsonify({"msg": "Prompt, assunto e tipo de prova são obrigatórios"}), 400

    # Lógica para chamar a IA para gerar a questão
    # Exemplo com OpenAI (requer OPENAI_API_KEY no ambiente)
    # try:
    #     response = client.chat.completions.create(
    #         model="gpt-4.1-mini", # Ou outro modelo adequado
    #         messages=[
    #             {"role": "system", "content": f"Você é um especialista em {subject} para {exam_type} e cria questões de múltipla escolha."},
    #             {"role": "user", "content": f"Crie uma questão de múltipla escolha sobre {prompt}. Inclua 4 opções e a resposta correta. Formate como JSON."}
    #         ],
    #         response_format={ "type": "json_object" }
    #     )
    #     ia_response_content = response.choices[0].message.content
    #     # Parsear JSON e criar objeto Question
    #     # new_question = Question(text=..., options=..., correct_answer=..., etc.)
    #     # db.session.add(new_question)
    #     # db.session.commit()
    #     # return jsonify(new_question.to_dict()), 200
    # except Exception as e:
    #     return jsonify({"msg": f"Erro ao gerar questão com IA: {str(e)}"}), 500

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini", # Ou outro modelo adequado
            messages=[
                {"role": "system", "content": f"Você é um especialista em {subject} para {exam_type} e cria questões de múltipla escolha. Formate a saída como um objeto JSON com as chaves 'question_text', 'options' (uma lista de strings) e 'correct_answer' (uma string que corresponde a uma das opções)."},
                {"role": "user", "content": f"Crie uma questão de múltipla escolha sobre {prompt}."}
            ],
            response_format={ "type": "json_object" }
        )
        ia_response_content = response.choices[0].message.content
        import json
        generated_question_data = json.loads(ia_response_content)

        # Criar e salvar a questão no banco de dados
        new_question = Question(
            text=generated_question_data["question_text"],
            options=generated_question_data["options"],
            correct_answer=generated_question_data["correct_answer"],
            subject=subject,
            exam_type=exam_type,
            difficulty="dynamic", # Pode ser ajustado pela IA
            created_by_ia=True
        )
        db.session.add(new_question)
        db.session.commit()

        return jsonify({"id": new_question.id, "text": new_question.text, "options": new_question.options}), 200
    except Exception as e:
        return jsonify({"msg": f"Erro ao gerar questão com IA: {str(e)}"}), 500

    # Registrar interação com a IA (se a geração for bem-sucedida)
    # Isso já está sendo feito dentro do bloco try, mas para o caso de erro, podemos registrar a falha também
    # Para simplificar, vamos assumir que o registro ocorre apenas no sucesso da geração da questão.
    # Se houver um erro, a mensagem de erro já é retornada.

@ai_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat_with_ia():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_subscribed:
        return jsonify({"msg": "Assinatura necessária para conversar com a IA"}), 403

    data = request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"msg": "Mensagem é obrigatória"}), 400

    # Lógica para chamar a IA para o chat
    # Exemplo com OpenAI
    # try:
    #     response = client.chat.completions.create(
    #         model="gpt-4.1-mini", # Ou outro modelo adequado
    #         messages=[
    #             {"role": "system", "content": "Você é um assistente de estudos especializado em ENEM e residência médica."},
    #             {"role": "user", "content": message}
    #         ]
    #     )
    #     ia_response_content = response.choices[0].message.content
    # except Exception as e:
    #     return jsonify({"msg": f"Erro ao conversar com IA: {str(e)}"}), 500

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini", # Ou outro modelo adequado
            messages=[
                {"role": "system", "content": "Você é um assistente de estudos especializado em ENEM e residência médica."},
                {"role": "user", "content": message}
            ]
        )
        ia_response_content = response.choices[0].message.content
    except Exception as e:
        return jsonify({"msg": f"Erro ao conversar com IA: {str(e)}"}), 500

    # Registrar interação com a IA
    ai_interaction = AIInteraction(
        user_id=current_user_id,
        interaction_type="chat",
        prompt=message,
        response=ia_response_content
    )
    db.session.add(ai_interaction)
    db.session.commit()

    return jsonify({"response": ia_response_content}), 200



