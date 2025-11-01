import React, { useEffect, useState } from "react";
import "./Leaderboard.css";
import { fetchWithAuth } from '../utils/api'; //USE `fetchWithAuth` INSTEAD OF `fetch` - for token

function Leaderboard() {
  const currentUser = "Ioana Vasilescu";
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/leaderboard")
      .then((res) => res.json())
      .then((data) => {
        setUsers(data.leaderboard); // matches backend response shape
      })
      .catch((err) => console.error("Failed to load leaderboard:", err));
  }, []);

  const getMedal = (rank) => {
    if (rank === 1) return "🥇";
    if (rank === 2) return "🥈";
    if (rank === 3) return "🥉";
    return `#${rank}`;
  };

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
              u.name === currentUser ? "highlight" : ""
            }`}
          >
            <span className="rank">{getMedal(i + 1)}</span>
            <span className="name">{u.user}</span>
            <span className="points">{u.points} ⚡︎</span>
          </li>
        ))}
      </ul>

      <div className="leaderboard-footer">
        🌱Save energy daily to climb to the top!
      </div>
    </div>
  );
}

export default Leaderboard;
