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
    untitled_index = 1
    for note in user_notes:
        if not note.get("title"):
            note["title"] = f"my notes {untitled_index}"
            untitled_index += 1
        note["_id"] = str(note["_id"])
    return fl.jsonify(user_notes)

@notes_bp.route('/api/notes', methods=['POST'])
@login_required
def add_note():
    data = fl.request.get_json(silent=True)
    title = (data.get("title") or "").strip()
    content = data.get("content")
    if not content:
        return fl.jsonify({"message": "Note content is required"}), 400
    if not title:
        untitled_count = notes_col.count_documents({
            "owner": fl.session["user"],
            "$or": [{"title": {"$exists": False}}, {"title": ""}]
        })
        title = f"my notes {untitled_count + 1}"
    
    note_id = notes_col.insert_one({
        "owner": fl.session["user"],
        "title": title,
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
    title = (data.get("title") or "").strip()
    content = data.get("content")
    if not content:
        return fl.jsonify({"message": "Note content is required"}), 400
    try:
        update_fields = {"content": content}
        if title:
            update_fields["title"] = title[:80]
        result = notes_col.update_one(
            {"_id": ObjectId(note_id), "owner": fl.session["user"]},
            {"$set": update_fields},
        )
        if result.matched_count:
            return fl.jsonify({"message": "Note updated"}), 200
        return fl.jsonify({"message": "Note not found"}), 404
    except:
        return fl.jsonify({"message": "Invalid note ID"}), 400
