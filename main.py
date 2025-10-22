""""""

Smart Knowledge Repository - Production VersionMain CLI Application

Modern modular architecture with service layer separationCommand-line interface for Smart Knowledge Repository

""""""



import streamlit as stimport argparse

import sysimport logging

import osimport sys

import loggingfrom pathlib import Path

from pathlib import Path

# Add src to path

# Add src to Python pathproject_root = Path(__file__).parent

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))sys.path.insert(0, str(project_root))



# Import servicesfrom src.database.migrations import initialize_database

from src.services.chat_service import ChatServicefrom src.search.vector_search import VectorSearch

from src.services.knowledge_service import KnowledgeServicefrom src.search.indexing import ContentIndexer

from src.services.scraping_service import ScrapingServicefrom src.scrapers.profile_scraper import ProfileScraper

from src.scrapers.content_discovery import ContentDiscovery

# Import UI modulesfrom src.services.knowledge_service import KnowledgeService

from src.ui.chat_interface import render_chat_interfacefrom src.services.chat_service import ChatService

from src.ui.browse_interface import render_browse_interfacefrom src.services.scraping_service import ScrapingService

from src.ui.admin_interface import render_admin_interface, render_quick_actions

# Setup logging

# Configure logginglogging.basicConfig(

logging.basicConfig(    level=logging.INFO,

    level=logging.INFO,    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

)logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)



# Page configurationclass KnowledgeCLI:

st.set_page_config(    """Command-line interface for knowledge repository"""

    page_title="Smart Knowledge Repository",    

    page_icon="🧠",    def __init__(self):

    layout="wide",        """Initialize CLI and services"""

    initial_sidebar_state="expanded"        logger.info("Initializing services...")

)        

        # Database

# Custom CSS for modern UI        self.repository = initialize_database()

st.markdown("""        

<style>        # Search components

    /* Modern color scheme */        self.vector_search = VectorSearch()

    :root {        self.indexer = ContentIndexer(self.repository, self.vector_search)

        --primary-color: #667eea;        

        --secondary-color: #764ba2;        # Scrapers

    }        self.profile_scraper = ProfileScraper()

            self.content_discovery = ContentDiscovery("config/scraping_targets.yaml")

    /* Clean chat interface */        

    .stChatMessage {        # Services

        background-color: transparent !important;        self.knowledge_service = KnowledgeService(

        border: none !important;            self.repository, self.vector_search, self.indexer

        padding: 1rem 0 !important;        )

    }        self.chat_service = ChatService(self.knowledge_service, self.repository)

            self.scraping_service = ScrapingService(

    /* Profile card styling */            self.profile_scraper, self.content_discovery, self.knowledge_service

    .profile-card {        )

        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);        

        padding: 1.5rem;        logger.info("Services initialized")

        border-radius: 12px;    

        margin-bottom: 1.5rem;    def add_knowledge(self, args):

        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);        """Add knowledge item manually"""

        color: white;        item_id = self.knowledge_service.add_knowledge(

    }            title=args.title,

                content=args.content,

    .profile-name {            url=args.url,

        font-size: 1.5rem;            source_type=args.source_type or 'manual',

        font-weight: bold;            category=args.category or 'general',

        color: white;            auto_index=not args.no_index

        margin-bottom: 0.5rem;        )

    }        

            if item_id:

    .profile-role {            print(f"✓ Knowledge item added successfully! (ID: {item_id})")

        font-size: 1.1rem;        else:

        color: rgba(255, 255, 255, 0.9);            print("✗ Failed to add knowledge item")

        margin-bottom: 0.5rem;            sys.exit(1)

    }    

        def search_knowledge(self, args):

    .department-badge {        """Search knowledge base"""

        display: inline-block;        results = self.knowledge_service.search_knowledge(

        background: rgba(255, 255, 255, 0.2);            query=args.query,

        color: white;            scope=args.scope,

        padding: 0.25rem 0.75rem;            top_k=args.top_k,

        border-radius: 1rem;            use_semantic=not args.text_only

        font-size: 0.9rem;        )

        margin-top: 0.5rem;        

        backdrop-filter: blur(10px);        if not results:

    }            print("No results found")

                return

    /* Photo container */        

    .photo-container {        print(f"\nFound {len(results)} results:\n")

        margin: 1.5rem 0;        

        text-align: center;        for i, result in enumerate(results, 1):

    }            print(f"{i}. {result['title']}")

                if result.get('similarity_score'):

    .photo-container img {                print(f"   Score: {result['similarity_score']}")

        max-width: 300px;            print(f"   Category: {result.get('category', 'N/A')}")

        border-radius: 12px;            if result.get('url'):

        box-shadow: 0 8px 16px rgba(0,0,0,0.15);                print(f"   URL: {result['url']}")

        transition: transform 0.3s ease;            print(f"   Content: {result['content'][:200]}...")

    }            print()

        

    .photo-container img:hover {    def scrape_url(self, args):

        transform: scale(1.05);        """Scrape a URL"""

    }        print(f"Scraping {args.url}...")

            

    /* Sidebar styling */        item_id = self.scraping_service.scrape_url(

    .css-1d391kg {            url=args.url,

        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);            category=args.category

    }        )

            

    /* Metrics */        if item_id:

    [data-testid="stMetricValue"] {            print(f"✓ Successfully scraped and added! (ID: {item_id})")

        font-size: 2rem;        else:

        font-weight: bold;            print("✗ Failed to scrape URL")

    }            sys.exit(1)

        

    /* Buttons */    def scrape_batch(self, args):

    .stButton > button {        """Scrape multiple URLs"""

        border-radius: 8px;        with open(args.file, 'r') as f:

        font-weight: 500;            urls = [line.strip() for line in f if line.strip()]

        transition: all 0.3s ease;        

    }        print(f"Scraping {len(urls)} URLs...")

            

    .stButton > button:hover {        stats = self.scraping_service.scrape_multiple_urls(

        transform: translateY(-2px);            urls=urls,

        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);            category=args.category,

    }            max_workers=args.workers

</style>        )

""", unsafe_allow_html=True)        

        print(f"\nScraping complete!")

        print(f"  Total: {stats['total']}")

