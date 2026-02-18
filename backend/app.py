"""
Kick Lab AI Backend API - Production Ready
Complete user management, payments, predictions, and analytics
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
import stripe
import os
from datetime import datetime, timedelta
import json
from functools import wraps
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'kicklab-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///kicklab.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
CORS(app)

# Stripe setup
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')

# ==================== DATABASE MODELS ====================

class User(UserMixin, db.Model):
    """User account model"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    
    # Subscription
    subscription_tier = db.Column(db.String(20), default='free')  # free, pro, vip
    subscription_active = db.Column(db.Boolean, default=False)
    subscription_end = db.Column(db.DateTime)
    stripe_customer_id = db.Column(db.String(255))
    stripe_subscription_id = db.Column(db.String(255))
    
    # Preferences
    notification_email = db.Column(db.Boolean, default=True)
    notification_sms = db.Column(db.Boolean, default=False)
    notification_telegram = db.Column(db.Boolean, default=False)
    phone_number = db.Column(db.String(20))
    telegram_id = db.Column(db.String(50))
    preferred_leagues = db.Column(db.String(255), default='EPL')  # Comma-separated
    
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    total_roi_percent = db.Column(db.Float, default=0.0)
    total_profit = db.Column(db.Float, default=0.0)
    win_count = db.Column(db.Integer, default=0)
    loss_count = db.Column(db.Integer, default=0)
    
    # Relationships
    bets = db.relationship('UserBet', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'subscription_tier': self.subscription_tier,
            'subscription_active': self.subscription_active,
            'total_roi_percent': round(self.total_roi_percent, 2),
            'total_profit': round(self.total_profit, 2),
            'win_count': self.win_count,
            'loss_count': self.loss_count,
            'win_rate': round(self.win_count / max(self.win_count + self.loss_count, 1) * 100, 1),
            'created_at': self.created_at.isoformat(),
        }


class Prediction(db.Model):
    """Daily predictions from the ML model"""
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(50), nullable=False, index=True)
    date = db.Column(db.DateTime, nullable=False, index=True)
    home_team = db.Column(db.String(80), nullable=False)
    away_team = db.Column(db.String(80), nullable=False)
    league = db.Column(db.String(20), nullable=False)  # EPL, LaLiga, Serie A, etc
    
    # Prediction details
    predicted_winner = db.Column(db.String(20))  # Home, Away, Draw
    confidence = db.Column(db.Float)  # 0-100
    expected_value = db.Column(db.Float)  # 2.5% to -2.5%
    home_win_prob = db.Column(db.Float)
    draw_prob = db.Column(db.Float)
    away_win_prob = db.Column(db.Float)
    
    # Betting odds
    home_odds = db.Column(db.Float)
    draw_odds = db.Column(db.Float)
    away_odds = db.Column(db.Float)
    
    # Injury/team info
    home_injuries = db.Column(db.String(500))
    away_injuries = db.Column(db.String(500))
    travel_distance_miles = db.Column(db.Float)
    
    # Result
    actual_result = db.Column(db.String(20))  # Home, Away, Draw, Pending
    result_timestamp = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_bets = db.relationship('UserBet', backref='prediction', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'match_id': self.match_id,
            'date': self.date.isoformat(),
            'home_team': self.home_team,
            'away_team': self.away_team,
            'league': self.league,
            'predicted_winner': self.predicted_winner,
            'confidence': round(self.confidence, 1) if self.confidence else None,
            'expected_value': round(self.expected_value, 2) if self.expected_value else None,
            'home_win_prob': round(self.home_win_prob, 3) if self.home_win_prob else None,
            'draw_prob': round(self.draw_prob, 3) if self.draw_prob else None,
            'away_win_prob': round(self.away_win_prob, 3) if self.away_win_prob else None,
            'home_odds': round(self.home_odds, 2) if self.home_odds else None,
            'draw_odds': round(self.draw_odds, 2) if self.draw_odds else None,
            'away_odds': round(self.away_odds, 2) if self.away_odds else None,
            'home_injuries': self.home_injuries,
            'away_injuries': self.away_injuries,
            'travel_distance_miles': self.travel_distance_miles,
            'actual_result': self.actual_result,
            'is_correct': self.actual_result == self.predicted_winner if self.actual_result != 'Pending' else None,
        }


