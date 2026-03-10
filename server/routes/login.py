import flask as fl
from monkey import col, login_required

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
    
    if not username or not password:
        return fl.jsonify({"message": "Missing username or password"}), 400
        
    if col.find_one({"username": username}):
        return fl.jsonify({"message": "username already exists"}), 400 
    
    # Users receive placeholder role 'user', the admin will be setting their actual roles later on.

    role = "user"
    
    col.insert_one({"username": username, "password": password, "role": role})
    return fl.jsonify({
        "message": f"registered successfully as {role}"
    }), 201


# Calls the supersecretkey into session.
@login_bp.route('/debug_session')
def debug_session():
    return fl.jsonify(dict(fl.session))

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if fl.request.method == 'GET':
        return fl.render_template("login.html", name="Login")
    
    data = fl.request.get_json(silent=True) or fl.request.form
    username = data.get("username")
    password = data.get("password")
    
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
    return fl.jsonify({"message": "Protected delete endpoint"}), 200


