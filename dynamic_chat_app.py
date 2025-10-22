"""
Dynamic Knowledge Base Chat Interface
User can add any website, scrape team info, and ask questions
"""

import streamlit as st
from database import (search_profiles, get_all_profiles, get_profiles_by_department, 
                      get_departments, get_profile_count, init_database, insert_profiles, 
                      clear_database)
from enhanced_scraper import (scrape_team_page, find_team_page, validate_url, 
                              scrape_with_discovery, scrape_individual_profile)
from vector_db import vector_search_profiles, generate_ai_answer, update_vector_database
from typing import List, Dict, Any
import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Smart Knowledge Repository",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Clean chat interface */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 1rem 0 !important;
    }
    
    /* Profile card styling */
    .profile-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: white;
    }
    .profile-name {
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
        margin-bottom: 0.5rem;
    }
    .profile-role {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 0.5rem;
    }
    .department-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        backdrop-filter: blur(10px);
    }
    
    /* Photo container */
    .photo-container {
        margin: 1.5rem 0;
        text-align: center;
    }
    .photo-container img {
        max-width: 300px;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        transition: transform 0.3s ease;
    }
    .photo-container img:hover {
        transform: scale(1.05);
    }
    
    /* Success and error boxes */
    .success-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .success-box h3 {
        color: white;
        margin-top: 0;
    }
    .error-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border: none;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Chat input styling */
    .stChatInputContainer {
        border-top: 2px solid #f0f2f6;
        padding-top: 1rem;
        margin-top: 1rem;
    }
    
    /* Remove extra spacing in chat messages */
    .stChatMessage > div {
        background-color: transparent !important;
    }
    
    /* Smooth scrolling */
    .main {
        scroll-behavior: smooth;
    }
