import flask as fl
from bson.objectid import ObjectId
from monkey import login_required, notes_col

# Define the blueprint
notes_bp = fl.Blueprint('notes_bp', __name__)
@notes_bp.route('/notes')
@login_required
def notes():
    return fl.render_template("notes.html", name="notes")

@notes_bp.route('/api/notes', methods=['GET'])
@login_required
def get_notes():
    user_notes = list(notes_col.find({"owner": fl.session["user"]}))
    for note in user_notes:
        note["_id"] = str(note["_id"])
    return fl.jsonify(user_notes)

@notes_bp.route('/api/notes', methods=['POST'])
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

@notes_bp.route('/api/notes/<note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    try:
        result = notes_col.delete_one({"_id": ObjectId(note_id), "owner": fl.session["user"]})
        if result.deleted_count:
            return fl.jsonify({"message": "Note deleted"}), 200
        return fl.jsonify({"message": "Note not found"}), 404
    except:
        return fl.jsonify({"message": "Invalid note ID"}), 400

@notes_bp.route('/api/notes/<note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    data = fl.request.get_json(silent=True) or {}
    content = data.get("content")
    if not content:
        return fl.jsonify({"message": "Note content is required"}), 400
    try:
        result = notes_col.update_one(
            {"_id": ObjectId(note_id), "owner": fl.session["user"]},
            {"$set": {"content": content}},
        )
        if result.matched_count:
            return fl.jsonify({"message": "Note updated"}), 200
        return fl.jsonify({"message": "Note not found"}), 404
    except:
        return fl.jsonify({"message": "Invalid note ID"}), 400
