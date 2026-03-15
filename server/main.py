import flask as fl
import os


# This calls the files - templates/ and beaut/ cause its outside server/ .
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app = fl.Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "beaut"),
    template_folder=os.path.join(BASE_DIR, "templates"),
)

app.secret_key = "super_secret_key_123"

from routes.login import login_bp
from routes.notes import notes_bp
from routes.admin import admin_bp
from routes.share import share_bp

app.register_blueprint(login_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(share_bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
