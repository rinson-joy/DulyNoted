import flask as fl
from bson.objectid import ObjectId
from datetime import datetime
from monkey import login_required, notes_col, share_col, col

# Define the blueprint
share_bp = fl.Blueprint('share_bp', __name__)

@share_bp.route('/api/notes/share', methods=['POST'])
@login_required
def share_note():
    data = fl.request.get_json(silent=True) or {}
    note_id = data.get("note_id")
    recipient = data.get("recipient")
    if not note_id or not recipient:
        return fl.jsonify({"message": "Missing note_id or recipient"}), 400

    if recipient == fl.session["user"]:
        return fl.jsonify({"message": "Cannot share to yourself"}), 400

    if not col.find_one({"username": recipient}):
        return fl.jsonify({"message": "Recipient not found"}), 404

    try:
        note_obj_id = ObjectId(note_id)
    except:
        return fl.jsonify({"message": "Invalid note ID"}), 400

    note = notes_col.find_one({"_id": note_obj_id, "owner": fl.session["user"]})
    if not note:
        return fl.jsonify({"message": "Note not found"}), 404

    existing = share_col.find_one({
        "note_id": note_id,
        "owner": fl.session["user"],
        "recipient": recipient,
        "status": "pending",
    })
    if existing:
        return fl.jsonify({"message": "Share request already pending"}), 409

    request_id = share_col.insert_one({
        "note_id": note_id,
        "note_content": note.get("content", ""),
        "owner": fl.session["user"],
        "recipient": recipient,
        "status": "pending",
        "created_at": datetime.utcnow(),
    }).inserted_id

    return fl.jsonify({"message": "Share request sent", "id": str(request_id)}), 201

@share_bp.route('/api/notes/requests', methods=['GET'])
@login_required
def get_share_requests():
    requests = list(share_col.find({
        "recipient": fl.session["user"],
        "status": "pending",
    }))
    for req in requests:
        req["_id"] = str(req["_id"])
    return fl.jsonify(requests)

@share_bp.route('/api/notes/requests/<request_id>/accept', methods=['POST'])
@login_required
def accept_share_request(request_id):
    try:
        req_obj_id = ObjectId(request_id)
    except:
        return fl.jsonify({"message": "Invalid request ID"}), 400

    req = share_col.find_one({
        "_id": req_obj_id,
        "recipient": fl.session["user"],
        "status": "pending",
    })
    if not req:
        return fl.jsonify({"message": "Share request not found"}), 404

    try:
        note_obj_id = ObjectId(req.get("note_id"))
    except:
        return fl.jsonify({"message": "Invalid note ID"}), 400

    note = notes_col.find_one({"_id": note_obj_id, "owner": req.get("owner")})
    if not note:
        return fl.jsonify({"message": "Original note not found"}), 404

    notes_col.insert_one({
        "owner": fl.session["user"],
        "content": note.get("content", ""),
        "shared_from": req.get("owner"),
    })

    share_col.update_one(
        {"_id": req_obj_id},
        {"$set": {"status": "accepted", "responded_at": datetime.utcnow()}}
    )

    return fl.jsonify({"message": "Share request accepted"}), 200

@share_bp.route('/api/notes/requests/<request_id>/reject', methods=['POST'])
@login_required
def reject_share_request(request_id):
    try:
        req_obj_id = ObjectId(request_id)
    except:
        return fl.jsonify({"message": "Invalid request ID"}), 400

    req = share_col.find_one({
        "_id": req_obj_id,
        "recipient": fl.session["user"],
        "status": "pending",
    })
    if not req:
        return fl.jsonify({"message": "Share request not found"}), 404

    share_col.update_one(
        {"_id": req_obj_id},
        {"$set": {"status": "rejected", "responded_at": datetime.utcnow()}}
    )

    return fl.jsonify({"message": "Share request rejected"}), 200

@share_bp.route('/api/users', methods=['GET'])
@login_required
def list_users():
    users = list(col.find({}, {"username": 1}))
    result = []
    for user in users:
        username = user.get("username")
        if username and username != fl.session.get("user"):
            result.append({"username": username})
    return fl.jsonify(result)

@share_bp.route('/share/<note_id>', methods=['POST'])
def share(note_id):
    # Get the ID of the user we are sharing with.
    target_user_id = fl.request.form.get('user_id')

    if share_col(note_id, target_user_id):
        return {"message": "Shared successfully!"}, 200
    else:
        return {"message": "Failed to share or already shared."}, 400
