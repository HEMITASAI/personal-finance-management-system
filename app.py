from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import date

app = Flask(__name__, static_folder="static", static_url_path="/static")


# =========================================================
# DATABASE
# =========================================================

from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# =========================================================
# HELPERS
# =========================================================

def get_current_month_summary(cursor):

    cursor.execute("""
        SELECT
            COALESCE(SUM(
                CASE
                    WHEN transaction_type = 'income'
                    THEN Amount
                    ELSE 0
                END
            ), 0) AS total_income,

            COALESCE(SUM(
                CASE
                    WHEN transaction_type = 'expense'
                    THEN Amount
                    ELSE 0
                END
            ), 0) AS total_expenses

        FROM Finance

        WHERE YEAR(Date) = YEAR(CURDATE())
        AND MONTH(Date) = MONTH(CURDATE())
    """)

    result = cursor.fetchone()

    total_income = float(result["total_income"] or 0)
    total_expenses = float(result["total_expenses"] or 0)

    balance = total_income - total_expenses

    return total_income, total_expenses, balance


def get_overall_summary(cursor):

    cursor.execute("""
        SELECT
            COALESCE(SUM(
                CASE
                    WHEN transaction_type = 'income'
                    THEN Amount
                    ELSE 0
                END
            ), 0) AS total_income,

            COALESCE(SUM(
                CASE
                    WHEN transaction_type = 'expense'
                    THEN Amount
                    ELSE 0
                END
            ), 0) AS total_expenses

        FROM Finance
    """)

    result = cursor.fetchone()

    total_income = float(result["total_income"] or 0)
    total_expenses = float(result["total_expenses"] or 0)

    balance = total_income - total_expenses

    return total_income, total_expenses, balance


def get_salary(cursor):

    cursor.execute("""
        SELECT
            Transaction_ID AS transaction_id,
            Date AS date,
            Category AS category,
            Amount AS amount,
            Payment_Method AS payment_method,
            Description AS description,
            transaction_type

        FROM Finance

        WHERE transaction_type = 'income'
        AND LOWER(Category) = 'salary'

        ORDER BY Date DESC, Transaction_ID DESC

        LIMIT 1
    """)

    return cursor.fetchone()


def get_all_transactions(cursor):

    cursor.execute("""
        SELECT
            Transaction_ID AS transaction_id,
            Date AS date,
            Category AS category,
            Amount AS amount,
            Payment_Method AS payment_method,
            Description AS description,
            transaction_type

        FROM Finance

        ORDER BY Date ASC, Transaction_ID ASC
    """)

    return cursor.fetchall()


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def dashboard():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # CURRENT MONTH TRANSACTIONS ONLY
    cursor.execute("""
        SELECT
            Transaction_ID AS transaction_id,
            Date AS date,
            Category AS category,
            Amount AS amount,
            Payment_Method AS payment_method,
            Description AS description,
            transaction_type

        FROM Finance

        WHERE YEAR(Date) = YEAR(CURDATE())
        AND MONTH(Date) = MONTH(CURDATE())

        ORDER BY Date ASC, Transaction_ID ASC
    """)

    transactions = cursor.fetchall()

    # CURRENT MONTH INCOME
    cursor.execute("""
        SELECT
            COALESCE(SUM(Amount), 0) AS total_income

        FROM Finance

        WHERE transaction_type = 'income'

        AND YEAR(Date) = YEAR(CURDATE())
        AND MONTH(Date) = MONTH(CURDATE())
    """)

    total_income = float(
        cursor.fetchone()["total_income"] or 0
    )

    # CURRENT MONTH EXPENSES
    cursor.execute("""
        SELECT
            COALESCE(SUM(Amount), 0) AS total_expenses

        FROM Finance

        WHERE transaction_type = 'expense'

        AND YEAR(Date) = YEAR(CURDATE())
        AND MONTH(Date) = MONTH(CURDATE())
    """)

    total_expenses = float(
        cursor.fetchone()["total_expenses"] or 0
    )

    # CURRENT MONTH BALANCE
    balance = total_income - total_expenses

    salary = get_salary(cursor)

    cursor.close()
    db.close()

    return render_template(
        "index.html",

        transactions=transactions,

        total_income=total_income,

        total_expenses=total_expenses,

        balance=balance,

        salary=salary,

        current_month=date.today().strftime("%B %Y")
    )


# =========================================================
# INCOME
# =========================================================

