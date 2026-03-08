import flask as fl
import pymongo as pm
from functools import wraps
import os
from bson.objectid import ObjectId

# Connect to MongoDB
key = os.getenv('banana')
client = pm.MongoClient(key)
db = client["juicy"]
col = db["userdata"]
notes_col = db["notes"] # New collection for notes

app = fl.Flask(__name__, static_folder="beaut")
app.secret_key = "super_secret_key_123"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in fl.session:
            return fl.redirect(fl.url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in fl.session or fl.session.get("role") != "master":
            return fl.jsonify({"message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/home')
def home():
    return fl.render_template("home.html", name="Menu")

@app.route('/register', methods=['GET', 'POST'])
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
    
    # Check if this is the first user
    user_count = col.count_documents({})
    role = "master" if user_count == 0 else "user"
    
    col.insert_one({"username": username, "password": password, "role": role})
    return fl.jsonify({
        "message": f"registered successfully as {role}"
    }), 201

@app.route('/debug_session')
def debug_session():
    return fl.jsonify(dict(fl.session))

@app.route('/login', methods=['GET', 'POST'])
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
        # MANDATE: Store the role from DB into session
        fl.session["role"] = user.get("role", "user") 
        return fl.jsonify({
            "message": "Login successful",
            "username": user["username"],
            "role": fl.session["role"]
        }), 200
    
    return fl.jsonify({"message": "Invalid credentials"}), 401

@app.route('/admin')
@admin_required
def admin_panel():
    return fl.render_template("admin.html", name="Admin Panel")

@app.route('/admin/users')
@admin_required
def get_users():
    users = list(col.find({"role": {"$ne": "master"}}, {"_id": 0, "username": 1, "role": 1}))
    return fl.jsonify(users)

@app.route('/admin/assign_role', methods=['POST'])
@admin_required
def assign_role():
    # MANDATE: Only admin will be able to assign roles to a user
    data = fl.request.get_json(silent=True) or fl.request.form
    target_user = data.get("username")
    new_role = data.get("role")

    if not target_user or not new_role:
        return fl.jsonify({"message": "Missing target username or role"}), 400

    result = col.update_one({"username": target_user}, {"$set": {"role": new_role}})
    if result.matched_count:
        return fl.jsonify({"message": f"Role for {target_user} updated to {new_role}"}), 200
    return fl.jsonify({"message": "User not found"}), 404

@app.route('/logout')
def logout():
    fl.session.clear()
    return fl.redirect(fl.url_for("login"))

@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete_user():
    # ... logic for deletion ...
    if fl.request.method == 'GET':
        return fl.render_template("delete.html", name="Delete")
    return fl.jsonify({"message": "Protected delete endpoint"}), 200

@app.route('/notes')
@login_required
def notes():
    return fl.render_template("notes.html", name="notes")

@app.route('/api/notes', methods=['GET'])
@login_required
def get_notes():
    user_notes = list(notes_col.find({"owner": fl.session["user"]}))
    for note in user_notes:
        note["_id"] = str(note["_id"])
    return fl.jsonify(user_notes)

@app.route('/api/notes', methods=['POST'])
@login_required
def add_note():
    data = fl.request.get_json(silent=True)
    content = data.get("content")
    if not content:
        return fl.jsonify({"message": "Note content is required"}), 400
    
    note_id = notes_col.insert_one({
        "owner": fl.session["user"],
        "content": content
    }).inserted_id
    
    return fl.jsonify({"message": "Note added", "id": str(note_id)}), 201

@app.route('/api/notes/<note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    try:
        result = notes_col.delete_one({"_id": ObjectId(note_id), "owner": fl.session["user"]})
        if result.deleted_count:
            return fl.jsonify({"message": "Note deleted"}), 200
        return fl.jsonify({"message": "Note not found"}), 404
    except:
        return fl.jsonify({"message": "Invalid note ID"}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
