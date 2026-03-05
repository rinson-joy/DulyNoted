import flask as fl
import pymongo as pm

client = pm.MongoClient("mongodb+srv://rinsonjoy530_:1212@fatty.we0zaf4.mongodb.net/")
db = client["juicy"]
col = db["userdata"]

app = fl.Flask(__name__, static_folder="beaut")
@app.route('/home')
def home():
    name = "Menu"
    return fl.render_template("home.html", name=name)

@app.route('/register', methods=['GET', 'POST'])
def add_user():
    if fl.request.method == 'GET':
        return fl.render_template("register.html", name="Register")
    data = fl.request.get_json(silent=True) or fl.request.form
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")
    if not username or not password or not role:
        return fl.jsonify({"message": "Missing username, password, or role"}), 400
    col.insert_one({"username": username, "password": password, "role": role})
    return fl.jsonify({
        "message": "User added successfully",
        "username": username, 
        "role": role
    }), 201

@app.route('/login', methods=['GET', 'POST'])
def login():
    if fl.request.method == 'GET':
        return fl.render_template("login.html", name="Login")
    data = fl.request.get_json(silent=True) or fl.request.form
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")
    if not username or not password or not role:
        return fl.jsonify({"message": "Missing username, password, or role"}), 400
    user = col.find_one({"username": username})
    if user and user.get("password") == password:
        if user.get("role") != role:
            return fl.jsonify({"message": "Invalid account"}), 401
        return fl.jsonify({
            "message": "Login successful",
            "username": user["username"],
            "role": user["role"]
        }), 200
    return fl.jsonify({"message": "Invalid credentials"}), 401

@app.route('/delete', methods=['GET', 'POST'])
def delete_user():
    if fl.request.method == 'GET':
        return fl.render_template("delete.html", name="Delete")
    data = fl.request.get_json(silent=True) or fl.request.form
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")
    if not username or not password or not role:
        return fl.jsonify({"message": "Missing username, password, or role"}), 400
    result = col.delete_one({"username": username, "password": password, "role": role})
    if result.deleted_count:
        return fl.jsonify({"message": "User deleted successfully"}), 200
    else:
        return fl.jsonify({"message": "No matching account found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