</style>
""", unsafe_allow_html=True)

# SCOPE ENFORCEMENT
TEAM_KEYWORDS = [
    'who', 'ceo', 'cto', 'cfo', 'president', 'director', 'head', 'lead', 'leader',
    'team', 'leadership', 'executive', 'founder', 'manager', 'officer', 'chief',
    'role', 'position', 'title', 'department', 'responsible', 'charge', 'oversee',
    'name', 'person', 'people', 'staff', 'employee', 'member', 'contact', 'email'
]

OUT_OF_SCOPE_RESPONSES = [
    "I only have information about the team members from the scraped website. Try asking:\n- 'Who is the CEO?'\n- 'Show me the technology leaders'\n- 'List all team members'",
    "I'm specialized in answering questions about the team members. I can help you find information about people, their roles, and departments.",
    "That's outside my knowledge area. I can only answer questions about the team members and their roles."
]


def is_team_question(query: str) -> bool:
    """Check if question is about team members."""
    query_lower = query.lower()
    
    for keyword in TEAM_KEYWORDS:
        if keyword in query_lower:
            return True
    
    out_of_scope_patterns = [
        r'\b(weather|stock|price|market|news|sport|food|restaurant|lunch|dinner)\b',
        r'\b(how to|what is|when|where|why)\b.*\b(python|code|program|algorithm)\b',
        r'\b(movie|music|game|tv show)\b'
    ]
    
    for pattern in out_of_scope_patterns:
        if re.search(pattern, query_lower):
            return False
    
    return True


def answer_question(query: str, department_filter: str = None) -> str:
    """Answer questions about team members using AI-powered vector search."""
    if not is_team_question(query):
        import random
        return random.choice(OUT_OF_SCOPE_RESPONSES)
    
    try:
        # Use vector search for better semantic matching
        results = vector_search_profiles(query, limit=5)
        
        # Fallback to traditional search if vector search fails
        if not results:
            results = search_profiles(query, department=department_filter)
            if not results:
                if department_filter:
                    results = get_profiles_by_department(department_filter)
                else:
                    results = get_all_profiles()
        
        if not results:
            return "I couldn't find any team members matching your query. Try browsing all profiles in the 'Browse Profiles' tab."
        
        # Generate AI-powered answer
        ai_answer = generate_ai_answer(query, results)
        
        # Add fallback information if AI fails
        if not ai_answer or len(ai_answer) < 50:
            response = f"I found {len(results)} team member(s):\n\n"
            for i, profile in enumerate(results[:5], 1):
                response += f"**{i}. {profile['name']}**\n"
                if profile.get('role'):
                    response += f"   - Role: {profile['role']}\n"
                if profile.get('department'):
                    response += f"   - Department: {profile['department']}\n"
                if profile.get('bio') and len(profile['bio']) > 10:
                    response += f"   - Bio: {profile['bio'][:100]}...\n"
                response += "\n"
            
            if len(results) > 5:
                response += f"\n_...and {len(results) - 5} more. Check the 'Browse Profiles' tab to see all results._"
            
            return response
        
        return ai_answer
        
    except Exception as e:
        logger.error(f"Error in answer_question: {e}")
        return f"Sorry, I encountered an error: {str(e)}"


def render_profile_card(profile: Dict[str, Any]) -> None:
    """Render a profile card with enhanced display - photos visible, bio expandable."""
    
    # Enhanced profile card with gradient background
    photo_url = profile.get('photo_url', '')
    name = profile['name']
    role = profile.get('role', 'Team Member')
    
    st.markdown(f"""
    <div class="profile-card">
        <div style="text-align: center; margin-bottom: 1rem;">
            <img src="{photo_url if photo_url else 'https://via.placeholder.com/150?text=No+Photo'}" 
                 alt="{name}" 
                 style="width: 120px; height: 120px; border-radius: 50%; border: 4px solid rgba(255,255,255,0.3); box-shadow: 0 4px 8px rgba(0,0,0,0.2); object-fit: cover;"
                 onerror="this.src='https://via.placeholder.com/150?text=No+Photo';">
        </div>
        <div class="profile-name" style="text-align: center;">{name}</div>
        <div class="profile-role" style="text-align: center;">{role}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show department if different from role
    if profile.get('department'):
        st.markdown(f"**Department:** {profile['department']}")
    
    # Bio - expandable only (show preview)
    if profile.get('bio') and len(profile.get('bio', '')) > 10:
        bio_preview = profile['bio'][:150] + "..." if len(profile['bio']) > 150 else profile['bio']
        st.markdown(f"**About:** {bio_preview}")
        with st.expander("📖 Read Full Bio"):
            st.write(profile['bio'])
    
    # Contact Information Section
    contact_info = []
    if profile.get('contact'):
        contact_info.append(f"📧 **Email:** {profile['contact']}")
    if profile.get('phone'):
        contact_info.append(f"� **Phone:** {profile['phone']}")
    if profile.get('linkedin'):
        contact_info.append(f"💼 **LinkedIn:** [{profile['linkedin']}]({profile['linkedin']})")
    if profile.get('twitter'):
        contact_info.append(f"🐦 **Twitter:** [{profile['twitter']}]({profile['twitter']})")
    if profile.get('profile_url'):
        contact_info.append(f"🔗 **Profile:** [{profile['profile_url']}]({profile['profile_url']})")
    
    if contact_info:
        with st.expander("📞 Contact Information"):
            for info in contact_info:
                st.markdown(info)


# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'website_scraped' not in st.session_state:
    st.session_state['website_scraped'] = False

if 'current_website' not in st.session_state:
    st.session_state['current_website'] = ""

if 'scrape_status' not in st.session_state:
    st.session_state['scrape_status'] = ""

# Initialize database
init_database()

# Check if database has data
profile_count = get_profile_count()

# MAIN LAYOUT
st.title("🧠 Smart Knowledge Repository")
st.caption("Add any website and chat with its team information")

