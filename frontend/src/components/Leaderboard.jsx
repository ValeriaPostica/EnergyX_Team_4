import React from "react";
import "./Leaderboard.css";

function Leaderboard() {
  const currentUser = "Ioana Vasilescu"; 

  const users = [
    { name: "Maria Ionescu", points: 150 },
    { name: "Ion Georgescu", points: 140 },
    { name: "Ioana Vasilescu", points: 135 }, 
    { name: "Elena Radu", points: 120 },
    { name: "Gabriel Marinescu", points: 115 },
    { name: "Ana Dumitrescu", points: 100 },
    { name: "Vlad Mihăilescu", points: 95 },
    { name: "Cristina Dobre", points: 90 },
  ];

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
            <span className="name">{u.name}</span>
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
