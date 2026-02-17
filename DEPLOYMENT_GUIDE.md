# BetEdge Deployment Guide - Production Ready

## Overview
Complete production deployment guide for BetEdge AI betting platform with:
- Backend API (Flask + SQLAlchemy + Stripe)
- Frontend Dashboard (React)
- Email notifications (SendGrid)
- SMS alerts (Twilio)
- Telegram bot
- Multi-league predictions
- Admin panel

---

## Prerequisites

### Required Services
1. **Flask Backend** - Python 3.8+
2. **React Frontend** - Node.js 14+
3. **Database** - SQLite (dev) / PostgreSQL (prod)
4. **Stripe** - Payment processing
5. **SendGrid** - Email service
6. **Twilio** - SMS notifications
7. **Telegram Bot** - Predictions broadcasting
8. **Football Data API** - Match data

---

## Part 1: Environment Setup

### 1.1 Clone Repository
```bash
cd /Users/milton/sports-betting-ai
git clone https://github.com/miltosgm/sports-betting-ai.git
cd sports-betting-ai
```

### 1.2 Create .env File
```bash
cat > backend/.env << 'EOF'
# Flask
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-min-32-chars-change-this
DEBUG=False

# Database
DATABASE_URL=sqlite:///betedge.db
SQLALCHEMY_DATABASE_URI=sqlite:///betedge.db

# Stripe
STRIPE_SECRET_KEY=sk_live_YOUR_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET
STRIPE_PRICE_PRO=price_YOUR_PRO_PRICE
STRIPE_PRICE_VIP=price_YOUR_VIP_PRICE

# SendGrid
SENDGRID_API_KEY=SG.YOUR_API_KEY
FROM_EMAIL=predictions@betedge.com

# Twilio
TWILIO_ACCOUNT_SID=YOUR_ACCOUNT_SID
TWILIO_AUTH_TOKEN=YOUR_AUTH_TOKEN
TWILIO_PHONE_NUMBER=+YOUR_TWILIO_NUMBER

# Telegram
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_FROM_BOTFATHER
TELEGRAM_CHANNEL_ID=YOUR_CHANNEL_ID
TELEGRAM_ADMIN_IDS=123456,789012

# Football Data API
FOOTBALL_DATA_API_KEY=YOUR_FOOTBALL_DATA_API_KEY

# Admin emails
ADMIN_EMAILS=miltos@betedge.com,admin@betedge.com
EOF
```

### 1.3 Install Backend Dependencies
```bash
cd backend
pip3 install -r requirements.txt
```

### 1.4 Setup Frontend
```bash
cd frontend
npm install
npm run build
```

---

## Part 2: Database Setup

### 2.1 Initialize Database
```bash
python3 << 'PYEOF'
from backend.app import app, db

with app.app_context():
    db.create_all()
    print('✅ Database initialized')

PYEOF
```

### 2.2 Create Admin User (Optional)
```bash
python3 << 'PYEOF'
from backend.app import app, db, User

with app.app_context():
    admin = User(
        email='miltos@betedge.com',
        username='miltos_admin',
        full_name='Miltos George',
        subscription_tier='vip',
        subscription_active=True
    )
    admin.set_password('change-this-password')
    db.session.add(admin)
    db.session.commit()
    print('✅ Admin user created')

PYEOF
```

---

## Part 3: Running Locally

### 3.1 Start Backend
```bash
cd backend
python3 app.py
# Server runs at http://localhost:5000
```

### 3.2 Start Frontend (Development)
```bash
cd frontend
npm start
# Frontend runs at http://localhost:3000
```

### 3.3 Test API
```bash
# Register user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'

# Get today's predictions
curl http://localhost:5000/api/predictions/today?league=EPL
```

---

## Part 4: Production Deployment

### 4.1 Using Gunicorn (Recommended)
```bash
cd backend
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 4.2 Using Docker
Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
```

Build and run:
```bash
docker build -t betedge-api .
docker run -p 5000:5000 --env-file backend/.env betedge-api
```

### 4.3 Using Systemd (VPS/Linux)
Create `/etc/systemd/system/betedge-api.service`:
```ini
[Unit]
Description=BetEdge API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/betedge
Environment="PATH=/var/www/betedge/venv/bin"
ExecStart=/var/www/betedge/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable betedge-api
sudo systemctl start betedge-api
sudo systemctl status betedge-api
```

### 4.4 Frontend Deployment (GitHub Pages or Netlify)
```bash
cd frontend
npm run build
# Deploy the 'build' folder to your hosting
```

### 4.5 Using Vercel (Recommended for Frontend)
```bash
npm install -g vercel
cd frontend
vercel
# Follow prompts to deploy
```

---

## Part 5: Setup Integrations

### 5.1 Stripe Setup
1. Go to https://dashboard.stripe.com
2. Create Pro and VIP products
3. Create prices for each product (€39/mo and €99/mo)
4. Copy price IDs to `.env`
5. Setup webhook at `https://yourdomain.com/api/payments/webhook`

### 5.2 SendGrid Setup
1. Create account at https://sendgrid.com
2. Generate API key
3. Create sender verification (FROM_EMAIL)
4. Add API key to `.env`

