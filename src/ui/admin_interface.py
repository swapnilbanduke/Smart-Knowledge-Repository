"""Admin interface"""
import streamlit as st
def render_admin_interface(scraping_service, knowledge_service):
    st.header(" Admin")
    st.metric("Profiles", knowledge_service.get_profile_count())
    url = st.text_input("Website URL")
    if st.button("Scrape"):
        result = scraping_service.scrape_and_save(url, deep_scrape=True)
        if result["success"]:
            st.success(f"Scraped {result['profiles_count']} profiles")
        else:
            st.error(result.get("error"))
def render_quick_actions(scraping_service):
    pass
