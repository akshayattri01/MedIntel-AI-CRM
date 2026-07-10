# 🏥 MedIntel AI CRM

An AI-first Healthcare CRM built using **React**, **FastAPI**, **PostgreSQL**, **LangGraph**, and **Groq Llama 3.3 70B**. The application helps Medical Representatives efficiently manage Healthcare Professional (HCP) interactions using AI-powered workflows such as interaction logging, follow-up planning, sentiment analysis, analytics, and intelligent CRM assistance.

---

# ✨ Features

## 📊 Dashboard
- Total HCP statistics
- Today's meetings
- Pending follow-ups
- Monthly interaction analytics
- Recent CRM activity
- Sentiment overview

---

## 👨‍⚕️ HCP Directory

- Add HCP
- Edit HCP
- Delete HCP
- Search HCP
- View doctor profile

---

## 📝 Interaction Management

- Log Interaction
- Edit Interaction
- Delete Interaction
- Interaction History
- AI-assisted interaction summarization

---

## 🤖 AI Assistant

Powered by **LangGraph + Groq Llama 3.3 70B**

Supports:

- Summarize Interactions
- Generate Follow-up Plans
- Draft Follow-up Emails
- Find Doctors by Sentiment
- Explain Dashboard Analytics
- AI Insights

---

# 🧠 LangGraph Agent Workflow

```
User Prompt
      │
      ▼
Intent Detection
      │
      ▼
Entity Extraction
      │
      ▼
Tool Selection
      │
      ▼
Tool Execution
      │
      ▼
LLM Response Generation
      │
      ▼
Final Response
```

---

# 🔧 LangGraph Tools

The project implements five AI tools required by the assignment.

### 1️⃣ Log Interaction

Captures HCP interaction details from user input and stores structured CRM records.

Example:

- Doctor Name
- Discussion Summary
- Samples Shared
- Sentiment
- Follow-up Actions

---

### 2️⃣ Edit Interaction

Allows editing previously logged interactions.

Can update:

- Summary
- Sentiment
- Materials Shared
- Follow-up Notes
- Meeting Details

---

### 3️⃣ Interaction Summarizer

Summarizes interaction history using Llama 3.3 70B.

---

### 4️⃣ Follow-up Planner

Generates AI-powered follow-up recommendations.

---

### 5️⃣ CRM Analytics

Explains dashboard analytics and suggests next best actions.

---

# ⚙️ Tech Stack

## Frontend

- React
- Redux Toolkit
- TypeScript
- Tailwind CSS
- React Router
- Recharts

## Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- LangGraph
- Groq API

## AI

- LangGraph
- Groq Llama 3.3 70B
- Prompt Engineering

---

# 📂 Project Structure

```
MedIntel-AI-CRM
│
├── backend
│
├── frontend
│
├── screenshots
│   ├── dashboard.png
│   ├── hcp-directory.png
│   └── ai-assistant.png
│
└── README.md
```

---

# 📸 Screenshots

## Dashboard

![Dashboard](screenshots/dashboard.png)

Shows CRM overview including HCP count, meetings, follow-ups, monthly interactions, recent activity, and sentiment.

---

## HCP Directory

![HCP Directory](screenshots/hcp-directory.png)

Manage Healthcare Professionals using complete CRUD operations.

---

## AI Assistant

![AI Assistant](screenshots/ai-assistant.png)

LangGraph-powered assistant for CRM intelligence including summarization, follow-up planning, analytics explanation, and AI insights.

---

# ✅ CRUD Operations

✔ Add HCP

✔ Edit HCP

✔ Delete HCP

✔ Search HCP

✔ Log Interaction

✔ Edit Interaction

✔ Delete Interaction

✔ View Interaction History

---

# 💾 Database

PostgreSQL stores:

- HCP Profiles
- Interaction Logs
- Follow-up Plans
- Analytics Data
- Sentiment Information

---

# 🚀 Running the Project

## Clone Repository

```bash
git clone https://github.com/akshayattri01/MedIntel-AI-CRM.git
```

---

## Backend

```bash
cd backend

python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# 🔑 Environment Variables

Backend

```env
DATABASE_URL=

GROQ_API_KEY=

JWT_SECRET=
```

Frontend

```env
VITE_API_URL=http://localhost:8000
```

---

# 🎯 Assignment Requirements Covered

- ✅ LangGraph Agent
- ✅ LLM Integration (Groq Llama 3.3 70B)
- ✅ Log Interaction Tool
- ✅ Edit Interaction Tool
- ✅ HCP CRUD
- ✅ AI Assistant
- ✅ Dashboard Analytics
- ✅ PostgreSQL Database
- ✅ FastAPI Backend
- ✅ React Frontend
- ✅ GitHub Repository
- ✅ README Documentation

---

# 🔮 Future Enhancements

- Voice Interaction Logging
- OCR Prescription Scanner
- WhatsApp Integration
- Email Automation
- Appointment Scheduling
- Predictive CRM Analytics
- Multi-user Authentication

---

# 👨‍💻 Author

**Akshay Attri**

GitHub:
https://github.com/akshayattri01

---

# 📄 License

This project was developed as part of an AI-First CRM technical assignment using **LangGraph**, **FastAPI**, **React**, **PostgreSQL**, and **Groq Llama 3.3 70B**.