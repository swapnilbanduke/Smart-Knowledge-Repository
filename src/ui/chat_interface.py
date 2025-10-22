"""Chat interface"""
import streamlit as st
def render_chat_interface(chat_service, knowledge_service):
    st.header(" Chat")
    for msg in chat_service.get_history():
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if prompt := st.chat_input("Ask about team..."):
        chat_service.add_message("user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            response = chat_service.process_message(prompt)
            st.markdown(response)
