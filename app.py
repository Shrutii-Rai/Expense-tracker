from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///expense.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    amount = db.Column(db.Float)
    category = db.Column(db.String(50))
    type = db.Column(db.String(20))

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    transactions = Transaction.query.all()
    transactions_list = [{'id': t.id, 'title': t.title, 'amount': t.amount, 'category': t.category, 'type': t.type} for t in transactions]

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
        warning = "⚠️ Warning! 50% budget used!"
    else:
        warning = "✅ Safe! You are within budget!"

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
                    insights.append(f"💡 Tip: Reduce {cat} spending — it's {cat_percentage:.0f}% of your income!")

        if percentage >= 80:
            insights.append("🚨 Critical: You have spent 80% of income — stop non-essential spending!")
        elif percentage >= 60:
            insights.append("⚠️ Warning: 60% budget used — avoid luxury expenses now!")
        elif percentage >= 40:
            insights.append("📌 Note: 40% budget used — keep tracking!")

    return render_template('index.html',
                         transactions=transactions_list,
                         total_income=total_income,
                         total_expense=total_expense,
                         savings=savings,
                         warning=warning,
                         percentage=round(percentage, 1),
                         insights=insights)

@app.route('/add', methods=['POST'])
def add():
    title = request.form['title']
    amount = float(request.form['amount'])
    category = request.form['category']
    type = request.form['type']

    t = Transaction(title=title, amount=amount, category=category, type=type)
    db.session.add(t)
    db.session.commit()

    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    t = Transaction.query.get(id)
    db.session.delete(t)
    db.session.commit()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)