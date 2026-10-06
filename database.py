import sqlite3

DB = "influencers.db"


def create_db():
    conn = sqlite3.connect(DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS influencers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            platform TEXT,
            username TEXT,
            followers TEXT,
            category TEXT,
            location TEXT,
            profile_url TEXT UNIQUE,
            email TEXT,
            description TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_influencer(data):
    conn = sqlite3.connect(DB)

    try:
        conn.execute("""
            INSERT OR IGNORE INTO influencers
            (name, platform, username, followers,
             category, location, profile_url,
             email, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("name"),
            data.get("platform"),
            data.get("username"),
            data.get("followers"),
            data.get("category"),
            data.get("location"),
            data.get("profile_url"),
            data.get("email"),
            data.get("description")
        ))

        conn.commit()

    finally:
        conn.close()


def get_influencers():
    conn = sqlite3.connect(DB)

    rows = conn.execute("""
        SELECT * FROM influencers
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return rows


create_db()