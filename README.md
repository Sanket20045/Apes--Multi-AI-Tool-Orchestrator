# Apes — Multi-Tool AI Agent

**Apes** is an intelligent, multi-tool AI orchestrator built for the AI Hackathon. It accepts natural-language user requests and leverages **Google Gemini LLM** with native **Function Calling** to select, execute, and synthesize results from multiple specialized local logic and external REST API tools.

---

## Interfaces Available

1. **Anime.js Web UI (`http://localhost:8000`):** Interactive UI built using the design aesthetics and components of **[animejs.com](https://animejs.com/)**, featuring a kinetic staggered matrix background, toolbox modules shelf, execution timeline scrubber, and spring-physics chat rendering.
2. **Terminal Interactive CLI (`python main.py`):** Fast REPL chat session with real-time tool selection visibility.

---

## High-Level Architecture

```text
┌────────────────────────────────────────────────────────┐
│                   BROWSER CLIENT                       │
│        index.html  │  style.css  │  app.js             │
└───────────────────────────┬────────────────────────────┘
                            │ Fetch API (POST /api/chat)
                            ▼
┌────────────────────────────────────────────────────────┐
│               PYTHON BACKEND SERVER                    │
│                     server.py                          │
│            (Standard library http.server)              │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                   APES ORCHESTRATOR                    │
│                   orchestrator.py                      │
│        Gemini LLM Function Calling + 4 Tools           │
└───────────────────────────┬────────────────────────────┘
                            │
                         Tool Selection
                            │
    ┌─────────────────┬─────┴───────────┬─────────────────┐
    │                 │                 │                 │
    ▼                 ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│  Calculator  │ │   Weather    │ │ Text Utility │ │ Currency (Ext.)  │
│  (Safe AST)  │ │ (Open-Meteo) │ │   (Local)    │ │  (Frankfurter)   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └────────┬─────────┘
       │                │                │                  │
       ▼                ▼                ▼                  ▼
     Result        Open-Meteo API      Result        Frankfurter API
                        │                                   │
                        ▼                                   ▼
                      Result                              Result
       │                │                │                  │
       └────────────────┼────────────────┴──────────────────┘
                        │ Structured Tool Result(s)
                        ▼
            ┌────────────────────────┐
            │      GEMINI LLM        │
            │                        │
            │   Response Generator   │
            └───────────┬────────────┘
                        │
                        ▼ Natural Language Response
                         USER
```

---

## Supported Tools

| Tool | File | Purpose | API / Mechanism |
|------|------|---------|-----------------|
| **Calculator** | [`calculator.py`](file:///calculator.py) | Evaluates arithmetic, precedence, decimals, constants (`pi`, `e`), and functions (`sqrt`, `sin`, `cos`, `tan`, `log`) | Safe AST parsing (Zero `eval()`, DoS protected) |
| **Weather Lookup** | [`weather.py`](file:///weather.py) | Fetches live current weather (temperature, wind speed, conditions) for supported cities | Open-Meteo REST API (No key required) |
| **Text Utility** | [`text_utils.py`](file:///text_utils.py) | Word count, character count, string reversing, uppercase/lowercase, and sentence counting | Pure local string logic |
| **Currency Converter** | [`currency.py`](file:///currency.py) | Live exchange rate conversions between international currencies (USD, INR, EUR, GBP, JPY, CAD, AUD, etc.) | Frankfurter REST API (No key required) |

---

## Project Structure

```text
Apes/
│
├── server.py           # Zero-dependency Web backend server (http.server)
├── web/                # Pure HTML / CSS / JS Frontend Assets
│   ├── index.html      # Clean glassmorphic web app interface
│   ├── style.css       # Design tokens, typography & animations
│   └── app.js          # Client logic & tool execution badges
│
├── main.py             # Main CLI chat interface with tool visibility
├── orchestrator.py     # Gemini LLM function-calling orchestrator & tool dispatcher
│
├── calculator.py       # Tool 1: Safe AST calculator logic
├── weather.py          # Tool 2: Open-Meteo weather lookup logic
├── text_utils.py       # Tool 3: Word/Text utility operations
├── currency.py         # Tool 4: Frankfurter currency converter logic
│
├── test_calculator.py  # Calculator automated unit tests (43 tests)
├── test_weather.py     # Weather lookup automated unit tests (17 tests)
├── test_text_utils.py  # Text utility automated unit tests (14 tests)
├── test_currency.py    # Currency converter automated unit tests (10 tests)
├── test_orchestrator.py# Orchestrator dispatch & declaration tests (9 tests)
│
├── requirements.txt    # Dependencies (requests, python-dotenv, google-genai)
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules (.env, __pycache__, etc.)
└── README.md           # Documentation & project guide
```

---

## Installation & Setup

1. **Navigate to the project directory:**
   ```bash
   cd ai-hackatho
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Set your Google Gemini API key in `.env`:
   ```env
   GEMINI_API_KEY=YOUR_GEMINI_API_KEY
   ```

---

## How to Run

### 1. Launch the Web UI
```bash
python server.py
```
Open **`http://localhost:8000`** in your browser.

### 2. Launch the Interactive CLI
```bash
python main.py
```

### 3. Direct Command-Line Query
```bash
python main.py "What is 125 * 24?"
python main.py "What is the weather in Mumbai?"
python main.py "Convert 100 USD to INR"
```

---

## Running Automated Tests

Run the complete test suite (93 unit tests):

```bash
python -m unittest discover -v
```
