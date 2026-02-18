# Kick Lab AI - Telegram Bot Documentation

⚡ Production-ready Telegram bot for sports betting AI predictions

## Features

- **Direct messaging bot** - Users can DM the bot for predictions
- **Channel broadcasting** - Auto-post picks to your Telegram channel
- **Premium formatting** - Beautiful HTML-formatted messages with emojis
- **Multiple commands** - Full command suite for different use cases
- **Auto-posting support** - Cron-ready scripts for automation
- **Error handling** - Retry logic, rate limiting, graceful failures
- **Logging** - Complete audit trail of all bot activities

---

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with inline keyboard |
| `/today` | Today's AI picks with full details |
| `/tomorrow` | Tomorrow's predictions |
| `/acca` | AI Accumulator of the Day (top 3-4 picks) |
| `/stats` | Overall performance statistics |
| `/value` | Only value bets (edge > 10%) |
| `/help` | List all commands |
| `/subscribe` | Link to pricing/payment page |

---

## Setup

### 1. Environment Variables

Create a `.env` file or set these in your environment:

```bash
# Required
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHANNEL_ID=@kicklabai  # or -1001234567890

# Optional
TELEGRAM_ADMIN_IDS=123456789,987654321  # Comma-separated user IDs
```

**How to get these:**

1. **Bot Token**: Talk to [@BotFather](https://t.me/botfather)
   - Send `/newbot`
   - Choose name and username
   - Copy the token

2. **Channel ID**: 
   - Add your bot as admin to the channel
   - Forward a message from the channel to [@userinfobot](https://t.me/userinfobot)
   - Copy the channel ID

3. **Admin IDs**:
   - Send any message to [@userinfobot](https://t.me/userinfobot)
   - Copy your user ID

### 2. Install Dependencies

```bash
pip install python-telegram-bot==22.5
```

### 3. Test the Bot

```bash
# Test import
python3 -c "from backend.services.telegram_bot import KickLabTelegramBot; print('✅ Bot imports successfully')"

# Run bot in standalone mode (for testing)
python3 backend/services/telegram_bot.py
```

### 4. Integration with Flask App

```python
from backend.services.telegram_bot import init_telegram_bot

# In your Flask app initialization
if __name__ == '__main__':
    asyncio.run(init_telegram_bot())
    app.run(debug=True)
```

---

## Auto-Posting with Cron

Use `scripts/telegram_post.py` for automated posting:

### Usage

```bash
# Post today's picks
python3 scripts/telegram_post.py --action picks

# Post tomorrow's picks
python3 scripts/telegram_post.py --action tomorrow

# Post yesterday's results
python3 scripts/telegram_post.py --action results

# Post accumulator of the day
python3 scripts/telegram_post.py --action acca

# Post weekly stats
python3 scripts/telegram_post.py --action stats

# Dry run (test without posting)
python3 scripts/telegram_post.py --action picks --dry-run
```

### Cron Examples

Edit your crontab: `crontab -e`

```bash
# Post today's picks at 9:00 AM every day
0 9 * * * cd /Users/milton/sports-betting-ai && python3 scripts/telegram_post.py --action picks

# Post acca at 10:00 AM
0 10 * * * cd /Users/milton/sports-betting-ai && python3 scripts/telegram_post.py --action acca

# Post yesterday's results at 11:00 PM
0 23 * * * cd /Users/milton/sports-betting-ai && python3 scripts/telegram_post.py --action results

# Post weekly stats every Monday at 9:00 AM
0 9 * * 1 cd /Users/milton/sports-betting-ai && python3 scripts/telegram_post.py --action stats
```

**Tip**: Redirect output to a log file:

```bash
0 9 * * * cd /Users/milton/sports-betting-ai && python3 scripts/telegram_post.py --action picks >> /tmp/telegram_post.log 2>&1
```

---

## Data Format

### Predictions JSON

Location: `data/predictions/YYYY-MM-DD_predictions.json`

```json
{
  "predictions": [
    {
      "home_team": "Wolves",
      "away_team": "Arsenal",
      "time": "20:00",
      "league": "Premier League",
      "prediction": "Away Win",
      "confidence": 76,
      "odds": 1.88,
      "edge": 23,
      "reasoning": [
        "Arsenal away form: 7W-2D-1L (70%)",
        "Wolves home: 3W-2D-6L (27%)"
      ]
    }
  ],
  "date": "2026-02-18",
  "generated_at": "2026-02-18T08:00:00Z"
}
```

### Results JSON

Location: `data/results/YYYY-MM-DD_results.json`

```json
{
  "results": [
    {
      "home_team": "Arsenal",
      "away_team": "Newcastle",
      "prediction": "Home Win",
      "odds": 1.88,
      "outcome": "won",
      "profit": 88,
      "actual_score": "3-1"
    }
  ],
  "date": "2026-02-17"
}
```

### Stats JSON

Location: `data/stats.json`

```json
{
  "wins": 37,
  "losses": 10,
  "total": 47,
  "win_rate": 78.72,
  "profit": 3525,
  "roi": 75.0,
  "streak": 3,
  "last_updated": "2026-02-17T23:00:00Z"
}
```

---

## Message Examples

### Daily Picks

```
⚡ KICK LAB AI — Daily Picks
📅 18 February 2026

━━━━━━━━━━━━━━━━━━━

⚽ Wolves vs Arsenal
🕐 20:00 GMT+2 | Premier League

🎯 Prediction: Away Win
📊 Confidence: 76%
💰 Odds: 1.88
🔥 Edge: +23% — VALUE BET

🧠 AI Reasoning:
→ Arsenal away form: 7W-2D-1L (70%)
→ Wolves home: 3W-2D-6L (27%)
→ Arsenal won 4/5 last meetings

━━━━━━━━━━━━━━━━━━━

📊 Season Stats: 37W-10L (79%) | +€3,525

⚡ kicklabai.com
```

### Accumulator

```
🎰 KICK LAB AI — Acca of the Day
📅 18 February 2026

━━━━━━━━━━━━━━━━━━━

1️⃣ Wolves vs Arsenal → Away Win @1.88
2️⃣ Forest vs Liverpool → Over 2.5 @1.72
3️⃣ Spurs vs Arsenal → BTTS @1.58

💰 Combined Odds: @5.11
📈 €10 → €51.10
📈 €50 → €255.50

⚡ kicklabai.com
```

### Results Update

```
📊 KICK LAB AI — Results Update
📅 17 February 2026

✅ Arsenal Home Win @1.88 — WON +€88
✅ Liverpool Over 2.5 @1.72 — WON +€72
❌ Chelsea Home Win @1.65 — LOST -€100

━━━━━━━━━━━━━━━━━━━
📊 Today: 2W-1L | +€60
📊 Season: 37W-10L (79%) | +€3,525
```

---

## Troubleshooting

### Bot doesn't respond

1. Check token: `echo $TELEGRAM_BOT_TOKEN`
2. Check bot is running: `ps aux | grep telegram_bot`
3. Check logs: `tail -f telegram_bot.log`

### Channel posting fails

1. Make sure bot is admin in the channel
2. Verify channel ID is correct (should start with `-100` or `@username`)
3. Check logs for rate limiting errors

### Import errors

```bash
# Verify python-telegram-bot version
pip show python-telegram-bot

# Should be 22.5 (async version)
pip install python-telegram-bot==22.5
```

### Rate limiting

The bot includes automatic retry with exponential backoff. If you hit rate limits:

- Reduce posting frequency
- Combine multiple updates into fewer messages
- Respect Telegram's limits (30 messages/second to different users)

---

## Logs

- Bot operations: `telegram_bot.log`
- Cron posts: `logs/telegram_post.log`

---

## Security

- **Never commit** `.env` files or tokens to git
- Keep `TELEGRAM_BOT_TOKEN` secret
- Use `TELEGRAM_ADMIN_IDS` to restrict admin commands
- Channel should be set to private or public based on your preference

---

## Future Enhancements

- [ ] User subscriptions database
- [ ] Personalized notifications based on leagues
- [ ] Betting slip tracking
- [ ] Live score updates
- [ ] Interactive bet builder
- [ ] Payment integration (Stripe/PayPal)

---

## Support

For issues or questions:
- Check logs first
- Review [python-telegram-bot docs](https://docs.python-telegram-bot.org/)
- Test with `--dry-run` flag

⚡ **Kick Lab AI** - Powered by Machine Learning
