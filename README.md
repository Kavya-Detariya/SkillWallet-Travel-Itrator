# Personalized Travel Itinerary Planner ✈️

**Skill Wallet Capstone Project 4**

A production-grade, AI-powered travel planning web application built with Streamlit, Python, ReportLab, and Google Gemini / Groq LLMs.

Designed with a modern wanderlust aesthetic, this application solves common travel-planning friction points through **smart geographic clustering**, **transparent cost estimation**, **single-activity vibe swapping**, and **publication-quality PDF dossier generation**.

---

## 🌟 Key Features

1. **Smart Destination Recommender (Tab 1)**
   - Recommends top destinations based on travel vibe, budget tier, party size, pace, season suitability, and traveler interests.
   - Works with live AI (Gemini / Groq) and includes a rich curated offline database for instant demo discovery.

2. **Day-by-Day Itinerary Generator with Geographic Clustering (Tab 2)**
   - Breaks each day into structured **Morning**, **Lunch**, **Afternoon**, and **Evening** slots.
   - **Geographic Clustering:** Groups attractions in the same neighborhood/district to eliminate backtracking and long commutes.
   - Detailed activity attributes: Time, Duration, Estimated Cost, Category, and Specific Location.

3. **Transparent Cost Tracking**
   - Live daily expense breakdown (Activities, Dining, Transport).
   - Full trip financial summary including accommodation estimates in **INR (₹)** and **USD ($)**.
   - Currency toggle with clearly labeled demo conversion rates.

4. **Vibe Customization & Granular Activity Swapping (Tab 3)**
   - Allows users to swap a single activity (e.g., "Find vegetarian lunch", "Outdoor market instead of museum", "Cheaper alternative") without regenerating the whole trip.
   - **Preserves geographic proximity** in the neighborhood cluster.
   - Supports single-day regeneration while preserving the rest of the multi-day trip.

5. **Trip Management & Local Persistence (Tab 4)**
   - Zero external database dependencies: stores saved trips in `data/trips.json` combined with Streamlit session state.
   - Full CRUD: Save, Load, Rename, Duplicate, Delete, and JSON Export.

6. **Publication-Quality PDF Dossier Export**
   - Built with ReportLab.
   - Contains Cover, Trip Summary, Clustered Day-by-Day Schedule, Cost Breakdown, and Essential Travel & Emergency Checklist.

7. **Zero-API-Key Demo Mode**
   - 100% functional out of the box without requiring Gemini or Groq credentials.
   - Pre-populated curated data for destinations like Goa, Kyoto, Bali, Paris, Singapore, Jaipur, Mumbai, Delhi, and custom synthesized locations.

---

## 📂 Project Structure

```text
SkillWallet/
├── app.py                      # Main Streamlit UI & interactive orchestration
├── requirements.txt            # Minimal, pinned dependencies
├── README.md                   # Documentation & deployment guide
├── .gitignore                  # Git exclusions (secrets, venv, pycache)
│
├── .streamlit/
│   └── config.toml             # Custom wanderlust theme styling & port settings
│
├── modules/
│   ├── ai_engine.py            # AI abstraction layer (Gemini, Groq, & Demo Fallbacks)
│   ├── itinerary.py            # Itinerary logic, geographic clustering, cost calculations
│   ├── destinations.py         # Curated destination database & offline recommendation engine
│   ├── pdf_export.py           # ReportLab PDF dossier generator
│   ├── storage.py              # Local JSON persistence & CRUD operations
│   └── utils.py                # Currency formatting, JSON parsers, custom CSS
│
└── data/
    └── trips.json              # Local JSON storage for saved itineraries
```

---

## 🚀 How to Run Locally

### 1. Prerequisites
- Python 3.10+ installed.

### 2. Setup Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run app.py
```
The app will launch at `http://localhost:8501`.

---

## 🔑 Optional API Key Setup

The app runs completely in **Demo Mode** without any keys. To enable live AI generations:

### Option A: Enter via UI
Enter your **Gemini** or **Groq** API key directly into the sidebar password field. Keys are kept securely in memory and never exposed or persisted to disk.

### Option B: Local Streamlit Secrets
Create a `.streamlit/secrets.toml` file (this file is ignored in `.gitignore`):
```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
GROQ_API_KEY = "your-groq-api-key-here"
```

---

## ☁️ Deployment to Streamlit Community Cloud

Deploying to **Streamlit Community Cloud** takes under 2 minutes:

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Personalized Travel Itinerary Planner"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

2. **Open Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
   - Click **New app**.

3. **Select Repository**:
   - Repository: `<your-username>/<your-repo-name>`
   - Branch: `main`
   - Main file path: `app.py`

4. **Configure Secrets (Optional)**:
   - In App Settings > **Secrets**, paste:
     ```toml
     GEMINI_API_KEY = "your-gemini-api-key"
     GROQ_API_KEY = "your-groq-api-key"
     ```

5. **Deploy**:
   - Click **Deploy!**
   - The app will build automatically using `requirements.txt` and `.streamlit/config.toml`.

---

## 🛡️ Architecture & Security Considerations
- **No Hardcoded Secrets:** Keys are read dynamically via `st.secrets` or password input.
- **Fail-Safe Fallbacks:** Any network timeout or API rate limit falls back gracefully to curated demo data without crashing the interface.
- **Lightweight Footprint:** Zero external database overhead.

