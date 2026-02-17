# BetEdge API Documentation

## Base URL
```
https://api.betedge.com/api
http://localhost:5000/api (development)
```

---

## Authentication

### Register User
```
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "secure_password",
  "full_name": "Full Name"
}

Response: 201 Created
{
  "message": "Registration successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "subscription_tier": "free",
    ...
  }
}
```

### Login
```
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}

Response: 200 OK
{
  "message": "Login successful",
  "user": { ... }
}
```

### Logout
```
POST /auth/logout
Authorization: Bearer {token}

Response: 200 OK
{
  "message": "Logged out"
}
```

### Get Current User
```
GET /auth/me
Authorization: Bearer {token}

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "subscription_tier": "free",
  "total_roi_percent": 12.5,
  ...
}
```

---

## Predictions

### Get Today's Predictions
```
GET /predictions/today?league=EPL
Authorization: Bearer {token}

Query Parameters:
  league (optional): EPL, LaLiga, Serie A, Bundesliga, Ligue 1
           Default: EPL

Response: 200 OK
[
  {
    "id": 1,
    "match_id": "match_123",
    "date": "2026-02-17T15:00:00Z",
    "home_team": "Arsenal",
    "away_team": "Manchester City",
    "league": "EPL",
    "predicted_winner": "Home",
    "confidence": 75.3,
    "expected_value": 2.45,
    "home_win_prob": 0.753,
    "draw_prob": 0.152,
    "away_win_prob": 0.095,
    "home_odds": 1.85,
    "draw_odds": 3.50,
    "away_odds": 4.20,
    "home_injuries": ["Saka (Hamstring)"],
    "away_injuries": [],
    "travel_distance_miles": 180,
    "actual_result": "Pending",
    "is_correct": null
  },
  ...
]
```

### Get Upcoming Predictions
```
GET /predictions/upcoming?league=EPL&limit=10
Authorization: Bearer {token}

Query Parameters:
  league (optional): EPL, LaLiga, Serie A, Bundesliga, Ligue 1
           Default: EPL
  limit (optional): Max results, Default: 10

Response: 200 OK
[ ... array of predictions ... ]
```

### Get Prediction History
```
GET /predictions/history?league=EPL&limit=50&offset=0
Authorization: Bearer {token}

Query Parameters:
  league (optional): Filter by league
  limit (optional): Results per page, Default: 50
  offset (optional): Pagination offset, Default: 0

Response: 200 OK
{
  "predictions": [ ... ],
  "total": 1247,
  "limit": 50,
  "offset": 0
}
```

### Get Prediction Stats
```
GET /predictions/stats?league=EPL
Authorization: Bearer {token}

Query Parameters:
  league (optional): EPL, LaLiga, Serie A, Bundesliga, Ligue 1
           Default: EPL

Response: 200 OK
{
  "league": "EPL",
  "total_predictions": 380,
  "correct": 289,
  "accuracy_percent": 76.1,
  "win_count": 289,
  "loss_count": 91
}
```

---

## Bets

### Place Bet
```
POST /bets/place
Authorization: Bearer {token}
Content-Type: application/json

{
  "prediction_id": 1,
  "bet_type": "MoneyLine",
  "bet_amount": 50.00,
  "odds_at_bet": 1.85
}

Response: 201 Created
{
  "message": "Bet placed",
  "bet": {
    "id": 1,
    "user_id": 1,
    "prediction_id": 1,
    "bet_type": "MoneyLine",
    "bet_amount": 50.00,
    "odds_at_bet": 1.85,
    "potential_profit": 42.50,
    "status": "pending",
    "actual_profit": null,
    "roi_percent": null,
    "created_at": "2026-02-17T12:00:00Z",
    "resolved_at": null
  }
}
```

### Get User's Bets
```
GET /bets/my-bets?status=pending&limit=50
Authorization: Bearer {token}

Query Parameters:
  status (optional): pending, won, lost, cancelled
           Default: pending
  limit (optional): Default: 50

Response: 200 OK
[ ... array of bets ... ]
```

### Get Bet Statistics
```
GET /bets/stats
Authorization: Bearer {token}

Response: 200 OK
{
  "total_bets": 47,
  "won": 28,
  "lost": 19,
  "win_rate_percent": 59.6,
  "total_wagered": 2350.00,
  "total_profit": 487.50,
  "roi_percent": 20.74
}
```

---

## Payments

