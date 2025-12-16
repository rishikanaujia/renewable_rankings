# Global Renewable Market Rankings System

AI-Powered Renewable Energy Investment Analysis Platform

## 🌟 Overview

This system provides comprehensive rankings of global renewable energy markets using a multi-agent AI architecture. It analyzes 21 parameters across 6 subcategories to help investors make informed decisions.

### Key Features

- **Interactive Chat Interface** - Ask questions in natural language
- **Global Rankings** - Compare countries across multiple dimensions
- **Expert Knowledge Capture** - Learn from expert corrections
- **Multi-Agent AI** - 32 specialized agents analyze different parameters
- **Memory System** - Preserve decades of expert wisdom

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone or extract project
cd renewable-rankings

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip tooling
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run the application
python -m src.ui.app
```

The UI will be available at: http://localhost:7860

## 📁 Project Structure

```
renewable-rankings/
├── config/                 # Configuration files
│   ├── app_config.yaml    # Main app configuration
│   ├── parameters.yaml    # 21 parameter definitions
│   └── weights.yaml       # Subcategory weights
├── src/
│   ├── ui/                # Gradio UI module
│   ├── agents/            # Multi-agent system (Phase 2)
│   ├── memory/            # Memory system (Phase 2)
│   ├── data/              # Data layer (Phase 2)
│   ├── models/            # Data models
│   ├── core/              # Core utilities
│   └── services/          # Business logic
├── tests/                 # Tests
├── data/                  # Data storage
├── logs/                  # Log files
└── docs/                  # Documentation
```

## 🎯 Usage Examples

### Chat Interface

```
User: "Show me top 10 countries"
System: [Displays ranked table]

User: "What's Brazil's score?"
System: [Shows detailed Brazil ranking]

User: "Compare Germany and USA"
System: [Shows side-by-side comparison]
```

### Expert Corrections (Phase 2)

```
User: "Brazil Contract Terms should be 9, not 8"
System: "Why? (minimum 50 characters)"
User: "Curtailment improved from 3-4% to 2.1% in Q3"
System: "✅ Updated. Apply to Colombia, Chile?"
```

## 📊 Scoring System

### Three-Level Hierarchy

**Level I: Critical (55-70%)**
- Regulation (20-25%)
- Profitability (20-25%)
- Accommodation (15-20%)

**Level II: Important (20-30%)**
- Market Size & Fundamentals (10-15%)
- Competition & Ease (10-15%)

**Level III: Modifiers (5-10%)**
- System/External Modifiers (5-10%)

### Example: Brazil = 6.47/10

```
Regulation:              8.0 × 0.225 = 1.80
Profitability:           6.0 × 0.225 = 1.35
Accommodation:           5.5 × 0.175 = 0.96
Market & Fundamentals:   8.0 × 0.125 = 1.00
Competition & Ease:      7.3 × 0.125 = 0.91
System Modifiers:        6.0 × 0.075 = 0.45
                                    ------
FINAL SCORE:                        6.47 / 10
```

## 🏗️ Development Roadmap

### Phase 1: UI Foundation (Weeks 1-3) ✅
- ✅ Gradio interface
- ✅ Chat functionality
- ✅ Mock data
- ✅ Basic navigation

### Phase 2: Agent Integration (Weeks 4-9)
- 🔄 21 parameter agents
- 🔄 6 subcategory agents
- 🔄 Master orchestrator
- 🔄 Expert correction workflow
- 🔄 Memory system (PostgreSQL + Redis + ChromaDB)

### Phase 3: Production Polish (Weeks 10-12)
- 📅 React UI migration
- 📅 Report generation
- 📅 Advanced analytics
- 📅 Production deployment

### Phase 4: Advanced Features (Future)
- 📅 Voice input
- 📅 Mobile optimization
- 📅 Batch operations
- 📅 API access

## 🔧 Configuration

### Environment Variables (.env)

```env
APP_NAME=Renewable Energy Rankings
ENVIRONMENT=development
DEBUG=True

GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860

LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### App Configuration (config/app_config.yaml)

```yaml
app:
  name: "Global Renewable Market Rankings"
  version: "1.0.0"

ui:
  title: "Renewable Energy Market Rankings"
  theme: "soft"
  chat_history_limit: 50

system:
  mock_mode: true  # Set to false when real agents are ready
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_ui/test_chat_handler.py

# Run with coverage
pytest --cov=src tests/
```

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)

## 🛠️ Technology Stack

- **Frontend:** Gradio 4.0
- **Backend:** Python 3.9+
- **AI Framework:** LangChain + LangGraph (Phase 2)
- **Memory:** PostgreSQL + Redis + ChromaDB (Phase 2)
- **LLM:** Azure OpenAI / Claude (Phase 2)
- **Testing:** pytest

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 📞 Contact

For questions or feedback, contact the development team.

---

**Version:** 1.0.0 - Phase 1  
**Status:** UI Demo - Agent Integration Coming Soon  
**Built with ❤️ for renewable energy investors**
