from flask import Blueprint, jsonify, request
from app import db, mail
from app.models import User, Product, Card, Account, Purchase, PurchaseStatus
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Message,Mail
from datetime import datetime
import requests
from apscheduler.schedulers.background import BackgroundScheduler

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return jsonify(message="API is working.")


@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    print(email)
    print(password)

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    user = User.query.filter_by(email=email).first()

    # Use hashed password comparison
    #if not user or user.password != password:
    #    return jsonify({'error': 'Invalid credentials'}), 401

    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Still returning JWT token if needed for frontend
    access_token = create_access_token(identity={
        'id': user.id,
        'email': user.email,
        'is_admin': user.is_admin
    })

    return jsonify({'access_token': access_token}), 200

@main.route('/users/<int:id>', methods=['GET'])
def get_user_by_id(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "address": user.address,
        "city": user.city,
        "state": user.state,
        "phone_number": user.phone_number,
        "is_admin": user.is_admin,
        "is_verified": user.is_verified
    })

@main.route('/update-account/<int:id>', methods=['PATCH'])
def update_user_account(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    # Update only provided fields
    if 'name' in data:
        user.name = data['name']
    if 'surname' in data:
        user.surname = data['surname']
    if 'address' in data:
        user.address = data['address']
    if 'city' in data:
        user.city = data['city']
    if 'state' in data:
        user.state = data['state']
    if 'phone_number' in data:
        user.phone_number = data['phone_number']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = generate_password_hash(data['password'])

    try:
        db.session.commit()
        return jsonify({"message": "User updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database update failed", "details": str(e)}), 500


@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email already registered'}), 400

    hashed_password = generate_password_hash(data['password'])

    user = User(
        name=data.get('name'),
        surname=data.get('surname'),
        address=data.get('address'),
        city=data.get('city'),
        state=data.get('state'),
        phone_number=data.get('phone_number'),
        email=data.get('email'),
        password=hashed_password,
        is_admin=data.get('is_admin', False),
        is_verified=False
    )

    db.session.add(user)
    db.session.commit()

    #slanje mejla
    # Slanje mejla u try-except bloku
    try:
        msg = Message(
            'New User Registered',
            recipients=['tatjanakosic14@gmail.com'],
            body=f'A new admin user has registered:\n\nName: {user.name} {user.surname}\nEmail: {user.email}'
        )
        mail.send(msg)  # Pokušaj slanja mejla
    except Exception as e:
        # Ako dođe do greške pri slanju mejla, vrati grešku sa opisom
        return jsonify({'error': 'Failed to send email', 'details': str(e)}), 500


    return jsonify({'message': 'User registered successfully!'}), 201

@main.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'product_name': p.product_name,
        'price': p.price,
        'quantity': p.quantity,
        'currency': p.currency
    } for p in products]), 200

