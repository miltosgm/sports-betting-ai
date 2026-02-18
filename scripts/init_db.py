#!/usr/bin/env python3
"""
Kick Lab AI - Database Initialization Script
Creates tables and seeds with historical predictions
"""

import sys
import os

# Add parent directory to path so we can import backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app, db, User, Prediction, SubscriptionPlan
from datetime import datetime, timedelta
import random

def init_database():
    """Initialize database with tables and seed data"""
    
    print("🗄️  Initializing Kick Lab AI Database...")
    print()
    
    with app.app_context():
        # Drop all tables if they exist (fresh start)
        print("🔄 Dropping existing tables...")
        db.drop_all()
        
        # Create all tables
        print("📊 Creating database tables...")
        db.create_all()
        print("✅ Tables created: User, Prediction, UserBet, SubscriptionPlan")
        print()
        
        # Create demo admin user
        print("👤 Creating demo admin user...")
        admin = User(
            email='admin@kicklabai.com',
            username='admin',
            full_name='Admin User',
            subscription_tier='vip',
            subscription_active=True,
            subscription_end=datetime.utcnow() + timedelta(days=365),
            notification_email=True,
            total_roi_percent=0.0,
            total_profit=0.0,
            win_count=0,
            loss_count=0
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("✅ Admin user created:")
        print("   📧 Email: admin@kicklabai.com")
        print("   🔑 Password: admin123")
        print()
        
        # Create subscription plans
        print("💳 Creating subscription plans...")
        plans = [
            SubscriptionPlan(
                name='free',
                price_eur=0,
                daily_picks=3,
                leagues='EPL',
                features='["Basic picks", "EPL only", "Email updates"]'
            ),
            SubscriptionPlan(
                name='pro',
                price_eur=39,
                daily_picks=10,
                leagues='EPL,LaLiga,SerieA',
                features='["All picks", "3 leagues", "SMS alerts", "Telegram bot"]'
            ),
            SubscriptionPlan(
                name='vip',
                price_eur=99,
                daily_picks=999,
                leagues='ALL',
                features='["Unlimited picks", "All leagues", "Priority support", "Custom alerts", "API access"]'
            )
        ]
        for plan in plans:
            db.session.add(plan)
        print("✅ 3 subscription plans created (free, pro, vip)")
        print()
        
        # Seed historical predictions (Dec 2025 - Feb 2026)
        print("🎯 Seeding 47 historical predictions...")
        
        teams = {
            'EPL': [
                ('Arsenal', 'Man City'), ('Liverpool', 'Chelsea'),
                ('Tottenham', 'Man United'), ('Newcastle', 'Brighton'),
                ('Aston Villa', 'West Ham'), ('Everton', 'Fulham'),
                ('Brentford', 'Crystal Palace'), ('Wolves', 'Bournemouth'),
                ('Nottm Forest', 'Luton'), ('Burnley', 'Sheffield Utd')
            ],
            'LaLiga': [
                ('Real Madrid', 'Barcelona'), ('Atletico', 'Sevilla'),
                ('Real Sociedad', 'Valencia'), ('Villarreal', 'Athletic Bilbao'),
                ('Betis', 'Girona'), ('Osasuna', 'Rayo Vallecano')
            ],
            'SerieA': [
                ('Inter', 'Juventus'), ('AC Milan', 'Napoli'),
                ('Roma', 'Lazio'), ('Atalanta', 'Fiorentina'),
                ('Bologna', 'Torino')
            ]
        }
        
        predictions = []
        start_date = datetime(2024, 12, 1)  # Dec 2024
        
        # Generate 47 predictions over ~10 weeks
        for i in range(47):
            # Distribute across leagues
            if i < 25:
                league = 'EPL'
            elif i < 37:
                league = 'LaLiga'
            else:
                league = 'SerieA'
            
            # Pick random match
            home, away = random.choice(teams[league])
            
            # Generate realistic odds and probabilities
            home_prob = random.uniform(0.25, 0.60)
            draw_prob = random.uniform(0.20, 0.35)
            away_prob = 1.0 - home_prob - draw_prob
            
            # Determine prediction
            probs = {'Home': home_prob, 'Draw': draw_prob, 'Away': away_prob}
            predicted = max(probs, key=probs.get)
            confidence = probs[predicted] * 100
            
            # Generate odds (inverse of probability + bookmaker margin)
            home_odds = round(1.0 / home_prob * 1.05, 2)
            draw_odds = round(1.0 / draw_prob * 1.05, 2)
            away_odds = round(1.0 / away_prob * 1.05, 2)
            
            # Expected value calculation
            if predicted == 'Home':
                ev = (home_odds * home_prob - 1) * 100
            elif predicted == 'Away':
                ev = (away_odds * away_prob - 1) * 100
            else:
                ev = (draw_odds * draw_prob - 1) * 100
            
            # Simulate results for past predictions (85% accuracy)
            actual = predicted if random.random() < 0.85 else random.choice(['Home', 'Draw', 'Away'])
            
            pred = Prediction(
                match_id=f'{league}_{i}_{start_date.strftime("%Y%m%d")}',
                date=start_date + timedelta(days=i * 2),  # Every 2 days
                home_team=home,
                away_team=away,
                league=league,
                predicted_winner=predicted,
                confidence=round(confidence, 1),
                expected_value=round(ev, 2),
                home_win_prob=round(home_prob, 3),
                draw_prob=round(draw_prob, 3),
                away_win_prob=round(away_prob, 3),
                home_odds=home_odds,
                draw_odds=draw_odds,
                away_odds=away_odds,
                home_injuries=random.choice(['None', '1 player out', '2 players doubtful']),
                away_injuries=random.choice(['None', '1 player out', 'Key striker injured']),
                travel_distance_miles=random.randint(50, 500),
                actual_result=actual,
                result_timestamp=start_date + timedelta(days=i * 2, hours=2)
            )
            predictions.append(pred)
            db.session.add(pred)
        
        print(f"✅ Added {len(predictions)} predictions")
        print()
        
        # Commit all changes
        print("💾 Committing to database...")
        db.session.commit()
        
        # Calculate and display stats
        correct = sum(1 for p in predictions if p.actual_result == p.predicted_winner)
        total = len(predictions)
        accuracy = correct / total * 100
        
        avg_confidence = sum(p.confidence for p in predictions) / total
        avg_ev = sum(p.expected_value for p in predictions) / total
        
        print()
        print("=" * 50)
        print("✅ DATABASE INITIALIZATION COMPLETE!")
        print("=" * 50)
        print()
        print("📊 STATISTICS:")
        print(f"   Total Predictions: {total}")
        print(f"   Correct: {correct}")
        print(f"   Wrong: {total - correct}")
        print(f"   Accuracy: {accuracy:.1f}%")
        print(f"   Avg Confidence: {avg_confidence:.1f}%")
        print(f"   Avg Expected Value: {avg_ev:+.2f}%")
        print()
        print("🔐 ADMIN LOGIN:")
        print("   Email: admin@kicklabai.com")
        print("   Password: admin123")
        print()
        print("🚀 Ready to start the backend with: ./start.sh")
        print()

if __name__ == '__main__':
    init_database()
