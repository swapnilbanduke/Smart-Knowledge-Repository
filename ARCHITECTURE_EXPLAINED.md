# Project Architecture: How Everything Works Together

## 🏗️ System Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                             │
│                                                                      │
│  User asks: "Who is the CEO?"                                       │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      STREAMLIT APP                                   │
│                   (dynamic_chat_app.py)                             │
│                                                                      │
│  • Receives user question                                           │
│  • Routes to appropriate handler                                    │
│  • Displays results with photos                                     │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      VECTOR SEARCH                                   │
│                      (vector_db.py)                                 │
│                                                                      │
│  1. Convert question to embedding (OpenAI)                          │
│  2. Search database for similar embeddings                          │
│  3. Return top 5 matching profiles                                  │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    📊 SQLite DATABASE 📊                            │
│                     (leadership.db)                                 │
│                                                                      │
│  ┌────────────────────────────────────────────────────┐            │
│  │  PROFILES TABLE                                     │            │
│  │  ┌──────────────────────────────────────┐          │            │
│  │  │ id | name | role | bio | photo_url   │          │            │
│  │  ├────┼──────┼──────┼─────┼─────────────┤          │            │
│  │  │ 1  | Bala │ CEO  │ ... │ http://...  │          │            │
│  │  │ 2  | Ganna│ Pres │ ... │ http://...  │          │            │
│  │  │ 3  | Sam  │ VP   │ ... │ http://...  │          │            │
│  │  └────┴──────┴──────┴─────┴─────────────┘          │            │
│  │                                                      │            │
│  │  + linkedin, twitter, department, etc.              │            │
│  └────────────────────────────────────────────────────┘            │
│                                                                      │
│  ┌────────────────────────────────────────────────────┐            │
│  │  FTS5 SEARCH INDEX (profiles_fts)                  │            │
│  │  • Fast text search across name, role, bio         │            │
│  │  • Like Google search for profiles                 │            │
│  └────────────────────────────────────────────────────┘            │
│                                                                      │
│  ┌────────────────────────────────────────────────────┐            │
│  │  VECTOR EMBEDDINGS (stored in profiles table)      │            │
│  │  • 1536-dimensional vectors per profile            │            │
│  │  • Used for semantic similarity search             │            │
│  │  • Generated by OpenAI                             │            │
│  └────────────────────────────────────────────────────┘            │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AI ANSWER GENERATION                            │
│                      (vector_db.py)                                 │
│                                                                      │
│  1. Take top matching profiles                                      │
│  2. Send to OpenAI GPT-3.5                                          │
│  3. Generate human-friendly answer                                  │
│  4. Add photo if appropriate                                        │
│  5. Prevent hallucination (strict validation)                       │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DISPLAY RESULT                                  │
│                   (dynamic_chat_app.py)                             │
│                                                                      │
│  • Show AI answer                                                   │
│  • Display photo (if single person)                                 │
│  • Format with LinkedIn links                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Data Flow: First Time Setup

```
1. USER CLICKS "Scrape New Website"
   ↓
2. ENHANCED SCRAPER (enhanced_scraper.py)
   ├─ Visit https://amzur.com
   ├─ Find team page
   ├─ Extract profile links
   ├─ Deep scrape each profile
   │  ├─ Name
   │  ├─ Role
   │  ├─ Bio
   │  ├─ Photo URL
   │  ├─ LinkedIn
   │  └─ Contact info
   └─ Return 14 profiles
   ↓
3. DATABASE INSERT (database.py)
   ├─ Clear old data
   ├─ Insert 14 profiles into leadership.db
   └─ FTS5 index auto-updates
   ↓
4. VECTOR GENERATION (vector_db.py)
   ├─ For each profile:
   │  ├─ Combine name + role + bio
   │  ├─ Send to OpenAI embeddings API
   │  └─ Get 1536-dimensional vector
   └─ Store vectors in database
   ↓
5. READY! Database now has:
   ├─ 14 profiles with all details
   ├─ FTS5 search index
   └─ Vector embeddings
```

---

## 🔍 Query Flow: User Asks Question

