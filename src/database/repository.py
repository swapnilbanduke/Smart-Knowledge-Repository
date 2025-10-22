"""
SQLite Database with FTS5 for Leadership Profiles
Stores and searches leadership team data
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_PATH = "data/leadership.db"


def init_database(db_path: str = DATABASE_PATH) -> None:
    """
    Initialize SQLite database with profiles table and FTS5 search.
    
    Args:
        db_path: Path to SQLite database file
    """
    logger.info(f"Initializing database at {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create profiles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            bio TEXT,
            photo_url TEXT,
            contact TEXT,
            phone TEXT,
            linkedin TEXT,
            twitter TEXT,
            department TEXT,
            profile_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create FTS5 virtual table for full-text search
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS profiles_fts USING fts5(
            name,
            role,
            bio,
            department,
            content=profiles,
            content_rowid=id
        )
    """)
    
    # Create triggers to keep FTS5 table in sync
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS profiles_ai AFTER INSERT ON profiles BEGIN
            INSERT INTO profiles_fts(rowid, name, role, bio, department)
            VALUES (new.id, new.name, new.role, new.bio, new.department);
        END
    """)
    
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS profiles_ad AFTER DELETE ON profiles BEGIN
            INSERT INTO profiles_fts(profiles_fts, rowid, name, role, bio, department)
            VALUES('delete', old.id, old.name, old.role, old.bio, old.department);
        END
    """)
    
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS profiles_au AFTER UPDATE ON profiles BEGIN
            INSERT INTO profiles_fts(profiles_fts, rowid, name, role, bio, department)
            VALUES('delete', old.id, old.name, old.role, old.bio, old.department);
            INSERT INTO profiles_fts(rowid, name, role, bio, department)
            VALUES (new.id, new.name, new.role, new.bio, new.department);
        END
    """)
    
    # Create indexes for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_department ON profiles(department)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_role ON profiles(role)")
    
    conn.commit()
    conn.close()
    
    logger.info("Database initialized successfully")


def insert_profiles(profiles: List[Dict[str, Any]], db_path: str = DATABASE_PATH) -> int:
    """
    Insert leadership profiles into database.
    
    Args:
        profiles: List of profile dictionaries
        db_path: Path to SQLite database
        
    Returns:
        Number of profiles inserted
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    inserted = 0
    for profile in profiles:
        try:
            cursor.execute("""
                INSERT INTO profiles (name, role, bio, photo_url, contact, phone, linkedin, twitter, department, profile_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile.get('name', ''),
                profile.get('role', ''),
                profile.get('bio', ''),
                profile.get('photo_url', ''),
                profile.get('contact', ''),
                profile.get('phone', ''),
                profile.get('linkedin', ''),
                profile.get('twitter', ''),
                profile.get('department', ''),
                profile.get('profile_url', '')
            ))
            inserted += 1
        except sqlite3.Error as e:
            logger.error(f"Error inserting profile {profile.get('name')}: {e}")
    
    conn.commit()
    conn.close()
    
    logger.info(f"Inserted {inserted} profiles")
    return inserted


def search_profiles(query: str, department: Optional[str] = None, 
                   db_path: str = DATABASE_PATH) -> List[Dict[str, Any]]:
    """
    Search profiles using FTS5 full-text search.
    
    Args:
        query: Search query
        department: Optional department filter
        db_path: Path to SQLite database
        
    Returns:
        List of matching profiles with relevance scores
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if department:
        # Search with department filter
        cursor.execute("""
            SELECT p.*, 
                   bm25(profiles_fts) as rank
            FROM profiles p
            JOIN profiles_fts ON profiles_fts.rowid = p.id
            WHERE profiles_fts MATCH ?
              AND p.department = ?
            ORDER BY rank
        """, (query, department))
    else:
        # Search all profiles
        cursor.execute("""
            SELECT p.*, 
                   bm25(profiles_fts) as rank
            FROM profiles p
            JOIN profiles_fts ON profiles_fts.rowid = p.id
            WHERE profiles_fts MATCH ?
            ORDER BY rank
        """, (query,))
    
    results = []
    for row in cursor.fetchall():
        results.append(dict(row))
    
    conn.close()
    return results


def get_all_profiles(db_path: str = DATABASE_PATH) -> List[Dict[str, Any]]:
    """
    Get all profiles from database.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        List of all profiles
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM profiles ORDER BY name")
    
    results = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return results


def get_profiles_by_department(department: str, db_path: str = DATABASE_PATH) -> List[Dict[str, Any]]:
    """
    Get all profiles in a specific department.
    
    Args:
        department: Department name
        db_path: Path to SQLite database
        
    Returns:
        List of profiles in that department
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM profiles WHERE department = ? ORDER BY name", (department,))
    
    results = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return results


def get_departments(db_path: str = DATABASE_PATH) -> List[str]:
    """
    Get list of all departments.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        List of unique departments
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT department FROM profiles ORDER BY department")
    
    departments = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return departments


def clear_database(db_path: str = DATABASE_PATH) -> None:
    """
    Clear all profiles from database.
    
    Args:
        db_path: Path to SQLite database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM profiles")
    
    conn.commit()
    conn.close()
    
    logger.info("Database cleared")


def get_profile_count(db_path: str = DATABASE_PATH) -> int:
    """
    Get total number of profiles in database.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        Number of profiles
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM profiles")
    count = cursor.fetchone()[0]
    
    conn.close()
    return count


if __name__ == "__main__":
    # Test database creation
    print("🗄️  Creating SQLite database with FTS5...\n")
    
    init_database()
    
    print("✅ Database created successfully!")
    print(f"📍 Location: {DATABASE_PATH}")
