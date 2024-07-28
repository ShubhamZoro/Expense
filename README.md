# Expense Sharing Web Application

This is a Flask-based web application for managing and sharing daily expenses. Users can register, log in, add expenses, and download balance sheets.

## Features

- User registration and email verification
- User login and logout
- Adding and managing expenses
- Splitting expenses by exact amounts, percentages, and equal splits
- Downloading balance sheets as CSV files

1. **Clone the repository:**
   git clone https://github.com/ShubhamZoro/Expense.git
2. ** Installing requirement:**
   pip install -r requirements.txt
3. ** Run these command in sequence:**
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   python app.py


