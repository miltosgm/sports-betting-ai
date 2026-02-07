# ❓ FAQ

Frequently asked questions.

## About the Model

### Q: Will this make me rich?
**A:** No. It's designed for consistent small edge (54.2% accuracy = +1.8% edge). Expected return: $70k-100k/year if all works. That's good, not get-rich-quick.

### Q: Why not 100% accuracy?
**A:** Impossible. Even Vegas sharp bettors only get 52-54% long-term. Sports has randomness.

### Q: What's the historical backtest vs real trading difference?
**A:** Huge risk. Backtests are usually too optimistic. Real trading may be 50-80% of backtest results due to:
- Odds moving before you bet
- Slippage
- Your mistakes
- Model drift over time

### Q: Can I use this on other sports?
**A:** Not yet. Premier League specific. Could be adapted to other leagues/sports with new data.

---

## Getting Started

### Q: Do I need Python experience?
**A:** No. Just follow [Quick Start](quickstart.md). Minimal coding needed.

### Q: How long to set up?
**A:** 30 minutes:
- 5 min: Install
- 10 min: Download data
- 10 min: Train model
- 5 min: Run predictions

### Q: Can I run this on my laptop?
**A:** Yes. Needs 4GB RAM minimum, ~2GB disk. Works on Mac/Windows/Linux.

### Q: Can I run this on a phone?
**A:** No. Needs proper computer.

---

## Predictions & Betting

### Q: How many bets per day?
**A:** Target: 5-7 high-confidence bets. Could be 0 (no good opportunities) or 10+ (if we're feeling loose).

### Q: What if I lose?
**A:** You will lose some days. That's betting. If model works, you'll be +EV over time, but short-term losing streaks are normal.

### Q: When should I start betting real money?
**A:** After 2 weeks of paper trading showing profits matching backtest. Not before.

### Q: How much should I bet per game?
**A:** Maximum 2% of bankroll. Use Kelly Criterion for optimal sizing.

Example: $10k bankroll = $200 max per game

### Q: What if the model is wrong?
**A:** It will be sometimes. 54.2% accuracy means 45.8% losses. That's expected.

---

## Technical

### Q: Is the code open source?
**A:** Yes. Full GitHub: github.com/miltosgm/sports-betting-ai

### Q: Can I modify the model?
**A:** Yes. Fork the repo and make your own version. Be careful with changes.

### Q: Does it use real-time data?
**A:** Yes, as real-time as available APIs. 5-15 minute delay typical.

### Q: What if APIs go down?
**A:** Predictions won't work until restored. Always have backup data sources.

---

## Money & Legal

### Q: Is this legal?
**A:** In most places, yes. Check your local laws first.

### Q: Do I need to report profits?
**A:** Yes. Gambling profits are usually taxable income. Consult a tax professional.

### Q: What if I lose money?
**A:** That's on you. Model doesn't guarantee profits. Read the [Disclaimer](disclaimer.md).

### Q: Can I use this with DeFi betting?
**A:** Technically yes, but beware smart contract risks.

---

## Results

### Q: Why 54.2% accuracy specifically?
**A:** Tested on 160 out-of-sample games. That's the result. Statistical error margin ±3%.

### Q: Is 54.2% good?
**A:** Better than 52.4% (break-even). Small edge becomes big profits over 1000+ games.

### Q: What happens if I only bet high-confidence predictions?
**A:** Fewer bets (5-7 vs 10-15) but higher win rate (57-60%). Better ROI per bet.

---

## Troubleshooting

### Q: Model training fails - what's wrong?
**A:** See [Troubleshooting](troubleshooting.md) for solutions.

### Q: Data download is too slow
**A:** Normal for first run. Takes 10-20 minutes. Subsequent runs use cache.

### Q: Model accuracy is different from docs
**A:** Possible if you modified features or data. Check configuration.

---

## Community

### Q: Can I share results?
**A:** Yes! Show your paper trading results in GitHub Discussions.

### Q: Can I modify and redistribute?
**A:** Check LICENSE. MIT license = mostly yes, just give credit.

### Q: Want to contribute?
**A:** Great! Open a PR on GitHub. We review improvements.

---

## What's Next

### Q: When's Phase 5 (daily predictions)?
**A:** Feb 14, 2026

### Q: When can I paper trade?
**A:** After Phase 4 completes (Feb 10)

### Q: When real trading?
**A:** After 2+ weeks paper trading success (late Feb)

---

Can't find your question? 
→ Open an issue on [GitHub](https://github.com/miltosgm/sports-betting-ai/issues)
