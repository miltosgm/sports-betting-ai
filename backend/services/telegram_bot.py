"""
Kick Lab AI - Production Telegram Bot
⚡ Premium sports betting AI predictions via Telegram
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
import asyncio

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError, RetryAfter
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', '')
TELEGRAM_ADMIN_IDS = [int(id.strip()) for id in os.getenv('TELEGRAM_ADMIN_IDS', '').split(',') if id.strip()]

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PREDICTIONS_DIR = BASE_DIR / 'data' / 'predictions'
RESULTS_DIR = BASE_DIR / 'data' / 'results'


class KickLabTelegramBot:
    """Production Telegram bot for Kick Lab AI"""
    
    def __init__(self):
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
        logger.info("✅ Kick Lab AI Telegram Bot initialized")
    
    def _setup_handlers(self):
        """Register all command handlers"""
        self.app.add_handler(CommandHandler('start', self.start_command))
        self.app.add_handler(CommandHandler('today', self.today_command))
        self.app.add_handler(CommandHandler('tomorrow', self.tomorrow_command))
        self.app.add_handler(CommandHandler('acca', self.acca_command))
        self.app.add_handler(CommandHandler('stats', self.stats_command))
        self.app.add_handler(CommandHandler('value', self.value_command))
        self.app.add_handler(CommandHandler('help', self.help_command))
        self.app.add_handler(CommandHandler('subscribe', self.subscribe_command))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        logger.info("📋 All command handlers registered")
    
    # ==================== COMMAND HANDLERS ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message with inline keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("⚡ Today's Picks", callback_data='today'),
                InlineKeyboardButton("📅 Tomorrow", callback_data='tomorrow')
            ],
            [
                InlineKeyboardButton("🎰 Acca of the Day", callback_data='acca'),
                InlineKeyboardButton("💎 Value Bets", callback_data='value')
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data='stats'),
                InlineKeyboardButton("❓ Help", callback_data='help')
            ],
            [
                InlineKeyboardButton("🌐 Visit Website", url='https://kicklabai.com')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = (
            "⚡ <b>Welcome to KICK LAB AI</b>\n\n"
            "🤖 AI-powered football predictions using advanced machine learning\n"
            "📊 Data-driven insights from thousands of matches\n"
            "💰 Value betting with calculated edge\n\n"
            "Choose an option below to get started:"
        )
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        logger.info(f"👤 New user: {update.effective_user.id}")
    
    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send today's AI picks"""
        chat_id = update.effective_chat.id
        await self._send_daily_picks(chat_id, days_offset=0)
    
    async def tomorrow_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send tomorrow's picks"""
        chat_id = update.effective_chat.id
        await self._send_daily_picks(chat_id, days_offset=1)
    
    async def acca_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send AI accumulator of the day"""
        chat_id = update.effective_chat.id
        await self._send_acca(chat_id)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send overall performance statistics"""
        chat_id = update.effective_chat.id
        await self._send_stats(chat_id)
    
    async def value_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send only value bets (edge > 10%)"""
        chat_id = update.effective_chat.id
        await self._send_daily_picks(chat_id, days_offset=0, value_only=True)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all available commands"""
        help_text = (
            "⚡ <b>KICK LAB AI — Commands</b>\n\n"
            "/start — Welcome message & menu\n"
            "/today — Today's AI picks\n"
            "/tomorrow — Tomorrow's predictions\n"
            "/acca — Accumulator of the day\n"
            "/stats — Performance statistics\n"
            "/value — High-value bets only (edge >10%)\n"
            "/help — Show this help message\n"
            "/subscribe — Upgrade your plan\n\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            "💡 <i>Tip: Use inline buttons for faster access</i>\n\n"
            "⚡ kicklabai.com"
        )
        await update.message.reply_text(help_text, parse_mode='HTML')
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show subscription options"""
        subscribe_message = (
            "💎 <b>KICK LAB AI — Premium Plans</b>\n\n"
            "🥉 <b>Free Plan</b>\n"
            "→ Daily picks (limited)\n"
            "→ Basic stats\n\n"
            "🥈 <b>Pro — €39/month</b>\n"
            "→ All daily picks\n"
            "→ Value bets alerts\n"
            "→ Advanced stats\n"
            "→ Email notifications\n\n"
            "🥇 <b>VIP — €99/month</b>\n"
            "→ Everything in Pro\n"
            "→ Live predictions\n"
            "→ Custom accumulators\n"
            "→ Priority support\n"
            "→ API access\n\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            "🌐 Visit <b>kicklabai.com/pricing</b> to upgrade\n\n"
            "⚡ kicklabai.com"
        )
        
        keyboard = [
            [InlineKeyboardButton("🌐 View Plans", url='https://kicklabai.com/pricing')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            subscribe_message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        chat_id = query.message.chat_id
        
        if query.data == 'today':
            await self._send_daily_picks(chat_id, days_offset=0)
        elif query.data == 'tomorrow':
            await self._send_daily_picks(chat_id, days_offset=1)
        elif query.data == 'acca':
            await self._send_acca(chat_id)
        elif query.data == 'value':
            await self._send_daily_picks(chat_id, days_offset=0, value_only=True)
        elif query.data == 'stats':
            await self._send_stats(chat_id)
        elif query.data == 'help':
            await self.help_command(update, context)
    
    # ==================== CORE FUNCTIONALITY ====================
    
    async def _send_daily_picks(self, chat_id: int, days_offset: int = 0, value_only: bool = False):
        """Send formatted daily picks"""
        try:
            target_date = datetime.now() + timedelta(days=days_offset)
            predictions = self._load_predictions(target_date)
            
            if not predictions:
                day_label = "today" if days_offset == 0 else "tomorrow"
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=f"🤷‍♂️ No predictions available for {day_label}",
                    parse_mode='HTML'
                )
                return
            
            # Filter value bets if requested
            if value_only:
                predictions = [p for p in predictions if abs(p.get('edge', p.get('edge_pct', 0))) > 10]
                if not predictions:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text="💎 No high-value bets (edge >10%) available right now",
                        parse_mode='HTML'
                    )
                    return
            
            message = self._format_daily_picks(predictions, target_date, value_only)
            
            # Add inline keyboard
            keyboard = [
                [
                    InlineKeyboardButton("🎰 Acca", callback_data='acca'),
                    InlineKeyboardButton("📊 Stats", callback_data='stats')
                ],
                [InlineKeyboardButton("🌐 Dashboard", url='https://kicklabai.com')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            logger.info(f"✅ Sent picks to {chat_id}")
            
        except Exception as e:
            logger.error(f"❌ Error sending picks to {chat_id}: {e}")
            await self._send_error_message(chat_id, "picks")
    
    async def _send_acca(self, chat_id: int):
        """Send accumulator of the day"""
        try:
            target_date = datetime.now()
            predictions = self._load_predictions(target_date)
            
            if not predictions:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="🤷‍♂️ No predictions available for acca today",
                    parse_mode='HTML'
                )
                return
            
            # Select top 3-4 picks by confidence
            top_picks = sorted(predictions, key=lambda x: x.get('confidence', 0), reverse=True)[:4]
            
            message = self._format_acca(top_picks, target_date)
            
            keyboard = [
                [InlineKeyboardButton("⚡ Today's Picks", callback_data='today')],
                [InlineKeyboardButton("🌐 Dashboard", url='https://kicklabai.com')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            logger.info(f"✅ Sent acca to {chat_id}")
            
        except Exception as e:
            logger.error(f"❌ Error sending acca to {chat_id}: {e}")
            await self._send_error_message(chat_id, "acca")
    
    async def _send_stats(self, chat_id: int):
        """Send performance statistics"""
        try:
            stats = self._load_stats()
            
            if not stats:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="📊 Statistics will be available once we have prediction results",
                    parse_mode='HTML'
                )
                return
            
            message = self._format_stats(stats)
            
            keyboard = [
                [InlineKeyboardButton("⚡ Today's Picks", callback_data='today')],
                [InlineKeyboardButton("🌐 Dashboard", url='https://kicklabai.com')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            logger.info(f"✅ Sent stats to {chat_id}")
            
        except Exception as e:
            logger.error(f"❌ Error sending stats to {chat_id}: {e}")
            await self._send_error_message(chat_id, "stats")
    
    # ==================== CHANNEL POSTING ====================
    
    async def post_daily_picks(self, days_offset: int = 0):
        """Post daily picks to channel (for cron)"""
        if not TELEGRAM_CHANNEL_ID:
            logger.warning("⚠️ TELEGRAM_CHANNEL_ID not set, skipping channel post")
            return
        
        try:
            await self._send_daily_picks(TELEGRAM_CHANNEL_ID, days_offset=days_offset)
            logger.info(f"✅ Posted picks to channel {TELEGRAM_CHANNEL_ID}")
        except Exception as e:
            logger.error(f"❌ Failed to post to channel: {e}")
            await self._retry_with_backoff(
                self._send_daily_picks,
                TELEGRAM_CHANNEL_ID,
                days_offset=days_offset
            )
    
    async def post_results_update(self, date: Optional[datetime] = None):
        """Post results update to channel"""
        if not TELEGRAM_CHANNEL_ID:
            logger.warning("⚠️ TELEGRAM_CHANNEL_ID not set, skipping results post")
            return
        
        try:
            if date is None:
                date = datetime.now() - timedelta(days=1)  # Yesterday
            
            results = self._load_results(date)
            
            if not results:
                logger.info(f"No results available for {date.strftime('%Y-%m-%d')}")
                return
            
            message = self._format_results(results, date)
            
            await self.bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"✅ Posted results to channel")
            
        except Exception as e:
            logger.error(f"❌ Failed to post results: {e}")
    
    # ==================== DATA LOADING ====================
    
    def _load_predictions(self, date: datetime) -> List[Dict]:
        """Load predictions from JSON file"""
        filename = date.strftime('%Y-%m-%d') + '_predictions.json'
        filepath = PREDICTIONS_DIR / filename
        
        if not filepath.exists():
            logger.warning(f"⚠️ Predictions file not found: {filepath}")
            return []
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                # Handle both list and dict formats
                if isinstance(data, dict):
                    return data.get('predictions', [])
                return data
        except Exception as e:
            logger.error(f"❌ Error loading predictions: {e}")
            return []
    
    def _load_results(self, date: datetime) -> List[Dict]:
        """Load results from JSON file"""
        filename = date.strftime('%Y-%m-%d') + '_results.json'
        filepath = RESULTS_DIR / filename
        
        if not filepath.exists():
            logger.warning(f"⚠️ Results file not found: {filepath}")
            return []
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data.get('results', [])
                return data
        except Exception as e:
            logger.error(f"❌ Error loading results: {e}")
            return []
    
    def _load_stats(self) -> Optional[Dict]:
        """Load or calculate overall stats"""
        # Try to load from a stats file first
        stats_file = BASE_DIR / 'data' / 'stats.json'
        
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Error loading stats: {e}")
        
        # Otherwise calculate from results files
        return self._calculate_stats_from_results()
    
    def _calculate_stats_from_results(self) -> Optional[Dict]:
        """Calculate stats from all result files"""
        if not RESULTS_DIR.exists():
            return None
        
        total_wins = 0
        total_losses = 0
        total_profit = 0
        current_streak = 0
        
        result_files = sorted(RESULTS_DIR.glob('*_results.json'))
        
        for filepath in result_files:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    results = data.get('results', []) if isinstance(data, dict) else data
                    
                    for result in results:
                        if result.get('outcome') == 'won':
                            total_wins += 1
                            current_streak = max(0, current_streak) + 1
                            total_profit += result.get('profit', 0)
                        elif result.get('outcome') == 'lost':
                            total_losses += 1
                            current_streak = min(0, current_streak) - 1
                            total_profit += result.get('profit', 0)  # profit will be negative
            except Exception as e:
                logger.error(f"❌ Error processing {filepath}: {e}")
        
        total = total_wins + total_losses
        
        if total == 0:
            return None
        
        return {
            'wins': total_wins,
            'losses': total_losses,
            'total': total,
            'win_rate': (total_wins / total * 100) if total > 0 else 0,
            'profit': total_profit,
            'roi': (total_profit / total * 100) if total > 0 else 0,
            'streak': current_streak
        }
    
    # ==================== MESSAGE FORMATTING ====================
    
    def _format_daily_picks(self, predictions: List[Dict], date: datetime, value_only: bool = False) -> str:
        """Format daily picks message"""
        title = "⚡ <b>KICK LAB AI — Daily Picks</b>" if not value_only else "💎 <b>KICK LAB AI — Value Bets</b>"
        message = f"{title}\n📅 {date.strftime('%d %B %Y')}\n\n"
        message += "━━━━━━━━━━━━━━━━━━━\n\n"
        
        for prediction in predictions:
            home_team = prediction.get('home_team', 'Home')
            away_team = prediction.get('away_team', 'Away')
            match_time = prediction.get('time', prediction.get('kickoff', '15:00'))
            league = prediction.get('league', prediction.get('competition', 'Premier League'))
            pred_type = prediction.get('prediction', 'Home Win')
            # Handle confidence as decimal (0.76) or percentage (76)
            raw_conf = prediction.get('confidence', 0)
            confidence = raw_conf * 100 if raw_conf <= 1 else raw_conf
            
            # Handle odds: could be 'odds', 'odds_suggested', or 'suggested_odds' dict
            odds = prediction.get('odds', None)
            if odds is None:
                odds = prediction.get('odds_suggested', None)
            if odds is None:
                suggested = prediction.get('suggested_odds', {})
                if isinstance(suggested, dict):
                    # Pick the odds for the predicted outcome
                    pred_lower = pred_type.lower()
                    if 'away' in pred_lower:
                        odds = suggested.get('away', 1.50)
                    elif 'home' in pred_lower:
                        odds = suggested.get('home', 1.50)
                    else:
                        odds = suggested.get('draw', 1.50)
                else:
                    odds = 1.50
            
            # Handle edge: could be 'edge' or 'edge_pct'
            edge = prediction.get('edge', prediction.get('edge_pct', 0))
            edge = abs(edge) if edge < 0 else edge  # Show positive
            
            reasoning = prediction.get('reasoning', prediction.get('ai_reasoning', []))
            
            message += f"⚽ <b>{home_team} vs {away_team}</b>\n"
            message += f"🕐 {match_time} GMT+2 | {league}\n\n"
            message += f"🎯 Prediction: <b>{pred_type}</b>\n"
            message += f"📊 Confidence: <b>{confidence:.0f}%</b>\n"
            message += f"💰 Odds: <b>{odds:.2f}</b>\n"
            
            if edge > 10:
                message += f"🔥 Edge: <b>+{edge:.0f}%</b> — VALUE BET\n"
            else:
                message += f"📈 Edge: <b>+{edge:.0f}%</b>\n"
            
            if reasoning:
                message += f"\n🧠 <i>AI Reasoning:</i>\n"
                for reason in reasoning[:3]:  # Top 3 reasons
                    message += f"→ {reason}\n"
            
            message += "\n━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Add stats footer
        stats = self._load_stats()
        if stats:
            message += f"📊 <b>Season Stats:</b> {stats['wins']}W-{stats['losses']}L ({stats['win_rate']:.0f}%) | €{stats['profit']:+.0f}\n\n"
        
        message += "⚡ kicklabai.com"
        
        return message
    
    def _format_acca(self, picks: List[Dict], date: datetime) -> str:
        """Format accumulator message"""
        message = f"🎰 <b>KICK LAB AI — Acca of the Day</b>\n"
        message += f"📅 {date.strftime('%d %B %Y')}\n\n"
        message += "━━━━━━━━━━━━━━━━━━━\n\n"
        
        combined_odds = 1.0
        
        for i, pick in enumerate(picks, 1):
            home_team = pick.get('home_team', 'Home')
            away_team = pick.get('away_team', 'Away')
            pred_type = pick.get('prediction', 'Home Win')
            # Same odds extraction logic
            odds = pick.get('odds', None)
            if odds is None:
                odds = pick.get('odds_suggested', None)
            if odds is None:
                suggested = pick.get('suggested_odds', {})
                if isinstance(suggested, dict):
                    pred_lower = pred_type.lower()
                    if 'away' in pred_lower:
                        odds = suggested.get('away', 1.50)
                    elif 'home' in pred_lower:
                        odds = suggested.get('home', 1.50)
                    else:
                        odds = suggested.get('draw', 1.50)
                else:
                    odds = 1.50
            combined_odds *= odds
            
            emoji = ['1️⃣', '2️⃣', '3️⃣', '4️⃣'][i-1] if i <= 4 else f"{i}️⃣"
            message += f"{emoji} {home_team} vs {away_team} → <b>{pred_type}</b> @{odds:.2f}\n"
        
        message += f"\n💰 Combined Odds: <b>@{combined_odds:.2f}</b>\n"
        message += f"📈 €10 → <b>€{10 * combined_odds:.2f}</b>\n"
        message += f"📈 €50 → <b>€{50 * combined_odds:.2f}</b>\n\n"
        message += "⚡ kicklabai.com"
        
        return message
    
    def _format_results(self, results: List[Dict], date: datetime) -> str:
        """Format results update message"""
        message = f"📊 <b>KICK LAB AI — Results Update</b>\n"
        message += f"📅 {date.strftime('%d %B %Y')}\n\n"
        
        day_wins = 0
        day_losses = 0
        day_profit = 0
        
        for result in results:
            outcome = result.get('outcome', 'pending')
            home_team = result.get('home_team', 'Home')
            away_team = result.get('away_team', 'Away')
            prediction = result.get('prediction', 'Home Win')
            odds = result.get('odds', 1.50)
            profit = result.get('profit', 0)
            
            if outcome == 'won':
                emoji = "✅"
                day_wins += 1
                day_profit += profit
                message += f"{emoji} {home_team} vs {away_team} — {prediction} @{odds:.2f} — <b>WON +€{profit:.0f}</b>\n"
            elif outcome == 'lost':
                emoji = "❌"
                day_losses += 1
                day_profit += profit  # profit is negative
                message += f"{emoji} {home_team} vs {away_team} — {prediction} @{odds:.2f} — <b>LOST €{abs(profit):.0f}</b>\n"
        
        message += "\n━━━━━━━━━━━━━━━━━━━\n"
        message += f"📊 Today: {day_wins}W-{day_losses}L | €{day_profit:+.0f}\n"
        
        # Add season stats
        stats = self._load_stats()
        if stats:
            message += f"📊 Season: {stats['wins']}W-{stats['losses']}L ({stats['win_rate']:.0f}%) | €{stats['profit']:+.0f}\n"
        
        return message
    
    def _format_stats(self, stats: Dict) -> str:
        """Format statistics message"""
        message = "📊 <b>KICK LAB AI — Performance Stats</b>\n\n"
        message += "━━━━━━━━━━━━━━━━━━━\n\n"
        
        message += f"📈 <b>Overall Record:</b>\n"
        message += f"→ Total Predictions: {stats['total']}\n"
        message += f"→ Wins: {stats['wins']}\n"
        message += f"→ Losses: {stats['losses']}\n"
        message += f"→ Win Rate: <b>{stats['win_rate']:.1f}%</b>\n\n"
        
        message += f"💰 <b>Profit & Loss:</b>\n"
        message += f"→ Total P&L: <b>€{stats['profit']:+.2f}</b>\n"
        message += f"→ ROI: <b>{stats['roi']:+.1f}%</b>\n\n"
        
        streak = stats['streak']
        if streak > 0:
            message += f"🔥 <b>Current Streak:</b> {streak}W in a row\n\n"
        elif streak < 0:
            message += f"❄️ <b>Current Streak:</b> {abs(streak)}L in a row\n\n"
        
        message += "━━━━━━━━━━━━━━━━━━━\n\n"
        message += "⚡ kicklabai.com"
        
        return message
    
    async def _send_error_message(self, chat_id: int, feature: str):
        """Send generic error message"""
        await self.bot.send_message(
            chat_id=chat_id,
            text=f"⚠️ Sorry, there was an error loading {feature}. Please try again later.",
            parse_mode='HTML'
        )
    
    # ==================== RETRY LOGIC ====================
    
    async def _retry_with_backoff(self, func, *args, max_retries=3, **kwargs):
        """Retry function with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except RetryAfter as e:
                wait_time = e.retry_after + 1
                logger.warning(f"⏳ Rate limited, waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
            except TelegramError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"⚠️ Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"❌ All retry attempts failed: {e}")
                    raise
    
    # ==================== BOT LIFECYCLE ====================
    
    async def start(self):
        """Start the bot"""
        try:
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling(drop_pending_updates=True)
            logger.info("🚀 Kick Lab AI Bot is running...")
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            raise
    
    async def stop(self):
        """Stop the bot gracefully"""
        try:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
            logger.info("🛑 Bot stopped gracefully")
        except Exception as e:
            logger.error(f"❌ Error stopping bot: {e}")


# ==================== GLOBAL BOT INSTANCE ====================

telegram_bot: Optional[KickLabTelegramBot] = None


def get_bot() -> Optional[KickLabTelegramBot]:
    """Get or create bot instance"""
    global telegram_bot
    if telegram_bot is None and TELEGRAM_BOT_TOKEN:
        telegram_bot = KickLabTelegramBot()
    return telegram_bot


async def init_telegram_bot():
    """Initialize and start the bot"""
    bot = get_bot()
    if bot:
        await bot.start()
    else:
        logger.warning("⚠️ Telegram bot not initialized (missing token)")


# ==================== STANDALONE EXECUTION ====================

if __name__ == '__main__':
    """Run bot in standalone mode"""
    bot = KickLabTelegramBot()
    asyncio.run(bot.start())
