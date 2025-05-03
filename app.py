from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_conn():
    return sqlite3.connect("game.db")

@app.route("/")
def index():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id, wins, losses, draws, games FROM users ORDER BY wins DESC LIMIT 10")
    players = cur.fetchall()
    conn.close()
    return render_template("index.html", players=players)

@app.route("/player/<int:user_id>")
def player(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT wins, losses, draws, games FROM users WHERE user_id = ?", (user_id,))
    stats = cur.fetchone()
    cur.execute("""
        SELECT player1_move, player2_move, result, created_at, player1_id, player2_id
        FROM games
        WHERE player1_id = ? OR player2_id = ?
        ORDER BY created_at DESC LIMIT 20
    """, (user_id, user_id))
    history = cur.fetchall()
    conn.close()
    return render_template("player.html", user_id=user_id, stats=stats, history=history)

if __name__ == "__main__":
    app.run(debug=True)
