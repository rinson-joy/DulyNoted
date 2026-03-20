import flask as fl
from monkey import login_required

# Define the blueprint
dulytold_bp = fl.Blueprint("dulytold_bp", __name__)

@dulytold_bp.route('/dulytold')
def dulytold_home():
    return fl.render_template("dulytold.html", name="DulyTold", side="dulytold")

@dulytold_bp.route('/diary')
@login_required
def diary_page():
    return fl.render_template('notes.html', name='Diary', side="dulytold")

@dulytold_bp.route('/dulytold/settings')
@login_required
def diary_settings():
    return fl.render_template("settings.html", name="Diary Settings", side="dulytold")