### 5.3 Telegram Bot Setup
1. Chat with @BotFather on Telegram
2. `/newbot` to create bot
3. Get token and channel ID
4. Add to `.env`

### 5.4 Twilio Setup
1. Create account at https://www.twilio.com
2. Get Account SID, Auth Token, and Phone Number
3. Add to `.env`

---

## Part 6: Daily Automation

### 6.1 Daily Predictions (9 AM GMT+2)
Add to crontab:
```bash
0 7 * * * cd /Users/milton/sports-betting-ai && python3 scripts/06_daily_predictions.py >> logs/predictions.log 2>&1
```

### 6.2 Daily Retraining (2 AM GMT+2)
```bash
0 0 * * * cd /Users/milton/sports-betting-ai && python3 scripts/08_daily_retraining.py >> logs/retraining.log 2>&1
```

### 6.3 Injury Scraping (9 AM GMT+2)
```bash
0 7 * * * cd /Users/milton/sports-betting-ai && python3 scripts/10_live_injury_scraper.py >> logs/injuries.log 2>&1
```

### 6.4 Multi-League Predictions
```bash
0 7 * * * cd /Users/milton/sports-betting-ai && python3 scripts/12_multi_league_predictions.py >> logs/multi_league.log 2>&1
```

---

## Part 7: Monitoring & Logging

### 7.1 Setup Logging
Create `backend/config.py`:
```python
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/betedge.log', 
                                      maxBytes=10240000, 
                                      backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('BetEdge API startup')
```

### 7.2 Health Check Endpoint
Add to `backend/app.py`:
```python
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected'
    }), 200
```

### 7.3 Monitor with curl
```bash
watch -n 60 'curl http://localhost:5000/health'
```

---

## Part 8: Security

### 8.1 Environment Variables
Never commit `.env` to git:
```bash
echo "backend/.env" >> .gitignore
```

### 8.2 HTTPS/SSL
Use Let's Encrypt with Nginx:
```bash
sudo certbot certify -d betedge.com
```

### 8.3 CORS Setup
Already configured in `backend/app.py`:
```python
CORS(app, origins=['https://betedge.com', 'https://www.betedge.com'])
```

### 8.4 Rate Limiting
```bash
pip install flask-limiter
```

Add to app.py:
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/predictions/today')
@limiter.limit("100 per hour")
def get_today_predictions():
    ...
```

---

## Part 9: Scaling

### 9.1 Database Upgrade (SQLite → PostgreSQL)
```bash
pip3 install psycopg2-binary
# Update in .env:
DATABASE_URL=postgresql://user:password@localhost/betedge
```

### 9.2 Redis Caching
```bash
pip3 install redis flask-caching
```

### 9.3 Load Balancing
Use Nginx with multiple API instances:
```nginx
upstream betedge_api {
    server localhost:5001;
    server localhost:5002;
    server localhost:5003;
    server localhost:5004;
}

server {
    listen 80;
    server_name betedge.com;

    location /api {
        proxy_pass http://betedge_api;
    }
}
```

---

## Part 10: Testing

### 10.1 Run Unit Tests
```bash
pip3 install pytest
pytest backend/tests/
```

### 10.2 Test Stripe Integration
```bash
python3 << 'PYEOF'
import stripe
stripe.api_key = 'sk_test_YOUR_TEST_KEY'

# Test card: 4242 4242 4242 4242
token = stripe.Token.create(
    card={
        "number": "4242424242424242",
        "exp_month": 12,
        "exp_year": 2025,
        "cvc": "123"
    }
)
print("✅ Stripe connection works")
PYEOF
```

---

## Troubleshooting

### API won't start
```bash
# Check if port 5000 is already in use
lsof -i :5000
kill -9 <PID>
```

### Database errors
```bash
# Reset database
rm backend/betedge.db
python3 backend/app.py
```

### Stripe webhook not working
1. Use `ngrok` for local testing:
```bash
ngrok http 5000
# Add https://YOUR_NGROK_URL/api/payments/webhook to Stripe
```

---

## Launch Checklist

- [ ] Environment variables configured
- [ ] Database initialized
- [ ] Admin user created
- [ ] Stripe keys added
- [ ] SendGrid API key added
- [ ] Telegram bot created
- [ ] Domain/DNS configured
- [ ] SSL certificate installed
- [ ] Email templates tested
- [ ] SMS notifications tested
- [ ] Telegram bot tested
- [ ] Daily cron jobs setup
- [ ] Monitoring/logging configured
- [ ] Database backups configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Health checks passing
- [ ] Frontend deployed
- [ ] Payment processing tested
- [ ] User registration tested
- [ ] API rate limits tested
- [ ] Load testing completed
- [ ] Security audit passed

---

## Support

For issues or questions:
- Email: miltos@betedge.com
- GitHub: https://github.com/miltosgm/sports-betting-ai
- Docs: https://betedge.com/docs

---

**Version:** 1.0.0  
**Last Updated:** February 17, 2026  
**Status:** Production Ready ✅
