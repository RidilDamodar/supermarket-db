from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ridil006",
        database="supermarket"
    )

# LOGIN
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["user"] = "admin"
            return redirect("/dashboard")
        else:
            return "Invalid Login"

    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # JOIN QUERY 🔥
    cursor.execute("""
    SELECT p.id, p.name, c.name AS category, p.quantity, p.price
    FROM products p
    JOIN categories c ON p.category_id = c.id
    """)
    items = cursor.fetchall()

    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()

    total_qty = sum(i["quantity"] for i in items)
    total_value = sum(i["quantity"] * i["price"] for i in items)

    conn.close()

    return render_template("dashboard.html",
                           items=items,
                           categories=categories,
                           total_qty=total_qty,
                           total_value=total_value)

# ADD PRODUCT
@app.route("/add", methods=["POST"])
def add():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO products(name, category_id, quantity, price)
    VALUES (%s,%s,%s,%s)
    """,(request.form["name"],
         request.form["category"],
         request.form["quantity"],
         request.form["price"]))

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# DELETE
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id=%s",(id,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# UPDATE
@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE products 
    SET name=%s, category_id=%s, quantity=%s, price=%s
    WHERE id=%s
    """,(request.form["name"],
         request.form["category"],
         request.form["quantity"],
         request.form["price"],
         id))

    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)