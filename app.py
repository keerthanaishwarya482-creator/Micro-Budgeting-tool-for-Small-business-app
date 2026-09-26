from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ishu246@#",
        database="micro_budgeting_db"
    )


# =========================
# DASHBOARD
# =========================

@app.route("/")
def dashboard():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            COALESCE(SUM(
                CASE
                    WHEN transaction_type = 'Income'
                    THEN amount
                    ELSE 0
                END
            ), 0) AS income,

            COALESCE(SUM(
                CASE
                    WHEN transaction_type = 'Expense'
                    THEN amount
                    ELSE 0
                END
            ), 0) AS expense

        FROM transactions
    """)

    totals = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM transactions
        ORDER BY transaction_date DESC, transaction_id DESC
        LIMIT 5
    """)

    transactions = cursor.fetchall()

    cursor.close()
    db.close()

    balance = totals["income"] - totals["expense"]

    return render_template(
        "index.html",
        income=totals["income"],
        expense=totals["expense"],
        balance=balance,
        transactions=transactions
    )


# =========================
# ADD TRANSACTION
# =========================

@app.route("/add", methods=["GET", "POST"])
def add_transaction():

    if request.method == "POST":

        transaction_type = request.form["transaction_type"]
        amount = request.form["amount"]
        category = request.form["category"]
        transaction_date = request.form["transaction_date"]
        description = request.form["description"]

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO transactions
            (
                transaction_type,
                amount,
                category,
                transaction_date,
                description
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            transaction_type,
            amount,
            category,
            transaction_date,
            description
        ))

        db.commit()

        cursor.close()
        db.close()

        return redirect("/")

    return render_template("add.html")


# =========================
# VIEW ALL TRANSACTIONS
# =========================

@app.route("/transactions")
def transactions():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM transactions
        ORDER BY transaction_date DESC, transaction_id DESC
    """)

    data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "transactions.html",
        transactions=data,
        keyword=""
    )


# =========================
# SEARCH TRANSACTIONS
# =========================

@app.route("/search")
def search_transactions():

    keyword = request.args.get("keyword", "")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM transactions
        WHERE
            category LIKE %s
            OR description LIKE %s
            OR transaction_type LIKE %s
        ORDER BY transaction_date DESC, transaction_id DESC
    """, (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "transactions.html",
        transactions=data,
        keyword=keyword
    )


# =========================
# DELETE TRANSACTION
# =========================

@app.route("/delete/<int:transaction_id>")
def delete_transaction(transaction_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM transactions
        WHERE transaction_id = %s
    """, (transaction_id,))

    db.commit()

    cursor.close()
    db.close()

    return redirect("/transactions")


# =========================
# EDIT TRANSACTION
# =========================

@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
def edit_transaction(transaction_id):

    db = get_db_connection()

    if request.method == "POST":

        transaction_type = request.form["transaction_type"]
        amount = request.form["amount"]
        category = request.form["category"]
        transaction_date = request.form["transaction_date"]
        description = request.form["description"]

        cursor = db.cursor()

        cursor.execute("""
            UPDATE transactions
            SET
                transaction_type = %s,
                amount = %s,
                category = %s,
                transaction_date = %s,
                description = %s
            WHERE transaction_id = %s
        """, (
            transaction_type,
            amount,
            category,
            transaction_date,
            description,
            transaction_id
        ))

        db.commit()

        cursor.close()
        db.close()

        return redirect("/transactions")

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM transactions
        WHERE transaction_id = %s
    """, (transaction_id,))

    transaction = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template(
        "edit.html",
        transaction=transaction
    )


# =========================
# START APPLICATION
# =========================

if __name__ == "__main__":
    app.run(debug=True)