@app.route("/income")
def income():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            Transaction_ID AS transaction_id,
            Date AS date,
            Category AS category,
            Amount AS amount,
            Payment_Method AS payment_method,
            Description AS description,
            transaction_type

        FROM Finance

        WHERE transaction_type = 'income'

        ORDER BY Date DESC, Transaction_ID DESC
    """)

    transactions = cursor.fetchall()

    # Current month summary
    current_salary, current_expenses, current_balance = \
        get_current_month_summary(cursor)

    # All-time salary, expenses and balance
    cursor.execute("""
        SELECT COALESCE(SUM(Amount), 0)
        FROM Finance
        WHERE transaction_type = 'income'
    """)

    total_salary = cursor.fetchone()["COALESCE(SUM(Amount), 0)"]

    cursor.execute("""
        SELECT COALESCE(SUM(Amount), 0)
        FROM Finance
        WHERE transaction_type = 'expense'
    """)

    total_expenses_all = cursor.fetchone()["COALESCE(SUM(Amount), 0)"]

    total_balance = total_salary - total_expenses_all

    cursor.close()
    db.close()

    return render_template(
        "salary.html",
        transactions=transactions,

        # Current month
        total_income=current_salary,
        current_month_expenses=current_expenses,
        balance=current_balance,

        # Overall
        total_income_all=total_salary,
        total_expenses_all=total_expenses_all,
        total_balance=total_balance
    )
# =========================================================
# EXPENSES
# =========================================================

@app.route("/expenses")
def expenses():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            Transaction_ID AS transaction_id,
            Date AS date,
            Category AS category,
            Amount AS amount,
            Payment_Method AS payment_method,
            Description AS description,
            transaction_type

        FROM Finance

        WHERE transaction_type = 'expense'

        ORDER BY Date DESC, Transaction_ID DESC
    """)

    transactions = cursor.fetchall()

    total_income, total_expenses, balance = \
        get_current_month_summary(cursor)

    salary = get_salary(cursor)

    cursor.close()
    db.close()

    return render_template(
        "expenses.html",
        transactions=transactions,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        salary=salary
    )


# =========================================================
# ANALYTICS
# =========================================================

@app.route("/analytics")
def analytics():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # =========================
    # OVERALL TOTALS
    # =========================

    overall_income, overall_expenses, overall_balance = \
        get_overall_summary(cursor)


    # =========================
    # CURRENT MONTH TOTALS
    # =========================

    cursor.execute("""
        SELECT

            COALESCE(SUM(
                CASE
                    WHEN transaction_type = 'income'
                    THEN Amount
                    ELSE 0
                END
            ), 0) AS current_income,

            COALESCE(SUM(
                CASE
                    WHEN transaction_type = 'expense'
                    THEN Amount
                    ELSE 0
                END
            ), 0) AS current_expenses

        FROM Finance

        WHERE YEAR(Date) = YEAR(CURDATE())
        AND MONTH(Date) = MONTH(CURDATE())
    """)

    current_month = cursor.fetchone()

    current_income = float(
        current_month["current_income"] or 0
    )

    current_expenses = float(
        current_month["current_expenses"] or 0
    )

    current_balance = (
        current_income -
        current_expenses
    )


    # =========================
    # MONTHLY DATA
    # =========================

    cursor.execute("""
        SELECT

            DATE_FORMAT(
                MIN(Date),
                '%Y-%m'
            ) AS month_key,

            DATE_FORMAT(
                MIN(Date),
                '%M %Y'
            ) AS month_name,

            COALESCE(SUM(
                CASE
                    WHEN transaction_type = 'income'
                    THEN Amount
                    ELSE 0
                END
            ), 0) AS income,

            COALESCE(SUM(
                CASE
                    WHEN transaction_type = 'expense'
                    THEN Amount
                    ELSE 0
                END
            ), 0) AS expenses

        FROM Finance

        GROUP BY
            YEAR(Date),
            MONTH(Date)

        ORDER BY
            YEAR(Date),
            MONTH(Date)
    """)

    monthly_data = cursor.fetchall()


    for row in monthly_data:

        row["income"] = float(
            row["income"] or 0
        )

        row["expenses"] = float(
            row["expenses"] or 0
        )

        row["balance"] = (
            row["income"] -
            row["expenses"]
        )


    # =========================
    # YEARLY DATA
    # =========================

    cursor.execute("""
        SELECT

            YEAR(Date) AS year,

            COALESCE(SUM(
                CASE
                    WHEN transaction_type = 'income'
                    THEN Amount
                    ELSE 0
                END
            ), 0) AS income,

            COALESCE(SUM(
                CASE
                    WHEN transaction_type = 'expense'
                    THEN Amount
                    ELSE 0
                END
            ), 0) AS expenses

        FROM Finance

        GROUP BY YEAR(Date)

        ORDER BY YEAR(Date)
    """)

    yearly_data = cursor.fetchall()


    for row in yearly_data:

        row["year"] = int(
            row["year"]
        )

        row["income"] = float(
            row["income"] or 0
        )

        row["expenses"] = float(
            row["expenses"] or 0
        )

        row["balance"] = (
            row["income"] -
            row["expenses"]
        )


    # =========================
    # EXPENSE CATEGORIES
    # =========================

    cursor.execute("""
        SELECT

            Category AS category,

            SUM(Amount) AS total

        FROM Finance

        WHERE transaction_type = 'expense'

        GROUP BY Category

        ORDER BY total DESC
    """)

    category_expenses = cursor.fetchall()


    for row in category_expenses:

        row["total"] = float(
            row["total"] or 0
        )


    cursor.close()
    db.close()


    return render_template(
        "analytics.html",

        overall_income=overall_income,

        overall_expenses=overall_expenses,

        overall_balance=overall_balance,

        current_income=current_income,

        current_expenses=current_expenses,

        current_balance=current_balance,

        monthly_data=monthly_data,

        yearly_data=yearly_data,

        category_expenses=category_expenses
    )


