import sqlite3

DATABASE_NAME = "database.db"

def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():

    conn = get_db()

    # Users Table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        full_name TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        role TEXT NOT NULL,

        phone TEXT,

        city TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # Jobs Table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS jobs(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        company_name TEXT NOT NULL,

        job_title TEXT NOT NULL,

        location TEXT NOT NULL,

        job_type TEXT NOT NULL,

        salary TEXT NOT NULL,

        description TEXT NOT NULL,

        posted_by INTEGER,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(posted_by) REFERENCES users(id)

    )
    """)

    conn.commit()
    conn.close()