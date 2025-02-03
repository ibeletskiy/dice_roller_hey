import sqlite3

PATH = '/home/ibeletskiy/rollerDiceBot/dnd_bot.db'

class DataBase:

    def __init__(self):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, delete_time INTEGER DEFAULT 60)''')
        conn.commit()
        conn.close()

    def add_user(self, username):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (username, delete_time) VALUES (?, ?)", (username, 60))
        conn.commit()
        conn.close()

    def set_delete_time(self, username, time):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET delete_time = ? WHERE username = ?", (time, username))
        conn.commit()
        conn.close()

    def get_delete_time(self, username):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()
        c.execute("SELECT delete_time FROM users WHERE username = ?", (username,))
        time = c.fetchone()
        conn.close()
        return time[0] if time else 60
