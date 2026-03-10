import flask as fl
from monkey import admin_required, col

# Define the blueprint
admin_bp = fl.Blueprint("admin_bp", __name__)

@admin_bp.route('/admin')
@admin_required
def admin_panel():
    return fl.render_template("admin.html", name="Admin Panel")

@admin_bp.route('/admin/users')
@admin_required
def get_users():
    users = list(col.find({"role": {"$ne": "master"}}, {"_id": 0, "username": 1, "role": 1}))
    return fl.jsonify(users)

@admin_bp.route('/admin/assign_role', methods=['POST'])
@admin_required
def assign_role():
    # Only admin will be able to assign roles to a user
    data = fl.request.get_json(silent=True) or fl.request.form
    target_user = data.get("username")
    new_role = data.get("role")

    if not target_user or not new_role:
        return fl.jsonify({"message": "Missing target username or role"}), 400

    result = col.update_one({"username": target_user}, {"$set": {"role": new_role}})
    if result.matched_count:
        return fl.jsonify({"message": f"Role for {target_user} updated to {new_role}"}), 200
    return fl.jsonify({"message": "User not found"}), 404
