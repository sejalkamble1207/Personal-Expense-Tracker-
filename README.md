

ExpenseAI — Personal Expense Tracker
A beginner-friendly AI-inspired personal expense tracker built with Python, Flask, SQLite, HTML, CSS and JavaScript.
Features
Add, edit and delete expenses
Category-wise spending
Monthly total
Highest expense
Search and filters
Chart.js dashboard
Transparent Python-based spending analysis
Responsive modern UI
SQLite persistence
Run locally
Install Python 3.10+.
Open a terminal in this folder.
Create a virtual environment (recommended):
Windows: python -m venv venv then venv\\Scripts\\activate
macOS/Linux: python3 -m venv venv then source venv/bin/activate
Install dependencies: pip install -r requirements.txt
Start: python app.py
Open: http://127.0.0.1:5000
The SQLite database is created automatically on first run.
Note about AI
The included AI Analysis module is intentionally transparent and rule-based. It analyzes actual stored expenses and generates explainable observations/recommendations. It does not pretend that static demo text is AI. A real generative AI API can be added later as an optional extension.