# =========================================================
# SEARCH
# =========================================================

@app.route("/search")
def search():

    search_text = request.args.get(
        "search",
        ""
    ).strip()

    from_date = request.args.get(
        "from_date",
        ""
    )

    to_date = request.args.get(
        "to_date",
        ""
    )

    transaction_type = request.args.get(
        "transaction_type",
        "all"
    )

    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            Transaction_ID AS transaction_id,
            Date AS date,
            Category AS category,
            Amount AS amount,
            Payment_Method AS payment_method,
            Description AS description,
            transaction_type

        FROM Finance

        WHERE 1 = 1
    """

    params = []

    if search_text:

        query += """
            AND (
                Category LIKE %s
                OR Description LIKE %s
                OR Payment_Method LIKE %s
            )
        """

        value = f"%{search_text}%"

        params.extend([
            value,
            value,
            value
        ])

    if from_date:

        query += """
            AND Date >= %s
        """

        params.append(from_date)

    if to_date:

        query += """
            AND Date <= %s
        """

        params.append(to_date)

    if transaction_type in [
        "income",
        "expense"
    ]:

        query += """
            AND transaction_type = %s
        """

        params.append(transaction_type)

    query += """
        ORDER BY Date DESC, Transaction_ID DESC
    """

    cursor.execute(
        query,
        params
    )

    transactions = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "search.html",

        transactions=transactions,

        search_text=search_text,

        from_date=from_date,

        to_date=to_date,

        transaction_type=transaction_type
    )


# =========================================================
# ADD TRANSACTION
# =========================================================

@app.route(
    "/add_transaction",
    methods=["POST"]
)
def add_transaction():

    transaction_type = request.form.get(
        "transaction_type"
    )

    amount = request.form.get(
        "amount"
    )

    category = request.form.get(
        "category"
    )

    description = request.form.get(
        "description",
        ""
    )

    payment_method = request.form.get(
        "payment_method"
    )

    if not all([
        transaction_type,
        amount,
        category,
        payment_method
    ]):

        return redirect(
            request.referrer or
            url_for("dashboard")
        )

    transaction_date = date.today()

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO Finance
        (
            Date,
            Category,
            Amount,
            Payment_Method,
            Description,
            transaction_type
        )

        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """, (
        transaction_date,
        category,
        amount,
        payment_method,
        description,
        transaction_type
    ))

    db.commit()

    cursor.close()
    db.close()

    return redirect(
        request.referrer or
        url_for("dashboard")
    )


# =========================================================
# EDIT TRANSACTION
# =========================================================

@app.route(
    "/edit_transaction/<int:transaction_id>"
)
def edit_transaction(transaction_id):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            Transaction_ID AS transaction_id,
            Date AS date,
            Category AS category,
            Amount AS amount,
            Payment_Method AS payment_method,
            Description AS description,
            transaction_type

        FROM Finance

        WHERE Transaction_ID = %s
    """, (
        transaction_id,
    ))

    transaction = cursor.fetchone()

    cursor.close()
    db.close()

    if not transaction:

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "edit_transaction.html",
        transaction=transaction
    )


# =========================================================
# UPDATE TRANSACTION
# =========================================================

@app.route(
    "/update_transaction/<int:transaction_id>",
    methods=["POST"]
)
def update_transaction(transaction_id):

    transaction_type = request.form.get(
        "transaction_type"
    )

    amount = request.form.get(
        "amount"
    )

    category = request.form.get(
        "category"
    )

    description = request.form.get(
        "description",
        ""
    )

    payment_method = request.form.get(
        "payment_method"
    )

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE Finance

        SET
            Category = %s,
            Amount = %s,
            Payment_Method = %s,
            Description = %s,
            transaction_type = %s

        WHERE Transaction_ID = %s
    """, (
        category,
        amount,
        payment_method,
        description,
        transaction_type,
        transaction_id
    ))

    db.commit()

    cursor.close()
    db.close()

    return redirect(
        url_for("dashboard")
    )


# =========================================================
# DELETE
# =========================================================

@app.route(
    "/delete_transaction/<int:transaction_id>"
)
def delete_transaction(transaction_id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM Finance

        WHERE Transaction_ID = %s
    """, (
        transaction_id,
    ))

    db.commit()

    cursor.close()
    db.close()

    return redirect(
        request.referrer or
        url_for("dashboard")
    )


# =========================================================
# SETTINGS
# =========================================================

@app.route("/settings")
def settings():

    return render_template(
        "settings.html"
    )


# =========================================================
# PWA
# =========================================================

@app.route("/manifest.json")
def manifest():

    return app.send_static_file(
        "manifest.json"
    )


@app.route("/service-worker.js")
def service_worker():

    return app.send_static_file(
        "service-worker.js"
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )