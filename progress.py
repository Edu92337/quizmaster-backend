from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .app import db
from .models import UserProgress
from datetime import datetime

progress_bp = Blueprint("progress", __name__, url_prefix="/progress")

@progress_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_progress(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id:
        return jsonify({"msg": "Acesso não autorizado"}), 403

    # Buscar progresso dos últimos 365 dias para o calendário
    one_year_ago = datetime.utcnow() - timedelta(days=365)
    progress_data = UserProgress.query.filter(
        UserProgress.user_id == user_id,
        UserProgress.date >= one_year_ago.date()
    ).order_by(UserProgress.date.asc()).all()

    result = []
    for entry in progress_data:
        result.append({
            "date": entry.date.isoformat(),
            "questions_answered": entry.questions_answered,
            "correct_answers": entry.correct_answers,
            "score_percentage": (entry.correct_answers / entry.questions_answered * 100) if entry.questions_answered > 0 else 0
        })
    return jsonify(result), 200

from datetime import timedelta