@main.route('/create-product', methods=['POST'])
def add_product():
    data = request.get_json()
    new_product = Product(
        product_name=data.get('product_name'),
        price=data.get('price'),
        quantity=data.get('quantity'),
        currency=data.get('currency')
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product created successfully'}), 201

@main.route('/products/<int:product_id>/quantity', methods=['PATCH'])
def update_quantity(product_id):
    data = request.get_json()
    product = Product.query.get_or_404(product_id)
    product.quantity += data.get('quantity', 0)
    db.session.commit()
    return jsonify({'message': 'Quantity updated successfully'}), 200

@main.route('/add-newcard', methods=['POST'])
def add_card():
    data = request.get_json()

    if not all(k in data for k in ('cardNumber', 'expiry', 'cvv', 'user_id')):
        return jsonify({"error": "Missing required fields"}), 400

    new_card = Card(
        user_id=data['user_id'],
        number=data['cardNumber'],
        expiry=data['expiry'],
        cvv=data['cvv']
    )
    db.session.add(new_card)
    db.session.commit()

    return jsonify({"message": "Card added successfully."}), 201

@main.route('/get-user-card/<int:user_id>', methods=['GET'])
def get_user_card(user_id):
    card = Card.query.filter_by(user_id=user_id).first()
    if card:
        return jsonify({'card': {
            'number': card.number,
            'expiry': card.expiry,
            'cvv': card.cvv
        }}), 200
    return jsonify({'card': None}), 200

@main.route('/users-with-cards-unverified', methods=['GET'])
def get_unverified_users_with_cards():
    users = User.query.filter_by(is_verified=False).all()
    data = []

    for user in users:
        cards = Card.query.filter_by(user_id=user.id).all()
        if cards:
            data.append({
                'user_id': user.id,
                'user_email': user.email,
                'cards': [{
                    'card_id': card.id,
                    'card_number': card.number,
                    'expiry': card.expiry,
                    'cvv': card.cvv
                } for card in cards]
            })

    return jsonify(data), 200

@main.route('/verify-user/<int:user_id>', methods=['PUT'])
def verify_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.is_verified = True
    db.session.commit()
    return jsonify({'message': 'User verified successfully'}), 200

@main.route('/deposit-to-account', methods=['POST'])
def deposit():
    data = request.get_json()
    user_id = data.get('user_id')
    currency = data.get('currency')
    amount = data.get('amount')

    if not all([user_id, currency, amount]):
        return jsonify({'error': 'Missing fields'}), 400

    account = Account.query.filter_by(user_id=user_id, currency=currency).first()

    if not account:
        account = Account(user_id=user_id, currency=currency, balance=0.0)
        db.session.add(account)

    account.balance += float(amount)
    db.session.commit()

    return jsonify({
        'message': 'Deposit successful',
        'currency': currency,
        'new_balance': account.balance
    }), 200

@main.route('/get-user-accounts/<int:user_id>', methods=['GET'])
def get_user_accounts(user_id):
    accounts = Account.query.filter_by(user_id=user_id).all()

    account_list = [{
        'currency': acc.currency,
        'balance': acc.balance
    } for acc in accounts]

    return jsonify(account_list), 200


# dobavaljanje trenutne kursne liste

def get_exchange_rate(from_currency, to_currency):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    url = f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}"
    try:
        response = requests.get(url)
        data = response.json()
        print(f"Exchange rate API response: {data}")  # Debug

        rate = data.get('rates', {}).get(to_currency)
        if rate is None:
            print(f"Rate for {from_currency} to {to_currency} not found in response.")
            return None
        return rate
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None

    
@main.route('/convert', methods=['POST'])
def convert_currency():
    data = request.get_json()
    user_id = data.get('user_id')
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')
    amount = data.get('amount')

    if not all([user_id, from_currency, to_currency, amount]):
        return jsonify({'error': 'Missing fields'}), 400

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    print(from_currency)
    print(to_currency)

    if from_currency == to_currency:
        return jsonify({'error': 'Source and target currency must be different'}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid amount'}), 400

    rate = get_exchange_rate(from_currency, to_currency)
    if rate is None:
        return jsonify({'error': 'Exchange rate not available for this currency pair'}), 400

    from_account = Account.query.filter_by(user_id=user_id, currency=from_currency).first()
    to_account = Account.query.filter_by(user_id=user_id, currency=to_currency).first()

    if not from_account or from_account.balance < amount:
        return jsonify({'error': 'Insufficient funds or account not found'}), 400

    if not to_account:
        to_account = Account(user_id=user_id, currency=to_currency, balance=0.0)
        db.session.add(to_account)

    converted_amount = amount * rate

    from_account.balance -= amount
    to_account.balance += converted_amount

    db.session.commit()

    return jsonify({
        'message': 'Conversion successful',
        'from_currency': from_currency,
        'to_currency': to_currency,
        'converted_amount': round(converted_amount, 2),
        'new_balance_from_currency': from_account.balance,
        'new_balance_to_currency': to_account.balance
    }), 200

@main.route('/users/<int:id>/is_verified', methods=['GET'])
def check_user_verified(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "is_verified": user.is_verified
    })

