"""
Email service for daily predictions and notifications
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content, Email
from datetime import datetime

sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY', ''))
FROM_EMAIL = os.getenv('FROM_EMAIL', 'predictions@kicklabai.com')


def send_daily_picks_email(user_email, user_name, predictions, league='EPL'):
    """Send daily predictions to user"""
    
    if not predictions:
        return
    
    # Build email HTML
    html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #2563eb, #9333ea); color: white; padding: 20px; border-radius: 8px; }}
                .prediction {{ border: 1px solid #e5e7eb; padding: 15px; margin: 10px 0; border-radius: 6px; }}
                .prediction.high {{ border-left: 4px solid #10b981; }}
                .prediction.medium {{ border-left: 4px solid #f59e0b; }}
                .prediction.low {{ border-left: 4px solid #ef4444; }}
                .match-title {{ font-weight: bold; font-size: 16px; margin: 10px 0; }}
                .stat {{ display: inline-block; margin-right: 20px; }}
                .cta {{ margin-top: 30px; text-align: center; }}
                .button {{ background: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; }}
                .footer {{ margin-top: 40px; text-align: center; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 {league} Daily Picks</h1>
                    <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
                </div>
    """
    
    for pred in predictions:
        confidence_level = 'high' if pred['confidence'] > 75 else 'medium' if pred['confidence'] > 60 else 'low'
        
        html_content += f"""
        <div class="prediction {confidence_level}">
            <div class="match-title">
                {pred['home_team']} vs {pred['away_team']}
            </div>
            <div class="stat">
                <strong>Prediction:</strong> {pred['predicted_winner']}
            </div>
            <div class="stat">
                <strong>Confidence:</strong> {pred['confidence']:.1f}%
            </div>
            <div class="stat">
                <strong>EV:</strong> {pred['expected_value']:+.2f}%
            </div>
            <div class="stat">
                <strong>Odds:</strong> {pred.get('home_odds', 'N/A')}
            </div>
        </div>
        """
    
    html_content += """
                <div class="cta">
                    <p>Log in to place bets and track your performance</p>
                    <a href="https://kicklabai.com/login" class="button">View Dashboard</a>
                </div>
                
                <div class="footer">
                    <p>Kick Lab AI Predictions | Powered by ML Ensemble</p>
                    <p>© 2026 Kick Lab AI. All rights reserved.</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=user_email,
        subject=f'🎯 {league} Daily Picks - {datetime.now().strftime("%b %d")}',
        html_content=html_content
    )
    
    try:
        response = sg.send(message)
        print(f'Email sent to {user_email}: {response.status_code}')
        return True
    except Exception as e:
        print(f'Error sending email to {user_email}: {e}')
        return False


def send_bet_notification(user_email, user_name, prediction, action='placed'):
    """Send notification when user places/wins/loses bet"""
    
    if action == 'placed':
        subject = f'✅ Bet Placed: {prediction["home_team"]} vs {prediction["away_team"]}'
        message_text = f'Your bet has been placed successfully.'
    elif action == 'won':
        subject = f'🎉 Winning Bet: {prediction["home_team"]} vs {prediction["away_team"]}'
        message_text = f'Your prediction came true! Congratulations!'
    elif action == 'lost':
        subject = f'❌ Losing Bet: {prediction["home_team"]} vs {prediction["away_team"]}'
        message_text = f'This match didn\'t go your way, but there\'s always the next one!'
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h2>{subject}</h2>
                <p>Hi {user_name},</p>
                <p>{message_text}</p>
                <p>
                    <strong>Match:</strong> {prediction['home_team']} vs {prediction['away_team']}<br>
                    <strong>Prediction:</strong> {prediction['predicted_winner']}<br>
                    <strong>Confidence:</strong> {prediction['confidence']:.1f}%
                </p>
                <a href="https://kicklabai.com/dashboard" style="background: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px;">View Dashboard</a>
            </div>
        </body>
    </html>
    """
    
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=user_email,
        subject=subject,
        html_content=html_content
    )
    
    try:
        response = sg.send(message)
        return True
    except Exception as e:
        print(f'Error sending notification: {e}')
        return False


def send_subscription_confirmation(user_email, user_name, tier):
    """Send subscription confirmation"""
    
    tiers = {
        'pro': {'price': '€39/month', 'features': ['Daily picks', 'Email notifications', 'Full dashboard']},
        'vip': {'price': '€99/month', 'features': ['Unlimited picks', 'All notifications', 'Advanced analytics', 'Priority support']}
    }
    
    tier_info = tiers.get(tier, {})
    features_html = ''.join([f'<li>{f}</li>' for f in tier_info.get('features', [])])
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h2>Welcome to Kick Lab AI {tier.upper()}</h2>
                <p>Hi {user_name},</p>
                <p>Thank you for subscribing to Kick Lab AI {tier.upper()} at {tier_info.get('price', 'N/A')}!</p>
                
                <h3>Your Plan Includes:</h3>
                <ul>
                    {features_html}
                </ul>
                
                <p>Your subscription is now active and you'll start receiving daily picks.</p>
                <a href="https://kicklabai.com/dashboard" style="background: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px;">Go to Dashboard</a>
            </div>
        </body>
    </html>
    """
    
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=user_email,
        subject='Welcome to Kick Lab AI - Subscription Confirmed',
        html_content=html_content
    )
    
    try:
        response = sg.send(message)
        return True
    except Exception as e:
        print(f'Error sending subscription confirmation: {e}')
        return False
