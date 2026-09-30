from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import sqlite3
from datetime import date
from services.ai_analysis import analyze_expenses

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DATABASE = "expenses.db"

CATEGORIES = [
    "Food", "Travel", "Shopping", "Education",
    "Bills", "Entertainment", "Health", "Other"
]


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL CHECK(amount > 0),
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            expense_date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def get_dashboard_data(month=None):
    month = month or date.today().strftime("%Y-%m")
    conn = get_db()

    rows = conn.execute("""
        SELECT * FROM expenses
        WHERE substr(expense_date, 1, 7) = ?
        ORDER BY expense_date DESC, id DESC
    """, (month,)).fetchall()

    total = sum(row["amount"] for row in rows)
    highest = max((row["amount"] for row in rows), default=0)
    count = len(rows)

    category_rows = conn.execute("""
        SELECT category, SUM(amount) AS total
        FROM expenses
        WHERE substr(expense_date, 1, 7) = ?
        GROUP BY category
        ORDER BY total DESC
    """, (month,)).fetchall()

    top_category = category_rows[0]["category"] if category_rows else "—"

    conn.close()

    return {
        "month": month,
        "expenses": rows,
        "total": total,
        "highest": highest,
        "count": count,
        "top_category": top_category,
        "category_data": [
            {"category": row["category"], "total": round(row["total"], 2)}
            for row in category_rows
        ]
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    data = get_dashboard_data(month)
    return render_template(
        "dashboard.html",
        **data,
        categories=CATEGORIES
    )


@app.route("/expenses")
def expenses():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    month = request.args.get("month", "").strip()

    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    if search:
        query += " AND (description LIKE ? OR category LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if category:
        query += " AND category = ?"
        params.append(category)

    if month:
        query += " AND substr(expense_date, 1, 7) = ?"
        params.append(month)

    query += " ORDER BY expense_date DESC, id DESC"

    conn = get_db()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        "expenses.html",
        expenses=rows,
        categories=CATEGORIES,
        search=search,
        selected_category=category,
        selected_month=month
    )


@app.route("/expense/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        amount = request.form.get("amount", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        expense_date = request.form.get("expense_date", "").strip()

        try:
            amount_value = float(amount)
        except ValueError:
            amount_value = 0

        if amount_value <= 0 or not category or not description or not expense_date:
            flash("Please enter valid details for every field.", "error")
            return render_template(
                "expense_form.html",
                categories=CATEGORIES,
                expense=None,
                page_title="Add Expense",
                submit_label="Save Expense"
            )

        conn = get_db()
        conn.execute("""
            INSERT INTO expenses (amount, category, description, expense_date)
            VALUES (?, ?, ?, ?)
        """, (amount_value, category, description, expense_date))
        conn.commit()
        conn.close()

        flash("Expense added successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template(
        "expense_form.html",
        categories=CATEGORIES,
        expense=None,
        page_title="Add Expense",
        submit_label="Save Expense"
    )


@app.route("/expense/<int:expense_id>/edit", methods=["GET", "POST"])
def edit_expense(expense_id):
    conn = get_db()
    expense = conn.execute(
        "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()

    if not expense:
        conn.close()
        flash("Expense not found.", "error")
        return redirect(url_for("expenses"))

    if request.method == "POST":
        amount = request.form.get("amount", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        expense_date = request.form.get("expense_date", "").strip()

        try:
            amount_value = float(amount)
        except ValueError:
            amount_value = 0

        if amount_value <= 0 or not category or not description or not expense_date:
            conn.close()
            flash("Please enter valid details for every field.", "error")
            return render_template(
                "expense_form.html",
                categories=CATEGORIES,
                expense=expense,
                page_title="Edit Expense",
                submit_label="Update Expense"
            )

        conn.execute("""
            UPDATE expenses
            SET amount = ?, category = ?, description = ?, expense_date = ?
            WHERE id = ?
        """, (amount_value, category, description, expense_date, expense_id))
        conn.commit()
        conn.close()

        flash("Expense updated successfully.", "success")
        return redirect(url_for("expenses"))

    conn.close()
    return render_template(
        "expense_form.html",
        categories=CATEGORIES,
        expense=expense,
        page_title="Edit Expense",
        submit_label="Update Expense"
    )


@app.post("/expense/<int:expense_id>/delete")
def delete_expense(expense_id):
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    flash("Expense deleted.", "success")
    return redirect(request.referrer or url_for("expenses"))


@app.route("/analysis")
def analysis():
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM expenses
        WHERE substr(expense_date, 1, 7) = ?
        ORDER BY expense_date DESC, id DESC
    """, (month,)).fetchall()
    conn.close()

    result = analyze_expenses([dict(row) for row in rows], month)
    return render_template("analysis.html", analysis=result, month=month)


@app.get("/api/chart-data")
def chart_data():
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    data = get_dashboard_data(month)
    return jsonify({
        "month": month,
        "categories": [item["category"] for item in data["category_data"]],
        "values": [item["total"] for item in data["category_data"]]
    })


@app.get("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
