""""""

Database migrations and schema updatesDatabase Migrations - Schema management

""""""



import sqlite3import logging

import loggingfrom sqlalchemy import inspect

from .models import Base

logger = logging.getLogger(__name__)from .repository import KnowledgeRepository



logger = logging.getLogger(__name__)

def run_migrations(db_path: str):

    """

    Run all database migrationsclass DatabaseMigration:

        """Handle database schema migrations"""

    Args:    

        db_path: Path to SQLite database    def __init__(self, repository: KnowledgeRepository):

    """        self.repository = repository

    conn = sqlite3.connect(db_path)        self.engine = repository.engine

    cursor = conn.cursor()    

        def create_all_tables(self):

    try:        """Create all tables from models"""

        # Migration 1: Create profiles table        Base.metadata.create_all(self.engine)

        cursor.execute("""        logger.info("All tables created successfully")

            CREATE TABLE IF NOT EXISTS profiles (    

                id INTEGER PRIMARY KEY AUTOINCREMENT,    def drop_all_tables(self):

                name TEXT NOT NULL,        """Drop all tables (use with caution!)"""

                role TEXT NOT NULL,        Base.metadata.drop_all(self.engine)

                bio TEXT,        logger.warning("All tables dropped")

                photo_url TEXT,    

                contact TEXT,    def reset_database(self):

                phone TEXT,        """Reset database - drop and recreate all tables"""

                linkedin TEXT,        self.drop_all_tables()

                twitter TEXT,        self.create_all_tables()

                department TEXT,        logger.info("Database reset completed")

                profile_url TEXT,    

                embedding TEXT,    def check_tables_exist(self) -> bool:

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,        """Check if all required tables exist"""

                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP        inspector = inspect(self.engine)

            )        existing_tables = inspector.get_table_names()

        """)        

                required_tables = [

        # Migration 2: Create FTS5 search table            'categories',

        cursor.execute("""            'knowledge_items',

            CREATE VIRTUAL TABLE IF NOT EXISTS profiles_fts USING fts5(            'search_indices',

                name,            'chat_history'

                role,        ]

                bio,        

                department,        all_exist = all(table in existing_tables for table in required_tables)

                content=profiles,        

                content_rowid=id        if all_exist:

            )            logger.info("All required tables exist")

        """)        else:

                    missing = [t for t in required_tables if t not in existing_tables]

        # Migration 3: Create triggers for FTS sync            logger.warning(f"Missing tables: {missing}")

        cursor.execute("""        

            CREATE TRIGGER IF NOT EXISTS profiles_ai AFTER INSERT ON profiles BEGIN        return all_exist

                INSERT INTO profiles_fts(rowid, name, role, bio, department)    

                VALUES (new.id, new.name, new.role, new.bio, new.department);    def seed_initial_data(self):

            END        """Seed initial categories and sample data"""

        """)        default_categories = [

                    ("articles", "Blog posts and articles"),

        cursor.execute("""            ("documentation", "Technical documentation"),

            CREATE TRIGGER IF NOT EXISTS profiles_ad AFTER DELETE ON profiles BEGIN            ("tutorials", "How-to guides and tutorials"),

                INSERT INTO profiles_fts(profiles_fts, rowid, name, role, bio, department)            ("general", "General knowledge items"),

                VALUES('delete', old.id, old.name, old.role, old.bio, old.department);            ("research", "Research papers and studies"),

            END            ("profiles", "Personal and professional profiles")

        """)        ]

                

        cursor.execute("""        for name, description in default_categories:

            CREATE TRIGGER IF NOT EXISTS profiles_au AFTER UPDATE ON profiles BEGIN            try:

                INSERT INTO profiles_fts(profiles_fts, rowid, name, role, bio, department)                existing = self.repository.get_category_by_name(name)

                VALUES('delete', old.id, old.name, old.role, old.bio, old.department);                if not existing:

                INSERT INTO profiles_fts(rowid, name, role, bio, department)                    self.repository.create_category(name, description)

                VALUES (new.id, new.name, new.role, new.bio, new.department);                    logger.info(f"Created category: {name}")

            END            except Exception as e:

        """)                logger.error(f"Error creating category {name}: {str(e)}")

                

        conn.commit()        logger.info("Initial data seeding completed")

        logger.info("✅ All migrations completed successfully")

        

    except Exception as e:def initialize_database(database_url: str = "sqlite:///data/knowledge.db") -> KnowledgeRepository:

        logger.error(f"Migration error: {e}")    """Initialize database with all tables and seed data"""

        conn.rollback()    repository = KnowledgeRepository(database_url)

        raise    migration = DatabaseMigration(repository)

    finally:    

        conn.close()    if not migration.check_tables_exist():

        migration.create_all_tables()
        migration.seed_initial_data()
    
    return repository
