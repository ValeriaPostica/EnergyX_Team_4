import React, { useEffect, useState } from "react";
import "./Leaderboard.css";
import { fetchWithAuth } from '../utils/api';

function Leaderboard() {
  const [currentUser, setCurrentUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch both current user and leaderboard in parallel
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch current user
        const userResponse = await fetchWithAuth('http://localhost:5000/auth/verify');
        if (userResponse.ok) {
          const userData = await userResponse.json();
          setCurrentUser(userData.user.username);
          
          // Now fetch leaderboard with the current user available
          const leaderboardResponse = await fetch("http://localhost:5000/leaderboard");
          const leaderboardData = await leaderboardResponse.json();
          console.log("Current user:", userData.user.username);
          console.log("Leaderboard users:", leaderboardData.leaderboard);
          setUsers(leaderboardData.leaderboard || []);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getMedal = (rank) => {
    if (rank === 1) return "🥇";
    if (rank === 2) return "🥈";
    if (rank === 3) return "🥉";
    return `#${rank}`;
  };

  if (loading) {
    return (
      <div className="leaderboard-container">
        <div style={{textAlign: 'center', padding: '20px', color: '#666'}}>
          Loading leaderboard...
        </div>
      </div>
    );
  }

  return (
    <div className="leaderboard-container">
      <h2 className="leaderboard-title">🏆Top energy users</h2>
      <p className="leaderboard-subtitle">
        Compete with other users to save energy and climb the leaderboard!
      </p>

      <ul className="leaderboard-list">
        {users.map((u, i) => (
          <li
            key={i}
            className={`leaderboard-item ${
              u.username === currentUser ? "highlight" : ""
            }`}
          >
            <span className="rank">{getMedal(i + 1)}</span>
            <span className="name">{u.username}</span>
            <span className="points">{u.points} ⚡︎</span>
          </li>
        ))}
      </ul>

      {/* Add this empty state for better UX */}
      {users.length === 0 && (
        <div style={{textAlign: 'center', padding: '20px', color: '#666'}}>
          Loading leaderboard...
        </div>
      )}

      <div className="leaderboard-footer">
        🌱Save energy daily to climb to the top!
      </div>
    </div>
  );
}

export default Leaderboard;