### Create Subscription
```
POST /payments/subscribe
Authorization: Bearer {token}
Content-Type: application/json

{
  "tier": "pro"  // pro or vip
}

Response: 201 Created
{
  "subscription_id": "sub_123456",
  "client_secret": "pi_1234567890..."
}
```

### Webhook (Stripe → BetEdge)
```
POST /payments/webhook
X-Stripe-Signature: {signature}

Listens for:
  - customer.subscription.updated
  - customer.subscription.deleted
  - payment_intent.succeeded

Automatically updates user subscription status in database
```

---

## Leaderboard

### Get Top Users
```
GET /leaderboard/top-users?limit=20
Authorization: Bearer {token}

Query Parameters:
  limit (optional): Default: 20, Max: 100

Response: 200 OK
[
  {
    "rank": 1,
    "username": "pro_bettor_123",
    "total_roi_percent": 45.3,
    "total_profit": 2250.75,
    "win_count": 156,
    "win_rate": 62.4
  },
  {
    "rank": 2,
    "username": "smart_analyst",
    "total_roi_percent": 38.7,
    "total_profit": 1935.50,
    "win_count": 142,
    "win_rate": 59.2
  },
  ...
]
```

---

## Admin Routes

### Get All Users
```
GET /admin/users?limit=100
Authorization: Bearer {admin_token}

Query Parameters:
  limit (optional): Default: 100

Response: 200 OK
[ ... array of users with full details ... ]
```

### Add Prediction (Admin)
```
POST /admin/add-prediction
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "match_id": "match_123",
  "date": "2026-02-17T15:00:00Z",
  "home_team": "Arsenal",
  "away_team": "Manchester City",
  "league": "EPL",
  "predicted_winner": "Home",
  "confidence": 75.3,
  "expected_value": 2.45,
  "home_win_prob": 0.753,
  "draw_prob": 0.152,
  "away_win_prob": 0.095,
  "home_odds": 1.85,
  "draw_odds": 3.50,
  "away_odds": 4.20,
  "actual_result": "Pending"
}

Response: 201 Created
{ ... prediction object ... }
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid email or password"
}
```

### 404 Not Found
```json
{
  "error": "Prediction not found"
}
```

### 500 Server Error
```json
{
  "error": "Server error"
}
```

---

## Rate Limiting

- **Free tier:** 100 requests/hour
- **Pro tier:** 1,000 requests/hour
- **VIP tier:** 10,000 requests/hour

Headers included in response:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1613500000
```

---

## Webhooks

### Telegram Bot Commands
```
/start           - Show main menu
/today           - Get today's picks
/tomorrow        - Get tomorrow's picks
/stats           - Show current stats
/subscribe       - Show subscription options
```

### Email Notifications
Automatically sent at:
- **9:00 AM GMT+2** - Daily picks email
- **After match result** - Bet result notification
- **Weekly summary** - ROI and performance summary

### SMS Notifications (If enabled)
- Match alerts
- Injury updates
- Bet wins/losses
- Weekly stats

---

## SDK Examples

### Python
```python
import requests

API_URL = "https://api.betedge.com/api"
TOKEN = "your_auth_token"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Get today's picks
response = requests.get(f"{API_URL}/predictions/today", headers=headers)
picks = response.json()

# Place bet
bet_data = {
    "prediction_id": picks[0]['id'],
    "bet_type": "MoneyLine",
    "bet_amount": 50.00,
    "odds_at_bet": picks[0]['home_odds']
}
response = requests.post(f"{API_URL}/bets/place", 
                        json=bet_data, 
                        headers=headers)
print(response.json())
```

### JavaScript
```javascript
const API_URL = "https://api.betedge.com/api";
const TOKEN = "your_auth_token";

const headers = {
  "Authorization": `Bearer ${TOKEN}`,
  "Content-Type": "application/json"
};

// Get today's picks
async function getTodayPicks() {
  const response = await fetch(`${API_URL}/predictions/today`, { headers });
  return response.json();
}

// Place bet
async function placeBet(predictionId, amount, odds) {
  const response = await fetch(`${API_URL}/bets/place`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      prediction_id: predictionId,
      bet_type: "MoneyLine",
      bet_amount: amount,
      odds_at_bet: odds
    })
  });
  return response.json();
}
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-17 | Initial release |

---

## Support

- **Email:** api-support@betedge.com
- **Status Page:** https://status.betedge.com
- **GitHub Issues:** https://github.com/miltosgm/sports-betting-ai/issues

---

**Last Updated:** February 17, 2026
