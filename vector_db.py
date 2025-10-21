"""
Vector Database with OpenAI Embeddings for Enhanced Q&A
Uses OpenAI's text-embedding-3-small model for semantic search
"""

import openai
import numpy as np
import sqlite3
import logging
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please create a .env file with your API key.")
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_PATH = "data/leadership.db"


def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Get embedding for text using OpenAI API.
    
    Args:
        text: Text to embed
        model: OpenAI embedding model
        
    Returns:
        List of embedding values
    """
    try:
        # Clean and prepare text
        text = text.replace("\n", " ").strip()
        if not text:
            return []
        
        response = openai.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error getting embedding: {e}")
        return []


def create_profile_embedding(profile: Dict[str, Any]) -> str:
    """
    Create a comprehensive text representation of a profile for embedding.
    
    Args:
        profile: Profile dictionary
        
    Returns:
        Combined text for embedding
    """
    parts = []
    
    # Name and role
    if profile.get('name'):
        parts.append(f"Name: {profile['name']}")
    if profile.get('role'):
        parts.append(f"Role: {profile['role']}")
    if profile.get('department'):
        parts.append(f"Department: {profile['department']}")
    
    # Bio (most important for semantic search)
    if profile.get('bio'):
        parts.append(f"Biography: {profile['bio']}")
    
    # Contact information
    if profile.get('contact'):
        parts.append(f"Email: {profile['contact']}")
    if profile.get('linkedin'):
        parts.append(f"LinkedIn: {profile['linkedin']}")
    
    return " | ".join(parts)


def update_vector_database(db_path: str = DATABASE_PATH) -> None:
    """
    Update the vector database with embeddings for all profiles.
    
    Args:
        db_path: Path to SQLite database
    """
    logger.info("Updating vector database with OpenAI embeddings...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add embedding column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE profiles ADD COLUMN embedding TEXT")
        conn.commit()
        logger.info("Added embedding column to database")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    # Get all profiles
    cursor.execute("SELECT id, name, role, bio, department, contact, linkedin FROM profiles")
    profiles = cursor.fetchall()
    
    updated_count = 0
    for profile_data in profiles:
        profile_id = profile_data[0]
        profile = {
            'name': profile_data[1],
            'role': profile_data[2],
            'bio': profile_data[3],
            'department': profile_data[4],
            'contact': profile_data[5],
            'linkedin': profile_data[6]
        }
        
        # Create embedding text
        embedding_text = create_profile_embedding(profile)
        
        # Get embedding
        embedding = get_embedding(embedding_text)
        
        if embedding:
            # Store embedding as JSON
            embedding_json = json.dumps(embedding)
            cursor.execute(
                "UPDATE profiles SET embedding = ? WHERE id = ?",
                (embedding_json, profile_id)
            )
            updated_count += 1
            logger.info(f"Updated embedding for: {profile['name']}")
    
    conn.commit()
    conn.close()
    
    logger.info(f"Updated {updated_count} profile embeddings")


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not a or not b:
        return 0.0
    
    a = np.array(a)
    b = np.array(b)
    
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def vector_search_profiles(query: str, limit: int = 5, db_path: str = DATABASE_PATH) -> List[Dict[str, Any]]:
    """
    Search profiles using vector similarity with OpenAI embeddings.
    
    Args:
        query: Search query
        limit: Maximum number of results
        db_path: Path to SQLite database
        
    Returns:
        List of matching profiles with similarity scores
    """
    logger.info(f"Vector search for: {query}")
    
    # Get query embedding
    query_embedding = get_embedding(query)
    if not query_embedding:
        logger.error("Could not get embedding for query")
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all profiles with embeddings
    cursor.execute("""
        SELECT id, name, role, bio, photo_url, contact, phone, linkedin, twitter, 
               department, profile_url, embedding
        FROM profiles 
        WHERE embedding IS NOT NULL
    """)
    
    profiles = cursor.fetchall()
    conn.close()
    
    if not profiles:
        logger.warning("No profiles with embeddings found")
        return []
    
    # Calculate similarities
    results = []
    for profile_data in profiles:
        embedding_json = profile_data[11]  # embedding column
        
        try:
            profile_embedding = json.loads(embedding_json)
            similarity = cosine_similarity(query_embedding, profile_embedding)
            
            profile = {
                'id': profile_data[0],
                'name': profile_data[1],
                'role': profile_data[2],
                'bio': profile_data[3],
                'photo_url': profile_data[4],
                'contact': profile_data[5],
                'phone': profile_data[6],
                'linkedin': profile_data[7],
                'twitter': profile_data[8],
                'department': profile_data[9],
                'profile_url': profile_data[10],
                'similarity': similarity
            }
            
            results.append(profile)
            
        except Exception as e:
            logger.error(f"Error processing embedding for profile {profile_data[1]}: {e}")
            continue
    
    # Sort by similarity and return top results
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    logger.info(f"Found {len(results)} results, returning top {limit}")
    return results[:limit]


def generate_ai_answer(query: str, profiles: List[Dict[str, Any]]) -> str:
    """
    Generate an AI-powered answer using OpenAI with relevant profiles.
    
    Args:
        query: User question
        profiles: Relevant profiles from vector search
        
    Returns:
        AI-generated answer with proper formatting
    """
    if not profiles:
        return "I couldn't find any relevant team members for your question."
    
    # Prepare context from profiles (clean format without boxes)
    context = ""
    for i, profile in enumerate(profiles, 1):
        context += f"Person {i}: {profile['name']}\n"
        if profile.get('role'):
            context += f"Position: {profile['role']}\n"
        if profile.get('department'):
            context += f"Department: {profile['department']}\n"
        if profile.get('bio'):
            bio_preview = profile['bio'][:300] + "..." if len(profile['bio']) > 300 else profile['bio']
            context += f"Background: {bio_preview}\n"
        if profile.get('contact'):
            context += f"Email: {profile['contact']}\n"
        if profile.get('linkedin'):
            context += f"LinkedIn: {profile['linkedin']}\n"
        context += "\n"
    
    # Create prompt for OpenAI
    prompt = f"""Based on the team member information below, answer the user's question in a clean, professional way.

