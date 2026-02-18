# Kick Lab AI - Telegram Bot Quick Setup

⚡ Get your bot running in 5 minutes

## Step 1: Create Your Bot

1. Open Telegram and talk to [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Choose a name: **Kick Lab AI**
4. Choose a username: **kicklabai_bot** (must end in "bot")
5. Copy the token that looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

## Step 2: Create Your Channel (Optional)

1. Create a new Telegram channel
2. Make it public or private
3. Add your bot as an administrator with "Post messages" permission
4. Get the channel ID:
   - Forward a message from the channel to [@userinfobot](https://t.me/userinfobot)
   - Copy the ID (starts with `-100` for supergroups)
   - Or use `@channelname` if public

## Step 3: Set Environment Variables

Create a `.env` file in the project root:

```bash
# Required
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=@kicklabai  # or -1001234567890

# Optional (your user ID for admin commands)
TELEGRAM_ADMIN_IDS=123456789
```

**Get your user ID:**
- Send any message to [@userinfobot](https://t.me/userinfobot)

## Step 4: Test the Bot

```bash
# Load environment variables
source .env  # or use direnv, dotenv, etc.

# Test import
python3 -c "from backend.services.telegram_bot import KickLabTelegramBot; print('✅ Works!')"

# Test dry-run posting
python3 scripts/telegram_post.py --action picks --dry-run
```

## Step 5: Run the Bot

### Option A: Standalone Mode (recommended for testing)

```bash
python3 backend/services/telegram_bot.py
```

Keep this running in a terminal or use:

```bash
# Run in background
nohup python3 backend/services/telegram_bot.py > bot.log 2>&1 &
```

### Option B: With Flask App

Integrate into your Flask app:

```python
# In backend/app.py
from backend.services.telegram_bot import init_telegram_bot
import asyncio

if __name__ == '__main__':
    # Start Telegram bot
    asyncio.run(init_telegram_bot())
    
    # Start Flask
    app.run(debug=True)
```

## Step 6: Setup Auto-Posting (Optional)

Edit your crontab: `crontab -e`

```bash
# Export env vars for cron
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHANNEL_ID=@kicklabai

# Post picks at 9 AM daily
0 9 * * * cd /Users/milton/sports-betting-ai && python3 scripts/telegram_post.py --action picks

# Post results at 11 PM daily
0 23 * * * cd /Users/milton/sports-betting-ai && python3 scripts/telegram_post.py --action results
```

**Or use a systemd timer, launchd, or pm2**

## Step 7: Test with Telegram

1. Open Telegram
2. Search for your bot username
3. Send `/start`
4. Try commands: `/today`, `/acca`, `/stats`

## Verification Checklist

- [ ] Bot responds to `/start` command
- [ ] Bot shows inline keyboard buttons
- [ ] `/today` command shows picks (if data exists)
- [ ] `/help` command lists all commands
- [ ] Channel posting works (if configured)
- [ ] Cron script runs without errors

## Troubleshooting

### "TELEGRAM_BOT_TOKEN not set"
```bash
# Check environment
echo $TELEGRAM_BOT_TOKEN

# Make sure to export
export TELEGRAM_BOT_TOKEN=your_token
```

### "No predictions available"
```bash
# Check data files exist
ls -la data/predictions/

# Create example data
cp data/predictions/2026-02-18_predictions.json data/predictions/$(date +%Y-%m-%d)_predictions.json
```

### Bot doesn't respond
- Check token is correct
- Make sure bot is running (`ps aux | grep telegram_bot`)
- Check logs: `tail -f telegram_bot.log`

### Channel posting fails
- Bot must be admin in channel
- Check channel ID format
- Test with direct user chat first

## What's Next?

1. **Connect prediction pipeline** - Make sure `data/predictions/*.json` is generated daily
2. **Setup cron jobs** - Automate daily posting
3. **Monitor logs** - Check `telegram_bot.log` and `logs/telegram_post.log`
4. **Customize messages** - Edit formatting in `telegram_bot.py`
5. **Add features** - User subscriptions, live updates, etc.

## Need Help?

- Read full docs: `docs/TELEGRAM_BOT.md`
- Check logs first
- Test with `--dry-run` flag
- Use [@BotFather](https://t.me/botfather) for bot settings

---

⚡ **Kick Lab AI** - Your AI betting assistant is ready!
