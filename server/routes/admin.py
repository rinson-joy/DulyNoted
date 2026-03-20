import flask as fl
from monkey import admin_required, col

# Define the blueprint
admin_bp = fl.Blueprint("admin_bp", __name__)

@admin_bp.route('/admin')
@admin_required
def admin_page():
    return fl.render_template('admin.html', name='Admin', side="dulynoted")


@admin_bp.route('/admin/users')
@admin_required
def get_users():
    # Only fetch users who are not masters, and only their usernames.
    users = list(col.find({"role": {"$ne": "master"}}, {"_id": 0, "username": 1}))
    return fl.jsonify(users)
