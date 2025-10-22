# Database Explanation: `leadership.db`

## What is `leadership.db`?

`leadership.db` is a **SQLite database file** that stores all the team member information scraped from the Amzur website.

### 📊 Current Status
- **Location:** `data/leadership.db`
- **Type:** SQLite Database (single file)
- **Size:** Contains **14 team profiles**
- **Purpose:** Persistent storage of leadership data

---

## Why Do We Use a Database?

### Without Database ❌
```
Every time you ask a question:
1. Scrape website again (slow! 30+ seconds)
2. Extract all profiles
3. Process data
4. Answer question
⏱️ Result: VERY SLOW
```

### With Database ✅
```
First time only:
1. Scrape website once
2. Store in database (leadership.db)

Every question after:
1. Read from database (instant!)
2. Answer question
⏱️ Result: FAST (< 1 second)
```

---

## What's Stored in the Database?

### Profile Table Structure

Each team member profile contains:

```sql
CREATE TABLE profiles (
    id                  - Unique identifier
    name               - Person's name (e.g., "Ganna Vadlamaani")
    role               - Job title (e.g., "President and CEO")
    bio                - Biography/description
    photo_url          - Link to their photo
    contact            - Email address
    phone              - Phone number
    linkedin           - LinkedIn profile URL
    twitter            - Twitter handle
    department         - Department name
    profile_url        - Original webpage URL
    created_at         - When added to database
    updated_at         - Last updated time
)
```

### Example Record
```json
{
  "id": 2,
  "name": "Ganna Vadlamaani",
  "role": "President and CEO (Solutions Business & Growth Markets)",
  "bio": "Ganna brings extensive experience in...",
  "photo_url": "https://amzur.com/.../Ganna-Photo-Final-Version-4-500x500-1.webp",
  "linkedin": "https://www.linkedin.com/in/ganna-vadlamaani/",
  "department": "Executive",
  "profile_url": "https://amzur.com/leadership/ganna-vadlamaani/"
}
```

---

## Special Feature: FTS5 Full-Text Search

The database also has a **search index** called `profiles_fts`:

```sql
CREATE VIRTUAL TABLE profiles_fts USING fts5(
    name,
    role,
    bio,
    department
)
```

### What Does This Do?

**FTS5 = Full-Text Search (version 5)**

Allows super-fast text searching like Google!

**Example:**
```python
# Instead of scanning every profile manually:
for profile in all_profiles:
    if "ceo" in profile.name.lower() or "ceo" in profile.role.lower():
        # Found it!

# FTS5 does it instantly:
SELECT * FROM profiles_fts WHERE profiles_fts MATCH 'ceo'
⚡ Result: Instant search across all text fields!
```

---

## How the Database is Used

### 1. **Initial Scraping** (First Time)
```python
# enhanced_scraper.py
profiles = scrape_with_discovery("https://amzur.com", deep_scrape=True)

# database.py
insert_profiles(profiles)  # Save to leadership.db
```

### 2. **Searching** (Every Query)
```python
# database.py
results = search_profiles("CEO")  # Searches leadership.db using FTS5
# Returns: [Ganna Vadlamaani, Bala Nemani, ...]
```

### 3. **AI Vector Search** (Advanced)
```python
# vector_db.py
# Creates embeddings for each profile
# Stores them IN the same database
results = vector_search_profiles("who handles AI projects?")
# Uses semantic search (meaning-based, not just keywords)
```

---

## Database vs Vector Embeddings

Your project uses **BOTH**:

### Regular Database (SQLite)
- **Stores:** Raw profile data (name, role, bio, photo, etc.)
- **Search Method:** Text matching ("CEO" finds "CEO")
- **Use Case:** Exact searches, browsing all profiles

### Vector Database (Embeddings in SQLite)
- **Stores:** AI-generated embeddings (mathematical representations)
- **Search Method:** Semantic similarity (meaning-based)
- **Use Case:** "Who handles cloud infrastructure?" finds "Director of Operations"

Both stored in the **SAME `leadership.db` file**!

---

## Key Benefits

### ✅ Performance
- **First load:** 30 seconds (scrape + save to DB)
- **All future queries:** < 1 second (read from DB)

### ✅ Persistence
- Data survives app restarts
- No need to re-scrape every time
- Can work offline after initial scrape

### ✅ Search Power
- **FTS5:** Fast text search ("CEO", "director", etc.)
- **Vector embeddings:** Smart semantic search
- **SQL queries:** Filter by department, role, etc.

### ✅ Data Integrity
- Single source of truth
- Consistent data across app
- Easy to update (just re-scrape)

---

## Database Operations in Your Code

### Initialize (create tables)
```python
# database.py
init_database()  # Creates leadership.db with all tables
```

### Insert/Update
```python
# After scraping
insert_profiles(profiles)  # Add new profiles
```

### Search
```python
# Text search
search_profiles("CEO")

# Get by department
get_profiles_by_department("Executive")

# Get all
get_all_profiles()
```

### Vector Search (AI-powered)
```python
# vector_db.py
vector_search_profiles("who handles technology?")
# Returns profiles ranked by semantic similarity
```

---

## File Size & Storage

- **Database file:** `data/leadership.db` (usually < 1 MB)
- **Contains:** 
  - 14 profiles with full details
  - FTS5 search index
  - Vector embeddings (1536 dimensions per profile)
- **Excluded from Git:** Listed in `.gitignore` (data is user-specific)

---

## Why SQLite?

### Perfect for This Project ✅

1. **No server needed** - Just a file
2. **Fast** - Optimized for single-user apps
3. **Reliable** - Used by billions of devices (phones, browsers, etc.)
4. **Simple** - No complex setup
5. **Portable** - One file contains everything

### When NOT to Use SQLite ❌

- Multiple users editing simultaneously
- Very large datasets (100GB+)
- Distributed systems across servers

**For your use case (single-user knowledge base): SQLite is PERFECT!**

---

## Summary

**`leadership.db` is your project's memory!**

- 🧠 **Stores:** All 14 team profiles with details
- 🔍 **Enables:** Fast text search (FTS5)
- 🤖 **Powers:** AI semantic search (vector embeddings)
- ⚡ **Performance:** Instant queries vs 30s re-scraping
- 💾 **Persistent:** Data survives restarts

Without it, your app would need to scrape the website **every single time** someone asks a question!

---

## Want to Explore?

You can view the database using:

**Option 1: SQLite Browser (GUI)**
```bash
# Download from: https://sqlitebrowser.org/
# Open: data/leadership.db
```

**Option 2: Command Line**
```bash
sqlite3 data/leadership.db
.tables          # Show all tables
SELECT * FROM profiles LIMIT 5;
.quit
```

**Option 3: Python**
```python
import sqlite3
conn = sqlite3.connect('data/leadership.db')
cursor = conn.cursor()
cursor.execute("SELECT name, role FROM profiles")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")
```
