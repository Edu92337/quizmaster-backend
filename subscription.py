from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .app import db
from .models import User, Subscription
import stripe
import os

subscription_bp = Blueprint("subscription", __name__, url_prefix="/subscription")

# Configurar Stripe (substituir com sua chave secreta em produção)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_YOUR_STRIPE_SECRET_KEY")

@subscription_bp.route("/create-checkout-session", methods=["POST"])
@jwt_required()
def create_checkout_session():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404

    try:
        # Criar um cliente Stripe se ainda não existir
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(email=user.email)
            user.stripe_customer_id = customer.id
            db.session.commit()
        else:
            customer = stripe.Customer.retrieve(user.stripe_customer_id)

        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "brl",
                        "product_data": {
                            "name": "Assinatura Mensal de Questões",
                        },
                        "unit_amount": 2990, # R$ 29,90
                        "recurring": {
                            "interval": "month",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=os.environ.get("FRONTEND_URL", "http://localhost:3000") + "/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=os.environ.get("FRONTEND_URL", "http://localhost:3000") + "/cancel",
        )
        return jsonify({"checkout_url": checkout_session.url})
    except Exception as e:
        return jsonify(error=str(e)), 403

@subscription_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_YOUR_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return str(e), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return str(e), 400

    # Lidar com os eventos do Stripe
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")

        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            user.is_subscribed = True
            # Criar ou atualizar a assinatura no BD
            subscription = Subscription.query.filter_by(user_id=user.id).first()
            if not subscription:
                subscription = Subscription(user_id=user.id, stripe_customer_id=customer_id, stripe_subscription_id=subscription_id, status="active")
                db.session.add(subscription)
            else:
                subscription.stripe_subscription_id = subscription_id
                subscription.status = "active"
            db.session.commit()
            print(f"Usuário {user.email} assinou com sucesso!")

    elif event["type"] == "customer.subscription.updated":
        subscription_data = event["data"]["object"]
        subscription_id = subscription_data.get("id")
        status = subscription_data.get("status")

        subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
        if subscription:
            subscription.status = status
            if status == "canceled" or status == "unpaid":
                user = User.query.get(subscription.user_id)
                if user: user.is_subscribed = False
            db.session.commit()
            print(f"Assinatura {subscription_id} atualizada para {status}")

    elif event["type"] == "customer.subscription.deleted":
        subscription_data = event["data"]["object"]
        subscription_id = subscription_data.get("id")

        subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
        if subscription:
            user = User.query.get(subscription.user_id)
            if user: user.is_subscribed = False
            db.session.delete(subscription)
            db.session.commit()
            print(f"Assinatura {subscription_id} deletada.")

    return jsonify({"status": "success"}), 200

