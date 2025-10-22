"""Smart Knowledge Repository - Production v2.0"""
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.chat_service import ChatService
from src.services.knowledge_service import KnowledgeService
from src.services.scraping_service import ScrapingService
from src.ui.chat_interface import render_chat_interface
from src.ui.browse_interface import render_browse_interface
from src.ui.admin_interface import render_admin_interface

st.set_page_config(page_title="Smart Knowledge Repository", page_icon="", layout="wide")

st.markdown("""
<style>
.profile-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; color: white; }
.profile-name { font-size: 1.5rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def main():
    chat_service = ChatService()
    knowledge_service = KnowledgeService()
    scraping_service = ScrapingService()
    
    with st.sidebar:
        st.title(" Smart Knowledge Repository")
        st.metric("Profiles", knowledge_service.get_profile_count())
    
    tab1, tab2, tab3 = st.tabs([" Chat", " Browse", " Admin"])
    
    with tab1:
        render_chat_interface(chat_service, knowledge_service)
    with tab2:
        render_browse_interface(knowledge_service)
    with tab3:
        render_admin_interface(scraping_service, knowledge_service)

if __name__ == "__main__":
    main()