Question: {query}

Team Information:
{context}

CRITICAL INSTRUCTIONS:
- Write EVERYTHING as a single flowing response
- DO NOT use headers, titles, or role names as separate lines
- Integrate the person's name and role naturally into your sentence
- Example: "Kamesh Doddi is the Head of Managed Infrastructure Services at Amzur Technologies..."
- Keep it conversational and natural
- NO separate headers or title lines
- Include LinkedIn profile link if available

Answer:"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful corporate assistant. Write EVERYTHING in flowing paragraphs. NEVER put a person's name or role as a header. Always integrate their name and title naturally into sentences. Example: 'John Smith is the CEO of...' NOT 'CEO\n\nJohn Smith is...' Be professional and conversational."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Add photo information if the answer is about a specific person
        # IMPROVED: Check if answer mentions a single person prominently
        query_lower = query.lower()
        answer_lower = answer.lower()
        
        # Keywords that suggest asking about a person
        single_person_keywords = ['who is', 'about', 'tell me', 'show me', 'give me', 'what about', 
                                   'describe', 'info on', 'details', 'information about', 'photo of', 'picture of']
        
        # Role-specific queries (asking for someone by title)
        role_keywords = ['head of', 'director', 'ceo', 'cto', 'president', 'vice president', 
                         'manager', 'lead', 'chief', 'architect', 'executive']
        
        has_person_keyword = any(keyword in query_lower for keyword in single_person_keywords)
        has_role_keyword = any(keyword in query_lower for keyword in role_keywords)
        
        # Check if answer prominently features the first profile's name (mentioned early in answer)
        first_person_mentioned = False
        if profiles and profiles[0].get('name'):
            name_parts = profiles[0]['name'].lower().split()
            # Check if name is mentioned in first 150 characters (early in answer = focused on them)
            first_person_mentioned = any(part in answer_lower[:150] for part in name_parts if len(part) > 3)
        
        # Show photo if:
        # 1. Only one profile found, OR
        # 2. Query has person-specific keywords, OR
        # 3. Query asks for a role AND answer focuses on that person, OR
        # 4. Person's name is mentioned prominently in answer
        should_show_photo = (
            len(profiles) == 1 or 
            has_person_keyword or
            (has_role_keyword and first_person_mentioned) or
            first_person_mentioned
        )
        
        if should_show_photo and profiles:
            # Add photo URL for the first/most relevant profile
            profile = profiles[0]
            if profile.get('photo_url'):
                answer += f"\n\n📸PHOTO📸{profile['photo_url']}"
            else:
                # Log if photo is missing for debugging
                logger.warning(f"No photo URL available for {profile.get('name', 'Unknown')}")
        
        return answer
        
    except Exception as e:
        logger.error(f"Error generating AI answer: {e}")
        # Fallback to simple clean answer
        response = f"I found {len(profiles)} relevant team member(s):\n\n"
        for i, profile in enumerate(profiles[:3], 1):
            response += f"**{profile['name']}**"
            if profile.get('role'):
                response += f" - {profile['role']}"
            response += "\n"
            if profile.get('department'):
                response += f"Department: {profile['department']}\n"
            if profile.get('bio'):
                bio_short = profile['bio'][:150] + "..." if len(profile['bio']) > 150 else profile['bio']
                response += f"{bio_short}\n"
            response += "\n"
        
        # Add photo for single person using same marker
        if len(profiles) == 1 and profiles[0].get('photo_url'):
            response += f"📸PHOTO📸{profiles[0]['photo_url']}"
        
        return response


if __name__ == "__main__":
    # Test the vector database
    print("Testing vector database...")
    
    # Update embeddings
    update_vector_database()
    
    # Test search
    test_queries = [
        "Who is the CEO?",
        "Show me technology leaders",
        "Who handles artificial intelligence?",
        "Marketing team members"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = vector_search_profiles(query, limit=3)
        for i, profile in enumerate(results, 1):
            print(f"  {i}. {profile['name']} - {profile.get('role', 'N/A')} (similarity: {profile.get('similarity', 0):.3f})")