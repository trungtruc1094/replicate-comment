import sqlite3
import os
import logging

def initialize_database():
    """Create a temporary SQLite database to store comments."""
    conn = sqlite3.connect('comments.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS comments
                 (id TEXT PRIMARY KEY, text TEXT, sent INTEGER)''')
    conn.commit()
    return conn

def store_comments(conn, comments):
    """Store new comments in the SQLite database."""
    logging.info(f"Storing {len(comments)} comments to the database.")
    c = conn.cursor()
    for unique_id, text in comments:
        try:
            c.execute('''INSERT OR IGNORE INTO comments (id, text, sent)
                         VALUES (?, ?, 0)''', (unique_id, text))
            logging.info(f"Stored comment ID: {unique_id} - Text: {text}")
        except Exception as e:
            logging.error(f"Failed to store comment ID: {unique_id} - Text: {text}. Error: {e}")
    conn.commit()
    logging.info("All comments stored successfully.")

def get_unsent_comments(conn):
    """Retrieve all unsent comments from the database."""
    logging.info("Retrieving unsent comments from the database.")
    c = conn.cursor()
    try:
        c.execute('SELECT id, text FROM comments WHERE sent=0')
        unsent_comments = c.fetchall()
        logging.info(f"Retrieved {len(unsent_comments)} unsent comments.")
    except Exception as e:
        logging.error(f"Error retrieving unsent comments: {e}")
        unsent_comments = []
    return unsent_comments

def mark_comment_as_sent(conn, unique_id):
    """Mark a comment as sent in the database."""
    logging.info(f"Marking comment ID {unique_id} as sent.")
    c = conn.cursor()
    try:
        c.execute('UPDATE comments SET sent = 1 WHERE id = ?', (unique_id,))
        conn.commit()
        logging.info(f"Comment ID {unique_id} marked as sent successfully.")
    except Exception as e:
        logging.error(f"Failed to mark comment ID {unique_id} as sent. Error: {e}")


def close_database(conn):
    """Close the SQLite database."""
    conn.close()

def delete_database():
    """Delete the SQLite database file."""
    if os.path.exists('comments.db'):
        os.remove('comments.db')
        logging.info("Database file deleted.")
    else:
        logging.info("No database file found to delete.")