def initialize_services():        print(f"  Successful: {stats['successful']}")

    """Initialize all service instances."""        print(f"  Failed: {stats['failed']}")

    db_path = "data/leadership.db"    

        def scrape_config(self, args):

    # Initialize services        """Scrape from configuration file"""

    chat_service = ChatService(db_path=db_path)        print(f"Scraping from {args.config}...")

    knowledge_service = KnowledgeService(db_path=db_path)        

    scraping_service = ScrapingService(db_path=db_path)        stats = self.scraping_service.scrape_from_config(args.config)

            

    return chat_service, knowledge_service, scraping_service        if 'error' in stats:

            print(f"✗ Error: {stats['error']}")

            sys.exit(1)

def main():        

    """Main application entry point."""        print(f"\nScraping complete!")

            print(f"  Total: {stats['total']}")

    # Initialize services        print(f"  Successful: {stats['successful']}")

    chat_service, knowledge_service, scraping_service = initialize_services()        print(f"  Failed: {stats['failed']}")

        

    # Sidebar    def rebuild_index(self, args):

    with st.sidebar:        """Rebuild search index"""

        st.title("🧠 Smart Knowledge Repository")        print("Rebuilding search index...")

        st.markdown("### AI-Powered Team Intelligence")        

        st.markdown("---")        stats = self.knowledge_service.rebuild_search_index()

                

        # Quick stats        print(f"\nIndex rebuild complete!")

        total_profiles = knowledge_service.get_profile_count()        print(f"  Total: {stats['total']}")

        st.metric("📊 Profiles", total_profiles)        print(f"  Indexed: {stats['indexed']}")

                print(f"  Failed: {stats['failed']}")

        # Quick actions    

        render_quick_actions(scraping_service)    def show_stats(self, args):

            """Show repository statistics"""

    # Main content - Tabs        stats = self.knowledge_service.get_statistics()

    tab1, tab2, tab3 = st.tabs([        

        "💬 Chat",        print("\n=== Repository Statistics ===\n")

        "👥 Browse Profiles",        print(f"Total Items: {stats['total_items']}")

        "⚙️ Admin"        print(f"Categories: {stats['total_categories']}")

    ])        print(f"Indexed Items: {stats['indexed_items']}")

            print(f"Index Coverage: {stats['index_coverage']:.1f}%")

    with tab1:        print(f"Embedding Model: {stats['embedding_model']}")

        render_chat_interface(chat_service, knowledge_service)        

            print("\n=== Category Distribution ===\n")

    with tab2:        for category, count in stats['category_distribution'].items():

        render_browse_interface(knowledge_service)            print(f"  {category}: {count} items")

        

    with tab3:    def chat(self, args):

        render_admin_interface(scraping_service, knowledge_service)        """Interactive chat mode"""

            session_id = self.chat_service.create_session(scope=args.scope)

    # Footer        

    st.sidebar.markdown("---")        print("=== Knowledge Assistant ===")

    st.sidebar.markdown("""        print(f"Scope: {args.scope or 'All categories'}")

        <div style='text-align: center; color: #666; font-size: 0.8rem;'>        print("Type 'exit' or 'quit' to end the session\n")

            <p>🚀 Production v2.0</p>        

            <p>Modular Architecture</p>        while True:

        </div>            try:

    """, unsafe_allow_html=True)                user_input = input("You: ").strip()

                

                if user_input.lower() in ['exit', 'quit', 'q']:

