# 💰 Expense Tracker

A full-stack web application to track personal income and expenses, built with Flask and PostgreSQL.

🔗 **Live Demo:** [https://expense-tracker-lsia.onrender.com](https://expense-tracker-lsia.onrender.com)

---

## ✨ Features

- 🔐 User Authentication (Register / Login / Logout)
- ➕ Add Income and Expense transactions
- 📊 View transaction history
- 🗑️ Delete transactions
- 💾 Persistent data storage with PostgreSQL.
- 📱 Responsive UI

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | PostgreSQL|
| Frontend | HTML, CSS, JavaScript , BootStrap 5 |
| Auth | Flask-Login |
| Deployment | Render |

---

## 🚀 Getting Started (Local Setup)

### Prerequisites
- Python 3.x installed
- Git installed

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Shrutii-Rai/Expense-tracker.git

# 2. Navigate to project directory
cd Expense-tracker

# 3. Install dependencies
pip install -r requirements.txt


# 3. Create virtual environment 
python -m venv venv
source venv/bin/activate   # For Linux/Mac
venv\Scripts\activate      # For Windows

# 4. Run the application
python app.py
```

### Open in Browser
```
http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
Expense-tracker/
│
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Procfile            # Render deployment config
│
├── instance/
│   └── *.db            # SQLite database
│
└── templates/
    └── index.html      # Frontend HTML
```

---

## 🌐 Deployment

This app is deployed on **Render** (Free Tier).

> ⚠️ Note: Free instance may take 30-50 seconds to load after inactivity.

---

## 👩‍💻 Author

**Shrutii Rai**
- GitHub: [@Shrutii-Rai](https://github.com/Shrutii-Rai)
- Live App: [expense-tracker-lsia.onrender.com](https://expense-tracker-lsia.onrender.com)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).