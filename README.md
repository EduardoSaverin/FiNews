# 📰 FiNews — AI-Powered Fintech News Summarizer for India

> **FiNews** is an AI-powered fintech news aggregator built in Python. It fetches the latest updates from multiple RSS and financial sources, filters noise, refines content using LangGraph + LLMs, and delivers concise, high-quality summaries — including automated updates via WhatsApp channels.

---

## 🚀 Features

- 🔄 **Automated RSS Fetching** — Collects fintech news periodically using Celery tasks.
- 🧠 **AI Summarization** — Refines and improves content via LangGraph feedback loops.
- 🧹 **Content Filtering** — Removes redundant or low-quality articles before summarization.
- 💬 **WhatsApp Integration** — Sends curated fintech updates automatically.
- 🕒 **Celery + Redis Scheduling** — Efficient background task management.
- 🇮🇳 **Focused on India** — Sources fintech news relevant to the Indian market.

---

## ⚙️ Tech Stack

- **Python 3.10+**
- **Celery + Redis** for background jobs
- **LangGraph + LLMs** for summarization
- **FastAPI** (optional API)
- **PostgreSQL** for article storage

---

## 🧩 How It Works

1. Celery Beat triggers a task every few minutes.  
2. RSS Fetcher pulls new fintech articles.
3. Raw Content is then saved into database.
4. Content is cleaned and filtered.
5. LangGraph summarizer refines articles with AI feedback.  
6. Summaries are sent to WhatsApp or stored for reading.

---

## 🛠️ Setup

```bash
git clone https://github.com/EduardoSaverin/FiNews.git
cd FiNews
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
