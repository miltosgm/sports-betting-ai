import React, { useState, useEffect } from 'react';
import './Dashboard.css';

export default function Dashboard({ user }) {
  const [stats, setStats] = useState(null);
  const [todayPicks, setTodayPicks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, picksRes] = await Promise.all([
        fetch('/api/bets/stats'),
        fetch('/api/predictions/today')
      ]);

      const statsData = await statsRes.json();
      const picksData = await picksRes.json();

      setStats(statsData);
      setTodayPicks(picksData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  if (loading) return <div className="dashboard-loading">Loading...</div>;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Welcome back, {user.username}! 👋</h1>
        <p className="subscription-badge">{user.subscription_tier.toUpperCase()} Member</p>
      </div>

      <div className="dashboard-grid">
        {/* Stats Cards */}
        <div className="stats-section">
          <h2>Your Performance</h2>
          <div className="stats-cards">
            <div className="stat-card">
              <div className="stat-value">{stats?.total_bets || 0}</div>
              <div className="stat-label">Total Bets</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats?.win_rate_percent || 0}%</div>
              <div className="stat-label">Win Rate</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">€{stats?.total_profit?.toFixed(2) || '0.00'}</div>
              <div className="stat-label">Total Profit</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats?.roi_percent?.toFixed(1) || '0'}%</div>
              <div className="stat-label">ROI</div>
            </div>
          </div>
        </div>

        {/* Today's Predictions */}
        <div className="predictions-section">
          <h2>🎯 Today's Picks</h2>
          {todayPicks.length > 0 ? (
            <div className="predictions-list">
              {todayPicks.map((pred, idx) => (
                <div key={idx} className={`prediction-card confidence-${Math.round(pred.confidence / 25)}`}>
                  <div className="prediction-match">
                    <span className="team">{pred.home_team}</span>
                    <span className="vs">vs</span>
                    <span className="team">{pred.away_team}</span>
                  </div>
                  <div className="prediction-details">
                    <span className="prediction">
                      <strong>{pred.predicted_winner}</strong>
                    </span>
                    <span className="confidence">
                      💯 {pred.confidence?.toFixed(1)}%
                    </span>
                    <span className="ev">
                      EV: {pred.expected_value?.toFixed(2)}%
                    </span>
                  </div>
                  <div className="prediction-action">
                    <button className="bet-btn">Place Bet</button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-picks">No predictions available for today</div>
          )}
        </div>

        {/* Active Bets */}
        <div className="active-bets-section">
          <h2>Active Bets</h2>
          <div className="placeholder">Your active bets will appear here</div>
        </div>

        {/* Chart Placeholder */}
        <div className="chart-section">
          <h2>ROI Over Time</h2>
          <div className="chart-placeholder">
            <p>📈 Chart coming soon</p>
          </div>
        </div>
      </div>
    </div>
  );
}
