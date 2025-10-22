# 🧠 Smart Knowledge Repository - Production v2.0

> AI-Powered Team Intelligence Platform with Modern Modular Architecture

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

```bash
# 1. Clone repository
git clone <your-repo-url>
cd "Smart Knowledge Repository"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env

# 4. Run the application
streamlit run main.py
```

## 📁 Project Structure

```
project_root/
├── main.py                          # Application entry point
├── src/                             # Source code (modular architecture)
│   ├── scrapers/                    # Web scraping modules
│   │   ├── profile_scraper.py       # Profile extraction logic
│   │   └── content_discovery.py    # Team page discovery
│   ├── database/                    # Data persistence layer
│   │   ├── models.py                # Data models & schemas
│   │   ├── repository.py            # Database operations
│   │   └── migrations.py            # Schema migrations
│   ├── search/                      # Search & indexing
│   │   ├── vector_search.py         # Semantic vector search
│   │   └── indexing.py              # Embedding creation
│   ├── services/                    # Business logic layer
│   │   ├── knowledge_service.py     # Knowledge queries
│   │   ├── chat_service.py          # Conversational AI
│   │   └── scraping_service.py      # Scraping orchestration
│   └── ui/                          # User interface components
│       ├── chat_interface.py        # Chat UI
│       ├── browse_interface.py      # Profile browsing
│       └── admin_interface.py       # Admin panel
├── data/                            # Data storage
│   ├── leadership.db                # SQLite database
│   └── embeddings/                  # Vector embeddings cache
├── config/                          # Configuration files
│   └── scraping_targets.yaml        # Scraping configuration
└── docs/                            # Documentation
    ├── DATABASE_EXPLAINED.md        # Database architecture
    └── ARCHITECTURE_EXPLAINED.md    # System design
```

## 🎯 Features

### 💬 AI Chat Interface
- Natural language Q&A about team members
- Context-aware responses
- Department filtering
- Conversation history

### 👥 Profile Browsing
- Search by name, role, bio, or department
- AI semantic search or traditional text search
- Photo display with smart loading
- Department organization

### ⚙️ Admin Panel
- Web scraping from any company website
- Automatic team page discovery
- Deep profile extraction
- Vector embedding management
- Database management tools

### 🔍 Smart Search
- **Vector Search**: AI-powered semantic understanding
- **FTS5 Search**: Fast full-text search
- **Hybrid Search**: Combine both for best results
- Department and role filtering

### 🛡️ Hallucination Prevention
- Only answers based on scraped data
- Source attribution
- Confidence scoring
- Graceful handling of unknown queries

## 🏗️ Architecture

### Service Layer Pattern
The application follows a clean service-oriented architecture:

- **UI Layer** (`src/ui/`): Streamlit components, user interactions
- **Service Layer** (`src/services/`): Business logic, orchestration
- **Data Layer** (`src/database/`, `src/search/`): Persistence, search
- **Scraper Layer** (`src/scrapers/`): Data acquisition

### Benefits
- ✅ **Separation of Concerns**: Each module has a single responsibility
- ✅ **Testability**: Services can be tested independently
- ✅ **Maintainability**: Easy to find and update code
- ✅ **Scalability**: Add new features without modifying existing code
- ✅ **Production-Ready**: Professional structure for deployment

## 🔧 Configuration

### Scraping Targets (`config/scraping_targets.yaml`)
```yaml
default_target:
  name: Amzur Technologies
  url: https://amzur.com/
  deep_scrape: true

scraping:
  timeout: 30
  retry_attempts: 3

database:
  path: data/leadership.db

ui:
  app_title: Smart Knowledge Repository
  layout: wide
```

## 📊 Database Schema

### Profiles Table
- `id`: Unique identifier
- `name`: Person's name
- `role`: Job title/position
- `bio`: Biography text
- `photo_url`: Profile photo URL
- `contact`: Email address
- `phone`: Phone number
- `linkedin`: LinkedIn profile URL
- `twitter`: Twitter handle
- `department`: Department/team name
- `profile_url`: Source profile URL
- `embedding`: JSON array of vector embeddings
- `created_at`: Timestamp

### FTS5 Virtual Table
- Full-text search index on: name, role, bio, department

## 🔐 Security

- ✅ API keys stored in `.env` (never committed to git)
- ✅ `.gitignore` configured for sensitive files
- ✅ Input validation on all forms
- ✅ SQL injection prevention via parameterized queries

## 🚀 Deployment

### Local Development
```bash
streamlit run main.py
```

### Production Deployment
```bash
# Using Streamlit Cloud
streamlit run main.py --server.port 8501 --server.address 0.0.0.0

# Using Docker (create Dockerfile first)
docker build -t smart-knowledge-repo .
docker run -p 8501:8501 smart-knowledge-repo
```

## 📈 Performance

- **Search Speed**: < 100ms for vector search (cached embeddings)
- **Scraping**: ~2-5 seconds per profile (deep scrape)
- **Database**: SQLite with FTS5 (handles 1000+ profiles easily)
- **Memory**: ~100MB for typical usage

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Check specific features
python test_enhanced_features.py
python final_verification.py
```

## 📝 Usage Examples

### Add a New Website
1. Go to **Admin** tab
2. Enter website URL (e.g., `https://company.com`)
3. Enable "Deep Scrape" for detailed profiles
4. Click "Start Scraping"

### Chat with AI
1. Go to **Chat** tab
2. Ask questions like:
   - "Who are the software engineers?"
   - "Tell me about the leadership team"
   - "Who works in data science?"

### Browse Profiles
1. Go to **Browse Profiles** tab
2. Use search bar or department filter
3. Toggle AI semantic search on/off
4. View profile photos and details

## 🤝 Contributing

This is a production-grade application. When contributing:

1. Follow the existing modular structure
2. Add new features as services
3. Write tests for business logic
4. Update documentation
5. Keep UI components separate from logic

## 📄 License

[Your License Here]

## 🆘 Troubleshooting

### "No profiles found"
- Make sure you've scraped a website first (Admin tab)
- Check that the website has a team/leadership page

### "OpenAI API error"
- Verify your API key in `.env` file
- Check your OpenAI account has credits

### Photos not loading
- Some websites block external photo loading
- Try re-scraping with deep scrape enabled

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version is 3.8+

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with** ❤️ **using Python, Streamlit, OpenAI, and SQLite**