class UserBet(db.Model):
    """User bets on predictions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey('prediction.id'), nullable=False, index=True)
    
    # Bet details
    bet_type = db.Column(db.String(20), nullable=False)  # MoneyLine, Spread, Over/Under
    bet_amount = db.Column(db.Float, nullable=False)
    odds_at_bet = db.Column(db.Float, nullable=False)
    potential_profit = db.Column(db.Float)
    
    # Result
    status = db.Column(db.String(20), default='pending')  # pending, won, lost, cancelled
    actual_profit = db.Column(db.Float)
    roi_percent = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'prediction_id': self.prediction_id,
            'bet_type': self.bet_type,
            'bet_amount': round(self.bet_amount, 2),
            'odds_at_bet': round(self.odds_at_bet, 2),
            'potential_profit': round(self.potential_profit, 2) if self.potential_profit else None,
            'status': self.status,
            'actual_profit': round(self.actual_profit, 2) if self.actual_profit else None,
            'roi_percent': round(self.roi_percent, 2) if self.roi_percent else None,
            'created_at': self.created_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
        }


class SubscriptionPlan(db.Model):
    """Subscription tiers"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # free, pro, vip
    price_eur = db.Column(db.Float, nullable=False)
    daily_picks = db.Column(db.Integer)  # max picks per day
    leagues = db.Column(db.String(255))  # allowed leagues
    features = db.Column(db.String(1000))  # JSON array of features
    stripe_price_id = db.Column(db.String(255))


