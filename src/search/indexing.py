""""""

Indexing module for vector embeddingsContent Indexing - Build and manage search indices

Handles creation and management of vector embeddings for semantic search"""

"""

import logging

import openaifrom typing import List, Dict, Optional

import numpy as npfrom datetime import datetime

import loggingimport os

from typing import List, Dict, Any, Optionalimport json

import os

from dotenv import load_dotenvlogger = logging.getLogger(__name__)



load_dotenv()

class ContentIndexer:

logging.basicConfig(level=logging.INFO)    """Build and manage search indices for knowledge items"""

logger = logging.getLogger(__name__)    

    def __init__(self, repository, vector_search):

# Configure OpenAI        """

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")        Initialize content indexer

if not OPENAI_API_KEY:        

    raise ValueError("OPENAI_API_KEY not found in environment variables")        Args:

openai.api_key = OPENAI_API_KEY            repository: KnowledgeRepository instance

            vector_search: VectorSearch instance

        """

def create_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:        self.repository = repository

    """        self.vector_search = vector_search

    Create an embedding vector for text using OpenAI's API.        self.index_path = "data/embeddings/"

            

    Args:        # Create embeddings directory if it doesn't exist

        text: Text to embed        os.makedirs(self.index_path, exist_ok=True)

        model: OpenAI embedding model to use    

            def index_knowledge_item(self, item_id: int) -> bool:

    Returns:        """

        List of floats representing the embedding vector        Create search index for a single knowledge item

    """        

    try:        Args:

        response = openai.embeddings.create(            item_id: ID of knowledge item to index

            input=text,            

            model=model        Returns:

        )            True if successful, False otherwise

        return response.data[0].embedding        """

    except Exception as e:        try:

        logger.error(f"Error creating embedding: {e}")            # Get knowledge item from database

        return []            session = self.repository.get_session()

            from database.models import KnowledgeItem

            

def create_embeddings_batch(texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:            item = session.query(KnowledgeItem).filter(

    """                KnowledgeItem.id == item_id

    Create embeddings for multiple texts in a batch.            ).first()

                

    Args:            if not item:

        texts: List of texts to embed                logger.error(f"Knowledge item {item_id} not found")

        model: OpenAI embedding model to use                session.close()

                        return False

    Returns:            

        List of embedding vectors            # Prepare text for embedding

    """            text_content = f"{item.title}\n\n{item.content}"

    try:            

        response = openai.embeddings.create(            # Generate embedding

            input=texts,            embedding = self.vector_search.generate_embedding(text_content)

            model=model            

        )            if not embedding:

        return [data.embedding for data in response.data]                logger.error(f"Failed to generate embedding for item {item_id}")

    except Exception as e:                session.close()

        logger.error(f"Error creating embeddings batch: {e}")                return False

        return []            

            # Get scope from category

            scope = item.category.name if item.category else 'general'

def create_profile_embedding(profile: Dict[str, Any]) -> List[float]:            

    """            # Add to database

    Create a comprehensive embedding for a profile.            self.repository.add_search_index(

    Combines name, role, bio, and department information.                knowledge_item_id=item_id,

                    embedding=embedding,

    Args:                embedding_model=self.vector_search.model_name,

        profile: Profile dictionary                text_content=text_content,

                        scope=scope

    Returns:            )

        Embedding vector for the profile            

    """            session.close()

    # Combine relevant fields for embedding            logger.info(f"Indexed knowledge item: {item_id}")

    text_parts = []            return True

                

    if profile.get('name'):        except Exception as e:

        text_parts.append(f"Name: {profile['name']}")            logger.error(f"Error indexing item {item_id}: {str(e)}")

    if profile.get('role'):            return False

        text_parts.append(f"Role: {profile['role']}")    

    if profile.get('department'):    def index_all_items(self, reindex: bool = False) -> Dict[str, int]:

        text_parts.append(f"Department: {profile['department']}")        """

    if profile.get('bio'):        Index all knowledge items

        text_parts.append(f"Bio: {profile['bio']}")        

            Args:

    combined_text = " | ".join(text_parts)            reindex: If True, recreate indices even if they exist

                

    if not combined_text:        Returns:

        logger.warning(f"Empty profile data for embedding: {profile.get('name', 'Unknown')}")            Dictionary with indexing statistics

        return []        """

            stats = {

    return create_embedding(combined_text)            'total': 0,

            'indexed': 0,

            'skipped': 0,

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:            'failed': 0

    """        }

    Calculate cosine similarity between two vectors.        

            try:

    Args:            # Get all knowledge items

        vec1: First vector            items = self.repository.get_all_knowledge_items(limit=10000)

        vec2: Second vector            stats['total'] = len(items)

                    

    Returns:            logger.info(f"Indexing {len(items)} knowledge items...")

        Cosine similarity score (0 to 1)            

    """            for item in items:

    if not vec1 or not vec2:                # Check if already indexed

        return 0.0                if not reindex:

                        session = self.repository.get_session()

    vec1_arr = np.array(vec1)                    from database.models import SearchIndex

    vec2_arr = np.array(vec2)                    

                        existing = session.query(SearchIndex).filter(

    dot_product = np.dot(vec1_arr, vec2_arr)                        SearchIndex.knowledge_item_id == item.id

    norm1 = np.linalg.norm(vec1_arr)                    ).first()

    norm2 = np.linalg.norm(vec2_arr)                    session.close()

                        

    if norm1 == 0 or norm2 == 0:                    if existing:

        return 0.0                        stats['skipped'] += 1

                            continue

    return float(dot_product / (norm1 * norm2))                

                # Index the item

                success = self.index_knowledge_item(item.id)

def update_index(profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:                

    """                if success:

    Update embeddings for a list of profiles.                    stats['indexed'] += 1

                    else:

    Args:                    stats['failed'] += 1

        profiles: List of profile dictionaries            

                    logger.info(f"Indexing complete: {stats}")

    Returns:            return stats

        List of profiles with updated embeddings            

    """        except Exception as e:

    logger.info(f"Updating embeddings for {len(profiles)} profiles...")            logger.error(f"Error in bulk indexing: {str(e)}")

                return stats

    updated_profiles = []    

    for profile in profiles:    def build_embedding_cache(self, scope: Optional[str] = None) -> Dict[int, List[float]]:

        embedding = create_profile_embedding(profile)        """

        if embedding:        Build in-memory cache of embeddings for fast search

            profile['embedding'] = embedding        

            updated_profiles.append(profile)        Args:

        else:            scope: Optional scope to filter by

            logger.warning(f"Failed to create embedding for: {profile.get('name', 'Unknown')}")            

            Returns:

    logger.info(f"✅ Successfully updated {len(updated_profiles)} embeddings")            Dictionary mapping item IDs to embeddings

    return updated_profiles        """

        session = self.repository.get_session()
        try:
            from database.models import SearchIndex
            
            query = session.query(SearchIndex)
            
            if scope:
                query = query.filter(SearchIndex.scope == scope)
            
            indices = query.all()
            
            cache = {
                index.knowledge_item_id: index.embedding
                for index in indices
                if index.embedding
            }
            
            logger.info(f"Built embedding cache with {len(cache)} items")
            return cache
            
        finally:
            session.close()
    
    def save_embedding_cache(self, cache: Dict[int, List[float]], 
                            filename: str = "embeddings_cache.json"):
        """Save embedding cache to file"""
        filepath = os.path.join(self.index_path, filename)
        self.vector_search.save_index(cache, filepath)
    
    def load_embedding_cache(self, filename: str = "embeddings_cache.json") -> Dict[int, List[float]]:
        """Load embedding cache from file"""
        filepath = os.path.join(self.index_path, filename)
        return self.vector_search.load_index(filepath)
    
    def get_index_stats(self) -> Dict[str, any]:
        """Get statistics about indexed content"""
        session = self.repository.get_session()
        try:
            from database.models import SearchIndex, KnowledgeItem
            
            total_items = session.query(KnowledgeItem).count()
            indexed_items = session.query(SearchIndex).count()
            
            # Get unique scopes
            scopes = session.query(SearchIndex.scope).distinct().all()
            scope_counts = {}
            
            for (scope,) in scopes:
                count = session.query(SearchIndex).filter(
                    SearchIndex.scope == scope
                ).count()
                scope_counts[scope or 'general'] = count
            
            stats = {
                'total_knowledge_items': total_items,
                'indexed_items': indexed_items,
                'coverage_percentage': (indexed_items / total_items * 100) if total_items > 0 else 0,
                'scope_distribution': scope_counts,
                'embedding_model': self.vector_search.model_name
            }
            
            return stats
            
        finally:
            session.close()
    
    def remove_stale_indices(self) -> int:
        """Remove indices for deleted knowledge items"""
        session = self.repository.get_session()
        removed = 0
        
        try:
            from database.models import SearchIndex, KnowledgeItem
            
            # Get all search indices
            indices = session.query(SearchIndex).all()
            
            for index in indices:
                # Check if knowledge item exists
                item = session.query(KnowledgeItem).filter(
                    KnowledgeItem.id == index.knowledge_item_id
                ).first()
                
                if not item:
                    session.delete(index)
                    removed += 1
            
            session.commit()
            logger.info(f"Removed {removed} stale indices")
            return removed
            
        except Exception as e:
            logger.error(f"Error removing stale indices: {str(e)}")
            session.rollback()
            return 0
        finally:
            session.close()
