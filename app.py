from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root1234",
        database="expense_db"
    )

@app.route('/')
def home():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()
    db.close()

    total_income = sum(float(t['amount']) for t in transactions if t['type'] == 'Income')
    total_expense = sum(float(t['amount']) for t in transactions if t['type'] == 'Expense')
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

    # Smart AI Insights
    insights = []
    if transactions:
        categories = {}
        for t in transactions:
            if t['type'] == 'Expense':
                cat = t['category']
                categories[cat] = categories.get(cat, 0) + float(t['amount'])

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
                insights.append(f"🔴 Danger! Saving only {saving_rate:.0f}%!-OVERSPENDING")

        expense_count = len([t for t in transactions if t['type'] == 'Expense'])
        insights.append(f"📊 Total {expense_count} expenses this month!")

        # Category wise advice
        if categories:
            for cat, amount in categories.items():
                cat_percentage = (amount / total_income) * 100 if total_income > 0 else 0
                if cat_percentage > 30:
                    insights.append(f"💡 Tip: Reduce {cat} spending — it's {cat_percentage:.0f}% of your income!")

        # Overall budget advice
        if percentage >= 80:
            insights.append("🚨 Critical: You have spent 80% of income — stop non-essential spending!")
        elif percentage >= 60:
            insights.append("⚠️ Warning: 60% budget used — avoid luxury expenses now!")
        elif percentage >= 40:
            insights.append("📌 Note: 40% budget used — keep tracking!")

    return render_template('index.html',
                         transactions=transactions,
                         total_income=total_income,
                         total_expense=total_expense,
                         savings=savings,
                         warning=warning,
                         percentage=round(percentage, 1),
                         insights=insights)

@app.route('/add', methods=['POST'])
def add():
    title = request.form['title']
    amount = request.form['amount']
    category = request.form['category']
    type = request.form['type']

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO transactions (title, amount, category, type) VALUES (%s, %s, %s, %s)",
                   (title, amount, category, type))
    db.commit()
    db.close()

    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = %s", (id,))
    db.commit()
    db.close()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)