# ============================================
# SETUP PAGE - If no data exists
# ============================================
if profile_count == 0 or not st.session_state['website_scraped']:
    st.markdown("---")
    st.subheader("🚀 Get Started")
    st.write("Enter a website URL to scrape team/leadership information:")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        website_url = st.text_input(
            "Website URL",
            placeholder="https://example.com or https://example.com/team",
            help="Enter the main website URL or direct link to team/leadership page",
            key="website_input"
        )
    
    with col2:
        st.write("")
        st.write("")
        scrape_button = st.button("🕷️ Scrape Website", type="primary", use_container_width=True)
    
    # Examples
    with st.expander("💡 Example URLs"):
        st.markdown("""
        - `https://amzur.com`
        - `https://amzur.com/leadership-team/`
        - `https://yourcompany.com/about-us/team`
        - `https://example.com/our-team`
        """)
    
    # Scraping process
    if scrape_button and website_url:
        with st.spinner("🔍 Validating website..."):
            is_valid, error_msg = validate_url(website_url)
            
            if not is_valid:
                st.error(f"❌ {error_msg}")
            else:
                # Try to find team page if not direct
                team_url = website_url
                
                if '/team' not in website_url.lower() and '/leadership' not in website_url.lower():
                    with st.spinner("🔍 Looking for team/leadership page..."):
                        found_url = find_team_page(website_url)
                        if found_url:
                            team_url = found_url
                            st.info(f"✅ Found team page: {team_url}")
                        else:
                            st.warning("⚠️ Couldn't find team page automatically. Trying main page...")
                
                # Option for deep scraping
                deep_scrape = st.checkbox(
                    "🔍 Enable Deep Scrape (Visit individual profile pages for photos, bios, contacts)", 
                    value=True,
                    help="Recommended: Extracts detailed information from each person's profile page"
                )
                
                # Scrape the page with intelligent discovery and progress bar
                st.markdown("---")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Progress callback function
                def update_progress(current, total, message):
                    progress = current / total if total > 0 else 0
                    progress_bar.progress(progress)
                    status_text.text(message)
                
                try:
                    if deep_scrape:
                        status_text.info("⚙️ Deep scraping enabled - Extracting detailed information...")
                        profiles = scrape_with_discovery(website_url, deep_scrape=True, progress_callback=update_progress)
                    else:
                        status_text.info("⚙️ Quick scraping - Extracting basic information...")
                        update_progress(50, 100, "📋 Scraping team page...")
                        profiles = scrape_team_page(team_url)
                        update_progress(100, 100, "✅ Complete!")
                    
                    if not profiles:
                        st.error("❌ No team members found on this page. Please try a different URL or direct team page link.")
                    else:
                        # Clear existing data and insert new
                        with st.spinner("💾 Storing data in database..."):
                            clear_database()
                            inserted = insert_profiles(profiles)
                        
                        # Create vector embeddings for AI-powered Q&A
                        with st.spinner("🧠 Creating AI embeddings for intelligent search..."):
                            try:
                                update_vector_database()
                                vector_status = "✅ AI embeddings created successfully!"
                            except Exception as e:
                                logger.error(f"Vector database error: {e}")
                                vector_status = "⚠️ Basic search available (AI embeddings failed)"
                        
                        st.markdown(f"""
                        <div class="success-box">
                            <h3>✅ Success!</h3>
                            <p>Found and stored <strong>{inserted} team members</strong> from {team_url}</p>
                            <p>{vector_status}</p>
                            <p>You can now ask questions about the team!</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Update session state
                        st.session_state['website_scraped'] = True
                        st.session_state['current_website'] = team_url
                        st.session_state['messages'] = [
                            {"role": "assistant", "content": f"👋 Hi! I've loaded {inserted} team members from {website_url}. Ask me anything about them!"}
                        ]
                        
                        # Show preview
                        st.markdown("### 👥 Preview of Team Members")
                        cols = st.columns(3)
                        for idx, profile in enumerate(profiles[:6]):
                            with cols[idx % 3]:
                                st.write(f"**{profile['name']}**")
                                st.caption(profile.get('role', 'Team Member'))
                        
                        st.info("👆 Refresh the page or click below to start chatting!")
                        if st.button("🔄 Continue to Chat", type="primary"):
                            st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Error during scraping: {str(e)}")
                    logger.error(f"Scraping error: {e}", exc_info=True)
                finally:
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()

# ============================================
# CHAT & BROWSE PAGE - If data exists
# ============================================
else:
    # Sidebar
    st.sidebar.title("📊 Repository Info")
    
    # Current website info
    if st.session_state.get('current_website'):
        st.sidebar.info(f"**Current Source:**\n{st.session_state['current_website']}")
    
    # Stats
    total_profiles = get_profile_count()
    st.sidebar.metric("Total Team Members", total_profiles)
    
    # Department filter
    departments = get_departments()
    department_filter = st.sidebar.selectbox(
        "Filter by Department",
        options=["All Departments"] + departments,
        key="dept_filter"
    )
    
    selected_dept = None if department_filter == "All Departments" else department_filter
    
    # Sample questions
    st.sidebar.divider()
    st.sidebar.subheader("💡 Try asking:")
    st.sidebar.markdown("""
    - Who is the CEO?
    - Show me technology leaders
    - List all executives
    - Who works in [Department]?
    - Tell me about [Name]
    """)
    
    # Scrape new website
    st.sidebar.divider()
    if st.sidebar.button("🔄 Scrape New Website", use_container_width=True):
        st.session_state['website_scraped'] = False
        clear_database()
        st.session_state['messages'] = []
        st.rerun()
    
    st.sidebar.caption(f"💾 {total_profiles} profiles loaded")
    
    # Main tabs
    tab1, tab2 = st.tabs(["💬 Chat", "📋 Browse Profiles"])
    
    # TAB 1: CHAT
    with tab1:
        # Initialize messages if empty
        if not st.session_state['messages']:
            st.session_state['messages'] = [
                {"role": "assistant", "content": f"👋 Hi! I have information about {total_profiles} team members. Ask me anything!"}
            ]
        
        # Initialize input counter for clearing
        if 'input_counter' not in st.session_state:
            st.session_state['input_counter'] = 0
        
        # CHAT INPUT AT TOP
        st.markdown("### 💬 Ask a Question")
        prompt = st.text_input(
            "Ask about team members...", 
            key=f"chat_input_{st.session_state['input_counter']}", 
            placeholder="e.g., Who is the Chief Solution Architect?"
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state['messages'] = [
                    {"role": "assistant", "content": f"👋 Hi! I have information about {total_profiles} team members. Ask me anything!"}
                ]
                st.session_state['input_counter'] += 1
                st.rerun()
        
        st.divider()
        
        # Process question if asked
        if ask_button and prompt:
            # Add user message to the START of the list (newest first)
            st.session_state['messages'].insert(0, {"role": "user", "content": prompt})
            
            # Generate response
            with st.spinner("🔍 Searching..."):
                response = answer_question(prompt, department_filter=selected_dept)
            
            # Add assistant response to the START of the list (newest first)
            st.session_state['messages'].insert(0, {"role": "assistant", "content": response})
            
            # Increment counter to clear input field
            st.session_state['input_counter'] += 1
            
            st.rerun()
        
        # Display chat messages in REVERSE order (newest at top)
        st.markdown("### 💭 Conversation")
        for message in st.session_state['messages']:
            with st.chat_message(message["role"]):
                content = message["content"]
                
                # Check if content has photo URL marker
                if "📸PHOTO📸" in content:
                    # Split content and photo URL
                    parts = content.split("📸PHOTO📸")
                    text_part = parts[0].strip()
                    photo_url = parts[1].strip() if len(parts) > 1 else ""
                    
                    # Display text first
                    st.markdown(text_part)
                    
                    # Display photo if URL exists
                    if photo_url and photo_url.startswith('http'):
                        # Clean, centered photo display with better styling
                        st.markdown(f"""
                        <div style="text-align: center; margin: 20px 0;">
                            <img src="{photo_url}" 
                                 alt="Profile Photo"
                                 style="max-width: 300px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"
                                 onerror="this.onerror=null; this.style.display='none'; this.parentElement.innerHTML='<p style=color:#999;>Photo unavailable</p>';">
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(content)
    
    # TAB 2: BROWSE PROFILES
    with tab2:
        st.subheader("📋 All Team Profiles")
        
        # Get profiles
        if selected_dept:
            profiles = get_profiles_by_department(selected_dept)
            st.info(f"Showing {len(profiles)} profiles from **{selected_dept}** department")
        else:
            profiles = get_all_profiles()
            st.info(f"Showing all {len(profiles)} profiles")
        
        # Search box
        search_term = st.text_input("🔍 Search profiles", placeholder="Enter name, role, or keyword...")
        
        if search_term:
            filtered = [p for p in profiles if 
                       search_term.lower() in p['name'].lower() or 
                       search_term.lower() in p.get('role', '').lower() or
                       search_term.lower() in p.get('department', '').lower()]
            profiles = filtered
            st.caption(f"Found {len(profiles)} matching profiles")
        
        # Display profiles in columns
        if profiles:
            cols = st.columns(2)
            
            for idx, profile in enumerate(profiles):
                with cols[idx % 2]:
                    render_profile_card(profile)
        else:
            st.warning("No profiles found matching your criteria.")

# Footer
st.divider()
st.caption("🚀 Smart Knowledge Repository • Built with Streamlit & SQLite FTS5")
