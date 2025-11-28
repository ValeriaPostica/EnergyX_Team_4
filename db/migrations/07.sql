CREATE TABLE IF NOT EXISTS leaderboard (
    leaderboard_id VARCHAR(100) PRIMARY KEY,
    user_id INT,
    points INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE OR REPLACE VIEW v_leaderboard AS
	SELECT u.username,
	       l.points
    FROM leaderboard l
    JOIN users u ON u.id = l.user_id;

