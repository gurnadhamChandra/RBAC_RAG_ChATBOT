# 🤖 RBAC-Based RAG Chatbot

A secure and intelligent AI chatbot designed for internal organizational use.  
Built using **Next.js (Frontend)**, **FastAPI (Backend)**, and **RAG with FAISS**, FinBot delivers **role-based, context-aware answers** using **LLMs (Groq - LLaMA 3)**.

---

## 🚀 Overview

 AI-powered chatbot that provides **department-specific insights** based on user roles.  
It uses **Retrieval-Augmented Generation (RAG)** to fetch relevant information from documents and generate accurate responses in real time.

---

## ⚡ Tech Stack

### 🎨 Frontend
- Next.js – Modern React framework for UI
- Tailwind CSS / CSS – Styling

### 🚀 Backend
- FastAPI – High-performance API framework
- JWT Authentication – Secure login & access control

### 🧠 AI / ML
- Groq API (LLaMA 3 - llama3-8b-8192)
- LangChain – Orchestration
- FAISS – Vector database for semantic search
- RAG (Retrieval-Augmented Generation)

---

## 📌 Features

### 🔐 Role-Based Access Control (RBAC)
- Users are assigned roles (HR, Finance, etc.)
- Access to chatbot responses is restricted based on role
- Ensures secure and relevant information delivery

---

### 💬 AI Chatbot (RAG + LLaMA 3)
- Uses FAISS vector store for document retrieval
- Generates fast and accurate responses using Groq LLM
- Provides **context-aware answers**

---

### 🖥️ Next.js Frontend
- Interactive chatbot UI
- Clean and responsive design
---

### 🛡️ JWT Authentication (Backend)
- Secure login system
- Token-based authentication
- User roles stored and validated via backend

> ⚠️ Note: JWT is implemented in backend; frontend integration can be enhanced further.

---

### 🧠 Conversation Memory
- Maintains chat context
- Improves response quality and continuity

---

### 📄 Dynamic Vector Store
- Documents are converted into embeddings
- Stored in FAISS for fast retrieval
- Supports role-based document filtering

---

## 🗂️ Project Structure

```bash
RBAC_RAG_CHATBOT/
│
├── backend/
│   ├── app/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── faiss_vectors/
│   ├── resources/
│   ├── users.json
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   └── services/
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
│
└── README.md
```



## ⚙️ Setup Instructions

### 1. Clone the Repository
git clone https://github.com/your-username/RBAC_RAG_CHATBOT.git
cd RBAC_RAG_CHATBOT


### 2. Backend Setup
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
uvicorn main:app --reload

### 3. Frontend Setup
cd frontend
npm install
npm run dev

### 4. Environment Variables
Create .env file in backend:
GROQ_API_KEY=your_api_key_here

### 🔐 Roles & Access
Role	Access Scope
HR	---Employee data, payroll, policies
Finance ---	Expenses, budgets, revenue
Marketing ---	Campaigns, leads
Engineering	--- Dev docs, architecture
C-Level Exec	----Full access
Employee	---General FAQs

### 💬 Sample Queries
HR → "Who has the most leave balance?"
Finance → "List reimbursements above ₹10,000"
Engineering → "Explain CI/CD pipeline"
Employee → "How to apply for leave?"

### 👨‍💻 Author

Gurnadham Chandra
Senior Software Engineer | AI/ML Enthusiast
