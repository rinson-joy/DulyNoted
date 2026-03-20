import flask as fl
from bson.objectid import ObjectId
from monkey import login_required, notes_col
from datetime import datetime

# Define the blueprint
notes_bp = fl.Blueprint('notes_bp', __name__)
@notes_bp.route('/notes')
@login_required
def notes_page():
    return fl.render_template('notes.html', name='Notes', side="dulynoted")

@notes_bp.route('/api/notes/export', methods=['GET'])
@login_required
def export_notes():
    user = fl.session.get("user")
    export_format = fl.request.args.get("format", "json")
    notes = list(notes_col.find({"owner": user}, {"_id": 0}))

    if export_format == "txt":
        # Concatenate all notes into a single text file
        output = []
        for note in notes:
            title = note.get("title", "Untitled")
            content = note.get("content", "")
            output.append(f"{title}\n{'=' * len(title)}\n\n{content}\n\n{'-' * 40}\n\n")
        
        txt_content = "".join(output)
        response = fl.Response(txt_content, mimetype='text/plain')
        response.headers.set('Content-Disposition', 'attachment', filename=f'dulynoted_export_{user}.txt')
        return response
    
    # Default to JSON response that prompts a download
    response = fl.jsonify(notes)
    response.headers.set('Content-Disposition', 'attachment', filename=f'dulynoted_export_{user}.json')
    return response

@notes_bp.route('/api/notes/import', methods=['POST'])
@login_required
def import_notes():
    user = fl.session.get("user")
    if 'file' not in fl.request.files:
        return fl.jsonify({"message": "No file part"}), 400

    file = fl.request.files['file']
    if file.filename == '':
        return fl.jsonify({"message": "No selected file"}), 400

    import_format = fl.request.form.get('format', 'json')

    try:
        if import_format == 'txt':
            content = file.read().decode('utf-8', errors='ignore')
            title = file.filename.rsplit('.', 1)[0] or "Imported Note"
            
            now = datetime.utcnow().isoformat()
            notes_col.insert_one({
                "owner": user,
                "title": title,
                "content": content,
                "created_at": now,
                "modified_at": now
            })
            return fl.jsonify({"message": "Successfully imported note from text file."}), 200

        import json
        data = json.load(file)
        if not isinstance(data, list):
            return fl.jsonify({"message": "Invalid file format. Expected a list of notes."}), 400

        imported_count = 0
        now = datetime.utcnow().isoformat()
        for item in data:
            if 'content' in item:
                note = {
                    "owner": user,
                    "title": item.get("title", "Imported Note"),
                    "content": item["content"],
                    "created_at": item.get("created_at", now),
                    "modified_at": item.get("modified_at", now),
                }
                notes_col.insert_one(note)
                imported_count += 1

        return fl.jsonify({"message": f"Successfully imported {imported_count} notes."}), 200
    except Exception as e:
        return fl.jsonify({"message": f"Error during import: {str(e)}"}), 500


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
    events = data.get("events") # Added for unified recordings
    if not content:
        return fl.jsonify({"message": "Note content is required"}), 400
    if not title:
        untitled_count = notes_col.count_documents({
            "owner": fl.session["user"],
            "$or": [{"title": {"$exists": False}}, {"title": ""}]
        })
        title = f"my notes {untitled_count + 1}"
    
    now = datetime.utcnow().isoformat()
    note_data = {
        "owner": fl.session["user"],
        "title": title,
        "content": content,
        "created_at": now,
        "modified_at": now
    }
    if events:
        note_data["events"] = events
        
    note_id = notes_col.insert_one(note_data).inserted_id
    
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

@notes_bp.route('/api/notes/clear', methods=['POST'])
@login_required
def clear_notes():
    try:
        result = notes_col.delete_many({"owner": fl.session["user"]})
        return fl.jsonify({"message": f"Successfully deleted {result.deleted_count} notes"}), 200
    except Exception as e:
        return fl.jsonify({"message": "Failed to clear notes"}), 500

@notes_bp.route('/api/notes/<note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    data = fl.request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    content = data.get("content")
    events = data.get("events") # Added for unified recordings
    if not content:
        return fl.jsonify({"message": "Note content is required"}), 400
    try:
        update_fields = {
            "content": content,
            "modified_at": datetime.utcnow().isoformat()
        }
        if title:
            update_fields["title"] = title[:80]
        if events:
            update_fields["events"] = events
            
        result = notes_col.update_one(
            {"_id": ObjectId(note_id), "owner": fl.session["user"]},
            {"$set": update_fields},
        )
        if result.matched_count:
            return fl.jsonify({"message": "Note updated"}), 200
        return fl.jsonify({"message": "Note not found"}), 404
    except:
        return fl.jsonify({"message": "Invalid note ID"}), 400
