# ⚖️ Disclaimer & Risk

**READ THIS BEFORE USING THE MODEL**

---

## ⚠️ Important Disclaimer

This project is for **educational and research purposes only**. It is not financial advice.

### Past Performance ≠ Future Results

- Historical backtesting shows promise (54.2% accuracy)
- Real-world performance may differ significantly
- Market conditions change
- Model may overfit despite precautions
- There are no guarantees

### Do Not Treat This As Guaranteed Income

**Losses are possible.** In fact, they're likely in the short term.

Before using:
1. Paper trade for at least 2 weeks (fake money)
2. Only then use small real money
3. Never bet more than you can afford to lose
4. Start with 1% of bankroll per game (not 2%)

---

## 🎲 Risk Management

### Bankroll Management

**CRITICAL:** Never bet more than 2% of bankroll per game.

```
Example:
Bankroll: $10,000
Max per game: $200 (2%)
Daily (5 games): $1,000 max
```

### Kelly Criterion

For optimal bet sizing:

```
Optimal Bet% = (Edge × Win% - Loss%) / Odds
```

We recommend:
- **Fractional Kelly** (Kelly / 2): Conservative, safer
- **Full Kelly:** For experienced bettors only

### Stop-Loss Rules

```
Daily loss limit: -5% of bankroll
Weekly loss limit: -10% of bankroll
If hit: STOP TRADING
```

---

## 🚨 Major Risks

### Model Risk
- **Overfitting:** Model might memorize training data
- **Data quality:** Bad data → bad predictions
- **Time decay:** Old model on new games may fail

### Market Risk
- **Odds change:** Vegas moves lines, affecting our edge
- **Public information:** Big injuries/transfers may shift odds
- **Sharp money:** Professionals might be on opposite side
- **Liquidity:** Hard to place bets during off-hours

### Operational Risk
- **Data delays:** Missing injury reports, late team news
- **API failures:** Data source goes down
- **Execution:** Mistaken bet placements
- **Account limits:** Sportsbooks restrict limits on winning players

### Behavioral Risk
- **Chasing losses:** Betting more to recover
- **Overconfidence:** Ignoring stop-losses
- **Tilt:** Emotional betting after losses
- **Over-trading:** Betting on marginal opportunities

---

## Legal Considerations

### Before You Bet

- **Check local laws:** Sports betting is illegal in some jurisdictions
- **Verify sportsbook:** Use licensed, regulated books only
- **Age requirements:** Must be 18+ (21+ in some areas)
- **Account:** Verify your identity with sportsbook
- **Taxes:** You may owe taxes on profits

### Where Betting Is Legal

- ✅ Most of USA (varies by state)
- ✅ UK, Ireland, Australia, Canada
- ❌ Some US states, some countries
- ❓ Check your local regulations

---

## What Can Go Wrong

### Scenario 1: Model Breaks
```
Model accuracy: 54.2% in backtest
Real-world accuracy: 49.0% (random)
Result: Losses instead of profits
```

### Scenario 2: Odds Adjust Too Fast
```
Model finds edge at 54.2% accuracy
Vegas adjusts lines within 30 minutes
Edge disappears
```

### Scenario 3: Black Swan Event
```
Major injury not in data → 50% odds drop
Model predicts wrong class
Loss on that game
```

### Scenario 4: Account Limits
```
You win consistently
Sportsbook limits your bets from $100 to $10
Profitability drops 90%
```

---

## Before Using Real Money

### Checklist

- [ ] Understand all features (see [Features](features.md))
- [ ] Understand model limitations (see [Model Performance](model-performance.md))
- [ ] Paper trade for 2+ weeks
- [ ] Verify profit in paper trading
- [ ] Set bankroll size (amount you're OK losing)
- [ ] Start with 1% per game
- [ ] Track every bet meticulously
- [ ] Review results weekly
- [ ] Have stop-loss rules ready
- [ ] Read this disclaimer again before first real bet

---

## Our Responsibility & Yours

**We provide:**
- Model code (transparent)
- Backtesting results (honest)
- Risk disclaimers (clear)
- Documentation (complete)

**You are responsible for:**
- Your own research
- Verifying the model works *for you*
- Setting your own risk limits
- Following local laws
- Controlling your emotions
- Accepting losses

---

## Support & Questions

If you have questions:
- GitHub Issues: Report bugs
- Email: [contact info]
- Discord: Join community discussions

---

## Final Words

🚀 **This model has potential** — but potential ≠ guarantee.

💰 **Treat it like a business** — not a get-rich-quick scheme.

⚡ **Paper trade first** — always, no exceptions.

📊 **Track everything** — you can't improve what you don't measure.

❌ **Never ignore risk management** — that's how people go broke.

---

**I acknowledge the risks and will paper trade before real money.**

(Not a legal document. Consult a lawyer for legal questions.)

Last Updated: Feb 7, 2026
