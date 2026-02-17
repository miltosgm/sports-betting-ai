"""
Telegram bot for sending daily predictions and updates
"""

import os
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', '')
ADMIN_IDS = [int(id.strip()) for id in os.getenv('TELEGRAM_ADMIN_IDS', '').split(',') if id.strip()]


class BetEdgeTelegramBot:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_TOKEN)
        self.app = Application.builder().token(TELEGRAM_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command handlers"""
        self.app.add_handler(CommandHandler('start', self.start_command))
        self.app.add_handler(CommandHandler('today', self.today_picks_command))
        self.app.add_handler(CommandHandler('tomorrow', self.tomorrow_picks_command))
        self.app.add_handler(CommandHandler('stats', self.stats_command))
        self.app.add_handler(CommandHandler('subscribe', self.subscribe_command))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        keyboard = [
            [InlineKeyboardButton("📊 Today's Picks", callback_data='today')],
            [InlineKeyboardButton("📈 Stats", callback_data='stats')],
            [InlineKeyboardButton("💰 Subscribe", callback_data='subscribe')],
            [InlineKeyboardButton("🌐 Dashboard", url='https://betedge.com')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            '🎯 Welcome to BetEdge AI!\n\n'
            'Your AI-powered football betting predictions using ensemble ML.\n\n'
            'Choose an option below:',
            reply_markup=reply_markup
        )
    
    async def today_picks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send today's picks"""
        await self.send_daily_picks(update.message.chat_id)
    
    async def tomorrow_picks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send tomorrow's picks"""
        await self.send_daily_picks(update.message.chat_id, days_ahead=1)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send current stats"""
        from backend.app import Prediction
        
        predictions = Prediction.query.filter(
            Prediction.actual_result != 'Pending'
        ).all()
        
        total = len(predictions)
        correct = sum(1 for p in predictions if p.actual_result == p.predicted_winner)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        message = (
            f'📊 BetEdge Stats\n\n'
            f'Total Predictions: {total}\n'
            f'Correct: {correct}\n'
            f'Accuracy: {accuracy:.1f}%\n'
            f'Win Rate: {(correct/total*100):.1f}%'
        )
        
        await update.message.reply_text(message)
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle subscription"""
        keyboard = [
            [InlineKeyboardButton("Pro - €39/month", callback_data='subscribe_pro')],
            [InlineKeyboardButton("VIP - €99/month", callback_data='subscribe_vip')],
            [InlineKeyboardButton("Cancel", callback_data='cancel')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            '💰 Choose your subscription:\n\n'
            '✨ Pro: Daily picks, Email notifications, Dashboard access\n'
            '👑 VIP: Unlimited picks, All notifications, Advanced analytics',
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'today':
            await self.send_daily_picks(query.message.chat_id)
        elif query.data == 'stats':
            await self.stats_command(update, context)
        elif query.data in ['subscribe_pro', 'subscribe_vip']:
            tier = 'pro' if query.data == 'subscribe_pro' else 'vip'
            await query.edit_message_text(
                f'To upgrade to {tier.upper()}, please visit:\n'
                f'https://betedge.com/upgrade?tier={tier}'
            )
        elif query.data == 'cancel':
            await query.edit_message_text('Cancelled.')
    
    async def send_daily_picks(self, chat_id, days_ahead=0):
        """Send daily predictions to Telegram"""
        from backend.app import Prediction, db
        from datetime import datetime, timedelta
        
        target_date = datetime.utcnow().date() + timedelta(days=days_ahead)
        tomorrow = target_date + timedelta(days=1)
        
        predictions = Prediction.query.filter(
            Prediction.date >= target_date,
            Prediction.date < tomorrow,
            Prediction.actual_result == 'Pending'
        ).order_by(Prediction.date).all()
        
        if not predictions:
            await self.bot.send_message(
                chat_id=chat_id,
                text=f'No predictions available for {target_date.strftime("%b %d")}'
            )
            return
        
        date_str = target_date.strftime('%A, %b %d')
        message = f'🎯 BetEdge Picks - {date_str}\n\n'
        
        for i, pred in enumerate(predictions, 1):
            confidence_emoji = '🔥' if pred.confidence > 75 else '⚡' if pred.confidence > 60 else '💡'
            message += (
                f'{confidence_emoji} #{i} {pred.home_team} vs {pred.away_team}\n'
                f'   📍 Prediction: {pred.predicted_winner}\n'
                f'   💯 Confidence: {pred.confidence:.0f}%\n'
                f'   📊 EV: {pred.expected_value:+.2f}%\n'
                f'   💰 Odds: {pred.home_odds if pred.predicted_winner == "Home" else pred.away_odds}\n\n'
            )
        
        # Add keyboard with actions
        keyboard = [
            [InlineKeyboardButton("🌐 View Dashboard", url='https://betedge.com')],
            [InlineKeyboardButton("📱 Place Bets", url='https://betedge.com/bets')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self.bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def send_notification(self, user_telegram_id, message_text):
        """Send direct message to user"""
        try:
            await self.bot.send_message(
                chat_id=user_telegram_id,
                text=message_text,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f'Failed to send Telegram notification: {e}')
    
    async def send_channel_announcement(self, message_text):
        """Announce to public channel"""
        try:
            await self.bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=message_text,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f'Failed to send channel announcement: {e}')
    
    async def start(self):
        """Start the bot"""
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
    
    async def stop(self):
        """Stop the bot"""
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()


# Global bot instance
telegram_bot = None


def init_telegram_bot():
    """Initialize Telegram bot"""
    global telegram_bot
    if TELEGRAM_TOKEN and not telegram_bot:
        telegram_bot = BetEdgeTelegramBot()
        asyncio.create_task(telegram_bot.start())


def send_daily_picks_telegram(predictions, league='EPL'):
    """Send picks to Telegram channel/users"""
    if not telegram_bot:
        return
    
    message = f'🎯 {league} Daily Picks - {datetime.now().strftime("%b %d")}\n\n'
    
    for pred in predictions[:5]:  # Limit to 5 for Telegram
        message += (
            f'⚽ {pred["home_team"]} vs {pred["away_team"]}\n'
            f'  → {pred["predicted_winner"]} ({pred["confidence"]:.0f}%)\n'
            f'  → EV: {pred["expected_value"]:+.2f}%\n\n'
        )
    
    asyncio.create_task(telegram_bot.send_channel_announcement(message))