# ==================== AUTHENTICATION ROUTES ====================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.json
    
    if not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400
    
    user = User(
        email=data['email'],
        username=data['username'],
        full_name=data.get('full_name', ''),
        subscription_tier='free'
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    login_user(user)
    
    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict()
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    login_user(user)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    logout_user()
    return jsonify({'message': 'Logged out'}), 200


@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user info"""
    return jsonify(current_user.to_dict()), 200


# ==================== PREDICTIONS ROUTES ====================

@app.route('/api/predictions/today', methods=['GET'])
def get_today_predictions():
    """Get today's predictions"""
    league = request.args.get('league', 'EPL')
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    
    predictions = Prediction.query.filter(
        Prediction.league == league,
        Prediction.date >= today,
        Prediction.date < tomorrow
    ).all()
    
    return jsonify([p.to_dict() for p in predictions]), 200


@app.route('/api/predictions/upcoming', methods=['GET'])
def get_upcoming_predictions():
    """Get upcoming predictions (next 7 days)"""
    league = request.args.get('league', 'EPL')
    limit = request.args.get('limit', 10, type=int)
    
    today = datetime.utcnow().date()
    future = today + timedelta(days=7)
    
    predictions = Prediction.query.filter(
        Prediction.league == league,
        Prediction.date >= today,
        Prediction.date < future,
        Prediction.actual_result == 'Pending'
    ).order_by(Prediction.date).limit(limit).all()
    
    return jsonify([p.to_dict() for p in predictions]), 200


@app.route('/api/predictions/history', methods=['GET'])
def get_prediction_history():
    """Get historical predictions with results"""
    league = request.args.get('league', 'EPL')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    predictions = Prediction.query.filter(
        Prediction.league == league,
        Prediction.actual_result != 'Pending'
    ).order_by(Prediction.date.desc()).limit(limit).offset(offset).all()
    
    total = Prediction.query.filter(
        Prediction.league == league,
        Prediction.actual_result != 'Pending'
    ).count()
    
    return jsonify({
        'predictions': [p.to_dict() for p in predictions],
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200


@app.route('/api/predictions/stats', methods=['GET'])
def get_prediction_stats():
    """Get aggregate prediction stats"""
    league = request.args.get('league', 'EPL')
    
    all_predictions = Prediction.query.filter(
        Prediction.league == league,
        Prediction.actual_result != 'Pending'
    ).all()
    
    total = len(all_predictions)
    correct = sum(1 for p in all_predictions if p.actual_result == p.predicted_winner)
    accuracy = (correct / total * 100) if total > 0 else 0
    
    return jsonify({
        'league': league,
        'total_predictions': total,
        'correct': correct,
        'accuracy_percent': round(accuracy, 1),
        'win_count': correct,
        'loss_count': total - correct
    }), 200


# ==================== PUBLIC API ENDPOINTS (NO AUTH) ====================

@app.route('/api/predictions/latest', methods=['GET'])
def get_latest_predictions():
    """Get latest predictions across all leagues (PUBLIC - for dashboard)"""
    limit = request.args.get('limit', 10, type=int)
    league = request.args.get('league')  # Optional filter
    
    query = Prediction.query.order_by(Prediction.date.desc())
    
    if league:
        query = query.filter(Prediction.league == league)
    
    predictions = query.limit(limit).all()
    
    return jsonify({
        'predictions': [p.to_dict() for p in predictions],
        'count': len(predictions),
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/api/stats', methods=['GET'])
def get_global_stats():
    """Get overall platform statistics (PUBLIC - for dashboard)"""
    
    # Get all completed predictions
    all_predictions = Prediction.query.filter(
        Prediction.actual_result != 'Pending'
    ).all()
    
    total = len(all_predictions)
    correct = sum(1 for p in all_predictions if p.actual_result == p.predicted_winner)
    accuracy = (correct / total * 100) if total > 0 else 0
    
    # Calculate by league
    leagues_stats = {}
    for league in ['EPL', 'LaLiga', 'SerieA']:
        league_preds = [p for p in all_predictions if p.league == league]
        league_correct = sum(1 for p in league_preds if p.actual_result == p.predicted_winner)
        league_total = len(league_preds)
        
        leagues_stats[league] = {
            'total': league_total,
            'correct': league_correct,
            'accuracy': round((league_correct / league_total * 100), 1) if league_total > 0 else 0
        }
    
    # Calculate total profit (simulated)
    total_profit = sum(
        (p.expected_value / 100) * 100  # Simulate $100 bets
        for p in all_predictions
        if p.actual_result == p.predicted_winner
    )
    
    # Get recent predictions (last 10)
    recent = Prediction.query.order_by(Prediction.date.desc()).limit(10).all()
    
    return jsonify({
        'overall': {
            'total_predictions': total,
            'correct': correct,
            'wrong': total - correct,
            'accuracy_percent': round(accuracy, 1),
            'win_rate': round(accuracy, 1),
            'total_profit_simulated': round(total_profit, 2),
            'roi_percent': round((total_profit / (total * 100)) * 100, 2) if total > 0 else 0
        },
        'by_league': leagues_stats,
        'recent_predictions': [p.to_dict() for p in recent],
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# ==================== USER BETS ROUTES ====================

@app.route('/api/bets/place', methods=['POST'])
@login_required
def place_bet():
    """Place a bet on a prediction"""
    data = request.json
    prediction = Prediction.query.get(data['prediction_id'])
    
    if not prediction:
        return jsonify({'error': 'Prediction not found'}), 404
    
    if prediction.actual_result != 'Pending':
        return jsonify({'error': 'This match already finished'}), 400
    
    potential_profit = data['bet_amount'] * (data['odds_at_bet'] - 1)
    
    bet = UserBet(
        user_id=current_user.id,
        prediction_id=data['prediction_id'],
        bet_type=data.get('bet_type', 'MoneyLine'),
        bet_amount=data['bet_amount'],
        odds_at_bet=data['odds_at_bet'],
        potential_profit=potential_profit,
        status='pending'
    )
    
    db.session.add(bet)
    db.session.commit()
    
    return jsonify({
        'message': 'Bet placed',
        'bet': bet.to_dict()
    }), 201


@app.route('/api/bets/my-bets', methods=['GET'])
@login_required
def get_user_bets():
    """Get current user's bets"""
    status = request.args.get('status', 'pending')
    limit = request.args.get('limit', 50, type=int)
    
    bets = UserBet.query.filter_by(
        user_id=current_user.id,
        status=status
    ).order_by(UserBet.created_at.desc()).limit(limit).all()
    
    return jsonify([b.to_dict() for b in bets]), 200


@app.route('/api/bets/stats', methods=['GET'])
@login_required
def get_user_bet_stats():
    """Get user's betting statistics"""
    bets = UserBet.query.filter_by(user_id=current_user.id).all()
    
    won = [b for b in bets if b.status == 'won']
    lost = [b for b in bets if b.status == 'lost']
    
    total_wagered = sum(b.bet_amount for b in bets)
    total_won = sum(b.actual_profit or 0 for b in won)
    
    return jsonify({
        'total_bets': len(bets),
        'won': len(won),
        'lost': len(lost),
        'win_rate_percent': round(len(won) / max(len(bets), 1) * 100, 1),
        'total_wagered': round(total_wagered, 2),
        'total_profit': round(total_won, 2),
        'roi_percent': round(total_won / max(total_wagered, 1) * 100, 2)
    }), 200


# ==================== PAYMENT ROUTES ====================

@app.route('/api/payments/subscribe', methods=['POST'])
@login_required
def create_subscription():
    """Create Stripe subscription"""
    data = request.json
    tier = data['tier']  # pro, vip
    
    # Get or create Stripe customer
    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.full_name
        )
        current_user.stripe_customer_id = customer.id
        db.session.commit()
    
    # Create subscription
    try:
        subscription = stripe.Subscription.create(
            customer=current_user.stripe_customer_id,
            items=[
                {
                    'price': get_stripe_price_id(tier),
                }
            ],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )
        
        current_user.subscription_tier = tier
        current_user.stripe_subscription_id = subscription.id
        db.session.commit()
        
        return jsonify({
            'subscription_id': subscription.id,
            'client_secret': subscription.latest_invoice.payment_intent.client_secret
        }), 201
    except stripe.error.CardError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/payments/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET', '')
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    
    if event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        user = User.query.filter_by(stripe_subscription_id=subscription['id']).first()
        if user:
            user.subscription_active = subscription['status'] == 'active'
            db.session.commit()
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        user = User.query.filter_by(stripe_subscription_id=subscription['id']).first()
        if user:
            user.subscription_active = False
            user.subscription_tier = 'free'
            db.session.commit()
    
    return jsonify({'received': True}), 200


def get_stripe_price_id(tier):
    """Get Stripe price ID for tier"""
    prices = {
        'pro': os.getenv('STRIPE_PRICE_PRO', ''),
        'vip': os.getenv('STRIPE_PRICE_VIP', '')
    }
    return prices.get(tier, '')


# ==================== LEADERBOARD ROUTES ====================

@app.route('/api/leaderboard/top-users', methods=['GET'])
def get_leaderboard():
    """Get top users by ROI"""
    limit = request.args.get('limit', 20, type=int)
    
    users = User.query.filter(
        User.subscription_active == True
    ).order_by(User.total_roi_percent.desc()).limit(limit).all()
    
    return jsonify([{
        'rank': i+1,
        'username': u.username,
        'total_roi_percent': round(u.total_roi_percent, 2),
        'total_profit': round(u.total_profit, 2),
        'win_count': u.win_count,
        'win_rate': round(u.win_count / max(u.win_count + u.loss_count, 1) * 100, 1)
    } for i, u in enumerate(users)]), 200


# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    """Get all users (admin only)"""
    if not is_admin(current_user):
        return jsonify({'error': 'Unauthorized'}), 401
    
    limit = request.args.get('limit', 100, type=int)
    users = User.query.limit(limit).all()
    return jsonify([u.to_dict() for u in users]), 200


@app.route('/api/admin/add-prediction', methods=['POST'])
def admin_add_prediction():
    """Add prediction manually (admin)"""
    if not is_admin(current_user):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    pred = Prediction(**data)
    db.session.add(pred)
    db.session.commit()
    
    return jsonify(pred.to_dict()), 201


def is_admin(user):
    """Check if user is admin"""
    return user and user.email in ['miltos@kicklabai.com', 'admin@kicklabai.com']


# ==================== ERROR HANDLING ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    return jsonify({'error': 'Server error'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=os.getenv('FLASK_ENV') == 'development', port=5555)