```
USER: "Who is the CEO?"
   ↓
STREAMLIT receives question
   ↓
VECTOR_DB: Create embedding of question
   ├─ OpenAI: "Who is the CEO?" → [0.123, -0.456, 0.789, ...]
   ↓
SEARCH DATABASE using cosine similarity
   ├─ Compare question embedding with all profile embeddings
   ├─ Find most similar profiles
   └─ Return top 5:
       1. Ganna Vadlamaani (score: 0.89)
       2. Bala Nemani (score: 0.87)
       3. Sam Velu (score: 0.65)
       4. ...
   ↓
HALLUCINATION CHECK
   ├─ Is question about external company? NO ✓
   ├─ Is data in database? YES ✓
   └─ Safe to answer
   ↓
AI ANSWER GENERATION
   ├─ Send profiles + question to OpenAI GPT-3.5
   ├─ Generate natural answer
   └─ Add photo if single person
   ↓
PHOTO LOGIC
   ├─ Is query general ("list all")? NO
   ├─ Does answer mention 1 person? YES
   ├─ Match photo to person in answer
   └─ Attach: 📸PHOTO📸[URL]
   ↓
DISPLAY to user with formatted text + photo
```

---

## 🗄️ Database as Central Hub

```
                    ┌─────────────────────┐
                    │   leadership.db     │
                    │   (SQLite File)     │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  WRITE          │  │  READ           │  │  SEARCH         │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│                 │  │                 │  │                 │
│ • Scraper saves │  │ • Browse tab    │  │ • FTS5 text     │
│   profiles      │  │   shows all     │  │   search        │
│                 │  │   profiles      │  │                 │
│ • Vector DB     │  │                 │  │ • Vector        │
│   stores        │  │ • Chat displays │  │   semantic      │
│   embeddings    │  │   results       │  │   search        │
│                 │  │                 │  │                 │
│ • Updates       │  │ • Photo URLs    │  │ • Department    │
│   metadata      │  │   loaded        │  │   filters       │
│                 │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## 🔑 Why Database is Critical

### Without Database
```
User asks question
  → Scrape website (30 seconds)
  → Extract profiles
  → Search
  → Answer

EVERY. SINGLE. TIME. 😫
```

### With Database
```
First time:
  → Scrape website (30 seconds)
  → Save to database ✓

Every other time:
  → Read from database (0.1 seconds)
  → Search
  → Answer

INSTANT! 🚀
```

---

## 📊 Database Tables Breakdown

### Table 1: `profiles`
**Purpose:** Store all profile data  
**Records:** 14 (one per team member)  
**Size:** ~500 KB

**Columns:**
- `id` - Auto-incrementing number
- `name` - "Ganna Vadlamaani"
- `role` - "President and CEO"
- `bio` - Full biography text
- `photo_url` - Link to photo
- `linkedin`, `twitter` - Social links
- `department` - "Executive"
- `embedding` - 1536-number vector (for AI search)

### Table 2: `profiles_fts` (Virtual)
**Purpose:** Fast text search  
**Type:** FTS5 (Full-Text Search)  
**Auto-synced:** Changes to `profiles` automatically update this

**Enables queries like:**
```sql
SELECT * FROM profiles_fts WHERE profiles_fts MATCH 'director'
-- Returns all profiles with "director" in name/role/bio
```

---

## 🎯 Key Takeaways

1. **`leadership.db`** = Your app's memory
2. **Stores everything** scraped from website
3. **Enables instant queries** (vs slow re-scraping)
4. **Powers 3 search types:**
   - Text search (FTS5)
   - Semantic search (Vector embeddings)
   - Browse all (SQL queries)
5. **Persists across restarts** - no data loss
6. **Single file** - easy to backup/share

---

## 🔧 Maintenance

### Update Database
```python
# Re-scrape website
streamlit run dynamic_chat_app.py
# Click "🔄 Scrape New Website"
```

### Backup Database
```bash
# Copy the file
cp data/leadership.db data/leadership_backup.db
```

### Reset Database
```bash
# Delete and re-scrape
rm data/leadership.db
# Restart app, scrape website
```

### View Database
```bash
# Install SQLite Browser (free)
# https://sqlitebrowser.org/
# Open: data/leadership.db
```

---

**The database is the HEART of your application!** 💓
