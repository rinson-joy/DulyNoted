import flask as fl
import pymongo as pm
from functools import wraps
import os

# Connect to MongoDB.
key = os.getenv("banana")
client = pm.MongoClient(key)
db = client["juicy"]
col = db["userdata"]
notes_col = db["notes"]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in fl.session:
            return fl.redirect(fl.url_for("login_bp.login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in fl.session or fl.session.get("role") != "master":
            return fl.jsonify({"message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function
