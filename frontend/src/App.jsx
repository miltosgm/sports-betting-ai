import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import Predictions from './pages/Predictions';
import MyBets from './pages/MyBets';
import Leaderboard from './pages/Leaderboard';
import Account from './pages/Account';
import Login from './pages/Login';
import Register from './pages/Register';
import Admin from './pages/Admin';

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    fetch('/api/auth/me')
      .then(r => r.json())
      .then(data => {
        if (data.id) setCurrentUser(data);
      })
      .catch(e => console.log('Not logged in'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <BrowserRouter>
      <Navigation user={currentUser} onLogout={() => setCurrentUser(null)} />
      <Routes>
        {currentUser ? (
          <>
            <Route path="/" element={<Dashboard user={currentUser} />} />
            <Route path="/predictions" element={<Predictions user={currentUser} />} />
            <Route path="/my-bets" element={<MyBets user={currentUser} />} />
            <Route path="/leaderboard" element={<Leaderboard />} />
            <Route path="/account" element={<Account user={currentUser} setUser={setCurrentUser} />} />
            {['miltos@betedge.com', 'admin@betedge.com'].includes(currentUser.email) && (
              <Route path="/admin" element={<Admin />} />
            )}
          </>
        ) : (
          <>
            <Route path="/" element={<Login setUser={setCurrentUser} />} />
            <Route path="/register" element={<Register setUser={setCurrentUser} />} />
          </>
        )}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
