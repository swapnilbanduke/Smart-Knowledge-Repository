"""Admin interface with intelligent scraping stats"""
import streamlit as st
def render_admin_interface(scraping_service, knowledge_service):
    st.header("⚙️ Admin - Intelligent Scraping")
    
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Total Profiles", knowledge_service.get_profile_count())
    with col2:
        st.metric("📁 Departments", len(knowledge_service.get_departments()))
    with col3:
        st.metric("🔍 Scraper", "Intelligent v2.0")
    
    st.markdown("---")
    
    # Scraping form
    st.subheader("🌐 Intelligent Web Scraping")
    st.info("✨ **Features:** Auto-discovery • Multi-template extraction • Duplicate detection • Contact parsing")
    
    url = st.text_input("Website URL", placeholder="https://company.com")
    
    col1, col2 = st.columns(2)
    with col1:
        deep = st.checkbox("Deep Scrape", value=True, help="Extract detailed profile data")
    with col2:
        replace = st.checkbox("Replace Existing", help="Clear database before scraping")
    
    if st.button("🚀 Start Intelligent Scraping", type="primary"):
        if url:
            progress_bar = st.progress(0)
            status = st.empty()
            
            def progress_callback(current, total, message):
                progress_bar.progress(current / total)
                status.text(message)
            
            with st.spinner("Processing..."):
                result = scraping_service.scrape_and_save(
                    url, deep_scrape=deep, replace_existing=replace, 
                    progress_callback=progress_callback
                )
            
            if result["success"]:
                st.success(f"✅ Scraped {result['profiles_count']} profiles!")
                
                # Show detailed stats
                if "stats" in result:
                    stats = result["stats"]
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Discovered", stats.get('profiles_discovered', 0))
                    with col2:
                        st.metric("Extracted", stats.get('profiles_extracted', 0))
                    with col3:
                        st.metric("Duplicates Removed", stats.get('duplicates_removed', 0))
                    with col4:
                        st.metric("Emails Found", stats.get('emails_found', 0))
                
                if result.get("departments"):
                    st.info(f"📁 Departments: {', '.join(result['departments'])}")
                
                st.balloons()
            else:
                st.error(f"❌ {result.get('error', 'Unknown error')}")

def render_quick_actions(scraping_service):
    pass
