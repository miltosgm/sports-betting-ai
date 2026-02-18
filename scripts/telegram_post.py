#!/usr/bin/env python3
"""
Kick Lab AI - Telegram Auto-Posting Script
⚡ Standalone script for cron jobs

Usage:
    python3 scripts/telegram_post.py --action picks
    python3 scripts/telegram_post.py --action results
    python3 scripts/telegram_post.py --action acca
    python3 scripts/telegram_post.py --action stats

Cron examples:
    # Post today's picks at 9:00 AM
    0 9 * * * cd /Users/milton/sports-betting-ai && python3 scripts/telegram_post.py --action picks
    
    # Post yesterday's results at 11:00 PM
    0 23 * * * cd /Users/milton/sports-betting-ai && python3 scripts/telegram_post.py --action results
    
    # Post acca at 10:00 AM
    0 10 * * * cd /Users/milton/sports-betting-ai && python3 scripts/telegram_post.py --action acca
    
    # Post weekly stats on Monday at 9:00 AM
    0 9 * * 1 cd /Users/milton/sports-betting-ai && python3 scripts/telegram_post.py --action stats
"""

import os
import sys
import argparse
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.telegram_bot import KickLabTelegramBot

# Configure logging
LOG_DIR = PROJECT_ROOT / 'logs'
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'telegram_post.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def post_picks(bot: KickLabTelegramBot, days_offset: int = 0):
    """Post daily picks to channel"""
    try:
        logger.info(f"📤 Posting picks (days_offset={days_offset})...")
        await bot.post_daily_picks(days_offset=days_offset)
        logger.info("✅ Picks posted successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to post picks: {e}")
        return False


async def post_results(bot: KickLabTelegramBot):
    """Post yesterday's results to channel"""
    try:
        logger.info("📤 Posting results update...")
        yesterday = datetime.now() - timedelta(days=1)
        await bot.post_results_update(date=yesterday)
        logger.info("✅ Results posted successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to post results: {e}")
        return False


async def post_acca(bot: KickLabTelegramBot):
    """Post accumulator of the day"""
    try:
        logger.info("📤 Posting acca...")
        channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        if not channel_id:
            logger.error("❌ TELEGRAM_CHANNEL_ID not set")
            return False
        
        await bot._send_acca(channel_id)
        logger.info("✅ Acca posted successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to post acca: {e}")
        return False


async def post_stats(bot: KickLabTelegramBot):
    """Post performance stats"""
    try:
        logger.info("📤 Posting stats...")
        channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        if not channel_id:
            logger.error("❌ TELEGRAM_CHANNEL_ID not set")
            return False
        
        await bot._send_stats(channel_id)
        logger.info("✅ Stats posted successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to post stats: {e}")
        return False


async def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description='Kick Lab AI - Telegram Auto-Posting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--action',
        type=str,
        required=True,
        choices=['picks', 'tomorrow', 'results', 'acca', 'stats'],
        help='Action to perform'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test without actually posting'
    )
    
    args = parser.parse_args()
    
    # Validate environment
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        logger.error("❌ TELEGRAM_BOT_TOKEN not set in environment")
        sys.exit(1)
    
    if not os.getenv('TELEGRAM_CHANNEL_ID'):
        logger.error("❌ TELEGRAM_CHANNEL_ID not set in environment")
        sys.exit(1)
    
    # Initialize bot
    try:
        bot = KickLabTelegramBot()
        logger.info("✅ Bot initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize bot: {e}")
        sys.exit(1)
    
    # Dry run mode
    if args.dry_run:
        logger.info("🧪 DRY RUN MODE - No messages will be sent")
        logger.info(f"Action: {args.action}")
        sys.exit(0)
    
    # Execute action
    success = False
    
    try:
        if args.action == 'picks':
            success = await post_picks(bot, days_offset=0)
        elif args.action == 'tomorrow':
            success = await post_picks(bot, days_offset=1)
        elif args.action == 'results':
            success = await post_results(bot)
        elif args.action == 'acca':
            success = await post_acca(bot)
        elif args.action == 'stats':
            success = await post_stats(bot)
    except KeyboardInterrupt:
        logger.info("⚠️ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)
    
    # Exit code
    if success:
        logger.info("🎉 Task completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Task failed")
        sys.exit(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ Interrupted by user")
        sys.exit(130)
