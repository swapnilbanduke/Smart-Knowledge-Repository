""""""

Browse Interface ModuleBrowse Interface - Browse and search knowledge repository

Handles the profile browsing and search interface"""

"""

import streamlit as st

import streamlit as stimport pandas as pd

from typing import List, Dict, Any, Optionalfrom typing import Optional

import loggingimport logging



from src.services.knowledge_service import KnowledgeServicelogger = logging.getLogger(__name__)

from src.ui.chat_interface import render_profile_card



logging.basicConfig(level=logging.INFO)class BrowseInterface:

logger = logging.getLogger(__name__)    """Streamlit interface for browsing knowledge"""

    

    def __init__(self, knowledge_service):

def render_browse_interface(knowledge_service: KnowledgeService):        """

    """        Initialize browse interface

    Render the browse/search interface for viewing all profiles.        

            Args:

    Args:            knowledge_service: KnowledgeService instance

        knowledge_service: Knowledge service instance        """

    """        self.knowledge_service = knowledge_service

    st.header("👥 Browse Team Profiles")    

        def render(self):

    # Get profile statistics        """Render the browse interface"""

    total_profiles = knowledge_service.get_profile_count()        st.title("📚 Knowledge Repository")

    departments = knowledge_service.get_departments()        st.markdown("Browse, search, and explore your knowledge base")

            

    # Sidebar filters        # Tabs for different views

    with st.sidebar:        tab1, tab2, tab3 = st.tabs(["🔍 Search", "📂 Browse", "📊 Statistics"])

        st.subheader("🎯 Filters")        

                with tab1:

        # Department filter            self._render_search()

        dept_options = ["All Departments"] + departments        

        selected_dept = st.selectbox(        with tab2:

            "Department",            self._render_browse()

            options=dept_options,        

            key="browse_dept_filter"        with tab3:

        )            self._render_statistics()

        dept_filter = None if selected_dept == "All Departments" else selected_dept    

            def _render_search(self):

        # Search method        """Render search interface"""

        st.subheader("🔍 Search Method")        st.header("Search Knowledge")

        use_vector_search = st.checkbox(        

            "Use AI Semantic Search",        col1, col2 = st.columns([3, 1])

            value=True,        

            help="AI-powered semantic search for better results"        with col1:

        )            query = st.text_input("Search query", placeholder="Enter your search...")

                

        # Show photos toggle        with col2:

        show_photos = st.checkbox(            search_type = st.selectbox("Search Type", ["Semantic", "Text"])

            "Show Profile Photos",        

            value=True,        # Filters

            help="Display profile photos in results"        col3, col4 = st.columns(2)

        )        

            with col3:

    # Display stats            categories = self.knowledge_service.get_all_categories()

    col1, col2, col3 = st.columns(3)            category_names = ["All"] + [cat['name'] for cat in categories]

    with col1:            selected_category = st.selectbox("Category", category_names)

        st.metric("Total Profiles", total_profiles)        

    with col2:        with col4:

        st.metric("Departments", len(departments))            top_k = st.slider("Number of results", 1, 20, 5)

    with col3:        

        if dept_filter:        # Search button

            filtered_count = knowledge_service.get_profile_count(department=dept_filter)        if st.button("Search", type="primary") or query:

            st.metric("Filtered Profiles", filtered_count)            if query:

        else:                with st.spinner("Searching..."):

            st.metric("Search Method", "AI" if use_vector_search else "Text")                    scope = None if selected_category == "All" else selected_category

                        use_semantic = search_type == "Semantic"

    # Search bar                    

    search_query = st.text_input(                    results = self.knowledge_service.search_knowledge(

        "🔍 Search profiles by name, role, bio, or department...",                        query=query,

        placeholder="e.g., 'Software Engineer' or 'Data Science team'",                        scope=scope,

        key="profile_search"                        top_k=top_k,

    )                        use_semantic=use_semantic

                        )

    # Get profiles                

    if search_query:                if results:

        st.subheader(f"🔍 Search Results for: '{search_query}'")                    st.success(f"Found {len(results)} results")

        profiles = knowledge_service.search(                    

            query=search_query,                    for i, result in enumerate(results, 1):

            use_vector_search=use_vector_search,                        with st.expander(f"{i}. {result['title']}", expanded=(i == 1)):

            department=dept_filter,                            st.markdown(result['content'])

            limit=20                            

        )                            col_info1, col_info2, col_info3 = st.columns(3)

                                    with col_info1:

        if not profiles:                                if result.get('category'):

            st.warning("😕 No profiles found matching your search. Try different keywords.")                                    st.caption(f"📂 {result['category']}")

            return                            with col_info2:

                                            if result.get('similarity_score'):

        st.info(f"Found {len(profiles)} matching profile(s)")                                    st.caption(f"🎯 Score: {result['similarity_score']}")

    else:                            with col_info3:

        # Show all profiles                                if result.get('url'):

        st.subheader("📋 All Profiles")                                    st.caption(f"🔗 [Source]({result['url']})")

        profiles = knowledge_service.get_all(department=dept_filter)                else:

                            st.warning("No results found")

        if not profiles:    

            st.warning("😕 No profiles found. Please scrape a website first.")    def _render_browse(self):

            return        """Render browse interface"""

            st.header("Browse by Category")

    # Display profiles        

    for i, profile in enumerate(profiles, 1):        categories = self.knowledge_service.get_all_categories()

        with st.container():        

            render_profile_card(profile, show_photo=show_photos)        # Category selector

                    col1, col2 = st.columns([2, 1])

            # Add similarity score for vector search        

            if search_query and use_vector_search and profile.get('similarity'):        with col1:

                st.caption(f"🎯 Relevance: {profile['similarity']:.1%}")            selected_cat = st.selectbox(

                "Select Category",

                [cat['name'] for cat in categories],

def render_departments_view(knowledge_service: KnowledgeService):                format_func=lambda x: f"{x} ({next(c['item_count'] for c in categories if c['name'] == x)} items)"

    """            )

    Render a department-organized view of profiles.        

            with col2:

    Args:            limit = st.number_input("Items to show", 10, 100, 50)

        knowledge_service: Knowledge service instance        

    """        if selected_cat:

    st.header("🏢 Browse by Department")            items = self.knowledge_service.repository.get_all_knowledge_items(

                    category_name=selected_cat,

    departments = knowledge_service.get_departments()                limit=limit

                )

    if not departments:            

        st.warning("No departments found. Please scrape a website first.")            st.subheader(f"{selected_cat.title()} ({len(items)} items)")

        return            

                for item in items:

    # Create tabs for each department                with st.expander(f"📄 {item.title}"):

    tabs = st.tabs(departments)                    st.markdown(item.content)

                        

    for dept, tab in zip(departments, tabs):                    col_meta1, col_meta2, col_meta3 = st.columns(3)

        with tab:                    with col_meta1:

            profiles = knowledge_service.get_all(department=dept)                        if item.source_type:

            st.subheader(f"{dept} ({len(profiles)} members)")                            st.caption(f"Type: {item.source_type}")

                                with col_meta2:

            for profile in profiles:                        if item.created_at:

                with st.container():                            st.caption(f"Added: {item.created_at.strftime('%Y-%m-%d')}")

                    render_profile_card(profile, show_photo=True)                    with col_meta3:

                        if item.url:
                            st.caption(f"[View Source]({item.url})")
                    
                    # Action buttons
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button(f"View Details", key=f"view_{item.id}"):
                            self._show_item_details(item.id)
                    with col_btn2:
                        if st.button(f"Delete", key=f"del_{item.id}"):
                            if st.session_state.get(f'confirm_del_{item.id}'):
                                self.knowledge_service.delete_knowledge(item.id)
                                st.success("Deleted!")
                                st.rerun()
                            else:
                                st.session_state[f'confirm_del_{item.id}'] = True
                                st.warning("Click again to confirm")
    
    def _render_statistics(self):
        """Render statistics dashboard"""
        st.header("Repository Statistics")
        
        stats = self.knowledge_service.get_statistics()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Items", stats['total_items'])
        with col2:
            st.metric("Categories", stats['total_categories'])
        with col3:
            st.metric("Indexed Items", stats['indexed_items'])
        with col4:
            st.metric("Index Coverage", f"{stats['index_coverage']:.1f}%")
        
        # Category distribution
        st.subheader("Items by Category")
        
        if stats['category_distribution']:
            df = pd.DataFrame([
                {'Category': cat, 'Items': count}
                for cat, count in stats['category_distribution'].items()
            ])
            
            st.bar_chart(df.set_index('Category'))
            st.dataframe(df, use_container_width=True)
        
        # Embedding model info
        st.info(f"🤖 Embedding Model: {stats['embedding_model']}")
        
        # Action buttons
        col_act1, col_act2 = st.columns(2)
        
        with col_act1:
            if st.button("Rebuild Search Index", type="primary"):
                with st.spinner("Rebuilding index..."):
                    rebuild_stats = self.knowledge_service.rebuild_search_index()
                st.success(f"Index rebuilt! Indexed: {rebuild_stats['indexed']}, Failed: {rebuild_stats['failed']}")
        
        with col_act2:
            if st.button("Refresh Statistics"):
                st.rerun()
    
    def _show_item_details(self, item_id: int):
        """Show detailed view of an item"""
        item = self.knowledge_service.get_knowledge_by_id(item_id)
        
        if item:
            st.modal(f"Details: {item['title']}")
            st.json(item)


def run_browse_interface(knowledge_service):
    """Run the browse interface"""
    st.set_page_config(
        page_title="Knowledge Browser",
        page_icon="📚",
        layout="wide"
    )
    
    interface = BrowseInterface(knowledge_service)
    interface.render()
