from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# --- Rule-based Natural Language → SQL ---
def nl_to_sql(nl_query):
    q = nl_query.lower()

    if "total revenue" in q and "year" in q:
        # extract year number
        words = q.split()
        year = None
        for w in words:
            if w.isdigit() and len(w) == 4:
                year = w
        if year:
            return f"SELECT SUM(revenue) as total_revenue FROM revenue WHERE year={year};"

    if "total revenue" in q:
        return "SELECT SUM(revenue) as total_revenue FROM revenue;"

    if "average revenue by year" in q or "avg revenue by year" in q:
        return "SELECT year, AVG(revenue) as avg_revenue FROM revenue GROUP BY year;"

    if "all records" in q or "show all" in q:
        return "SELECT * FROM revenue;"

    if "highest revenue" in q:
        return "SELECT * FROM revenue ORDER BY revenue DESC LIMIT 1;"

    if "lowest revenue" in q:
        return "SELECT * FROM revenue ORDER BY revenue ASC LIMIT 1;"

    # fallback
    return "SELECT * FROM revenue LIMIT 5;"

# --- Run SQL Query ---
def run_sql(sql_query):
    conn = sqlite3.connect("revenue.db")
    cursor = conn.cursor()
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    return {"columns": columns, "rows": rows}

# --- Convert Results → Natural Language ---
def results_to_nl(user_query, results):
    if not results["rows"]:
        return "No results found."

    if "total_revenue" in results["columns"]:
        return f"The {user_query} is {results['rows'][0][0]}."

    if "avg_revenue" in results["columns"]:
        text = "The average revenue by year:\n"
        for row in results["rows"]:
            text += f"Year {row[0]}: {row[1]}\n"
        return text

    if "year" in results["columns"] and "revenue" in results["columns"]:
        return f"Here are the records:\n{results['rows']}"

    return f"Query results: {results['rows']}"
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running! Use POST /query with JSON body."})
# --- API Endpoint ---
@app.route("/query", methods=["POST"])
def query():
    user_query = request.json.get("query")

    sql_query = nl_to_sql(user_query)
    results = run_sql(sql_query)
    answer = results_to_nl(user_query, results)

    return jsonify({
        "user_query": user_query,
        "sql_query": sql_query,
        "results": results,
        "answer": answer
    })

if __name__ == "__main__":
    app.run(debug=True)
