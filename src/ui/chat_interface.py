""""""

Chat Interface ModuleChat Interface - Streamlit-based chat UI

Handles the conversational AI interface for the Smart Knowledge Repository"""

"""

import streamlit as st

import streamlit as stfrom typing import Optional

from typing import List, Dict, Anyimport logging

import logging

logger = logging.getLogger(__name__)

from src.services.chat_service import ChatService

from src.services.knowledge_service import KnowledgeService

class ChatInterface:

logging.basicConfig(level=logging.INFO)    """Streamlit chat interface for AI assistant"""

logger = logging.getLogger(__name__)    

    def __init__(self, chat_service):

        """

def render_chat_interface(chat_service: ChatService, knowledge_service: KnowledgeService):        Initialize chat interface

    """        

    Render the chat interface tab with AI-powered Q&A.        Args:

                chat_service: ChatService instance

    Args:        """

        chat_service: Chat service instance        self.chat_service = chat_service

        knowledge_service: Knowledge service instance    

    """    def render(self):

    st.header("💬 Ask Questions")        """Render the chat interface"""

            st.title("🤖 Knowledge Assistant")

    # Department filter in sidebar        st.markdown("Ask questions and get answers from your knowledge repository")

    with st.sidebar:        

        st.subheader("🔍 Filter by Department")        # Initialize session state

        departments = knowledge_service.get_departments()        if 'session_id' not in st.session_state:

        department_filter = st.selectbox(            st.session_state.session_id = None

            "Department",        if 'messages' not in st.session_state:

            options=["All Departments"] + departments,            st.session_state.messages = []

            key="chat_dept_filter"        if 'current_scope' not in st.session_state:

        )            st.session_state.current_scope = None

        selected_dept = None if department_filter == "All Departments" else department_filter        

            # Sidebar for scope selection

    # Display chat history        self._render_sidebar()

    for message in chat_service.get_history():        

        with st.chat_message(message["role"]):        # Create session if needed

            st.markdown(message["content"])        if st.session_state.session_id is None:

                st.session_state.session_id = self.chat_service.create_session(

    # Chat input                scope=st.session_state.current_scope

    if prompt := st.chat_input("Ask me anything about the team..."):            )

        # Add user message to chat            logger.info(f"Created new session: {st.session_state.session_id}")

        chat_service.add_message("user", prompt)        

        with st.chat_message("user"):        # Display chat history

            st.markdown(prompt)        self._display_chat_history()

                

        # Get AI response        # Chat input

        with st.chat_message("assistant"):        self._render_chat_input()

            with st.spinner("🤔 Thinking..."):    

                response = chat_service.process_message(prompt, department=selected_dept)    def _render_sidebar(self):

                st.markdown(response)        """Render sidebar with scope controls"""

            st.sidebar.header("Chat Settings")

    # Clear chat button        

    if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):        # Get available scopes

        chat_service.clear_history()        scopes = self.chat_service.get_available_scopes()

        st.rerun()        scope_options = ["All Categories"] + scopes

        

        # Scope selector

def render_profile_card(profile: Dict[str, Any], show_photo: bool = True):        selected_scope = st.sidebar.selectbox(

    """            "Knowledge Scope",

    Render a profile card with consistent styling.            scope_options,

                help="Limit responses to specific category"

    Args:        )

        profile: Profile dictionary        

        show_photo: Whether to display profile photo        # Update scope if changed

    """        new_scope = None if selected_scope == "All Categories" else selected_scope

    st.markdown(f"""        if new_scope != st.session_state.current_scope:

        <div class="profile-card">            st.session_state.current_scope = new_scope

            <div class="profile-name">👤 {profile['name']}</div>            if st.session_state.session_id:

            <div class="profile-role">{profile['role']}</div>                self.chat_service.set_session_scope(

            {f'<span class="department-badge">📁 {profile["department"]}</span>' if profile.get('department') else ''}                    st.session_state.session_id,

        </div>                    new_scope

    """, unsafe_allow_html=True)                )

            

    # Display photo if available and enabled        # Session info

    if show_photo and profile.get('photo_url'):        if st.session_state.session_id:

        col1, col2, col3 = st.columns([1, 2, 1])            session_info = self.chat_service.get_session_info(st.session_state.session_id)

        with col2:            if session_info:

            try:                st.sidebar.info(f"Messages: {session_info['message_count']}")

                st.markdown('<div class="photo-container">', unsafe_allow_html=True)        

                st.image(profile['photo_url'], use_container_width=True)        # Clear chat button

                st.markdown('</div>', unsafe_allow_html=True)        if st.sidebar.button("Clear Chat"):

            except Exception as e:            self._clear_chat()

                logger.warning(f"Could not display photo for {profile['name']}: {e}")    

        def _display_chat_history(self):

    # Bio        """Display chat message history"""

    if profile.get('bio'):        for message in st.session_state.messages:

        with st.expander("📝 Bio", expanded=True):            with st.chat_message(message["role"]):

            st.write(profile['bio'])                st.markdown(message["content"])

                    

    # Contact information                # Show referenced knowledge for assistant messages

    contact_items = []                if message["role"] == "assistant" and "references" in message:

    if profile.get('contact'):                    with st.expander("📚 Referenced Knowledge"):

        contact_items.append(f"✉️ {profile['contact']}")                        for ref in message["references"]:

    if profile.get('phone'):                            st.markdown(f"**{ref['title']}** (Score: {ref.get('similarity_score', 'N/A')})")

        contact_items.append(f"📞 {profile['phone']}")                            st.caption(ref.get('url', 'No URL'))

    if profile.get('linkedin'):    

        contact_items.append(f"[🔗 LinkedIn]({profile['linkedin']})")    def _render_chat_input(self):

    if profile.get('twitter'):        """Render chat input and handle messages"""

        contact_items.append(f"[🐦 Twitter]({profile['twitter']})")        # Chat input

            if prompt := st.chat_input("Ask a question..."):

    if contact_items:            # Add user message to chat

        with st.expander("📧 Contact Info"):            st.session_state.messages.append({"role": "user", "content": prompt})

            for item in contact_items:            

                st.markdown(item)            # Display user message

                with st.chat_message("user"):

    st.markdown("---")                st.markdown(prompt)

            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = self.chat_service.chat(
                        session_id=st.session_state.session_id,
                        user_message=prompt
                    )
                
                if 'error' in response:
                    st.error(f"Error: {response['error']}")
                    st.markdown(response['response'])
                else:
                    st.markdown(response['response'])
                    
                    # Show referenced knowledge
                    if response.get('referenced_knowledge'):
                        with st.expander("📚 Referenced Knowledge"):
                            for ref in response['referenced_knowledge']:
                                st.markdown(f"**{ref['title']}** (Score: {ref.get('similarity_score', 'N/A')})")
                                st.caption(ref.get('url', 'No URL'))
                    
                    # Add to session state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response['response'],
                        "references": response.get('referenced_knowledge', [])
                    })
    
    def _clear_chat(self):
        """Clear chat history and create new session"""
        if st.session_state.session_id:
            self.chat_service.end_session(st.session_state.session_id)
        
        st.session_state.session_id = self.chat_service.create_session(
            scope=st.session_state.current_scope
        )
        st.session_state.messages = []
        st.rerun()


def run_chat_interface(chat_service):
    """Run the chat interface"""
    st.set_page_config(
        page_title="Knowledge Assistant",
        page_icon="🤖",
        layout="wide"
    )
    
    interface = ChatInterface(chat_service)
    interface.render()