if __name__ == "__main__":                    print("Goodbye!")

    try:                    break

        main()                

    except Exception as e:                if not user_input:

        logger.error(f"Application error: {e}", exc_info=True)                    continue

        st.error(f"❌ Application Error: {str(e)}")                

        st.info("Please check the logs for more details.")                response = self.chat_service.chat(session_id, user_input)

                
                print(f"\nAssistant: {response['response']}\n")
                
                if response.get('referenced_knowledge'):
                    print("Referenced Knowledge:")
                    for ref in response['referenced_knowledge']:
                        print(f"  - {ref['title']} (Score: {ref.get('similarity_score', 'N/A')})")
                    print()
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {str(e)}\n")
        
        self.chat_service.end_session(session_id)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Smart Knowledge Repository CLI"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add knowledge command
    add_parser = subparsers.add_parser('add', help='Add knowledge item')
    add_parser.add_argument('--title', required=True, help='Title')
    add_parser.add_argument('--content', required=True, help='Content')
    add_parser.add_argument('--url', help='Source URL')
    add_parser.add_argument('--category', help='Category')
    add_parser.add_argument('--source-type', help='Source type')
    add_parser.add_argument('--no-index', action='store_true', help='Skip indexing')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search knowledge')
    search_parser.add_argument('--query', required=True, help='Search query')
    search_parser.add_argument('--scope', help='Category scope')
    search_parser.add_argument('--top-k', type=int, default=5, help='Number of results')
    search_parser.add_argument('--text-only', action='store_true', help='Use text search')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape URL')
    scrape_parser.add_argument('--url', required=True, help='URL to scrape')
    scrape_parser.add_argument('--category', help='Category')
    
    # Batch scrape command
    batch_parser = subparsers.add_parser('batch-scrape', help='Scrape multiple URLs')
    batch_parser.add_argument('--file', required=True, help='File with URLs (one per line)')
    batch_parser.add_argument('--category', help='Category')
    batch_parser.add_argument('--workers', type=int, default=5, help='Concurrent workers')
    
    # Config scrape command
    config_parser = subparsers.add_parser('scrape-config', help='Scrape from config')
    config_parser.add_argument('--config', default='config/scraping_targets.yaml', help='Config file')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Manage search index')
    index_parser.add_argument('--rebuild', action='store_true', help='Rebuild index')
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics')
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Interactive chat')
    chat_parser.add_argument('--scope', help='Knowledge scope')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize CLI
    cli = KnowledgeCLI()
    
    # Execute command
    if args.command == 'add':
        cli.add_knowledge(args)
    elif args.command == 'search':
        cli.search_knowledge(args)
    elif args.command == 'scrape':
        cli.scrape_url(args)
    elif args.command == 'batch-scrape':
        cli.scrape_batch(args)
    elif args.command == 'scrape-config':
        cli.scrape_config(args)
    elif args.command == 'index':
        if args.rebuild:
            cli.rebuild_index(args)
        else:
            print("Use --rebuild to rebuild the index")
    elif args.command == 'stats':
        cli.show_stats(args)
    elif args.command == 'chat':
        cli.chat(args)


if __name__ == "__main__":
    main()
