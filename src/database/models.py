""""""

Database models and schema definitionsDatabase Models - SQLAlchemy ORM models

""""""



from dataclasses import dataclassfrom sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float, Boolean

from typing import Optionalfrom sqlalchemy.ext.declarative import declarative_base

from datetime import datetimefrom sqlalchemy.orm import relationship

from datetime import datetime



@dataclassBase = declarative_base()

class Profile:

    """Team member profile model"""

    id: Optional[int] = Noneclass Category(Base):

    name: str = ""    """Categories for organizing knowledge items"""

    role: str = ""    __tablename__ = 'categories'

    bio: Optional[str] = None    

    photo_url: Optional[str] = None    id = Column(Integer, primary_key=True)

    contact: Optional[str] = None    name = Column(String(100), unique=True, nullable=False)

    phone: Optional[str] = None    description = Column(Text)

    linkedin: Optional[str] = None    created_at = Column(DateTime, default=datetime.utcnow)

    twitter: Optional[str] = None    

    department: Optional[str] = None    # Relationships

    profile_url: Optional[str] = None    items = relationship('KnowledgeItem', back_populates='category')

    embedding: Optional[str] = None  # JSON string of vector    

    created_at: Optional[datetime] = None    def __repr__(self):

    updated_at: Optional[datetime] = None        return f"<Category(name='{self.name}')>"

    

    def to_dict(self):

        """Convert to dictionary"""class KnowledgeItem(Base):

        return {    """Main knowledge storage model"""

            'id': self.id,    __tablename__ = 'knowledge_items'

            'name': self.name,    

            'role': self.role,    id = Column(Integer, primary_key=True)

            'bio': self.bio,    title = Column(String(500), nullable=False)

            'photo_url': self.photo_url,    content = Column(Text, nullable=False)

            'contact': self.contact,    url = Column(String(1000), unique=True)

            'phone': self.phone,    source_type = Column(String(50))  # profile, article, documentation, etc.

            'linkedin': self.linkedin,    

            'twitter': self.twitter,    # Metadata

            'department': self.department,    metadata = Column(JSON)

            'profile_url': self.profile_url,    category_id = Column(Integer, ForeignKey('categories.id'))

            'embedding': self.embedding    

        }    # Profile-specific fields

        fingerprint = Column(String(32))  # MD5 hash for duplicate detection

    @classmethod    confidence_score = Column(Float)  # Extraction confidence (0-1)

    def from_dict(cls, data: dict):    is_duplicate = Column(Boolean, default=False)

        """Create from dictionary"""    parent_id = Column(Integer, ForeignKey('knowledge_items.id'))  # For duplicate merging

        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})    

    # Timestamps

    created_at = Column(DateTime, default=datetime.utcnow)

# Database schema SQL    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

PROFILES_TABLE_SQL = """    last_scraped = Column(DateTime)

CREATE TABLE IF NOT EXISTS profiles (    

    id INTEGER PRIMARY KEY AUTOINCREMENT,    # Relationships

    name TEXT NOT NULL,    category = relationship('Category', back_populates='items')

    role TEXT NOT NULL,    search_indices = relationship('SearchIndex', back_populates='knowledge_item', cascade='all, delete-orphan')

    bio TEXT,    parent = relationship('KnowledgeItem', remote_side=[id], backref='duplicates')

    photo_url TEXT,    

    contact TEXT,    def __repr__(self):

    phone TEXT,        return f"<KnowledgeItem(title='{self.title}', url='{self.url}')>"

    linkedin TEXT,

    twitter TEXT,

    department TEXT,class SearchIndex(Base):

    profile_url TEXT,    """Vector embeddings and search indices"""

    embedding TEXT,    __tablename__ = 'search_indices'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP    id = Column(Integer, primary_key=True)

)    knowledge_item_id = Column(Integer, ForeignKey('knowledge_items.id'), nullable=False)

"""    

    # Vector embedding

PROFILES_FTS_SQL = """    embedding = Column(JSON)  # Store as JSON array

CREATE VIRTUAL TABLE IF NOT EXISTS profiles_fts USING fts5(    embedding_model = Column(String(100))  # Model used for embedding

    name,    

    role,    # Full-text search fields

    bio,    text_content = Column(Text)

    department,    

    content=profiles,    # Metadata for search

    content_rowid=id    scope = Column(String(100))  # For scope-limited search

)    relevance_score = Column(Float)

"""    

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    knowledge_item = relationship('KnowledgeItem', back_populates='search_indices')
    
    def __repr__(self):
        return f"<SearchIndex(item_id={self.knowledge_item_id}, model='{self.embedding_model}')>"


class ChatHistory(Base):
    """Store chat interactions for context"""
    __tablename__ = 'chat_history'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    scope = Column(String(100))  # Scope of the conversation
    
    # Context information
    referenced_items = Column(JSON)  # IDs of knowledge items referenced
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ChatHistory(session='{self.session_id}', at='{self.created_at}')>"
