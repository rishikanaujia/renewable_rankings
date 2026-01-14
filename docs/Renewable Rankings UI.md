# Getting Started - Renewable Rankings UI

## ✅ You're Ready to Code!

This guide will help you get the UI running in 5 minutes.

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Setup Environment

```bash
# Navigate to project directory
cd renewable-rankings

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (optional for now)
# Default settings work fine for development
```

### Step 3: Run the Application

```bash
# Method 1: Using run script (simplest)
python run.py

# Method 2: Using Python module
python -m src.ui.app

# Method 3: After installation
pip install -e .
rankings-ui
```

### Step 4: Access the UI

Open your browser and navigate to:
```
http://localhost:7860
```

You should see the Gradio interface with 4 tabs:
- 💬 Chat Assistant
- 📊 Global Rankings  
- 🔍 Country Details
- ℹ️ About

---

## 🎯 Try These Commands

Once the UI is running, try these in the chat:

```
"Show top 10 countries"
"What's Brazil's score?"
"Show me Germany"
"Compare Brazil and Germany"
"Help"
```

---

## 📁 Project Structure Overview

```
renewable-rankings/
├── config/              ← Configuration files
│   ├── app_config.yaml  ← Main app settings
│   ├── parameters.yaml  ← 21 parameter definitions
│   └── weights.yaml     ← Subcategory weights
│
├── src/
│   ├── ui/              ← Gradio interface (START HERE)
│   │   ├── app.py       ← Main application
│   │   ├── handlers/    ← Chat message processing
│   │   └── utils/       ← Formatting helpers
│   │
│   ├── models/          ← Data models (Pydantic)
│   ├── services/        ← Business logic
│   │   └── mock_service.py ← Mock backend with sample data
│   └── core/            ← Utilities (logging, config)
│
└── tests/               ← Test files (coming soon)
```

---

## 🔧 Key Files to Understand

### 1. `src/ui/app.py` - Main Application
The entry point. Creates the Gradio interface with:
- Chat tab
- Rankings table
- Country details
- About page

### 2. `src/ui/handlers/chat_handler.py` - Chat Logic
Processes user messages and routes to appropriate handlers:
- Show rankings
- Show country details
- Comparisons
- Help

### 3. `src/services/mock_service.py` - Mock Backend
Provides sample data for 10 countries. **This is what you'll replace with real agents in Phase 2.**

### 4. `src/models/` - Data Models
Pydantic models for type safety:
- `ranking.py` - Country rankings
- `parameter.py` - Parameter scores
- `correction.py` - Expert corrections

### 5. `config/` - Configuration Files
YAML files for easy configuration:
- `app_config.yaml` - App settings
- `weights.yaml` - Subcategory weights
- `parameters.yaml` - Parameter definitions

---

## 🎨 How to Customize

### Change UI Theme

Edit `config/app_config.yaml`:
```yaml
ui:
  theme: "soft"  # Try: "default", "huggingface", "dark"
```

### Add More Sample Countries

Edit `src/services/mock_service.py` and add to `sample_data` list.

### Modify Chat Responses

Edit `src/ui/handlers/chat_handler.py` to change how messages are processed.

---

## 🐛 Troubleshooting

### Port Already in Use

Change port in `.env`:
```env
GRADIO_SERVER_PORT=7861
```

### Module Not Found Errors

Make sure you activated the virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

### Config File Not Found

Make sure you're running from the project root directory where `config/` exists.

---

## 📊 Understanding the Mock Data

The `mock_service.py` contains rankings for 10 countries:

| Rank | Country | Score |
|------|---------|-------|
| 1 | Germany | 8.75 |
| 2 | United Kingdom | 8.65 |
| 3 | USA | 8.42 |
| 4 | China | 8.31 |
| 5 | Spain | 8.10 |
| 6 | Australia | 7.85 |
| 7 | India | 7.25 |
| 8 | Chile | 6.95 |
| 9 | Vietnam | 6.80 |
| 10 | Brazil | 6.47 |

Each country has:
- Overall score (0-10)
- 6 subcategory scores
- Key strengths (3-5 items)
- Key weaknesses (2-4 items)

---

## 🚀 Next Steps

### Phase 1 (Current): UI Testing ✅
- ✅ Run the UI
- ✅ Test chat functionality
- ✅ Explore all tabs
- ✅ Try different queries

### Phase 2 (Next 6 weeks): Agent Integration
- 📝 Implement parameter agents (21 agents)
- 📝 Implement subcategory agents (6 agents)
- 📝 Build orchestrator
- 📝 Add memory system
- 📝 Integrate with UI

### Phase 3 (Weeks 10-12): Production Polish
- 📝 React UI migration
- 📝 Report generation
- 📝 Deployment

---

## 🤔 Common Questions

**Q: Can I deploy this to Hugging Face?**  
A: Yes! Just push to GitHub and connect to Hugging Face Spaces. Set `GRADIO_SHARE=True` in `.env`.

**Q: How do I add real AI agents?**  
A: That's Phase 2! You'll replace `mock_service.py` with real agent implementations.

**Q: Can I change the scoring system?**  
A: Yes! Edit `config/weights.yaml` and `config/parameters.yaml`.

**Q: Where are logs stored?**  
A: In `logs/app.log`. Check there if something goes wrong.

---

## 💡 Development Tips

### Enable Debug Mode

In `.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### Auto-reload on Code Changes

Gradio supports hot reloading. Just save your changes and refresh the browser.

### Test Without UI

```python
from src.services.mock_service import mock_service

# Get rankings
rankings = mock_service.get_rankings()
print(f"Total countries: {rankings.total_countries}")

# Get specific country
brazil = mock_service.get_country_ranking("Brazil")
print(f"Brazil score: {brazil.overall_score}")
```

---

## 📚 Additional Resources

- **README.md** - Full project documentation
- **config/parameters.yaml** - All 21 parameters defined
- **Implementation Guide.docx** - Detailed architecture
- **src/models/** - Understanding data structures

---

## ✨ You're All Set!

Run this command and start exploring:

```bash
python run.py
```

Then open: http://localhost:7860

**Happy coding! 🚀**
