""""""

Admin Interface ModuleAdmin Interface - Administrative functions and data management

Handles administrative functions like scraping and database management"""

"""

import streamlit as st

import streamlit as stimport pandas as pd

from typing import Optionalfrom datetime import datetime

import loggingimport logging



from src.services.scraping_service import ScrapingServicelogger = logging.getLogger(__name__)

from src.services.knowledge_service import KnowledgeService



logging.basicConfig(level=logging.INFO)class AdminInterface:

logger = logging.getLogger(__name__)    """Streamlit admin interface for data management"""

    

    def __init__(self, knowledge_service, scraping_service):

def render_admin_interface(scraping_service: ScrapingService, knowledge_service: KnowledgeService):        """

    """        Initialize admin interface

    Render the admin interface for managing data sources and scraping.        

            Args:

    Args:            knowledge_service: KnowledgeService instance

        scraping_service: Scraping service instance            scraping_service: ScrapingService instance

        knowledge_service: Knowledge service instance        """

    """        self.knowledge_service = knowledge_service

    st.header("⚙️ Admin Panel")        self.scraping_service = scraping_service

        

    # Statistics    def render(self):

    st.subheader("📊 Database Statistics")        """Render the admin interface"""

    col1, col2, col3 = st.columns(3)        st.title("⚙️ Administration")

            st.markdown("Manage your knowledge repository")

    total_profiles = knowledge_service.get_profile_count()        

    departments = knowledge_service.get_departments()        # Tabs for different admin functions

            tab1, tab2, tab3, tab4 = st.tabs([

    with col1:            "➕ Add Content",

        st.metric("Total Profiles", total_profiles)            "🌐 Web Scraping",

    with col2:            "🏷️ Categories",

        st.metric("Departments", len(departments))            "🔧 Maintenance"

    with col3:        ])

        st.metric("Status", "✅ Active" if total_profiles > 0 else "⚠️ Empty")        

            with tab1:

    st.markdown("---")            self._render_add_content()

            

    # Scraping section        with tab2:

    st.subheader("🌐 Add New Data Source")            self._render_scraping()

            

    with st.form("scraping_form"):        with tab3:

        website_url = st.text_input(            self._render_categories()

            "Website URL",        

            placeholder="https://example.com",        with tab4:

            help="Enter the website URL to scrape team/leadership information"            self._render_maintenance()

        )    

            def _render_add_content(self):

        col1, col2 = st.columns(2)        """Render manual content addition form"""

        with col1:        st.header("Add Knowledge Item")

            deep_scrape = st.checkbox(        

                "Deep Scrape",        with st.form("add_content_form"):

                value=True,            title = st.text_input("Title *", placeholder="Enter title...")

                help="Enable detailed profile scraping (slower but more complete)"            

            )            content = st.text_area(

        with col2:                "Content *",

            replace_existing = st.checkbox(                placeholder="Enter content...",

                "Replace Existing Data",                height=200

                value=False,            )

                help="Clear database before scraping (otherwise, data will be added)"            

            )            col1, col2 = st.columns(2)

                    

        submit_button = st.form_submit_button("🚀 Start Scraping", use_container_width=True)            with col1:

                        url = st.text_input("URL (optional)", placeholder="https://...")

        if submit_button and website_url:                

            with st.spinner("🔍 Scraping in progress..."):                categories = self.knowledge_service.get_all_categories()

                # Progress callback                category_names = [cat['name'] for cat in categories]

                progress_bar = st.progress(0)                category = st.selectbox("Category", category_names)

                status_text = st.empty()            

                            with col2:

                def progress_callback(current: int, total: int, message: str):                source_type = st.selectbox(

                    progress = current / total if total > 0 else 0                    "Source Type",

                    progress_bar.progress(progress)                    ["manual", "profile", "article", "documentation", "tutorial"]

                    status_text.text(message)                )

                                

                # Perform scraping                auto_index = st.checkbox("Auto-index for search", value=True)

                try:            

                    result = scraping_service.scrape_and_save(            submitted = st.form_submit_button("Add Knowledge Item", type="primary")

                        website_url=website_url,            

                        deep_scrape=deep_scrape,            if submitted:

                        replace_existing=replace_existing,                if not title or not content:

                        progress_callback=progress_callback                    st.error("Title and content are required!")

                    )                else:

                                        item_id = self.knowledge_service.add_knowledge(

                    if result['success']:                        title=title,

                        st.success(f"✅ Successfully scraped {result['profiles_count']} profiles!")                        content=content,

                        st.balloons()                        url=url if url else None,

                                                source_type=source_type,

                        # Show summary                        category=category,

                        if result.get('departments'):                        auto_index=auto_index

                            st.info(f"📁 Found departments: {', '.join(result['departments'])}")                    )

                                            

                        # Rerun to update stats                    if item_id:

                        st.rerun()                        st.success(f"✅ Knowledge item added successfully! (ID: {item_id})")

                    else:                    else:

                        st.error(f"❌ Scraping failed: {result.get('error', 'Unknown error')}")                        st.error("Failed to add knowledge item")

                    

                except Exception as e:    def _render_scraping(self):

                    logger.error(f"Scraping error: {e}")        """Render web scraping interface"""

                    st.error(f"❌ Error: {str(e)}")        st.header("Web Scraping")

            

    st.markdown("---")        # Single URL scraping

            st.subheader("Scrape Single URL")

    # Data management section        

    st.subheader("🗄️ Database Management")        col1, col2 = st.columns([3, 1])

            

    col1, col2 = st.columns(2)        with col1:

                url = st.text_input("URL to scrape", placeholder="https://example.com")

    with col1:        

        if st.button("🔄 Refresh Vector Embeddings", use_container_width=True):        with col2:

            with st.spinner("Updating embeddings..."):            categories = self.knowledge_service.get_all_categories()

                try:            category = st.selectbox("Category", [cat['name'] for cat in categories])

                    result = scraping_service.refresh_embeddings()        

                    if result['success']:        if st.button("Scrape URL"):

                        st.success(f"✅ Updated embeddings for {result['count']} profiles")            if url:

                    else:                with st.spinner(f"Scraping {url}..."):

                        st.error(f"❌ Failed to update embeddings: {result.get('error')}")                    item_id = self.scraping_service.scrape_url(url, category=category)

                except Exception as e:                

                    st.error(f"❌ Error: {str(e)}")                if item_id:

                        st.success(f"✅ Successfully scraped and added! (ID: {item_id})")

    with col2:                else:

        if st.button("🗑️ Clear Database", use_container_width=True, type="secondary"):                    st.error("Failed to scrape URL")

            st.warning("⚠️ This will delete all profiles!")            else:

            if st.button("✅ Confirm Clear Database", type="primary"):                st.warning("Please enter a URL")

                try:        

                    result = knowledge_service.clear_database()        st.divider()

                    if result['success']:        

                        st.success("✅ Database cleared successfully")        # Batch URL scraping

                        st.rerun()        st.subheader("Batch URL Scraping")

                    else:        

                        st.error(f"❌ Failed to clear database: {result.get('error')}")        urls_text = st.text_area(

                except Exception as e:            "URLs (one per line)",

                    st.error(f"❌ Error: {str(e)}")            placeholder="https://example.com/page1\nhttps://example.com/page2\n...",

                height=150

    # Export section        )

    st.markdown("---")        

    st.subheader("📤 Export Data")        col_batch1, col_batch2 = st.columns(2)

            

    if st.button("💾 Export All Profiles (JSON)", use_container_width=True):        with col_batch1:

        try:            batch_category = st.selectbox(

            profiles = knowledge_service.get_all()                "Batch Category",

            if profiles:                [cat['name'] for cat in categories],

                import json                key="batch_category"

                json_data = json.dumps(profiles, indent=2)            )

                st.download_button(        

                    label="⬇️ Download JSON",        with col_batch2:

                    data=json_data,            max_workers = st.slider("Concurrent Workers", 1, 10, 5)

                    file_name="profiles_export.json",        

                    mime="application/json",        if st.button("Start Batch Scraping"):

                    use_container_width=True            if urls_text:

                )                urls = [url.strip() for url in urls_text.split('\n') if url.strip()]

            else:                

                st.warning("No profiles to export")                if urls:

        except Exception as e:                    with st.spinner(f"Scraping {len(urls)} URLs..."):

            st.error(f"❌ Export error: {str(e)}")                        progress_bar = st.progress(0)

                        status_text = st.empty()

                        

def render_quick_actions(scraping_service: ScrapingService):                        stats = self.scraping_service.scrape_multiple_urls(

    """                            urls, category=batch_category, max_workers=max_workers

    Render quick action buttons in the sidebar.                        )

                            

    Args:                        progress_bar.progress(100)

        scraping_service: Scraping service instance                        status_text.text("Complete!")

    """                    

    st.sidebar.markdown("---")                    st.success(f"✅ Batch scraping complete!")

    st.sidebar.subheader("⚡ Quick Actions")                    st.json(stats)

                    else:

    if st.sidebar.button("🔄 Re-scrape Last Website", use_container_width=True):                    st.warning("No valid URLs provided")

        # Get last scraped URL from session state or config            else:

        last_url = st.session_state.get('last_scraped_url')                st.warning("Please enter URLs")

        if last_url:        

            with st.spinner(f"Re-scraping {last_url}..."):        st.divider()

                try:        

                    result = scraping_service.refresh_data(last_url)        # Config-based scraping

                    if result['success']:        st.subheader("Scrape from Configuration")

                        st.success(f"✅ Re-scraped {result['profiles_count']} profiles")        

                        st.rerun()        config_file = st.text_input(

                    else:            "Config file path",

                        st.error(f"❌ Failed: {result.get('error')}")            value="config/scraping_targets.yaml"

                except Exception as e:        )

                    st.error(f"❌ Error: {str(e)}")        

        else:        if st.button("Start Config Scraping"):

            st.warning("No previous website found. Please scrape a website first.")            with st.spinner("Scraping from configuration..."):

                stats = self.scraping_service.scrape_from_config(config_file)
            
            if 'error' in stats:
                st.error(f"Error: {stats['error']}")
            else:
                st.success("✅ Configuration scraping complete!")
                st.json(stats)
    
    def _render_categories(self):
        """Render category management"""
        st.header("Category Management")
        
        # List existing categories
        categories = self.knowledge_service.get_all_categories()
        
        st.subheader("Existing Categories")
        
        cat_data = []
        for cat in categories:
            cat_data.append({
                'Name': cat['name'],
                'Description': cat['description'] or 'N/A',
                'Items': cat['item_count']
            })
        
        if cat_data:
            df = pd.DataFrame(cat_data)
            st.dataframe(df, use_container_width=True)
        
        st.divider()
        
        # Add new category
        st.subheader("Add New Category")
        
        with st.form("add_category_form"):
            new_cat_name = st.text_input("Category Name")
            new_cat_desc = st.text_area("Description")
            
            if st.form_submit_button("Add Category"):
                if new_cat_name:
                    try:
                        self.knowledge_service.repository.create_category(
                            name=new_cat_name,
                            description=new_cat_desc
                        )
                        st.success(f"✅ Category '{new_cat_name}' created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Category name is required")
    
    def _render_maintenance(self):
        """Render maintenance functions"""
        st.header("Maintenance & Utilities")
        
        # Database stats
        st.subheader("Database Statistics")
        stats = self.knowledge_service.get_statistics()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Items", stats['total_items'])
        with col2:
            st.metric("Indexed", stats['indexed_items'])
        with col3:
            st.metric("Coverage", f"{stats['index_coverage']:.1f}%")
        
        st.divider()
        
        # Maintenance actions
        st.subheader("Maintenance Actions")
        
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.write("**Search Index**")
            
            if st.button("🔄 Rebuild Search Index", use_container_width=True):
                with st.spinner("Rebuilding index..."):
                    rebuild_stats = self.knowledge_service.rebuild_search_index()
                st.success("Index rebuilt!")
                st.json(rebuild_stats)
            
            if st.button("🧹 Remove Stale Indices", use_container_width=True):
                with st.spinner("Cleaning up..."):
                    removed = self.knowledge_service.indexer.remove_stale_indices()
                st.success(f"Removed {removed} stale indices")
        
        with col_m2:
            st.write("**Content Update**")
            
            max_age = st.number_input("Update content older than (days)", 1, 365, 30)
            
            if st.button("🔄 Update Old Content", use_container_width=True):
                with st.spinner("Updating content..."):
                    update_stats = self.scraping_service.update_existing_content(max_age)
                st.success("Content update complete!")
                st.json(update_stats)
        
        st.divider()
        
        # Export/Import
        st.subheader("Data Export/Import")
        
        col_e1, col_e2 = st.columns(2)
        
        with col_e1:
            if st.button("📥 Export Database", use_container_width=True):
                st.info("Export functionality coming soon...")
        
        with col_e2:
            uploaded_file = st.file_uploader("📤 Import Data", type=['json', 'csv'])
            if uploaded_file:
                st.info("Import functionality coming soon...")


def run_admin_interface(knowledge_service, scraping_service):
    """Run the admin interface"""
    st.set_page_config(
        page_title="Admin Panel",
        page_icon="⚙️",
        layout="wide"
    )
    
    interface = AdminInterface(knowledge_service, scraping_service)
    interface.render()
