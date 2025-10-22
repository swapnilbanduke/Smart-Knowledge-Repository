"""Browse interface"""
import streamlit as st
def render_browse_interface(knowledge_service):
    st.header(" Browse Profiles")
    profiles = knowledge_service.get_all()
    for p in profiles:
        st.markdown(f"**{p['name']}** - {p['role']}")
        if p.get('bio'): st.write(p['bio'])
        st.markdown("---")
