# Alfred Chatbot

Custom company chatbot for Alfred Lab using LangChain and local FAISS storage.

## What This Does

1. Scrapes public text from `https://alfred-lab.in/`
2. Splits website content into chunks
3. Creates embeddings locally without using OpenAI quota
4. Stores the knowledge base locally in FAISS
5. Answers questions using retrieval-augmented generation

## Storage Choice

This project uses **Option 1: Local FAISS**.

- Fast and simple for learning or small company chatbot projects
- Runs from local files after indexing
- FAISS data is stored in `data/faiss_index/`
- Scraped website text is saved in `data/scraped_pages.json`

---

## 🚀 Complete Setup Guide

### Step 1: Clone & Navigate

```powershell
cd "C:\Users\siddh\OneDrive\Desktop\Prince\alfred chatbot\alfred-chatbot"
```

### Step 2: Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory:

```env
# LLM Provider (groq or openai)
LLM_PROVIDER=groq

# Groq Configuration (FREE - no credit card required)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

# Embedding Configuration
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_DIMENSIONS=384

# Scraping Configuration
MAX_SCRAPE_PAGES=20
```

> **Get FREE Groq API Key**: Visit [console.groq.com](https://console.groq.com) - sign up with Google/GitHub, no credit card needed.

### Step 5: Scrape Website Data

```powershell
python main.py --scrape
```

This will:
- Fetch content from `https://alfred-lab.in/`
- Save scraped data to `data/scraped_pages.json`
- Create FAISS index in `data/faiss_index/`

---

## 🎯 How to Start Frontend & Backend

### Option 1: Using PowerShell Scripts (Recommended)

```powershell
# Start Backend (in one terminal)
.\start_backend.ps1

# Start Frontend (in another terminal)
cd frontend
.\start_frontend.ps1
```

### Option 2: Manual Start

**Backend:**
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run FastAPI server
python api.py
```

The backend will start at `http://localhost:8000`

**Frontend:**
```powershell
cd frontend

# Install frontend dependencies (one time)
npm install

# Start the frontend
npm run dev
```

The frontend will start at `http://localhost:5173`

---

## 📋 Usage

### CLI Mode (Terminal Chat)

```powershell
python main.py --chat
```

### Web UI Mode

1. Start backend: `.\start_backend.ps1`
2. Start frontend: `.\start_frontend.ps1`
3. Open browser: `http://localhost:5173`

---

## 🔧 Project Structure

```
alfred-chatbot/
├── api.py                    # FastAPI backend
├── main.py                   # CLI entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── start_backend.ps1        # Backend startup script
├── start_frontend.ps1       # Frontend startup script
├── src/
│   ├── chatbot.py           # LangChain chatbot logic
│   ├── config.py            # Configuration settings
│   ├── scraper.py           # Web scraper
│   └── vector_store.py     # FAISS vector store
├── data/
│   ├── faiss_index/         # Local FAISS vector storage
│   └── scraped_pages.json  # Scraped website content
└── frontend/
    ├── index.html           # Frontend entry
    ├── package.json         # Node dependencies
    └── src/                 # Frontend source code
```

---

## ⚠️ Difficulties & Solutions

### 1. API Key Issues

| Problem | Solution |
|---------|----------|
| "Invalid API key" error | Check `.env` file has correct `GROQ_API_KEY` or `OPENAI_API_KEY` |
| Rate limit exceeded | Wait a few minutes, Groq has rate limits on free tier |
| No quota left | Switch to Groq (free) or add credits to OpenAI |

### 2. Scraping Issues

| Problem | Solution |
|---------|----------|
| Website not accessible | Check internet connection, try again later |
| Empty scraped data | Website might be blocking bots - check `data/scraped_pages.json` |
| Too many pages | Reduce `MAX_SCRAPE_PAGES` in `.env` |

### 3. FAISS Index Issues

| Problem | Solution |
|---------|----------|
| "No vector store found" | Run `python main.py --scrape` first |
| Index corrupted | Delete `data/faiss_index/` folder and re-scrape |
| Memory error | Reduce chunk size in `src/config.py` |

### 4. Frontend Issues

| Problem | Solution |
|---------|----------|
| "Module not found" | Run `npm install` in frontend folder |
| Port already in use | Change port in `frontend/vite.config.js` |
| CORS errors | Ensure backend is running on port 8000 |

### 5. Common Errors

```
# Error: openai module not found
→ Run: pip install langchain-openai

# Error: faiss module not found  
→ Run: pip install faiss-cpu

# Error: FastAPI not found
→ Run: pip install fastapi uvicorn
```

---

## 📝 Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `groq` | LLM provider (groq/openai) |
| `GROQ_API_KEY` | - | Your Groq API key |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Groq model to use |
| `OPENAI_API_KEY` | - | Your OpenAI API key (if using OpenAI) |
| `EMBEDDING_PROVIDER` | `local` | Embedding provider (local/openai) |
| `MAX_SCRAPE_PAGES` | `20` | Maximum pages to scrape |
| `CHUNK_SIZE` | `1000` | Text chunk size for embeddings |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |

---

## 🆘 Troubleshooting

```powershell
# Reset everything
Remove-Item -Recurse -Force data/faiss_index/
python main.py --scrape

# Check API key is valid
python -c "from src.config import *; print('Config loaded!')"

# View scraped data
Get-Content data/scraped_pages.json | ConvertFrom-Json | Measure-Object
```

---

## 📄 License

MIT License - Feel free to use and modify for your own company chatbot!

Start chatting:

```powershell
python main.py --chat
```

Show source pages while chatting:

```powershell
python main.py --chat --verbose
```

Subcommands also work:

```powershell
python main.py scrape
python main.py chat
```

## Web Interface

The web app uses React for the UI and FastAPI for the Python AI backend.

Included UI features:

- Chat with source links from local FAISS retrieval
- Suggested question chips
- Official contact panel with phone, email, and reception hours
- One-on-one session request form
- Dark mode toggle
- Subtle screen animations

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the FastAPI backend:

```powershell
python -m uvicorn api:app --host 127.0.0.1 --port 8010
```

In a second terminal, start the React frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

API endpoints:

- `GET /api/health`
- `GET /api/contact`
- `POST /api/chat`
- `GET /api/history`
- `POST /api/clear`
- `POST /api/session-request`

## Project Structure

```text
alfred-chatbot/
  main.py
  requirements.txt
  .env
  src/
    config.py
    scraper.py
    vector_store.py
    chatbot.py
  data/
    scraped_pages.json
    faiss_index/
```

## Notes

- Run `python main.py --scrape` again whenever the website content changes.
- Do not commit your real `.env` API key.
- The chatbot answers from scraped website context. If the website does not contain the answer, it should say it does not have enough information.


## Terminal 1(backend)
- cd "C:\Users\siddh\OneDrive\Desktop\Prince\alfred chatbot\alfred-chatbot"
.\start_backend.ps1

## Terminal 2(frontend)
- cd "C:\Users\siddh\OneDrive\Desktop\Prince\alfred chatbot\alfred-chatbot"
.\start_frontend.ps1
