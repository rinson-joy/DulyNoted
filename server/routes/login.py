import flask as fl
from monkey import col, login_required, notes_col

# Define the blueprint
login_bp = fl.Blueprint("login_bp", __name__)

@login_bp.route('/')
@login_bp.route('/home')
def home():
    return fl.render_template("home.html", name="Menu", side="dulynoted")

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
    
    
    col.insert_one({
        "username": username,
        "password": password,
        "email": email,
        "allow_incoming_shares": True,
        "allow_share_notifications": True,
        "show_line_numbers": True,
    })
    return fl.jsonify({
        "message": f"registered successfully as {username}"
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
    
    if not username or not password:
        return fl.jsonify({"message": "Missing fields"}), 400
        
    user = col.find_one({"username": username, "password": password})
    if user and user["password"] == password and user["username"] == username:
        fl.session.clear()
        fl.session["user"] = user["username"]
        # Only "master" role is relevant now.
        role = user.get("role")
        if role == "master":
            fl.session["role"] = "master"
        
        return fl.jsonify({
            "message": "login successful",
            "username": user["username"],
            "role": fl.session.get("role")
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

    if not username or not password:
        return fl.jsonify({"message": "Missing username or password"}), 400

    # Only allow deleting your own account unless master.
    if fl.session.get("user") != username and fl.session.get("role") != "master":
        return fl.jsonify({"message": "Not allowed to delete this user"}), 403

    query = {"username": username, "password": password}
    user = col.find_one(query)
    if not user:
        return fl.jsonify({"message": "Invalid credentials"}), 401

    if user.get("role") == "master" and fl.session.get("role") != "master":
        return fl.jsonify({"message": "Cannot delete master account"}), 403

    result = col.delete_one({"username": username})
    if result.deleted_count:
        notes_col.delete_many({"owner": username})
        from monkey import diary_col
        diary_col.delete_many({"owner": username})
        if fl.session.get("user") == username:
            fl.session.clear()
        return fl.jsonify({"message": "User deleted"}), 200

    return fl.jsonify({"message": "User not found"}), 404

@login_bp.route('/settings')
@login_required
def settings():
    return fl.render_template("settings.html", name="Settings", side="dulynoted")

@login_bp.route('/api/settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    from monkey import notes_col, share_col
    data = fl.request.get_json(silent=True) or {}
    updates = {}
    old_username = fl.session.get("user")
    
    # Update username
    if "username" in data:
        new_username = data.get("username", "").strip()
        if new_username and new_username != old_username:
            if col.find_one({"username": new_username}):
                return fl.jsonify({"message": "Username already exists"}), 400
            
            col.update_one({"username": old_username}, {"$set": {"username": new_username}})
            notes_col.update_many({"owner": old_username}, {"$set": {"owner": new_username}})
            notes_col.update_many({"shared_from": old_username}, {"$set": {"shared_from": new_username}})
            share_col.update_many({"owner": old_username}, {"$set": {"owner": new_username}})
            share_col.update_many({"recipient": old_username}, {"$set": {"recipient": new_username}})
            
            fl.session["user"] = new_username
            updates["username"] = new_username

    # Update email
    if "email" in data:
        updates["email"] = data.get("email", "").strip()

    # Update password
    if "password" in data:
        password = data.get("password", "").strip()
        if password:
            updates["password"] = password

    if "allow_incoming_shares" in data:
        updates["allow_incoming_shares"] = bool(data.get("allow_incoming_shares"))
    if "allow_share_notifications" in data:
        updates["allow_share_notifications"] = bool(data.get("allow_share_notifications"))
    
    # UI & Workflow Settings
    if "editor_font_size" in data:
        updates["editor_font_size"] = data.get("editor_font_size", "medium")
    if "show_line_numbers" in data:
        updates["show_line_numbers"] = bool(data.get("show_line_numbers"))
    if "default_note_title" in data:
        updates["default_note_title"] = data.get("default_note_title", "untitled").strip()
    if "sort_order" in data:
        updates["sort_order"] = data.get("sort_order", "modified")
    if "theme" in data:
        updates["theme"] = data.get("theme", "light")
    
    if updates:
        col.update_one(
            {"username": fl.session.get("user")},
            {"$set": {k: v for k, v in updates.items() if k != "message"}},
        )
    
    if fl.request.method == 'GET':
        user = col.find_one(
            {"username": fl.session.get("user")},
            {"_id": 0, "username": 1, "email": 1, "allow_incoming_shares": 1, "allow_share_notifications": 1,
             "editor_font_size": 1, "show_line_numbers": 1, "default_note_title": 1, "sort_order": 1, "theme": 1},
        )
        return fl.jsonify({
            "username": user.get("username", ""),
            "email": user.get("email", ""),
            "allow_incoming_shares": user.get("allow_incoming_shares", True),
            "allow_share_notifications": user.get("allow_share_notifications", True),
            "editor_font_size": user.get("editor_font_size", "medium"),
            "show_line_numbers": user.get("show_line_numbers", True),
            "default_note_title": user.get("default_note_title", "untitled"),
            "sort_order": user.get("sort_order", "modified"),
            "theme": user.get("theme", "light"),
        }), 200

    updates["message"] = "Settings updated"
    return fl.jsonify(updates), 200

