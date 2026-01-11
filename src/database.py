import sqlite3
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "courses.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT NOT NULL,
            course_number TEXT NOT NULL,
            raw_data TEXT NOT NULL,
            UNIQUE(term, course_number)
        )
    ''')
    conn.commit()
    conn.close()


def course_exists(term, course_number):
    """Check if course data exists for a term."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT 1 FROM courses WHERE term = ? AND course_number = ?',
        (term, course_number)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


def save_course(term, course_number, raw_data):
    """Save course data to database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO courses (term, course_number, raw_data)
        VALUES (?, ?, ?)
    ''', (term, course_number, raw_data))
    conn.commit()
    conn.close()


def get_course(term, course_number):
    """Get course data from database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT raw_data FROM courses WHERE term = ? AND course_number = ?',
        (term, course_number)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_all_courses_for_term(term, course_numbers):
    """Get all course data for a term and list of course numbers."""
    conn = get_connection()
    cursor = conn.cursor()
    placeholders = ','.join('?' * len(course_numbers))
    cursor.execute(
        f'SELECT raw_data FROM courses WHERE term = ? AND course_number IN ({placeholders})',
        (term, *course_numbers)
    )
    results = cursor.fetchall()
    conn.close()
    return '\n'.join(r[0] for r in results)