@main.route('/purchase', methods=['POST'])
def create_purchase():
    data = request.get_json()
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    currency = data.get('currency')

    # Provera korisnika
    user = User.query.get(user_id)
    if not user or not user.is_verified:
        return jsonify({"error": "User not found or not verified"}), 400

    # Provera proizvoda i dostupnosti
    product = Product.query.get(product_id)
    if not product or product.quantity <= 0:
        return jsonify({"error": "Product not available"}), 400

    # Provera da li korisnik ima račun u traženoj valuti
    account = Account.query.filter_by(user_id=user_id, currency=currency).first()
    if not account:
        return jsonify({"error": f"No account with currency {currency}"}), 400

    # Konverzija cene ako je valuta različita
    final_price = product.price
    if product.currency != currency:
        rate = get_exchange_rate(product.currency, currency)
        if rate is None:
            return jsonify({"error": "Currency conversion failed"}), 500
        final_price *= rate
        final_price = round(final_price, 2)  # Zaokруживање на 2 децимале

    # Provera da li korisnik ima dovoljno sredstava
    if account.balance < final_price:
        return jsonify({"error": "Insufficient funds"}), 400

    # Kreiranje kupovine sa statusom PENDING
    purchase = Purchase(
        user_id=user_id,
        product_id=product_id,
        currency=currency,
        amount=final_price,
        status=PurchaseStatus.PENDING.value,
        created_at=datetime.utcnow()
    )
    db.session.add(purchase)
    db.session.commit()

    return jsonify({
        "message": f"Purchase created and pending. Final amount: {final_price} {currency}",
        "purchase_id": purchase.id
    }), 201

@main.route('/get-purchase-history/<int:user_id>', methods=['GET'])
def get_purchase_history(user_id):
    purchases = db.session.query(Purchase, Product)\
        .join(Product, Purchase.product_id == Product.id)\
        .filter(Purchase.user_id == user_id)\
        .all()

    result = []
    for purchase, product in purchases:
        result.append({
            'id': purchase.id,
            'product_id': purchase.product_id,
            'product_name': product.product_name,
            'currency': purchase.currency,
            'amount': purchase.amount,
            'status': purchase.status,
            'created_at': purchase.created_at.isoformat(),
            'processed_at': purchase.processed_at.isoformat() if purchase.processed_at else None
        })

    return jsonify(result)

@main.route('/get-all-purchase-history', methods=['GET'])
def get_all_purchase_history():
    purchases = db.session.query(
        Purchase.id,
        Purchase.amount,
        Purchase.currency,
        Purchase.status,
        Purchase.created_at,
        User.email.label('user_email'),
        User.name.label('user_name'),
        Product.product_name
    ).join(User, Purchase.user_id == User.id
    ).join(Product, Purchase.product_id == Product.id
    ).order_by(Purchase.created_at.desc()).all()

    history = [
        {
            'id': p.id,
            'user_email': p.user_email,
            'user_name': p.user_name,
            'product_name': p.product_name,
            'amount': p.amount,
            'currency': p.currency,
            'status': p.status,
            'created_at': p.created_at.isoformat()
        }
        for p in purchases
    ]

    #current_app.logger.info("Purchase history response: %s", json.dumps(history, indent=2))

    return jsonify(history), 200


def process_pending_purchases(app):
    with app.app_context():
        pending_purchases = Purchase.query.filter_by(status=PurchaseStatus.PENDING.value).all()
        if not pending_purchases:
            return

        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            print("No admin user found!")
            return

        admin_account = Account.query.filter_by(user_id=admin_user.id, currency='USD').first()
        if not admin_account:
            print("Admin account with USD not found!")
            return

        email_batches = []
        batch_messages = []

        for purchase in pending_purchases:
            user_account = Account.query.filter_by(user_id=purchase.user_id, currency=purchase.currency).first()
            product = Product.query.get(purchase.product_id)

            if user_account and product and product.quantity > 0 and user_account.balance >= purchase.amount:
                user_account.balance -= purchase.amount
                admin_account.balance += purchase.amount
                product.quantity -= 1
                purchase.status = PurchaseStatus.COMPLETED.value
                purchase.processed_at = datetime.utcnow()
                db.session.commit()

                batch_messages.append(
                    f"Purchase ID {purchase.id}: User {purchase.user_id} bought {product.product_name} for {purchase.amount} {purchase.currency}"
                )
            else:
                purchase.status = PurchaseStatus.FAILED.value
                purchase.processed_at = datetime.utcnow()
                db.session.commit()

            if len(batch_messages) == 5:
                email_batches.append('\n'.join(batch_messages))
                batch_messages = []

        if batch_messages:
            email_batches.append('\n'.join(batch_messages))

        for report in email_batches:
            msg = Message(subject="Purchase Report",
                          sender="noreply@yourdomain.com",
                          recipients=["tatjanakosic14@gmail.com"],
                          body=report)
            mail.send(msg)