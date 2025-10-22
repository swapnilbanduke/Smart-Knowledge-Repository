""""""

Smart Knowledge Repository - Main Application Entry PointMain Streamlit Application

Refactored with modular architectureMulti-page app for Smart Knowledge Repository

""""""



import streamlit as stimport streamlit as st

import sysimport sys

import osimport os

import logging

# Add src to Python pathfrom pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Add src to path

# Import from new modular structureproject_root = Path(__file__).parent

from services.knowledge_service import KnowledgeServicesys.path.insert(0, str(project_root))

from services.chat_service import ChatService  

from services.scraping_service import ScrapingServicefrom src.database.migrations import initialize_database

from src.search.vector_search import VectorSearch

# For now, import the old UI until we fully migratefrom src.search.indexing import ContentIndexer

import dynamic_chat_appfrom src.scrapers.profile_scraper import ProfileScraper

from src.scrapers.content_discovery import ContentDiscovery

# Run the existing appfrom src.services.knowledge_service import KnowledgeService

if __name__ == "__main__":from src.services.chat_service import ChatService

    dynamic_chat_app  # This will run the Streamlit appfrom src.services.scraping_service import ScrapingService


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Initialize services (cached for performance)
@st.cache_resource
def initialize_services():
    """Initialize all services"""
    logger.info("Initializing services...")
    
    # Database
    repository = initialize_database()
    
    # Search components
    vector_search = VectorSearch()
    indexer = ContentIndexer(repository, vector_search)
    
    # Scrapers
    profile_scraper = ProfileScraper()
    content_discovery = ContentDiscovery("config/scraping_targets.yaml")
    
    # Services
    knowledge_service = KnowledgeService(repository, vector_search, indexer)
    chat_service = ChatService(knowledge_service, repository)
    scraping_service = ScrapingService(profile_scraper, content_discovery, knowledge_service)
    
    logger.info("Services initialized successfully")
    
    return {
        'repository': repository,
        'vector_search': vector_search,
        'indexer': indexer,
        'knowledge_service': knowledge_service,
        'chat_service': chat_service,
        'scraping_service': scraping_service
    }


def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="Smart Knowledge Repository",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize services
    services = initialize_services()
    
    # Sidebar navigation
    st.sidebar.title("🧠 Smart Knowledge Repository")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigation",
        ["🤖 Chat Assistant", "📚 Browse & Search", "⚙️ Administration"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    # Display statistics in sidebar
    stats = services['knowledge_service'].get_statistics()
    st.sidebar.metric("Total Knowledge Items", stats['total_items'])
    st.sidebar.metric("Indexed Items", stats['indexed_items'])
    st.sidebar.metric("Index Coverage", f"{stats['index_coverage']:.1f}%")
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Version 1.0.0")
    
    # Route to appropriate page
    if page == "🤖 Chat Assistant":
        render_chat_page(services)
    elif page == "📚 Browse & Search":
        render_browse_page(services)
    elif page == "⚙️ Administration":
        render_admin_page(services)


def render_chat_page(services):
    """Render the chat interface page"""
    from src.ui.chat_interface import ChatInterface
    
    interface = ChatInterface(services['chat_service'])
    interface.render()


def render_browse_page(services):
    """Render the browse interface page"""
    from src.ui.browse_interface import BrowseInterface
    
    interface = BrowseInterface(services['knowledge_service'])
    interface.render()


def render_admin_page(services):
    """Render the admin interface page"""
    from src.ui.admin_interface import AdminInterface
    
    interface = AdminInterface(
        services['knowledge_service'],
        services['scraping_service']
    )
    interface.render()


if __name__ == "__main__":
    main()
