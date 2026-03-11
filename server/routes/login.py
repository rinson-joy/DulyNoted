import flask as fl
from monkey import col, login_required, notes_col

# Define the blueprint
login_bp = fl.Blueprint("login_bp", __name__)

@login_bp.route('/')
@login_bp.route('/home')
def home():
    return fl.render_template("home.html", name="Menu")

@login_bp.route('/register', methods=['GET', 'POST'])
def add_user():
    if fl.request.method == 'GET':
        return fl.render_template("register.html", name="Register")
    
    data = fl.request.get_json(silent=True) or fl.request.form
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    
    if not username or not password or not email:
        return fl.jsonify({"message": "Missing username, email, or password"}), 400
        
    if col.find_one({"username": username}):
        return fl.jsonify({"message": "username already exists"}), 400 
    
    # Users receive placeholder role 'user', the admin will be setting their actual roles later on.

    role = "user"
    
    col.insert_one({"username": username, "password": password, "role": role, "email": email})
    return fl.jsonify({
        "message": f"registered successfully as {role}"
    }), 201


# Calls the supersecretkey into session.
@login_bp.route('/debug_session')
def debug_session():
    return fl.jsonify(dict(fl.session))

# Log in.
@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if fl.request.method == 'GET':
        return fl.render_template("login.html", name="Login")
    
    data = fl.request.get_json(silent=True) or fl.request.form
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    
    if not username or not password:
        return fl.jsonify({"message": "Missing fields"}), 400
        
    user = col.find_one({"username": username, "password": password})
    if user:
        fl.session.clear()
        fl.session["user"] = user["username"]
        # Stores the role from DB into session.
        fl.session["role"] = user.get("role", "user")
        return fl.jsonify({
            "message": "Login successful",
            "username": user["username"],
            "role": fl.session["role"]
        }), 200
    
    return fl.jsonify({"message": "Invalid credentials"}), 401


@login_bp.route('/logout')
def logout():
    fl.session.clear()
    return fl.redirect(fl.url_for("login_bp.login"))

@login_bp.route('/delete', methods=['GET', 'POST'])
@login_required
def delete_user():
    if fl.request.method == 'GET':
        return fl.render_template("delete.html", name="Delete")
    
    data = fl.request.get_json(silent=True) or fl.request.form
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")

    if not username or not password:
        return fl.jsonify({"message": "Missing username or password"}), 400

    # Only allow deleting your own account unless master.
    if fl.session.get("user") != username and fl.session.get("role") != "master":
        return fl.jsonify({"message": "Not allowed to delete this user"}), 403

    query = {"username": username, "password": password}
    if role:
        query["role"] = role

    user = col.find_one(query)
    if not user:
        return fl.jsonify({"message": "Invalid credentials"}), 401

    if user.get("role") == "master" and fl.session.get("role") != "master":
        return fl.jsonify({"message": "Cannot delete master account"}), 403

    result = col.delete_one({"username": username})
    if result.deleted_count:
        notes_col.delete_many({"owner": username})
        if fl.session.get("user") == username:
            fl.session.clear()
        return fl.jsonify({"message": "User deleted"}), 200

    return fl.jsonify({"message": "User not found"}), 404

