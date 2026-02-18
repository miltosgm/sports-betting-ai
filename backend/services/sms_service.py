"""
SMS notifications via Twilio
"""

import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE = os.getenv('TWILIO_PHONE_NUMBER', '')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_sms_notification(phone_number, message):
    """Send SMS notification"""
    if not TWILIO_ACCOUNT_SID:
        print('SMS service not configured')
        return False
    
    try:
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE,
            to=phone_number
        )
        print(f'SMS sent: {message.sid}')
        return True
    except Exception as e:
        print(f'Error sending SMS: {e}')
        return False


def send_daily_picks_sms(phone_number, predictions, league='EPL'):
    """Send daily picks via SMS"""
    
    # Format picks for SMS (limited characters)
    message = f'🎯 {league} Picks:\n'
    
    for pred in predictions[:3]:  # Max 3 for SMS
        message += (
            f'\n{pred["home_team"]} vs {pred["away_team"]}\n'
            f'→ {pred["predicted_winner"]} ({pred["confidence"]:.0f}%)'
        )
    
    message += '\n\nKickLabAI.com'
    
    return send_sms_notification(phone_number, message)


def send_bet_result_sms(phone_number, prediction, result):
    """Send bet result via SMS"""
    
    if result == 'won':
        message = f'✅ You Won!\n{prediction["home_team"]} vs {prediction["away_team"]}'
    else:
        message = f'❌ Close one!\n{prediction["home_team"]} vs {prediction["away_team"]}'
    
    return send_sms_notification(phone_number, message)


def send_urgent_alert_sms(phone_number, message):
    """Send urgent alert (injury, line movement, etc)"""
    
    sms_message = f'⚠️ Kick Lab AI Alert:\n{message}\n\nCheck dashboard for details'
    
    return send_sms_notification(phone_number, sms_message)
