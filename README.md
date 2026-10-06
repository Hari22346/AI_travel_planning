# ✈️ HARI — AI Travel Planner

HARI is a **Multi-Agent AI Travel Planning System** built using **LangGraph**.

It searches for flights and hotels, creates an itinerary, and generates a complete travel plan based on the user's requirements.

---

## 🚀 Features

* ✈️ Flight Search
* 🏨 Hotel Search
* 🗺️ AI Itinerary Generation
* 🤖 Final Travel Plan Generation
* 🧠 PostgreSQL Memory
* 🌐 API Integration
* 💻 Streamlit Web Interface
* 📄 Download Travel Plan

---

## 🛠️ Tech Stack

* Python
* LangGraph
* LangChain
* Groq
* PostgreSQL
* Tavily
* AviationStack
* Streamlit

---

## 🤖 AI Agents

```text
User
  ↓
✈️ Flight Agent
  ↓
🏨 Hotel Agent
  ↓
🗺️ Itinerary Agent
  ↓
🧠 Final Response Agent
  ↓
Complete Travel Plan
```

| Agent           | Technology    | Purpose              |
| --------------- | ------------- | -------------------- |
| Flight Agent    | AviationStack | Flight information   |
| Hotel Agent     | Tavily        | Hotel search         |
| Itinerary Agent | Groq          | Day-by-day itinerary |
| Final Agent     | Groq          | Final travel plan    |

PostgreSQL stores the LangGraph state using a `thread_id`.

---

---

## ⚙️ Installation

### 1. Create Virtual Environment

```bash
python -m venv langgraph_env3
```

### Windows

```bash
langgraph_env3\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install langgraph langchain langchain-groq langchain-community langchain-tavily psycopg[binary] psycopg_pool python-dotenv tavily-python requests streamlit
```

```bash
pip install -U "psycopg[binary,pool]" langgraph-checkpoint-postgres
```

---

## 🐘 PostgreSQL Setup

Install PostgreSQL:

[PostgreSQL Download](https://www.postgresql.org/download/?utm_source=chatgpt.com)

Create the database:

```sql
CREATE DATABASE langgraph_memory_demo;
```

---

## 🔐 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key

DATABASE_URL=postgresql://postgres:your_password@localhost:5432/langgraph_memory_demo
```

> Never commit `.env` or API keys to GitHub.

### API Keys

* **Groq:** [Groq Console](https://console.groq.com?utm_source=chatgpt.com)
* **Tavily:** [Tavily](https://tavily.com?utm_source=chatgpt.com)
* **AviationStack:** [AviationStack](https://aviationstack.com?utm_source=chatgpt.com)

---

## ▶️ Run the Project

### Terminal

```bash
python main.py
```

### Streamlit

```bash
streamlit run frontend.py
```

---

## 💬 Example Request

```text
Plan a 7-day Japan trip from Bengaluru for 2 people
under ₹2 lakhs.

Include flights, hotels, sightseeing, and a day-by-day
itinerary. Prefer 3–4 star hotels.
```

---

## 📊 Streamlit Inputs

* Departure city
* Destination
* Departure date
* Return date
* Travelers
* Budget
* Currency
* Travel style
* Additional requirements

---

## 📄 Output

The generated travel plan can be downloaded as a Markdown file and is saved in:

```text
travel_plans/
```

---

## 🔒 `.gitignore`

```gitignore
.env
__pycache__/
*.pyc
langgraph_env3/
travel_plans/
```

---

## 🚀 Future Improvements

* Better flight filtering
* Dedicated hotel API
* Currency conversion
* Weather integration
* Maps integration
* Restaurant recommendations
* PDF export
* User authentication
