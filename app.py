from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import os
from collections import OrderedDict

app = Flask(_name_)
app.secret_key = 'shruti_expense_tracker_2026'

uri = os.environ.get('DATABASE_URL', 'sqlite:///expense.db')
if uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    amount = db.Column(db.Float)
    category = db.Column(db.String(50))
    type = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = bcrypt.generate_password_hash(password)
        user = User(username=username, password=hashed)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password!')
    return render_template('login.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Home
@app.route('/')
@login_required
def home():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    transactions_list = [{'id': t.id, 'title': t.title, 'amount': t.amount,
                          'category': t.category, 'type': t.type} for t in transactions]

    total_income = sum(t['amount'] for t in transactions_list if t['type'] == 'Income')
    total_expense = sum(t['amount'] for t in transactions_list if t['type'] == 'Expense')
    savings = total_income - total_expense

    if total_income > 0:
        percentage = (total_expense / total_income) * 100
    else:
        percentage = 0

    if percentage >= 80:
        warning = "🔴 Alert! 80% budget used!"
    elif percentage >= 50:
        warning = "🔺 Warning! 50% budget used!"
    else:
        warning = "🟢 Safe! You are within budget!"

    insights = []
    if transactions_list:
        categories = {}
        for t in transactions_list:
            if t['type'] == 'Expense':
                cat = t['category']
                categories[cat] = categories.get(cat, 0) + t['amount']

        if categories:
            top_category = max(categories, key=categories.get)
            insights.append(f"🔍 Highest spending: {top_category} (₹{categories[top_category]:.0f})")

        if total_income > 0:
            saving_rate = (savings / total_income) * 100
            if saving_rate >= 50:
                insights.append(f"🌟 Excellent! You are saving {saving_rate:.0f}% of your income!")
            elif saving_rate >= 30:
                insights.append(f"👍 Good! You are saving {saving_rate:.0f}% of your income!")
            elif saving_rate >= 10:
                insights.append(f"⚠️ Save more! Currently saving only {saving_rate:.0f}%!")
            else:
                insights.append(f"🔴 Danger! Saving only {saving_rate:.0f}%!")

        expense_count = len([t for t in transactions_list if t['type'] == 'Expense'])
        insights.append(f"📊 Total {expense_count} expenses this month!")

        if categories:
            for cat, amount in categories.items():
                cat_percentage = (amount / total_income) * 100 if total_income > 0 else 0
                if cat_percentage > 30:
                    insights.append(f"💡 Tip: Reduce {cat} spending - it's {cat_percentage:.0f}% of your income!")

        if percentage >= 80:
            insights.append("🚨 Critical: You have spent 80% of income - stop non-essential spending!")
        elif percentage >= 60:
            insights.append("⚠️ Warning: 60% budget used - avoid luxury expenses now!")
        elif percentage >= 40:
            insights.append("📌 Note: 40% budget used - keep tracking!")

    return render_template('index.html',
                           transactions=transactions_list,
                           total_income=total_income,
                           total_expense=total_expense,
                           savings=savings,
                           warning=warning,
                           percentage=round(percentage, 1),
                           insights=insights)

# Add Transaction
@app.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form['title']
    amount = float(request.form['amount'])
    category = request.form['category']
    type = request.form['type']
    t = Transaction(title=title, amount=amount, category=category,
                    type=type, user_id=current_user.id)
    db.session.add(t)
    db.session.commit()
    return redirect('/')

# Delete Transaction
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    t = Transaction.query.get(id)
    if t and t.user_id == current_user.id:
        db.session.delete(t)
        db.session.commit()
    return redirect('/')

# Archive
@app.route('/archive')
@login_required
def archive():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    monthly = {}
    for t in transactions:
        key = t.date.strftime('%B %Y')
        if key not in monthly:
            monthly[key] = []
        monthly[key].append(t)

    archive_data = {}
    for month, txns in monthly.items():
        income = sum(t.amount for t in txns if t.type == 'Income')
        expense = sum(t.amount for t in txns if t.type == 'Expense')
        archive_data[month] = {
            'transactions': [{'title': t.title, 'amount': t.amount,
                             'category': t.category, 'type': t.type,
                             'date': t.date.strftime('%d %b')} for t in txns],
            'income': income,
            'expense': expense,
            'savings': income - expense
        }

    archive_data = OrderedDict(
        sorted(archive_data.items(),
               key=lambda x: datetime.strptime(x[0], '%B %Y'),
               reverse=True)
    )

    return render_template('archive.html', archive_data=archive_data)

if _name_ == '_main_':
    app.run(debug=True)