import React, { useState, useEffect } from 'react';
import './Admin.css';

export default function Admin() {
  const [tab, setTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdminData();
  }, [tab]);

  const fetchAdminData = async () => {
    try {
      if (tab === 'users') {
        const res = await fetch('/api/admin/users');
        const data = await res.json();
        setUsers(data);
      } else if (tab === 'stats') {
        const res = await fetch('/api/predictions/stats');
        const data = await res.json();
        setStats(data);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching admin data:', error);
      setLoading(false);
    }
  };

  return (
    <div className="admin-panel">
      <h1>🔒 Admin Dashboard</h1>

      <div className="admin-tabs">
        <button 
          className={`tab ${tab === 'users' ? 'active' : ''}`}
          onClick={() => setTab('users')}
        >
          Users
        </button>
        <button 
          className={`tab ${tab === 'stats' ? 'active' : ''}`}
          onClick={() => setTab('stats')}
        >
          Statistics
        </button>
        <button 
          className={`tab ${tab === 'predictions' ? 'active' : ''}`}
          onClick={() => setTab('predictions')}
        >
          Add Prediction
        </button>
      </div>

      <div className="admin-content">
        {loading ? (
          <div>Loading...</div>
        ) : tab === 'users' ? (
          <div>
            <h2>Users ({users.length})</h2>
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Subscription</th>
                  <th>Bets</th>
                  <th>Win Rate</th>
                  <th>Profit</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(user => (
                  <tr key={user.id}>
                    <td>{user.email}</td>
                    <td><span className={`badge ${user.subscription_tier}`}>{user.subscription_tier}</span></td>
                    <td>{user.win_count + user.loss_count}</td>
                    <td>{user.win_rate}%</td>
                    <td>€{user.total_profit}</td>
                    <td>
                      <button className="admin-btn-small">Edit</button>
                      <button className="admin-btn-small danger">Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : tab === 'stats' ? (
          <div>
            <h2>Prediction Statistics</h2>
            {stats && (
              <div className="stats-grid">
                <div className="stat">
                  <div className="stat-value">{stats.total_predictions}</div>
                  <div className="stat-label">Total Predictions</div>
                </div>
                <div className="stat">
                  <div className="stat-value">{stats.correct}</div>
                  <div className="stat-label">Correct</div>
                </div>
                <div className="stat">
                  <div className="stat-value">{stats.accuracy_percent}%</div>
                  <div className="stat-label">Accuracy</div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div>
            <h2>Add New Prediction</h2>
            <form className="prediction-form">
              <input type="text" placeholder="Home Team" required />
              <input type="text" placeholder="Away Team" required />
              <select required>
                <option>Home</option>
                <option>Draw</option>
                <option>Away</option>
              </select>
              <input type="number" placeholder="Confidence %" min="0" max="100" required />
              <button type="submit">Add Prediction</button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
